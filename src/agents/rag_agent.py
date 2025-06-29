"""
Main RAG AI Agent for SQL database querying.
"""

from typing import Dict, Any, List, Optional
import time
from datetime import datetime

from ..utils.config import Config
from ..rag.sql_generator import SQLQueryGenerator


class RAGSQLAgent:
    """Main RAG AI Agent for natural language to SQL querying."""
    
    def __init__(self, config_path: str = "config/config.yaml"):
        self.config = Config()
        self.sql_generator = SQLQueryGenerator(self.config)
        self.query_history: List[Dict[str, Any]] = []
        self.is_initialized = False
        
    def initialize(self) -> bool:
        """Initialize the RAG SQL Agent."""
        try:
            print("🚀 Initializing RAG SQL Agent...")
            
            # Initialize the SQL query generator
            success = self.sql_generator.initialize()
            
            if success:
                self.is_initialized = True
                print("✅ RAG SQL Agent initialized successfully!")
                
                # Display available tables
                tables = self.sql_generator.get_available_tables()
                if tables:
                    print(f"📊 Available tables: {', '.join(tables)}")
                
                return True
            else:
                print("❌ Failed to initialize RAG SQL Agent")
                return False
                
        except Exception as e:
            print(f"❌ Initialization error: {e}")
            return False
    
    def ask(self, question: str) -> Dict[str, Any]:
        """Ask a question in natural language and get SQL results with analysis."""
        if not self.is_initialized:
            return {
                'success': False,
                'error': 'Agent not initialized. Call initialize() first.',
                'question': question
            }
        
        if not question.strip():
            return {
                'success': False,
                'error': 'Question cannot be empty',
                'question': question
            }
        
        print(f"🤔 Processing question: {question}")
        start_time = time.time()
        
        try:
            # Process the question
            result = self.sql_generator.process_question(question)
            
            # Add timing and metadata
            processing_time = time.time() - start_time
            result['processing_time'] = round(processing_time, 2)
            result['timestamp'] = datetime.now().isoformat()
            
            # Add to history
            self.query_history.append(result)
            
            # Keep only recent history
            if len(self.query_history) > self.config.app.max_query_history:
                self.query_history = self.query_history[-self.config.app.max_query_history:]
            
            # Display results
            self._display_result(result)
            
            return result
            
        except Exception as e:
            error_result = {
                'success': False,
                'error': f'Unexpected error: {str(e)}',
                'question': question,
                'processing_time': time.time() - start_time,
                'timestamp': datetime.now().isoformat()
            }
            
            self.query_history.append(error_result)
            return error_result
    
    def _display_result(self, result: Dict[str, Any]):
        """Display the result in a formatted way."""
        if result['success']:
            print(f"✅ Query processed successfully in {result['processing_time']}s")
            print(f"📝 Generated SQL: {result['sql_query']}")
            print(f"📊 Returned {result['result_count']} rows")
            
            if result.get('results'):
                print("\n🔍 Results:")
                # Display first few rows
                for i, row in enumerate(result['results'][:5]):
                    print(f"  {i+1}. {row}")
                
                if len(result['results']) > 5:
                    print(f"  ... and {len(result['results']) - 5} more rows")
            
            if result.get('analysis'):
                print(f"\n📈 Analysis:")
                print(result['analysis'])
        else:
            print(f"❌ Error: {result['error']}")
            if result.get('sql_query'):
                print(f"Generated SQL: {result['sql_query']}")
    
    def get_schema_info(self) -> Dict[str, Any]:
        """Get information about the database schema."""
        if not self.is_initialized:
            return {'error': 'Agent not initialized'}
        
        return self.sql_generator.get_schema_summary()
    
    def get_available_tables(self) -> List[str]:
        """Get list of available tables."""
        if not self.is_initialized:
            return []
        
        return self.sql_generator.get_available_tables()
    
    def refresh_schema(self) -> bool:
        """Refresh the database schema information."""
        if not self.is_initialized:
            return False
        
        print("🔄 Refreshing database schema...")
        success = self.sql_generator.refresh_schema()
        
        if success:
            print("✅ Schema refreshed successfully!")
        else:
            print("❌ Failed to refresh schema")
        
        return success
    
    def get_query_history(self, limit: Optional[int] = None) -> List[Dict[str, Any]]:
        """Get query history."""
        if limit:
            return self.query_history[-limit:]
        return self.query_history.copy()
    
    def clear_history(self):
        """Clear query history."""
        self.query_history.clear()
        print("🗑️ Query history cleared")
    
    def get_stats(self) -> Dict[str, Any]:
        """Get agent statistics."""
        if not self.query_history:
            return {
                'total_queries': 0,
                'successful_queries': 0,
                'failed_queries': 0,
                'success_rate': 0.0,
                'average_processing_time': 0.0
            }
        
        total_queries = len(self.query_history)
        successful_queries = sum(1 for q in self.query_history if q.get('success'))
        failed_queries = total_queries - successful_queries
        success_rate = (successful_queries / total_queries) * 100 if total_queries > 0 else 0
        
        processing_times = [q.get('processing_time', 0) for q in self.query_history if q.get('processing_time')]
        avg_processing_time = sum(processing_times) / len(processing_times) if processing_times else 0
        
        return {
            'total_queries': total_queries,
            'successful_queries': successful_queries,
            'failed_queries': failed_queries,
            'success_rate': round(success_rate, 1),
            'average_processing_time': round(avg_processing_time, 2)
        }
    
    def help(self) -> str:
        """Get help information."""
        return """
🤖 RAG SQL Agent Help

Available Commands:
- ask(question): Ask a natural language question about your database
- get_schema_info(): Get information about database schema
- get_available_tables(): Get list of available tables
- refresh_schema(): Refresh database schema information
- get_query_history(limit): Get query history
- clear_history(): Clear query history
- get_stats(): Get agent statistics
- help(): Show this help message

Example Questions:
- "What are the sales last month?"
- "Show me the top 10 customers by revenue"
- "What's the average order value this quarter?"
- "Which products have the highest profit margins?"
- "How many orders were placed yesterday?"

Tips:
- Be specific about time periods (last month, this year, etc.)
- Mention specific metrics you're interested in
- Ask about relationships between data (customers and orders, products and sales)
        """
    
    def close(self):
        """Clean up resources."""
        if self.sql_generator:
            self.sql_generator.close()
        print("👋 RAG SQL Agent closed")
