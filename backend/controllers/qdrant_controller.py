import os
import uuid
from typing import List

from fastapi import HTTPException, APIRouter, UploadFile, File
from models.collection import Collection
from services.qdrantService import QdrantService
from fastembed import TextEmbedding
from pypdf import PdfReader

qdrant_host = os.getenv("QDRANT_HOST", "localhost")
qdrant_port = int(os.getenv("QDRANT_PORT", 6333))

embedding_model = TextEmbedding()
qdrant_service = QdrantService(host=qdrant_host, port=qdrant_port)
BASE_DIR = os.path.dirname(os.path.dirname(__file__))
FILES_DIR = os.path.join(BASE_DIR, "files")

router = APIRouter(
    prefix="",
    tags=[""]
)


def chunk_text(text: str, chunk_size: int = 500, overlap: int = 50) -> List[str]:
    chunks: List[str] = []
    start = 0
    while start < len(text):
        end = start + chunk_size
        chunks.append(text[start:end])
        start += chunk_size - overlap
    return chunks

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


@router.post("/send_documents", tags=["Documents"])
async def send_documents(files: List[UploadFile] = File(...)):
    """Upload documents, chunk them, embed and store in Qdrant."""
    try:
        os.makedirs(FILES_DIR, exist_ok=True)
        for upload in files:
            content = await upload.read()
            if len(content) > 100 * 1024 * 1024:
                raise HTTPException(status_code=400, detail=f"File {upload.filename} exceeds 100MB limit")

            unique_name = f"{uuid.uuid4()}_{upload.filename}"
            file_path = os.path.join(FILES_DIR, unique_name)
            with open(file_path, "wb") as f:
                f.write(content)

            ext = os.path.splitext(upload.filename)[1].lower()
            if ext == ".pdf":
                reader = PdfReader(file_path)
                for page_number, page in enumerate(reader.pages, 1):
                    text = page.extract_text() or ""
                    for idx, chunk in enumerate(chunk_text(text)):
                        embedding = list(embedding_model.embed([chunk]))[0]
                        metadata = {
                            "file_name": upload.filename,
                            "page": page_number,
                            "chunk": idx,
                        }
                        qdrant_service.add_document(chunk, embedding, metadata)
            else:
                text = content.decode("utf-8", errors="ignore")
                for idx, chunk in enumerate(chunk_text(text)):
                    embedding = list(embedding_model.embed([chunk]))[0]
                    metadata = {
                        "file_name": upload.filename,
                        "page": 1,
                        "chunk": idx,
                    }
                    qdrant_service.add_document(chunk, embedding, metadata)

        return {"status": "success"}
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Failed to process documents: {str(e)}")
