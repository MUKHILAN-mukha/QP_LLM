from sentence_transformers import SentenceTransformer
from app.config import settings
import logging

logger = logging.getLogger(__name__)

class EmbeddingService:
    def __init__(self):
        logger.info(f"Loading embedding model: {settings.EMBEDDING_MODEL_ID}")
        self.model = SentenceTransformer(settings.EMBEDDING_MODEL_ID)

    def generate_embedding(self, text: str) -> list:
        return self.model.encode(text).tolist()

    def generate_embeddings(self, texts: list[str]) -> list:
        return self.model.encode(texts).tolist()

embedding_service = EmbeddingService()
