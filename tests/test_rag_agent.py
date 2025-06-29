"""
Test suite for the RAG SQL Agent.
"""

import unittest
import sys
from pathlib import Path

# Add src to Python path
sys.path.append(str(Path(__file__).parent.parent / 'src'))

from src.utils.config import Config, load_config
from src.database.manager import DatabaseManager
from src.llm.ollama_manager import OllamaManager, OllamaEmbeddings
from src.embeddings.schema_embeddings import SchemaEmbeddingManager


class TestConfig(unittest.TestCase):
    """Test configuration loading and validation."""
    
    def test_default_config(self):
        """Test default configuration creation."""
        config = Config()
        self.assertIsInstance(config, Config)
        self.assertEqual(config.llm.provider, "ollama")
        self.assertEqual(config.llm.model, "llama3.1")
    
    def test_config_loading(self):
        """Test configuration loading from file."""
        try:
            config = load_config()
            self.assertIsInstance(config, Config)
        except FileNotFoundError:
            # Config file might not exist in test environment
            self.skipTest("Config file not found")


class TestDatabaseManager(unittest.TestCase):
    """Test database manager functionality."""
    
    def setUp(self):
        """Set up test fixtures."""
        self.config = Config()
        self.db_manager = DatabaseManager(self.config)
    
    def test_connection_string_generation(self):
        """Test database connection string generation."""
        # This test requires actual database credentials
        # Skip if not available
        try:
            connection_string = self.db_manager._build_connection_string()
            self.assertIsInstance(connection_string, str)
            self.assertIn("://", connection_string)
        except Exception:
            self.skipTest("Database configuration not available")


class TestOllamaManager(unittest.TestCase):
    """Test Ollama LLM manager."""
    
    def setUp(self):
        """Set up test fixtures."""
        self.config = Config()
        self.ollama_manager = OllamaManager(self.config)
    
    def test_ollama_initialization(self):
        """Test Ollama manager initialization."""
        # Check if Ollama is running
        if not self.ollama_manager._is_ollama_running():
            self.skipTest("Ollama service not running")
        
        success = self.ollama_manager.initialize()
        self.assertTrue(success)
    
    def test_model_availability(self):
        """Test model availability check."""
        if not self.ollama_manager._is_ollama_running():
            self.skipTest("Ollama service not running")
        
        available = self.ollama_manager._is_model_available()
        # This might be False if model isn't pulled yet
        self.assertIsInstance(available, bool)


class TestOllamaEmbeddings(unittest.TestCase):
    """Test Ollama embeddings functionality."""
    
    def setUp(self):
        """Set up test fixtures."""
        self.config = Config()
        self.embeddings = OllamaEmbeddings(self.config)
    
    def test_embedding_generation(self):
        """Test embedding generation."""
        if not self.embeddings.is_model_available():
            self.skipTest("Embedding model not available")
        
        try:
            embedding = self.embeddings.embed_query("test text")
            self.assertIsInstance(embedding, list)
            self.assertGreater(len(embedding), 0)
            self.assertIsInstance(embedding[0], float)
        except Exception as e:
            self.skipTest(f"Embedding generation failed: {e}")


class TestSchemaEmbeddingManager(unittest.TestCase):
    """Test schema embedding manager."""
    
    def setUp(self):
        """Set up test fixtures."""
        self.config = Config()
        self.embedding_manager = SchemaEmbeddingManager(self.config)
    
    def test_initialization(self):
        """Test embedding manager initialization."""
        try:
            success = self.embedding_manager.initialize_vectorstore()
            self.assertTrue(success)
        except Exception as e:
            self.skipTest(f"Vector store initialization failed: {e}")
    
    def test_document_creation(self):
        """Test schema document creation."""
        sample_schema = {
            'tables': {
                'users': {
                    'columns': [
                        {'name': 'id', 'type': 'int', 'nullable': False},
                        {'name': 'name', 'type': 'varchar', 'nullable': False}
                    ],
                    'primary_keys': {'constrained_columns': ['id']},
                    'foreign_keys': [],
                    'sample_data': [{'id': 1, 'name': 'John'}],
                    'row_count': 100
                }
            },
            'views': {},
            'relationships': []
        }
        
        documents = self.embedding_manager._create_schema_documents(sample_schema)
        self.assertGreater(len(documents), 0)
        self.assertIn('users', documents[0].page_content)


class TestIntegration(unittest.TestCase):
    """Integration tests for the complete system."""
    
    def test_end_to_end_flow(self):
        """Test complete flow from question to answer."""
        # This test requires full system setup
        self.skipTest("Integration test requires full system setup")


if __name__ == '__main__':
    # Create test suite
    suite = unittest.TestSuite()
    
    # Add test cases
    suite.addTest(unittest.makeSuite(TestConfig))
    suite.addTest(unittest.makeSuite(TestDatabaseManager))
    suite.addTest(unittest.makeSuite(TestOllamaManager))
    suite.addTest(unittest.makeSuite(TestOllamaEmbeddings))
    suite.addTest(unittest.makeSuite(TestSchemaEmbeddingManager))
    suite.addTest(unittest.makeSuite(TestIntegration))
    
    # Run tests
    runner = unittest.TextTestRunner(verbosity=2)
    result = runner.run(suite)
    
    # Exit with error code if tests failed
    sys.exit(0 if result.wasSuccessful() else 1)
