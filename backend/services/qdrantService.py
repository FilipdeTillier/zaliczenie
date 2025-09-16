import uuid
import os
import asyncio
import mimetypes
from datetime import datetime
from typing import List, Optional, Dict, Any

from qdrant_client import QdrantClient,  models as qmodels

from helpers.embeding_helper import embed_texts, embed_texts_openai, get_model_dim

from const.env_variables import VECTOR_SIZE, QDRANT_COLLECTION_NAME, QDRANT_PORT, QDRANT_URL, QDRANT_COLLECTION, QDRANT_RECREATE_ON_MISMATCH

_qdrant: Optional[QdrantClient] = None

def parse_storage_key(storage_key: str) -> dict:
    parts = storage_key.split(os.sep)
    if len(parts) < 4:
        raise ValueError(f"Invalid storage_key: {storage_key}")
    a, b, checksum, filename = parts[-4:]
    return {"checksum": checksum, "filename": filename}

class QdrantService:
    def __init__(self, host='localhost', port=6333, collection_name=QDRANT_COLLECTION_NAME, vector_size=VECTOR_SIZE):
        self.collection_name = collection_name
        self.client = QdrantClient(host=host, port=port)

    def ensure_qdrant_ready(use_openai: bool = False) -> QdrantClient:
        """Zapewnia istnienie kolekcji z właściwym wymiarem (= wymiar modelu)."""
        global _qdrant
        if _qdrant is None:
            _qdrant = QdrantClient(url=QDRANT_URL)
        
        model_dim = get_model_dim(use_openai=use_openai)

        if not _qdrant.collection_exists(QDRANT_COLLECTION):
            _qdrant.create_collection(
                collection_name=QDRANT_COLLECTION,
                vectors_config=qmodels.VectorParams(size=model_dim, distance=qmodels.Distance.COSINE),
                on_disk_payload=True,
            )
        else:
            info = _qdrant.get_collection(QDRANT_COLLECTION)

            current_size = (
                info.config.params.vectors.size
                if hasattr(info.config.params.vectors, "size")
                else info.dict()["config"]["params"]["vectors"]["size"]
            )
            if current_size != model_dim:
                if QDRANT_RECREATE_ON_MISMATCH:
                    _qdrant.recreate_collection(
                        collection_name=QDRANT_COLLECTION,
                        vectors_config=qmodels.VectorParams(size=model_dim, distance=qmodels.Distance.COSINE),
                        on_disk_payload=True,
                    )
                else:
                    raise RuntimeError(
                        f"Qdrant collection '{QDRANT_COLLECTION}' ma size={current_size}, a model {model_dim}. "
                        f"Ustaw QDRANT_RECREATE_ON_MISMATCH=true albo dostosuj kolekcję/model."
                    )
        return _qdrant

    def get_collections(self) -> List[str]:
        """Get list of all collection names."""
        return [collection.name for collection in self.client.get_collections().collections]

    def upsert_chunks_to_qdrant(self, storage_key: str, chunks: List[str], metadata_list: Optional[List[Dict[str, Any]]] = None, job_id: Optional[str] = None, use_openai: bool = True) -> int:
        if not chunks:
            return 0

        info = parse_storage_key(storage_key)
        checksum = info["checksum"]
        filename = info["filename"]
        ctype, _ = mimetypes.guess_type(filename)

        if use_openai:
            vectors = asyncio.run(embed_texts_openai(chunks))
        else:
            vectors = embed_texts(chunks)
        
        if not vectors:
            return 0

        client = QdrantService.ensure_qdrant_ready(use_openai=use_openai)

        points = []
        for idx, (vec, text) in enumerate(zip(vectors, chunks)):
            chunk_metadata = metadata_list[idx] if metadata_list and idx < len(metadata_list) else {}
            
            payload = {
                "checksum_sha256": checksum,
                "storage_key": storage_key,
                "filename": filename,
                "content_type": ctype or "application/octet-stream",
                "source": "upload",
                "chunk_index": idx,
                "chunk_text": text,
                "chunk_char_count": len(text),
                "job_id": job_id,
                "page_number": chunk_metadata.get("page_number"),
                "source_type": chunk_metadata.get("source_type", "unknown"),
                "chunk_size": chunk_metadata.get("chunk_size", len(text)),
                "file_extension": os.path.splitext(filename)[1].lower(),
                "upload_timestamp": datetime.utcnow().isoformat(),
                "chunk_word_count": len(text.split()),
                "chunk_sentence_count": len([s for s in text.split('.') if s.strip()]),
            }
            points.append(qmodels.PointStruct(id=str(uuid.uuid4()), vector=vec, payload=payload))

        for i in range(0, len(points), 64):
            client.upsert(collection_name=QDRANT_COLLECTION, points=points[i:i + 64], wait=True)
        return len(points)
        
    def delete_points_by_checksum_and_filename(self, checksum_sha256: str, filename: str) -> int:
        """
        Remove all Qdrant points matching the given checksum_sha256 and filename.

        Args:
            checksum_sha256 (str): SHA-256 checksum to match.
            filename (str): Filename to match.

        Returns:
            int: Number of points deleted.
        """
        if not checksum_sha256 or not filename:
            raise ValueError("Both checksum_sha256 and filename are required.")

        client = QdrantService.ensure_qdrant_ready(use_openai=True)

        filter_condition = qmodels.Filter(
            must=[
                qmodels.FieldCondition(
                    key="checksum_sha256",
                    match=qmodels.MatchValue(value=checksum_sha256)
                ),
                qmodels.FieldCondition(
                    key="filename",
                    match=qmodels.MatchValue(value=filename)
                ),
            ]
        )

        scroll_res = client.scroll(
            collection_name=QDRANT_COLLECTION,
            scroll_filter=filter_condition,
            with_payload=False,
            with_vectors=False,
            limit=10000
        )
        point_ids = [point.id for point in scroll_res[0]]

        if not point_ids:
            return 0

        client.delete(
            collection_name=QDRANT_COLLECTION,
            points_selector=qmodels.PointIdsList(points=point_ids),
            wait=True
        )
        return len(point_ids)

    def create_collection(self, collection_name: str, vector_size: int, distance: str = "Cosine") -> None:
        """
        Create a new collection in Qdrant with the specified parameters.

        Args:
            collection_name (str): Name of the collection to create.
            vector_size (int): Size of the vectors to be stored.
            distance (str): Distance metric to use ("Cosine", "Euclid", "Dot").

        Raises:
            ValueError: If collection_name or vector_size is invalid.
            Exception: If Qdrant client fails to create the collection.
        """
        if not collection_name or not isinstance(collection_name, str):
            raise ValueError("collection_name must be a non-empty string.")
        if not isinstance(vector_size, int) or vector_size <= 0:
            raise ValueError("vector_size must be a positive integer.")

        client = QdrantService.ensure_qdrant_ready(use_openai=True)

        distance_map = {
            "Cosine": qmodels.Distance.COSINE,
            "Euclid": qmodels.Distance.EUCLID,
            "Dot": qmodels.Distance.DOT
        }
        distance_enum = distance_map.get(distance, qmodels.Distance.COSINE)

        try:
            client.create_collection(
                collection_name=collection_name,
                vectors_config=qmodels.VectorParams(
                    size=vector_size,
                    distance=distance_enum
                ),
                optimizers_config=None,
                shard_number=None,
                on_disk_payload=None,
                hnsw_config=None,
                wal_config=None,
                quantization_config=None,
                replication_factor=None,
                write_consistency_factor=None
            )
        except Exception as e:
            raise Exception(f"Failed to create collection '{collection_name}': {str(e)}")



qdrant_service = QdrantService(
    port=QDRANT_PORT,
    collection_name=QDRANT_COLLECTION_NAME,
    vector_size=VECTOR_SIZE
)
