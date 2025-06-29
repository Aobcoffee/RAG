"""
RAG (Retrieval-Augmented Generation) pipeline for SQL query generation.
"""

from typing import List, Dict, Any, Optional, Tuple
import re
from langchain_core.documents import Document
from langchain_core.prompts import PromptTemplate

from ..utils.config import Config
from ..database.manager import DatabaseManager
from ..embeddings.schema_embeddings import SchemaEmbeddingManager
from ..llm.ollama_manager import OllamaManager


class SQLQueryGenerator:
    """Generates SQL queries from natural language using RAG pipeline."""
    
    def __init__(self, config: Config):
        self.config = config
        self.db_manager = DatabaseManager(config)
        self.embedding_manager = SchemaEmbeddingManager(config)
        self.llm_manager = OllamaManager(config)
        
        # Query generation prompts
        self.sql_generation_prompt = PromptTemplate.from_template(
            """You are an expert SQL query generator. Your task is to convert natural language questions into accurate SQL queries based on the provided database schema information.

Database Schema Information:
{schema_context}

User Question: {question}

Instructions:
1. Analyze the question carefully to understand what data is being requested
2. Use the provided schema information to identify relevant tables and columns
3. Generate a syntactically correct SQL query that answers the question
4. Consider relationships between tables and use appropriate JOINs when needed
5. Use aggregate functions (SUM, COUNT, AVG, etc.) when appropriate
6. Include proper filtering with WHERE clauses when needed
7. Order results logically when applicable

Important Rules:
- Only use tables and columns that exist in the provided schema
- Use proper SQL syntax for the database type
- Be careful with date/time comparisons and formatting
- Include comments in the SQL to explain complex logic
- If the question cannot be answered with the available schema, explain why

Generate ONLY the SQL query, no explanations unless the query cannot be generated.

SQL Query:"""
        )
        
        self.query_analysis_prompt = PromptTemplate.from_template(
            """You are a data analyst expert. Analyze the following SQL query results and provide insights.

Original Question: {question}
SQL Query: {sql_query}
Query Results: {results}

Provide a comprehensive analysis including:
1. Summary of findings
2. Key insights and trends
3. Notable patterns or anomalies
4. Business implications if applicable
5. Recommendations based on the data

Analysis:"""
        )
    
    def initialize(self) -> bool:
        """Initialize all components of the RAG pipeline."""
        try:
            # Initialize database connection
            if not self.db_manager.connect():
                raise RuntimeError("Failed to connect to database")
            
            # Initialize LLM
            if not self.llm_manager.initialize():
                raise RuntimeError("Failed to initialize LLM")
            
            # Initialize vector store
            if not self.embedding_manager.initialize_vectorstore():
                raise RuntimeError("Failed to initialize vector store")
            
            # Check if schema is already embedded
            schema_summary = self.embedding_manager.get_schema_summary()
            if schema_summary.get('total_documents', 0) == 0:
                print("No schema information found in vector store. Embedding schema...")
                self.embed_database_schema()
            
            return True
            
        except Exception as e:
            print(f"Failed to initialize RAG pipeline: {e}")
            return False
    
    def embed_database_schema(self) -> bool:
        """Embed database schema information into vector store."""
        try:
            # Get schema information
            schema_info = self.db_manager.get_schema_info()
            
            # Embed schema information
            success = self.embedding_manager.embed_schema_information(schema_info)
            
            if success:
                print("Database schema embedded successfully")
            
            return success
            
        except Exception as e:
            print(f"Failed to embed database schema: {e}")
            return False
    
    def process_question(self, question: str) -> Dict[str, Any]:
        """Process a natural language question and return SQL query with results."""
        try:
            # Step 1: Retrieve relevant schema information
            relevant_schema = self.embedding_manager.search_similar_schema_with_scores(question)
            
            if not relevant_schema:
                return {
                    'success': False,
                    'error': 'No relevant schema information found for the question',
                    'question': question
                }
            
            # Step 2: Format schema context
            schema_context = self._format_schema_context(relevant_schema)
            
            # Step 3: Generate SQL query
            sql_query = self._generate_sql_query(question, schema_context)
            
            if not sql_query:
                return {
                    'success': False,
                    'error': 'Failed to generate SQL query',
                    'question': question,
                    'schema_context': schema_context
                }
            
            # Step 4: Validate and execute query
            is_valid, validation_error = self.db_manager.validate_query(sql_query)
            if not is_valid:
                return {
                    'success': False,
                    'error': f'Generated SQL query is invalid: {validation_error}',
                    'question': question,
                    'sql_query': sql_query,
                    'schema_context': schema_context
                }
            
            # Execute query
            try:
                results, columns = self.db_manager.execute_query(sql_query)
            except Exception as e:
                return {
                    'success': False,
                    'error': f'Query execution failed: {str(e)}',
                    'question': question,
                    'sql_query': sql_query,
                    'schema_context': schema_context
                }
            
            # Step 5: Analyze results
            analysis = self._analyze_results(question, sql_query, results)
            
            return {
                'success': True,
                'question': question,
                'sql_query': sql_query,
                'results': results,
                'columns': columns,
                'analysis': analysis,
                'schema_used': [doc.metadata.get('name') for doc, _ in relevant_schema],
                'result_count': len(results)
            }
            
        except Exception as e:
            return {
                'success': False,
                'error': f'Error processing question: {str(e)}',
                'question': question
            }
    
    def _format_schema_context(self, relevant_schema: List[Tuple[Document, float]]) -> str:
        """Format retrieved schema information for the prompt."""
        context_parts = []
        
        for doc, score in relevant_schema:
            context_parts.append(f"Relevance Score: {1-score:.2f}")
            context_parts.append(doc.page_content)
            context_parts.append("---")
        
        return "\n".join(context_parts)
    
    def _generate_sql_query(self, question: str, schema_context: str) -> Optional[str]:
        """Generate SQL query using LLM."""
        try:
            prompt = self.sql_generation_prompt.format(
                question=question,
                schema_context=schema_context
            )
            
            response = self.llm_manager.generate_response(prompt)
            
            # Extract SQL query from response
            sql_query = self._extract_sql_from_response(response)
            
            return sql_query
            
        except Exception as e:
            print(f"Failed to generate SQL query: {e}")
            return None
    
    def _extract_sql_from_response(self, response: str) -> Optional[str]:
        """Extract SQL query from LLM response."""
        # Remove markdown code blocks if present
        response = response.strip()
        
        # Look for SQL code blocks
        sql_pattern = r'```sql\s*(.*?)\s*```'
        match = re.search(sql_pattern, response, re.DOTALL | re.IGNORECASE)
        
        if match:
            return match.group(1).strip()
        
        # Look for code blocks without language specification
        code_pattern = r'```\s*(.*?)\s*```'
        match = re.search(code_pattern, response, re.DOTALL)
        
        if match:
            potential_sql = match.group(1).strip()
            # Check if it looks like SQL
            if any(keyword in potential_sql.upper() for keyword in ['SELECT', 'INSERT', 'UPDATE', 'DELETE', 'WITH']):
                return potential_sql
        
        # If no code blocks, try to find SQL-like content
        lines = response.split('\n')
        sql_lines = []
        in_sql = False
        
        for line in lines:
            line = line.strip()
            if any(line.upper().startswith(keyword) for keyword in ['SELECT', 'WITH', 'INSERT', 'UPDATE', 'DELETE']):
                in_sql = True
                sql_lines.append(line)
            elif in_sql and line and not line.startswith('--') and not line.startswith('#'):
                sql_lines.append(line)
            elif in_sql and (not line or line.endswith(';')):
                if line:
                    sql_lines.append(line)
                break
        
        if sql_lines:
            return '\n'.join(sql_lines)
        
        # Last resort: return the whole response if it looks like SQL
        if any(keyword in response.upper() for keyword in ['SELECT', 'FROM', 'WHERE', 'JOIN']):
            return response.strip()
        
        return None
    
    def _analyze_results(self, question: str, sql_query: str, results: List[Dict]) -> str:
        """Analyze query results using LLM."""
        try:
            # Limit results for analysis to avoid token limits
            analysis_results = results[:10] if len(results) > 10 else results
            
            prompt = self.query_analysis_prompt.format(
                question=question,
                sql_query=sql_query,
                results=analysis_results
            )
            
            analysis = self.llm_manager.generate_response(prompt)
            return analysis
            
        except Exception as e:
            return f"Analysis failed: {str(e)}"
    
    def get_schema_summary(self) -> Dict[str, Any]:
        """Get summary of available database schema."""
        try:
            return self.embedding_manager.get_schema_summary()
        except Exception as e:
            return {'error': str(e)}
    
    def get_available_tables(self) -> List[str]:
        """Get list of available tables."""
        try:
            return self.embedding_manager.get_all_table_names()
        except Exception as e:
            return []
    
    def refresh_schema(self) -> bool:
        """Refresh the embedded schema information."""
        try:
            return self.embed_database_schema()
        except Exception as e:
            print(f"Failed to refresh schema: {e}")
            return False
    
    def close(self):
        """Clean up resources."""
        if self.db_manager:
            self.db_manager.disconnect()
