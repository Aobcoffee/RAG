"""RAG SQL Agent - Main package."""

__version__ = "1.0.0"
__author__ = "RAG Development Team"
__description__ = "A powerful local RAG AI agent for SQL database querying using LangChain and Ollama"

from .agents import RAGSQLAgent

__all__ = ['RAGSQLAgent']
