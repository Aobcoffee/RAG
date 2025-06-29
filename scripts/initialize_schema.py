"""
Database schema initialization script.
Run this script to initialize and embed your database schema.
"""

import sys
from pathlib import Path

# Add src to Python path
sys.path.append(str(Path(__file__).parent.parent / 'src'))

from src.database.manager import DatabaseManager
from src.embeddings.schema_embeddings import SchemaEmbeddingManager
from src.utils.config import load_config
from src.utils.logger import setup_logger


def main():
    """Initialize database schema and embeddings."""
    print("🚀 Database Schema Initialization")
    print("=" * 50)
    
    # Setup logging
    setup_logger()
    
    try:
        # Load configuration
        config = load_config()
        print("✅ Configuration loaded")
        
        # Initialize database manager
        db_manager = DatabaseManager(config)
        print("🔌 Connecting to database...")
        
        if not db_manager.connect():
            print("❌ Failed to connect to database")
            return False
        
        print("✅ Database connected successfully")
        
        # Get schema information
        print("📊 Analyzing database schema...")
        schema_info = db_manager.get_schema_info()
        
        table_count = len(schema_info.get('tables', {}))
        view_count = len(schema_info.get('views', {}))
        relationship_count = len(schema_info.get('relationships', []))
        
        print(f"✅ Schema analysis complete:")
        print(f"   - Tables: {table_count}")
        print(f"   - Views: {view_count}")
        print(f"   - Relationships: {relationship_count}")
        
        # Initialize embedding manager
        embedding_manager = SchemaEmbeddingManager(config)
        print("🔧 Initializing vector store...")
        
        if not embedding_manager.initialize_vectorstore():
            print("❌ Failed to initialize vector store")
            return False
        
        print("✅ Vector store initialized")
        
        # Embed schema information
        print("🧠 Embedding schema information...")
        if not embedding_manager.embed_schema_information(schema_info):
            print("❌ Failed to embed schema information")
            return False
        
        print("✅ Schema information embedded successfully")
        
        # Verify embeddings
        summary = embedding_manager.get_schema_summary()
        print(f"📋 Embedding summary: {summary}")
        
        # Test search
        print("🔍 Testing schema search...")
        test_results = embedding_manager.search_similar_schema("sales revenue customers")
        print(f"✅ Search test complete - found {len(test_results)} relevant documents")
        
        # Cleanup
        db_manager.disconnect()
        print("✅ Database disconnected")
        
        print("\n" + "=" * 50)
        print("🎉 Schema initialization completed successfully!")
        print("You can now use the RAG SQL Agent to query your database.")
        
        return True
        
    except Exception as e:
        print(f"❌ Error during initialization: {e}")
        return False


if __name__ == "__main__":
    success = main()
    sys.exit(0 if success else 1)
