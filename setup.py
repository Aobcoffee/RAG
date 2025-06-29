#!/usr/bin/env python3
"""
Complete setup and run script for RAG SQL Agent.
This script handles the entire setup process and provides multiple run options.
"""

import os
import sys
import subprocess
import time
import shutil
from pathlib import Path


def print_banner():
    """Print welcome banner."""
    print("""
    ██████╗  █████╗  ██████╗     ███████╗ ██████╗ ██╗         
    ██╔══██╗██╔══██╗██╔════╝     ██╔════╝██╔═══██╗██║         
    ██████╔╝███████║██║  ███╗    ███████╗██║   ██║██║         
    ██╔══██╗██╔══██║██║   ██║    ╚════██║██║▄▄ ██║██║         
    ██║  ██║██║  ██║╚██████╔╝    ███████║╚██████╔╝███████╗    
    ╚═╝  ╚═╝╚═╝  ╚═╝ ╚═════╝     ╚══════╝ ╚══▀▀═╝ ╚══════╝    
                                                               
     █████╗  ██████╗ ███████╗███╗   ██╗████████╗               
    ██╔══██╗██╔════╝ ██╔════╝████╗  ██║╚══██╔══╝               
    ███████║██║  ███╗█████╗  ██╔██╗ ██║   ██║                  
    ██╔══██║██║   ██║██╔══╝  ██║╚██╗██║   ██║                  
    ██║  ██║╚██████╔╝███████╗██║ ╚████║   ██║                  
    ╚═╝  ╚═╝ ╚═════╝ ╚══════╝╚═╝  ╚═══╝   ╚═╝                  
    
    🤖 RAG SQL Agent - Natural Language Database Querying
    """)


def check_python_version():
    """Check if Python version is compatible."""
    if sys.version_info < (3, 8):
        print("❌ Python 3.8 or higher is required")
        return False
    print(f"✅ Python {sys.version_info.major}.{sys.version_info.minor} detected")
    return True


def check_and_install_requirements():
    """Check and install Python requirements."""
    print("📦 Checking Python dependencies...")
    
    requirements_file = Path("requirements.txt")
    if not requirements_file.exists():
        print("❌ requirements.txt not found")
        return False
    
    try:
        # Check if pip is available
        subprocess.run([sys.executable, "-m", "pip", "--version"], 
                      check=True, capture_output=True)
        
        # Install requirements
        print("📥 Installing Python dependencies...")
        result = subprocess.run([
            sys.executable, "-m", "pip", "install", "-r", "requirements.txt"
        ], check=True, capture_output=True, text=True)
        
        print("✅ Python dependencies installed successfully")
        return True
        
    except subprocess.CalledProcessError as e:
        print(f"❌ Failed to install dependencies: {e}")
        return False


def setup_environment():
    """Setup environment configuration."""
    print("🔧 Setting up environment...")
    
    # Check if .env exists
    env_file = Path(".env")
    env_example = Path("config/.env.example")
    
    if not env_file.exists() and env_example.exists():
        print("📋 Creating .env file from example...")
        shutil.copy(env_example, env_file)
        print("⚠️  Please edit .env file with your actual configuration")
        return False
    
    # Create necessary directories
    dirs_to_create = [
        "data/vectorstore",
        "logs"
    ]
    
    for dir_path in dirs_to_create:
        Path(dir_path).mkdir(parents=True, exist_ok=True)
    
    print("✅ Environment setup complete")
    return True


def check_ollama():
    """Check if Ollama is installed and running."""
    print("🔍 Checking Ollama installation...")
    
    try:
        # Check if ollama command exists
        subprocess.run(["ollama", "--version"], 
                      check=True, capture_output=True)
        print("✅ Ollama is installed")
        
        # Check if service is running
        import requests
        try:
            response = requests.get("http://localhost:11434/api/tags", timeout=5)
            if response.status_code == 200:
                print("✅ Ollama service is running")
                return True
            else:
                print("❌ Ollama service is not responding")
                return False
        except requests.RequestException:
            print("❌ Ollama service is not running")
            print("💡 Please start Ollama with: ollama serve")
            return False
            
    except (subprocess.CalledProcessError, FileNotFoundError):
        print("❌ Ollama is not installed")
        print("💡 Please install Ollama from: https://ollama.ai")
        return False


