from typing import Optional
from fastapi import HTTPException, APIRouter, Body

from models.collection import Collection
from services.qdrantService import QdrantService

from qdrant_client import models as qmodels

from helpers.embeding_helper import embed_texts

from const.env_variables import  QDRANT_HOST, QDRANT_PORT, QDRANT_COLLECTION

qdrant_service = QdrantService(host=QDRANT_HOST, port=QDRANT_PORT)

router = APIRouter(
    prefix="",
    tags=[""]
)

@router.get("/collections", tags=["Collections"])
async def get_collections():
    """
    Retrieve all available collections from Qdrant.
    
    Returns:
        List of collection names
    """
    try:
        collections = qdrant_service.get_collections()
        return {"collections": [c for c in collections]}
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Failed to get collections: {str(e)}")
        

@router.post("/collections", tags=["Collections"])
async def create_collection(collection: Collection):
    """
    Create a new collection in Qdrant.
    
    Args:
        collection: Collection configuration including name and vector settings
        
    Returns:
        Success message with collection name
    """
    try:
        qdrant_service.create_collection(
            collection_name=collection.name,
            vector_size=collection.vector_size,
            distance=collection.distance
        )
        return {"status": "success", "message": f"Collection {collection.name} created"}
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Failed to create collection: {str(e)}")

@router.post("/search", tags=["Search"])
async def search_post(
    query: str = Body(..., embed=True, min_length=1, description="Zapytanie tekstowe"),
    top_k: int = Body(5, embed=True, ge=1, le=50),
    collection_name: Optional[str] = Body(None, embed=True),
    checksum: Optional[str] = Body(None, embed=True, description="Zawęź do jednego dokumentu po checksumie"),
    filename: Optional[str] = Body(None, embed=True, description="Albo zawęź po nazwie pliku"),
    score_threshold: Optional[float] = Body(None, embed=True, description="Minimalny wynik podobieństwa, np. 0.35"),
):
    try:
        [query_vec] = embed_texts([query])

        must = []
        if checksum:
            must.append(qmodels.FieldCondition(
                key="checksum_sha256",
                match=qmodels.MatchValue(value=checksum)
            ))
        if filename:
            must.append(qmodels.FieldCondition(
                key="filename",
                match=qmodels.MatchValue(value=filename)
            ))
        flt = qmodels.Filter(must=must) if must else None

        client = QdrantService.ensure_qdrant_ready()

        hits = client.search(
            collection_name=collection_name or QDRANT_COLLECTION,
            query_vector=query_vec,
            limit=top_k,
            with_payload=True,
            score_threshold=score_threshold 
        ) if flt is None else client.search(
            collection_name=collection_name or QDRANT_COLLECTION,
            query_vector=query_vec,
            limit=top_k,
            with_payload=True,
            filter=flt,
            score_threshold=score_threshold
        )

        results = []
        for h in hits:
            p = h.payload or {}
            results.append({
                "id": getattr(h, "id", None),
                "score": h.score,
                "filename": p.get("filename"),
                "storage_key": p.get("storage_key"),
                "chunk_index": p.get("chunk_index"),
                "chunk_text": p.get("chunk_text", ""),
            })
        return {
            "collection": collection_name or QDRANT_COLLECTION,
            "query": query,
            "count": len(results),
            "results": results
        }
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Search failed: {str(e)}")