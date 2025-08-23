# memory/long_term.py

import chromadb
from chromadb.utils import embedding_functions
from config.config import Config

class LongTermMemory:
    def __init__(self, config: Config):
        # Persistent Chroma client (saves data to disk)
        self.client = chromadb.PersistentClient(path=config.chroma_db_path)
        # Create or get a collection named "agent_memory"
        self.collection = self.client.get_or_create_collection("agent_memory")

    def add(self, doc_id: str, text: str, metadata: dict = None):
        """Add a document (text and metadata) to the vector store."""
        self.collection.add(ids=[doc_id], documents=[text], metadatas=[metadata or {}])

    def query(self, query_text: str, n_results: int = 5):
        """Query the store for similar documents."""
        results = self.collection.query(query_texts=[query_text], n_results=n_results)
        return results
