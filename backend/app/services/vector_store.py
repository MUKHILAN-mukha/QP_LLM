import faiss
import pickle
import os
import numpy as np
from typing import List, Dict, Optional
from app.config import settings
from app.services.embedding_service import embedding_service
import logging

logger = logging.getLogger(__name__)

class VectorStore:
    def __init__(self):
        self.indices: Dict[int, faiss.IndexFlatL2] = {}
        self.metadata: Dict[int, List[Dict]] = {} # subject_id -> List[metadata]
        self.last_modified: Dict[int, float] = {} # subject_id -> timestamp
        self.dimension = 384 # all-MiniLM-L6-v2 dimension
        self._load_indices()

    def _get_index_path(self, subject_id: int) -> str:
        return os.path.join(settings.FAISS_INDEX_DIR, f"subject_{subject_id}.index")

    def _get_metadata_path(self, subject_id: int) -> str:
        return os.path.join(settings.FAISS_INDEX_DIR, f"subject_{subject_id}_metadata.pkl")

    def reload_if_stale(self, subject_id: int):
        """Reloads the index if the file on disk is newer than our in-memory version."""
        index_path = self._get_index_path(subject_id)
        if not os.path.exists(index_path):
            return

        current_mtime = os.path.getmtime(index_path)
        last_mtime = self.last_modified.get(subject_id, 0)

        if current_mtime > last_mtime:
            logger.info(f"Detected staleness in subject {subject_id}. Reloading...")
            try:
                self.indices[subject_id] = faiss.read_index(index_path)
                metadata_path = self._get_metadata_path(subject_id)
                if os.path.exists(metadata_path):
                    with open(metadata_path, "rb") as f:
                        self.metadata[subject_id] = pickle.load(f)
                self.last_modified[subject_id] = current_mtime
            except Exception as e:
                logger.error(f"Reload failed for subject {subject_id}: {e}")

    def _load_indices(self):
        if not os.path.exists(settings.FAISS_INDEX_DIR):
            os.makedirs(settings.FAISS_INDEX_DIR)
            return

        for filename in os.listdir(settings.FAISS_INDEX_DIR):
            if filename.endswith(".index"):
                try:
                    subject_id = int(filename.split("_")[1].split(".")[0])
                    self.reload_if_stale(subject_id)
                except Exception as e:
                    logger.error(f"Error loading initial index {filename}: {e}")

    def get_or_create_index(self, subject_id: int) -> faiss.IndexFlatL2:
        self.reload_if_stale(subject_id)
        if subject_id not in self.indices:
            self.indices[subject_id] = faiss.IndexFlatL2(self.dimension)
            self.metadata[subject_id] = []
            # Initialize mtime if creating new
            index_path = self._get_index_path(subject_id)
            if os.path.exists(index_path):
                self.last_modified[subject_id] = os.path.getmtime(index_path)
        return self.indices[subject_id]

    def add_texts(self, subject_id: int, texts: List[str], metadatas: List[Dict]):
        self.reload_if_stale(subject_id)
        index = self.get_or_create_index(subject_id)
        embeddings = embedding_service.generate_embeddings(texts)
        if not embeddings:
            return
            
        embeddings_np = np.array(embeddings).astype('float32')
        index.add(embeddings_np)
        
        if subject_id not in self.metadata:
            self.metadata[subject_id] = []
        self.metadata[subject_id].extend(metadatas)
        
        self.save_index(subject_id)

    def search(self, subject_id: int, query: str, k: int = 5, filter_dict: Optional[Dict] = None) -> List[Dict]:
        self.reload_if_stale(subject_id)
        if subject_id not in self.indices:
            return []
            
        index = self.indices[subject_id]
        if index.ntotal == 0:
            return []

        query_embedding = embedding_service.generate_embedding(query)
        query_np = np.array([query_embedding]).astype('float32')
        
        # Search for more candidates if we are filtering
        search_k = k * 3 if filter_dict else k
        distances, indices = index.search(query_np, search_k)
        
        results = []
        subject_metadata = self.metadata.get(subject_id, [])
        
        for i, idx in enumerate(indices[0]):
            if idx != -1 and idx < len(subject_metadata):
                meta = subject_metadata[idx]
                
                # Apply filter if provided
                if filter_dict:
                    match = True
                    for key, value in filter_dict.items():
                        meta_val = meta.get(key)
                        if isinstance(value, str) and isinstance(meta_val, str):
                            if value.lower() not in meta_val.lower():
                                match = False
                                break
                        elif meta_val != value:
                            match = False
                            break
                    if not match:
                        continue
                
                results.append({
                    "text": meta.get("text", ""),
                    "metadata": meta,
                    "score": float(distances[0][i])
                })
                
                if len(results) >= k:
                    break
        
        return results

    def remove_document(self, subject_id: int, doc_id: int):
        if subject_id in self.metadata:
            original_count = len(self.metadata[subject_id])
            self.metadata[subject_id] = [m for m in self.metadata[subject_id] if m.get("doc_id") != doc_id]
            new_count = len(self.metadata[subject_id])
            
            if original_count != new_count:
                logger.info(f"Removed document {doc_id} from subject {subject_id} metadata ({original_count} -> {new_count} chunks)")
                self.save_index(subject_id)
            else:
                logger.warning(f"No metadata found for document {doc_id} in subject {subject_id}")

    def save_index(self, subject_id: int):
        if subject_id in self.indices:
            faiss.write_index(self.indices[subject_id], self._get_index_path(subject_id))
            with open(self._get_metadata_path(subject_id), "wb") as f:
                pickle.dump(self.metadata[subject_id], f)

vector_store = VectorStore()