def setup_ollama_models():
    """Setup required Ollama models."""
    print("📥 Setting up Ollama models...")
    
    required_models = [
        ("llama3.1", "Main language model"),
        ("nomic-embed-text", "Embedding model")
    ]
    
    for model, description in required_models:
        print(f"🔄 Checking {model} ({description})...")
        
        try:
            # Check if model exists
            result = subprocess.run([
                "ollama", "list"
            ], capture_output=True, text=True, check=True)
            
            if model not in result.stdout:
                print(f"📥 Pulling {model}...")
                subprocess.run([
                    "ollama", "pull", model
                ], check=True)
                print(f"✅ {model} installed successfully")
            else:
                print(f"✅ {model} already available")
                
        except subprocess.CalledProcessError as e:
            print(f"❌ Failed to setup {model}: {e}")
            return False
    
    return True


def initialize_database_schema():
    """Initialize database schema embeddings."""
    print("🧠 Initializing database schema...")
    
    try:
        result = subprocess.run([
            sys.executable, "scripts/initialize_schema.py"
        ], check=True, capture_output=True, text=True)
        
        print("✅ Database schema initialized successfully")
        return True
        
    except subprocess.CalledProcessError as e:
        print(f"❌ Failed to initialize database schema: {e}")
        print("💡 Please check your database configuration in config/config.yaml")
        return False


def run_tests():
    """Run system tests."""
    print("🧪 Running system tests...")
    
    try:
        result = subprocess.run([
            sys.executable, "tests/test_rag_agent.py"
        ], check=True, capture_output=True, text=True)
        
        print("✅ All tests passed")
        return True
        
    except subprocess.CalledProcessError as e:
        print(f"⚠️  Some tests failed: {e}")
        return False


def main():
    """Main setup and run function."""
    print_banner()
    
    print("🚀 Starting RAG SQL Agent Setup")
    print("=" * 60)
    
    # Check Python version
    if not check_python_version():
        sys.exit(1)
    
    # Install requirements
    if not check_and_install_requirements():
        sys.exit(1)
    
    # Setup environment
    env_ready = setup_environment()
    
    # Check Ollama
    ollama_ready = check_ollama()
    
    # Setup Ollama models if service is running
    if ollama_ready:
        if not setup_ollama_models():
            print("⚠️  Ollama models setup failed, but continuing...")
    
    # Initialize database schema if environment is ready
    if env_ready and ollama_ready:
        schema_ready = initialize_database_schema()
    else:
        schema_ready = False
    
    # Run tests
    if schema_ready:
        run_tests()
    
    print("\n" + "=" * 60)
    print("🎉 Setup Complete!")
    print("=" * 60)
    
    if not env_ready:
        print("⚠️  Please complete environment setup:")
        print("   1. Edit .env file with your database credentials")
        print("   2. Update config/config.yaml with your settings")
    
    if not ollama_ready:
        print("⚠️  Please setup Ollama:")
        print("   1. Install Ollama from https://ollama.ai")
        print("   2. Start the service with: ollama serve")
        print("   3. Run: python scripts/setup_ollama.py")
    
    if not schema_ready:
        print("⚠️  Database schema not initialized:")
        print("   1. Configure your database connection")
        print("   2. Run: python scripts/initialize_schema.py")
    
    print("\n📋 Available Run Options:")
    print("   🖥️  Console Interface: python main.py")
    print("   🌐 Web Interface: streamlit run ui/streamlit_app.py")
    print("   🧪 Run Tests: python tests/test_rag_agent.py")
    print("   📊 Initialize Schema: python scripts/initialize_schema.py")
    
    print("\n💡 Quick Start:")
    print("   1. Configure database in config/config.yaml")
    print("   2. Run: python scripts/initialize_schema.py")
    print("   3. Run: python main.py")
    
    # Offer to run the application
    if schema_ready:
        print("\n🚀 Setup is complete! Would you like to start the agent?")
        choice = input("Enter 'c' for console, 'w' for web interface, or 'n' to exit: ").lower()
        
        if choice == 'c':
            print("🚀 Starting console interface...")
            subprocess.run([sys.executable, "main.py"])
        elif choice == 'w':
            print("🌐 Starting web interface...")
            subprocess.run(["streamlit", "run", "ui/streamlit_app.py"])
        else:
            print("👋 Setup complete. Run 'python main.py' when ready!")


if __name__ == "__main__":
    main()
