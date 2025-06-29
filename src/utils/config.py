"""
Configuration management using Pydantic for type safety and validation.
"""

import os
from typing import Optional
from pydantic import BaseModel, Field
from pydantic_settings import BaseSettings
import yaml


class DatabaseSQLServerConfig(BaseModel):
    """SQL Server database configuration."""
    driver: str = "ODBC Driver 17 for SQL Server"
    server: str = "localhost"
    port: int = 1433
    database: str = "your_database_name"
    username: str = "your_username"
    password: str = "your_password"
    trusted_connection: bool = False
    connection_timeout: int = 30


class DatabasePostgreSQLConfig(BaseModel):
    """PostgreSQL database configuration."""
    host: str = "localhost"
    port: int = 5432
    database: str = "your_database_name"
    username: str = "your_username"
    password: str = "your_password"


class DatabaseMySQLConfig(BaseModel):
    """MySQL database configuration."""
    host: str = "localhost"
    port: int = 3306
    database: str = "your_database_name"
    username: str = "your_username"
    password: str = "your_password"


class DatabaseConfig(BaseModel):
    """Database configuration."""
    sqlserver: DatabaseSQLServerConfig = DatabaseSQLServerConfig()
    postgresql: DatabasePostgreSQLConfig = DatabasePostgreSQLConfig()
    mysql: DatabaseMySQLConfig = DatabaseMySQLConfig()


class LLMConfig(BaseModel):
    """LLM configuration."""
    provider: str = "ollama"
    model: str = "llama3.1"
    temperature: float = 0.1
    max_tokens: int = 4096
    base_url: str = "http://localhost:11434"


class EmbeddingConfig(BaseModel):
    """Embedding configuration."""
    provider: str = "ollama"
    model: str = "nomic-embed-text"
    dimension: int = 768


class VectorStoreConfig(BaseModel):
    """Vector store configuration."""
    provider: str = "chroma"
    persist_directory: str = "./data/vectorstore"
    collection_name: str = "database_schema"


class RAGConfig(BaseModel):
    """RAG configuration."""
    chunk_size: int = 1000
    chunk_overlap: int = 200
    similarity_threshold: float = 0.7
    max_retrieved_docs: int = 5


class AppConfig(BaseModel):
    """Application configuration."""
    name: str = "RAG SQL Agent"
    version: str = "1.0.0"
    debug: bool = True
    log_level: str = "INFO"
    max_query_history: int = 100


class Config(BaseSettings):
    """Main configuration class."""
    database: DatabaseConfig = DatabaseConfig()
    llm: LLMConfig = LLMConfig()
    embeddings: EmbeddingConfig = EmbeddingConfig()
    vectorstore: VectorStoreConfig = VectorStoreConfig()
    rag: RAGConfig = RAGConfig()
    app: AppConfig = AppConfig()
    
    class Config:
        env_file = ".env"
        env_file_encoding = "utf-8"
        case_sensitive = False


def load_config(config_path: str = "config/config.yaml") -> Config:
    """Load configuration from YAML file and environment variables."""
    config_data = {}
    
    # Load from YAML file if it exists
    if os.path.exists(config_path):
        with open(config_path, 'r', encoding='utf-8') as f:
            config_data = yaml.safe_load(f)
    
    # Create config instance (will also load from .env file)
    if config_data:
        return Config(**config_data)
    else:
        return Config()
