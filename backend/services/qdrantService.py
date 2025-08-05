from qdrant_client import QdrantClient
from qdrant_client.models import PointStruct, Filter, FieldCondition, MatchValue
import uuid
import os

QDRANT_COLLECTION_NAME = os.getenv("QDRANT_COLLECTION_NAME", "rag_collection")


class QdrantService:
    def __init__(self, host='localhost', port=6333, collection_name=QDRANT_COLLECTION_NAME, vector_size=768):
        self.collection_name = collection_name
        self.client = QdrantClient(host=host, port=port)
        self._ensure_collection_exists(vector_size)

    def _ensure_collection_exists(self, vector_size):
        """Create or recreate the collection to match the embedding size."""
        collections = self.client.get_collections().collections
        if self.collection_name not in [c.name for c in collections]:
            self.client.recreate_collection(
                collection_name=self.collection_name,
                vectors_config={"size": vector_size, "distance": "Cosine"}
            )
        else:
            info = self.client.get_collection(self.collection_name)
            existing_size = info.config.params.vectors.size
            if existing_size != vector_size:
                self.client.recreate_collection(
                    collection_name=self.collection_name,
                    vectors_config={"size": vector_size, "distance": "Cosine"}
                )

    def add_document(self, text, embedding, metadata=None):
        # Ensure the collection dimensionality matches the embedding being
        # inserted. This safeguards against attempts to upsert vectors of a
        # different size than the existing collection configuration.
        self._ensure_collection_exists(len(embedding))

        point = PointStruct(
            id=str(uuid.uuid4()),
            vector=embedding,
            payload={"text": text, **(metadata or {})}
        )
        self.client.upsert(collection_name=self.collection_name, points=[point])

    def search(self, query_embedding, top_k=5, filter=None):
        results = self.client.search(
            collection_name=self.collection_name,
            query_vector=query_embedding,
            limit=top_k,
            query_filter=filter
        )
        return results

    def create_collection(self, collection_name, vector_size=768, distance="Cosine"):
        """
        Create a new collection in Qdrant with the specified name, vector size, and distance metric.
        """
        if collection_name not in [c.name for c in self.client.get_collections().collections]:
            self.client.create_collection(
                collection_name=collection_name,
                vectors_config={"size": vector_size, "distance": distance}
            )

    def get_collections(self):
        """
        Retrieve all available collections as an array of collection names.
        """
        collections_response = self.client.get_collections()
        return [c.name for c in collections_response.collections]
