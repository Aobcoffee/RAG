"""
Ollama LLM integration for local language model inference.
"""

from typing import List, Dict, Any, Optional
import requests
import json
from langchain_ollama import OllamaLLM
from langchain_core.language_models import BaseLanguageModel

from ..utils.config import Config


class OllamaManager:
    """Manages Ollama LLM operations."""
    
    def __init__(self, config: Config):
        self.config = config
        self.base_url = config.llm.base_url
        self.model = config.llm.model
        self.temperature = config.llm.temperature
        self.max_tokens = config.llm.max_tokens
        self.llm: Optional[BaseLanguageModel] = None
        
    def initialize(self) -> bool:
        """Initialize Ollama LLM."""
        try:
            # Check if Ollama is running
            if not self._is_ollama_running():
                raise RuntimeError("Ollama service is not running. Please start it with 'ollama serve'")
            
            # Check if model is available
            if not self._is_model_available():
                raise RuntimeError(f"Model '{self.model}' is not available. Please pull it with 'ollama pull {self.model}'")
            
            # Initialize LangChain Ollama LLM
            self.llm = OllamaLLM(
                base_url=self.base_url,
                model=self.model,
                temperature=self.temperature,
                num_ctx=self.max_tokens
            )
            
            return True
            
        except Exception as e:
            print(f"Failed to initialize Ollama: {e}")
            return False
    
    def _is_ollama_running(self) -> bool:
        """Check if Ollama service is running."""
        try:
            response = requests.get(f"{self.base_url}/api/tags", timeout=5)
            return response.status_code == 200
        except:
            return False
    
    def _is_model_available(self) -> bool:
        """Check if the specified model is available."""
        try:
            response = requests.get(f"{self.base_url}/api/tags", timeout=5)
            if response.status_code == 200:
                models = response.json().get('models', [])
                return any(model['name'].startswith(self.model) for model in models)
            return False
        except:
            return False
    
    def get_available_models(self) -> List[str]:
        """Get list of available models."""
        try:
            response = requests.get(f"{self.base_url}/api/tags", timeout=5)
            if response.status_code == 200:
                models = response.json().get('models', [])
                return [model['name'] for model in models]
            return []
        except:
            return []
    
    def generate_response(self, prompt: str, system_prompt: Optional[str] = None) -> str:
        """Generate response using Ollama LLM."""
        if not self.llm:
            raise RuntimeError("Ollama LLM not initialized")
        
        try:
            if system_prompt:
                full_prompt = f"System: {system_prompt}\n\nUser: {prompt}\n\nAssistant:"
            else:
                full_prompt = prompt
                
            response = self.llm.invoke(full_prompt)
            return response
            
        except Exception as e:
            raise RuntimeError(f"Failed to generate response: {e}")
    
    def generate_streaming_response(self, prompt: str, system_prompt: Optional[str] = None):
        """Generate streaming response using Ollama LLM."""
        if not self.llm:
            raise RuntimeError("Ollama LLM not initialized")
        
        try:
            if system_prompt:
                full_prompt = f"System: {system_prompt}\n\nUser: {prompt}\n\nAssistant:"
            else:
                full_prompt = prompt
            
            # Use the streaming capability
            for token in self.llm.stream(full_prompt):
                yield token
                
        except Exception as e:
            raise RuntimeError(f"Failed to generate streaming response: {e}")
    
    def pull_model(self, model_name: str) -> bool:
        """Pull a model from Ollama registry."""
        try:
            response = requests.post(
                f"{self.base_url}/api/pull",
                json={"name": model_name},
                timeout=300  # 5 minutes timeout for model download
            )
            return response.status_code == 200
        except:
            return False
    
    def get_model_info(self, model_name: Optional[str] = None) -> Dict[str, Any]:
        """Get information about a model."""
        model = model_name or self.model
        try:
            response = requests.post(
                f"{self.base_url}/api/show",
                json={"name": model},
                timeout=10
            )
            if response.status_code == 200:
                return response.json()
            return {}
        except:
            return {}


class OllamaEmbeddings:
    """Ollama embeddings for vector operations."""
    
    def __init__(self, config: Config):
        self.config = config
        self.base_url = config.llm.base_url
        self.model = config.embeddings.model
        
    def embed_documents(self, texts: List[str]) -> List[List[float]]:
        """Embed multiple documents."""
        embeddings = []
        for text in texts:
            embedding = self._get_embedding(text)
            embeddings.append(embedding)
        return embeddings
    
    def embed_query(self, text: str) -> List[float]:
        """Embed a single query."""
        return self._get_embedding(text)
    
    def _get_embedding(self, text: str) -> List[float]:
        """Get embedding for a single text."""
        try:
            response = requests.post(
                f"{self.base_url}/api/embeddings",
                json={
                    "model": self.model,
                    "prompt": text
                },
                timeout=30
            )
            
            if response.status_code == 200:
                return response.json()["embedding"]
            else:
                raise RuntimeError(f"Failed to get embedding: {response.text}")
                
        except Exception as e:
            raise RuntimeError(f"Failed to get embedding: {e}")
    
    def is_model_available(self) -> bool:
        """Check if embedding model is available."""
        try:
            response = requests.get(f"{self.base_url}/api/tags", timeout=5)
            if response.status_code == 200:
                models = response.json().get('models', [])
                return any(model['name'].startswith(self.model) for model in models)
            return False
        except:
            return False
