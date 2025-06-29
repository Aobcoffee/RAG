# Configuration Guide

This document explains how to configure the RAG SQL Agent for your environment.

## Database Configuration

### SQL Server
```yaml
database:
  sqlserver:
    driver: "ODBC Driver 17 for SQL Server"
    server: "your-server-name"
    port: 1433
    database: "your-database-name"
    username: "your-username"
    password: "your-password"
    trusted_connection: false
```

### PostgreSQL
```yaml
database:
  postgresql:
    host: "localhost"
    port: 5432
    database: "your-database-name"
    username: "your-username"
    password: "your-password"
```

### MySQL
```yaml
database:
  mysql:
    host: "localhost"
    port: 3306
    database: "your-database-name"
    username: "your-username"
    password: "your-password"
```

## LLM Configuration

### Ollama (Recommended)
```yaml
llm:
  provider: "ollama"
  model: "llama3.1"  # or codellama, mistral, etc.
  temperature: 0.1
  max_tokens: 4096
  base_url: "http://localhost:11434"
```

### OpenAI (Alternative)
```yaml
llm:
  provider: "openai"
  model: "gpt-4"
  temperature: 0.1
  max_tokens: 4096
  api_key: "your-openai-api-key"
```

## Embedding Configuration

### Ollama Embeddings
```yaml
embeddings:
  provider: "ollama"
  model: "nomic-embed-text"
  dimension: 768
```

### OpenAI Embeddings
```yaml
embeddings:
  provider: "openai"
  model: "text-embedding-3-small"
  dimension: 1536
```

## Vector Store Configuration

### ChromaDB (Recommended)
```yaml
vectorstore:
  provider: "chroma"
  persist_directory: "./data/vectorstore"
  collection_name: "database_schema"
```

### FAISS (Alternative)
```yaml
vectorstore:
  provider: "faiss"
  persist_directory: "./data/vectorstore"
  index_name: "schema_index"
```

## RAG Parameters

```yaml
rag:
  chunk_size: 1000          # Size of text chunks for embedding
  chunk_overlap: 200        # Overlap between chunks
  similarity_threshold: 0.7 # Minimum similarity for retrieval
  max_retrieved_docs: 5     # Maximum documents to retrieve
```

## Application Settings

```yaml
app:
  name: "RAG SQL Agent"
  version: "1.0.0"
  debug: true              # Enable debug mode
  log_level: "INFO"        # Logging level
  max_query_history: 100   # Maximum queries to keep in history
```

## Environment Variables

Create a `.env` file in the root directory:

```bash
# Database
DB_TYPE=sqlserver
DB_SERVER=localhost
DB_PORT=1433
DB_NAME=your_database
DB_USERNAME=your_username
DB_PASSWORD=your_password

# Ollama
OLLAMA_BASE_URL=http://localhost:11434
OLLAMA_MODEL=llama3.1
OLLAMA_EMBEDDING_MODEL=nomic-embed-text

# Application
LOG_LEVEL=INFO
DEBUG=True
```

## Security Considerations

1. **Database Credentials**: Store sensitive information in environment variables, not in configuration files.

2. **Network Security**: Ensure your database and Ollama service are properly secured.

3. **Data Privacy**: All processing happens locally when using Ollama, ensuring data privacy.

## Performance Tuning

### Database Optimization
- Ensure proper indexing on frequently queried columns
- Use connection pooling for high-load scenarios
- Monitor query performance and optimize as needed

### LLM Optimization
- Adjust `temperature` for more/less creative responses
- Modify `max_tokens` based on your query complexity
- Use faster models for simple queries, more capable models for complex analysis

### Vector Store Optimization
- Tune `chunk_size` and `chunk_overlap` based on your schema complexity
- Adjust `similarity_threshold` to balance relevance and recall
- Optimize `max_retrieved_docs` for your use case

## Troubleshooting

### Common Issues

1. **Database Connection Failed**
   - Check database credentials and network connectivity
   - Verify database driver installation
   - Ensure database server is running

2. **Ollama Model Not Found**
   - Run `ollama pull <model-name>` to download required models
   - Verify Ollama service is running with `ollama serve`

3. **Vector Store Initialization Failed**
   - Check directory permissions
   - Ensure sufficient disk space
   - Verify embedding model is available

4. **Poor Query Results**
   - Refresh schema embeddings with recent database changes
   - Adjust RAG parameters (similarity threshold, chunk size)
   - Review and optimize database schema documentation
