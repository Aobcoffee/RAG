# Quick Start Guide

This guide will help you get the RAG SQL Agent up and running quickly.

## Prerequisites

1. **Python 3.8+** installed on your system
2. **SQL Server database** (or PostgreSQL/MySQL) with sample data
3. **Ollama** installed for local AI processing

## Installation Steps

### Option 1: Automated Setup (Recommended)

1. **Run the setup script:**
   ```bash
   # On Windows
   setup.bat
   
   # On Linux/Mac
   python setup.py
   ```

2. **Follow the prompts** to complete the setup

### Option 2: Manual Setup

1. **Install Python dependencies:**
   ```bash
   pip install -r requirements.txt
   ```

2. **Install and setup Ollama:**
   ```bash
   # Download from https://ollama.ai
   ollama serve
   ollama pull llama3.1
   ollama pull nomic-embed-text
   ```

3. **Configure database connection:**
   ```bash
   # Copy example configuration
   cp config/.env.example .env
   
   # Edit .env with your database credentials
   # Edit config/config.yaml with your settings
   ```

4. **Initialize database schema:**
   ```bash
   python scripts/initialize_schema.py
   ```

## Configuration

### Database Setup

1. **Edit `.env` file:**
   ```bash
   DB_TYPE=sqlserver
   DB_SERVER=your-server
   DB_NAME=your-database
   DB_USERNAME=your-username
   DB_PASSWORD=your-password
   ```

2. **Or edit `config/config.yaml`:**
   ```yaml
   database:
     sqlserver:
       server: "your-server"
       database: "your-database"
       username: "your-username"
       password: "your-password"
   ```

### Sample Database (Optional)

If you don't have a database, you can use our sample schema:

```bash
# Run the sample database script on your SQL Server
sqlcmd -S your-server -d your-database -i data/sample_database.sql
```

## Running the Agent

### Console Interface
```bash
python main.py
```

### Web Interface
```bash
streamlit run ui/streamlit_app.py
```

## Example Usage

Once running, you can ask questions like:

- "What are the total sales last month?"
- "Show me the top 10 customers by revenue"
- "What's the average order value this quarter?"
- "Which products have the highest profit margins?"
- "How many new customers did we get this year?"

## Troubleshooting

### Common Issues

1. **Database Connection Failed**
   - Check your database credentials in `.env`
   - Ensure database server is running and accessible
   - Verify your database driver is installed

2. **Ollama Not Found**
   - Install Ollama from https://ollama.ai
   - Start the service: `ollama serve`
   - Pull required models: `ollama pull llama3.1`

3. **Import Errors**
   - Ensure all dependencies are installed: `pip install -r requirements.txt`
   - Check Python version: `python --version` (3.8+ required)

4. **Schema Not Found**
   - Run the schema initialization: `python scripts/initialize_schema.py`
   - Check that your database has tables with data

### Getting Help

1. Check the logs in the `logs/` directory
2. Run tests: `python tests/test_rag_agent.py`
3. Review configuration in `config/README.md`

## Next Steps

1. **Explore the Web Interface** - Try the Streamlit web app for a better user experience
2. **Customize Prompts** - Modify the SQL generation prompts in `src/rag/sql_generator.py`
3. **Add Your Data** - Connect to your actual production database
4. **Optimize Performance** - Tune the RAG parameters in the configuration

## Support

For issues or questions:
- Check the documentation in the `config/` directory
- Review the test files in `tests/` for examples
- Examine the sample database schema in `data/sample_database.sql`

Happy querying! 🤖📊
