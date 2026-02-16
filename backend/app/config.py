import os
from pydantic_settings import BaseSettings
from dotenv import load_dotenv

load_dotenv()

class Settings(BaseSettings):
    APP_NAME: str = "Exam Gen AI"
    # Local only - no cloud keys needed
    EMBEDDING_MODEL_ID: str = "sentence-transformers/all-MiniLM-L6-v2"
    OLLAMA_BASE_URL: str = "http://localhost:11434"
    OLLAMA_MODEL: str = "mistral"
    
    # Path logic anchored to the 'backend' folder
    # Assuming config.py is in backend/app/config.py
    ROOT_DIR: str = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
    UPLOAD_DIR: str = os.path.join(ROOT_DIR, "uploads")
    FAISS_INDEX_DIR: str = os.path.join(ROOT_DIR, "faiss_index")
    ALLOWED_ORIGINS: list = ["http://localhost:5173"]

    class Config:
        env_file = ".env"

settings = Settings()

# Ensure directories exist
os.makedirs(settings.UPLOAD_DIR, exist_ok=True)
os.makedirs(settings.FAISS_INDEX_DIR, exist_ok=True)
