from typing import Optional
from fastapi import HTTPException, APIRouter, Body

from models.collection import Collection
from services.qdrantService import QdrantService

from qdrant_client import models as qmodels

from helpers.embeding_helper import embed_texts, embed_texts_openai

from const.env_variables import  QDRANT_HOST, QDRANT_PORT, QDRANT_COLLECTION
from const.variables import qdrant_limit

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
    top_k: int = Body(qdrant_limit, embed=True, ge=1, le=50),
    collection_name: Optional[str] = Body(None, embed=True),
    checksum: Optional[str] = Body(None, embed=True, description="Zawęź do jednego dokumentu po checksumie"),
    filename: Optional[str] = Body(None, embed=True, description="Albo zawęź po nazwie pliku"),
    score_threshold: Optional[float] = Body(None, embed=True, description="Minimalny wynik podobieństwa, np. 0.35"),
):
    try:
        [query_vec] = await embed_texts_openai([query])

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

        client = QdrantService.ensure_qdrant_ready(use_openai=True)

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
                "checksum_sha256": p.get("checksum_sha256"),
                "content_type": p.get("content_type"),
                "source": p.get("source"),
                "job_id": p.get("job_id"),
                "page_number": p.get("page_number"),
                "source_type": p.get("source_type", "unknown"),
                "chunk_size": p.get("chunk_size"),
                "file_extension": p.get("file_extension"),
                "upload_timestamp": p.get("upload_timestamp"),
                "chunk_word_count": p.get("chunk_word_count"),
                "chunk_sentence_count": p.get("chunk_sentence_count"),
            })
        return {
            "collection": collection_name or QDRANT_COLLECTION,
            "query": query,
            "count": len(results),
            "results": results
        }
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Search failed: {str(e)}")

@router.get("/metadata/stats", tags=["Metadata"])
async def get_metadata_stats(
    collection_name: Optional[str] = None
):
    """
    Get metadata statistics about the documents in the collection.
    """
    try:
        client = QdrantService.ensure_qdrant_ready(use_openai=True)
        collection = collection_name or QDRANT_COLLECTION
        
        scroll_res = client.scroll(
            collection_name=collection,
            with_payload=True,
            with_vectors=False,
            limit=10000
        )
        
        points = scroll_res[0]
        if not points:
            return {"collection": collection, "stats": {"total_points": 0}}
        
        stats = {
            "total_points": len(points),
            "source_types": {},
            "file_extensions": {},
            "page_numbers": {},
            "total_files": 0,
            "unique_files": set()
        }
        
        for point in points:
            payload = point.payload or {}
            
            source_type = payload.get("source_type", "unknown")
            stats["source_types"][source_type] = stats["source_types"].get(source_type, 0) + 1
            
            file_ext = payload.get("file_extension", "unknown")
            stats["file_extensions"][file_ext] = stats["file_extensions"].get(file_ext, 0) + 1
            
            page_num = payload.get("page_number")
            if page_num is not None:
                stats["page_numbers"][str(page_num)] = stats["page_numbers"].get(str(page_num), 0) + 1
            
            checksum = payload.get("checksum_sha256")
            filename = payload.get("filename")
            if checksum and filename:
                stats["unique_files"].add(f"{checksum}_{filename}")
        
        stats["total_files"] = len(stats["unique_files"])
        del stats["unique_files"]
    
        if stats["page_numbers"]:
            sorted_pages = sorted(stats["page_numbers"].keys(), key=int)
            stats["page_numbers"] = {page: stats["page_numbers"][page] for page in sorted_pages}
        
        return {
            "collection": collection,
            "stats": stats
        }
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Failed to get metadata stats: {str(e)}")

@router.post("/search/advanced", tags=["Search"])
async def advanced_search(
    query: str = Body(..., embed=True, min_length=1, description="Zapytanie tekstowe"),
    top_k: int = Body(5, embed=True, ge=1, le=50),
    collection_name: Optional[str] = Body(None, embed=True),
    checksum: Optional[str] = Body(None, embed=True, description="Zawęź do jednego dokumentu po checksumie"),
    filename: Optional[str] = Body(None, embed=True, description="Albo zawęź po nazwie pliku"),
    page_number: Optional[int] = Body(None, embed=True, description="Filtruj po numerze strony"),
    source_type: Optional[str] = Body(None, embed=True, description="Filtruj po typie źródła (pdf, word, powerpoint, txt, md)"),
    file_extension: Optional[str] = Body(None, embed=True, description="Filtruj po rozszerzeniu pliku"),
    score_threshold: Optional[float] = Body(None, embed=True, description="Minimalny wynik podobieństwa, np. 0.35"),
):
    """
    Advanced search with metadata filtering capabilities.
    """
    try:
        [query_vec] = await embed_texts_openai([query])

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
        if page_number is not None:
            must.append(qmodels.FieldCondition(
                key="page_number",
                match=qmodels.MatchValue(value=page_number)
            ))
        if source_type:
            must.append(qmodels.FieldCondition(
                key="source_type",
                match=qmodels.MatchValue(value=source_type)
            ))
        if file_extension:
            must.append(qmodels.FieldCondition(
                key="file_extension",
                match=qmodels.MatchValue(value=file_extension)
            ))
            
        flt = qmodels.Filter(must=must) if must else None

        client = QdrantService.ensure_qdrant_ready(use_openai=True)

        hits = client.search(
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
                "page_number": p.get("page_number"),
                "source_type": p.get("source_type"),
                "chunk_size": p.get("chunk_size"),
                "file_extension": p.get("file_extension"),
                "upload_timestamp": p.get("upload_timestamp"),
                "chunk_word_count": p.get("chunk_word_count"),
                "chunk_sentence_count": p.get("chunk_sentence_count"),
            })
        return {
            "collection": collection_name or QDRANT_COLLECTION,
            "query": query,
            "count": len(results),
            "filters": {
                "checksum": checksum,
                "filename": filename,
                "page_number": page_number,
                "source_type": source_type,
                "file_extension": file_extension,
                "score_threshold": score_threshold
            },
            "results": results
        }
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Advanced search failed: {str(e)}")