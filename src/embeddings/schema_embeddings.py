"""
Vector embeddings and storage management for RAG pipeline.
"""

import os
from typing import List, Dict, Any, Optional, Tuple
import json
import numpy as np
from langchain_text_splitters import RecursiveCharacterTextSplitter
from langchain_community.vectorstores import Chroma
from langchain_core.documents import Document

from ..utils.config import Config
from ..llm.ollama_manager import OllamaEmbeddings


class SchemaEmbeddingManager:
    """Manages embedding and vector storage of database schema information."""
    
    def __init__(self, config: Config):
        self.config = config
        self.embeddings = OllamaEmbeddings(config)
        self.vectorstore: Optional[Chroma] = None
        self.text_splitter = RecursiveCharacterTextSplitter(
            chunk_size=config.rag.chunk_size,
            chunk_overlap=config.rag.chunk_overlap,
            separators=["\n\n", "\n", " ", ""]
        )
        
    def initialize_vectorstore(self) -> bool:
        """Initialize the vector store."""
        try:
            # Ensure the persist directory exists
            os.makedirs(self.config.vectorstore.persist_directory, exist_ok=True)
            
            # Initialize Chroma vector store
            self.vectorstore = Chroma(
                collection_name=self.config.vectorstore.collection_name,
                embedding_function=self.embeddings,
                persist_directory=self.config.vectorstore.persist_directory
            )
            
            return True
            
        except Exception as e:
            print(f"Failed to initialize vector store: {e}")
            return False
    
    def embed_schema_information(self, schema_info: Dict[str, Any]) -> bool:
        """Embed database schema information into vector store."""
        if not self.vectorstore:
            raise RuntimeError("Vector store not initialized")
        
        try:
            documents = self._create_schema_documents(schema_info)
            
            # Clear existing schema documents
            self._clear_existing_documents()
            
            # Add new documents
            if documents:
                self.vectorstore.add_documents(documents)
                print(f"Successfully embedded {len(documents)} schema documents")
            
            return True
            
        except Exception as e:
            print(f"Failed to embed schema information: {e}")
            return False
    
    def _create_schema_documents(self, schema_info: Dict[str, Any]) -> List[Document]:
        """Create documents from schema information."""
        documents = []
        
        # Process tables
        for table_name, table_info in schema_info.get('tables', {}).items():
            doc_content = self._format_table_info(table_name, table_info)
            
            document = Document(
                page_content=doc_content,
                metadata={
                    'type': 'table',
                    'name': table_name,
                    'row_count': table_info.get('row_count', 0)
                }
            )
            documents.append(document)
        
        # Process views
        for view_name, view_info in schema_info.get('views', {}).items():
            doc_content = self._format_view_info(view_name, view_info)
            
            document = Document(
                page_content=doc_content,
                metadata={
                    'type': 'view',
                    'name': view_name
                }
            )
            documents.append(document)
        
        # Process relationships
        if schema_info.get('relationships'):
            doc_content = self._format_relationships_info(schema_info['relationships'])
            
            document = Document(
                page_content=doc_content,
                metadata={
                    'type': 'relationships',
                    'name': 'database_relationships'
                }
            )
            documents.append(document)
        
        return documents
    
    def _format_table_info(self, table_name: str, table_info: Dict[str, Any]) -> str:
        """Format table information for embedding."""
        content = f"Table: {table_name}\n"
        content += f"Description: This is a database table named {table_name}\n"
        
        # Add column information
        content += "Columns:\n"
        for column in table_info.get('columns', []):
            col_info = f"- {column['name']} ({column['type']}"
            if column.get('nullable') is False:
                col_info += ", NOT NULL"
            if column.get('default'):
                col_info += f", DEFAULT {column['default']}"
            col_info += ")\n"
            content += col_info
        
        # Add primary keys
        pk_info = table_info.get('primary_keys', {})
        if pk_info.get('constrained_columns'):
            content += f"Primary Key: {', '.join(pk_info['constrained_columns'])}\n"
        
        # Add foreign keys
        for fk in table_info.get('foreign_keys', []):
            content += f"Foreign Key: {', '.join(fk['constrained_columns'])} -> {fk['referred_table']}.{', '.join(fk['referred_columns'])}\n"
        
        # Add sample data context
        sample_data = table_info.get('sample_data', [])
        if sample_data:
            content += "Sample data shows:\n"
            for row in sample_data[:2]:  # Only include first 2 rows
                content += f"- {row}\n"
        
        # Add row count
        row_count = table_info.get('row_count')
        if row_count is not None:
            content += f"Approximate row count: {row_count}\n"
        
        return content
    
    def _format_view_info(self, view_name: str, view_info: Dict[str, Any]) -> str:
        """Format view information for embedding."""
        content = f"View: {view_name}\n"
        content += f"Description: This is a database view named {view_name}\n"
        
        # Add column information
        content += "Columns:\n"
        for column in view_info.get('columns', []):
            content += f"- {column['name']} ({column['type']})\n"
        
        return content
    
    def _format_relationships_info(self, relationships: List[Dict[str, Any]]) -> str:
        """Format relationship information for embedding."""
        content = "Database Relationships:\n"
        content += "This document describes the foreign key relationships between tables.\n\n"
        
        for rel in relationships:
            content += f"- {rel['source_table']}.{', '.join(rel['source_columns'])} references {rel['target_table']}.{', '.join(rel['target_columns'])}\n"
        
        return content
    
    def _clear_existing_documents(self):
        """Clear existing documents from vector store."""
        try:
            # Get all document IDs and delete them
            collection = self.vectorstore._collection
            collection.delete()
        except Exception as e:
            print(f"Warning: Could not clear existing documents: {e}")
    
    def search_similar_schema(self, query: str, k: int = None) -> List[Document]:
        """Search for similar schema information."""
        if not self.vectorstore:
            raise RuntimeError("Vector store not initialized")
        
        k = k or self.config.rag.max_retrieved_docs
        
        try:
            # Search for similar documents
            docs = self.vectorstore.similarity_search(
                query=query,
                k=k
            )
            
            return docs
            
        except Exception as e:
            print(f"Failed to search schema: {e}")
            return []
    
    def search_similar_schema_with_scores(self, query: str, k: int = None) -> List[Tuple[Document, float]]:
        """Search for similar schema information with similarity scores."""
        if not self.vectorstore:
            raise RuntimeError("Vector store not initialized")
        
        k = k or self.config.rag.max_retrieved_docs
        
        try:
            # Search for similar documents with scores
            docs_with_scores = self.vectorstore.similarity_search_with_score(
                query=query,
                k=k
            )
            
            # Filter by similarity threshold
            filtered_docs = [
                (doc, score) for doc, score in docs_with_scores
                if score <= (1.0 - self.config.rag.similarity_threshold)  # Chroma uses distance, not similarity
            ]
            
            return filtered_docs
            
        except Exception as e:
            print(f"Failed to search schema with scores: {e}")
            return []
    
    def get_all_table_names(self) -> List[str]:
        """Get all table names from vector store."""
        if not self.vectorstore:
            return []
        
        try:
            # Get all documents with table type
            all_docs = self.vectorstore.get()
            
            table_names = []
            for metadata in all_docs.get('metadatas', []):
                if metadata.get('type') == 'table':
                    table_names.append(metadata.get('name'))
            
            return list(set(table_names))  # Remove duplicates
            
        except Exception as e:
            print(f"Failed to get table names: {e}")
            return []
    
    def get_schema_summary(self) -> Dict[str, Any]:
        """Get a summary of embedded schema information."""
        if not self.vectorstore:
            return {}
        
        try:
            all_docs = self.vectorstore.get()
            
            summary = {
                'total_documents': len(all_docs.get('documents', [])),
                'tables': 0,
                'views': 0,
                'relationships': 0
            }
            
            for metadata in all_docs.get('metadatas', []):
                doc_type = metadata.get('type', 'unknown')
                if doc_type in summary:
                    summary[doc_type] += 1
            
            return summary
            
        except Exception as e:
            print(f"Failed to get schema summary: {e}")
            return {}
