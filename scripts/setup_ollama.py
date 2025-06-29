"""
Setup script to install Ollama models and verify installation.
"""

import subprocess
import sys
import time
import requests
from pathlib import Path

# Add src to Python path
sys.path.append(str(Path(__file__).parent.parent / 'src'))


def run_command(command, description):
    """Run a command and handle errors."""
    print(f"🔧 {description}...")
    try:
        result = subprocess.run(command, shell=True, check=True, capture_output=True, text=True)
        print(f"✅ {description} completed successfully")
        return True
    except subprocess.CalledProcessError as e:
        print(f"❌ {description} failed: {e.stderr}")
        return False


def check_ollama_running():
    """Check if Ollama service is running."""
    try:
        response = requests.get("http://localhost:11434/api/tags", timeout=5)
        return response.status_code == 200
    except:
        return False


def main():
    """Setup Ollama models and verify installation."""
    print("🚀 RAG SQL Agent Setup")
    print("=" * 50)
    
    # Check if Ollama is installed
    print("🔍 Checking Ollama installation...")
    if not run_command("ollama --version", "Checking Ollama version"):
        print("❌ Ollama is not installed. Please install it from https://ollama.ai")
        return False
    
    # Start Ollama service (if not running)
    if not check_ollama_running():
        print("🚀 Starting Ollama service...")
        # On Windows, we need to start ollama serve in background
        try:
            subprocess.Popen(["ollama", "serve"], creationflags=subprocess.CREATE_NEW_CONSOLE)
            time.sleep(5)  # Wait for service to start
        except Exception as e:
            print(f"⚠️  Could not start Ollama service automatically: {e}")
            print("Please start Ollama manually by running 'ollama serve' in another terminal")
            input("Press Enter when Ollama is running...")
    
    if not check_ollama_running():
        print("❌ Ollama service is not running. Please start it with 'ollama serve'")
        return False
    
    print("✅ Ollama service is running")
    
    # Pull required models
    models = [
        ("llama3.1", "Main language model for SQL generation"),
        ("nomic-embed-text", "Embedding model for vector operations")
    ]
    
    for model, description in models:
        print(f"📥 Pulling {model} ({description})...")
        if not run_command(f"ollama pull {model}", f"Pulling {model}"):
            print(f"❌ Failed to pull {model}")
            return False
    
    # Verify models are available
    print("🔍 Verifying installed models...")
    try:
        response = requests.get("http://localhost:11434/api/tags", timeout=10)
        if response.status_code == 200:
            installed_models = [model['name'] for model in response.json().get('models', [])]
            print("✅ Available models:")
            for model in installed_models:
                print(f"   - {model}")
            
            # Check if required models are present
            required_models = ['llama3.1', 'nomic-embed-text']
            missing_models = []
            
            for req_model in required_models:
                if not any(model.startswith(req_model) for model in installed_models):
                    missing_models.append(req_model)
            
            if missing_models:
                print(f"❌ Missing required models: {', '.join(missing_models)}")
                return False
            
            print("✅ All required models are available")
        else:
            print("❌ Could not verify models")
            return False
    except Exception as e:
        print(f"❌ Error verifying models: {e}")
        return False
    
    # Test model functionality
    print("🧪 Testing model functionality...")
    try:
        test_payload = {
            "model": "llama3.1",
            "prompt": "Hello, respond with 'Test successful'",
            "stream": False
        }
        
        response = requests.post(
            "http://localhost:11434/api/generate",
            json=test_payload,
            timeout=30
        )
        
        if response.status_code == 200:
            print("✅ Language model test successful")
        else:
            print(f"❌ Language model test failed: {response.text}")
            return False
            
    except Exception as e:
        print(f"❌ Model test failed: {e}")
        return False
    
    # Test embedding model
    print("🧪 Testing embedding model...")
    try:
        embed_payload = {
            "model": "nomic-embed-text",
            "prompt": "test embedding"
        }
        
        response = requests.post(
            "http://localhost:11434/api/embeddings",
            json=embed_payload,
            timeout=30
        )
        
        if response.status_code == 200:
            embedding = response.json().get("embedding")
            if embedding and len(embedding) > 0:
                print("✅ Embedding model test successful")
            else:
                print("❌ Embedding model returned empty result")
                return False
        else:
            print(f"❌ Embedding model test failed: {response.text}")
            return False
            
    except Exception as e:
        print(f"❌ Embedding test failed: {e}")
        return False
    
    print("\n" + "=" * 50)
    print("🎉 Setup completed successfully!")
    print("\nNext steps:")
    print("1. Configure your database connection in config/config.yaml")
    print("2. Copy config/.env.example to .env and update with your settings")
    print("3. Run 'python scripts/initialize_schema.py' to embed your database schema")
    print("4. Run 'python main.py' to start the agent")
    print("5. Or run 'streamlit run ui/streamlit_app.py' for the web interface")
    
    return True


if __name__ == "__main__":
    success = main()
    sys.exit(0 if success else 1)
