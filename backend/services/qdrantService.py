from helpers.embeding_helper import embed_texts, get_model_dim
from qdrant_client import QdrantClient,  models as qmodels
import uuid
import os
from typing import List, Optional
import mimetypes
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

    def ensure_qdrant_ready() -> QdrantClient:
        """Zapewnia istnienie kolekcji z właściwym wymiarem (= wymiar modelu)."""
        global _qdrant
        if _qdrant is None:
            _qdrant = QdrantClient(url=QDRANT_URL)

        model_dim = get_model_dim()

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

    def upsert_chunks_to_qdrant(self, storage_key: str, chunks: List[str]) -> int:
        if not chunks:
            return 0

        info = parse_storage_key(storage_key)
        checksum = info["checksum"]
        filename = info["filename"]
        ctype, _ = mimetypes.guess_type(filename)

        vectors = embed_texts(chunks)
        if not vectors:
            return 0

        client = QdrantService.ensure_qdrant_ready()

        points = []
        for idx, (vec, text) in enumerate(zip(vectors, chunks)):
            payload = {
                "checksum_sha256": checksum,
                "storage_key": storage_key,
                "filename": filename,
                "content_type": ctype or "application/octet-stream",
                "source": "upload",
                "chunk_index": idx,
                "chunk_text": text,
                "chunk_char_count": len(text),
            }
            points.append(qmodels.PointStruct(id=str(uuid.uuid4()), vector=vec, payload=payload))

        for i in range(0, len(points), 64):
            client.upsert(collection_name=QDRANT_COLLECTION, points=points[i:i + 64], wait=True)
        return len(points)





qdrant_service = QdrantService(
    port=QDRANT_PORT,
    collection_name=QDRANT_COLLECTION_NAME,
    vector_size=VECTOR_SIZE
)
