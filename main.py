"""
Main entry point for the RAG SQL Agent.
"""

import os
import sys
from pathlib import Path

# Add src to Python path
sys.path.append(str(Path(__file__).parent / 'src'))

from src.agents.rag_agent import RAGSQLAgent
from src.utils.logger import setup_logger
from src.utils.config import load_config


def main():
    """Main function to run the RAG SQL Agent."""
    print("🚀 Starting RAG SQL Agent")
    print("=" * 50)
    
    # Setup logging
    setup_logger()
    
    # Load configuration
    try:
        config = load_config()
        print(f"📋 Configuration loaded successfully")
    except Exception as e:
        print(f"❌ Failed to load configuration: {e}")
        return
    
    # Initialize agent
    agent = RAGSQLAgent()
    
    if not agent.initialize():
        print("❌ Failed to initialize agent. Please check your configuration.")
        return
    
    print("\n" + "=" * 50)
    print("🤖 RAG SQL Agent is ready!")
    print("Type 'help' for available commands or 'quit' to exit.")
    print("=" * 50)
    
    # Interactive loop
    try:
        while True:
            try:
                user_input = input("\n💬 Ask me anything about your database: ").strip()
                
                if not user_input:
                    continue
                
                if user_input.lower() in ['quit', 'exit', 'q']:
                    print("👋 Goodbye!")
                    break
                
                elif user_input.lower() == 'help':
                    print(agent.help())
                
                elif user_input.lower() == 'stats':
                    stats = agent.get_stats()
                    print("\n📊 Agent Statistics:")
                    for key, value in stats.items():
                        print(f"  {key.replace('_', ' ').title()}: {value}")
                
                elif user_input.lower() == 'tables':
                    tables = agent.get_available_tables()
                    if tables:
                        print(f"\n📋 Available tables: {', '.join(tables)}")
                    else:
                        print("No tables found")
                
                elif user_input.lower() == 'schema':
                    schema_info = agent.get_schema_info()
                    print(f"\n📊 Schema Summary: {schema_info}")
                
                elif user_input.lower() == 'refresh':
                    agent.refresh_schema()
                
                elif user_input.lower() == 'history':
                    history = agent.get_query_history(5)  # Last 5 queries
                    if history:
                        print("\n📜 Recent Query History:")
                        for i, query in enumerate(history, 1):
                            status = "✅" if query.get('success') else "❌"
                            print(f"  {i}. {status} {query.get('question', 'Unknown')}")
                    else:
                        print("No query history available")
                
                elif user_input.lower() == 'clear':
                    agent.clear_history()
                
                else:
                    # Process as a natural language question
                    result = agent.ask(user_input)
                    
                    # The result display is handled by the agent
                    # Additional processing can be done here if needed
                
            except KeyboardInterrupt:
                print("\n👋 Goodbye!")
                break
            except Exception as e:
                print(f"❌ Error: {e}")
    
    finally:
        agent.close()


if __name__ == "__main__":
    main()
