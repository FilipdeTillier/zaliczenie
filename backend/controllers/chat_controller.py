import os
from typing import Any
from fastapi import HTTPException, APIRouter

from services.qdrantService import QdrantService
from models.query_request import QueryRequest
from services.openAiService import open_ai_service
from services.ollamaService import OllamaService


from helpers.embeding_helper import embed_texts
from const.server import app

from const.env_variables import QDRANT_COLLECTION

router = APIRouter(
    prefix="",
    tags=[""]
)

# def _text_from_query_obj(q: Any) -> str:
#     if isinstance(q, str):
#         return q
#     if hasattr(q, "messages"):
#         try:
#             return "\n".join(m.get("content", "") for m in q.messages)
#         except Exception:
#             pass
#     if hasattr(q, "text"):
#         return str(q.text)
#     return str(q)

# # Deprecated
# @router.post("/query", tags=["Search"])
# async def query_endpoint(request: QueryRequest):
#     """
#     Uwaga: gdy use_rag=True, embedding zapytania robimy tym samym SentenceTransformerem (768D).
#     """
#     try:
#         if not request.use_rag:
#             if request.use_local:
#                 ollama_service = OllamaService()
#                 response = await ollama_service.query_model(request.query)
#             else:
#                 response = await open_ai_service.query_model(
#                     messages=request.query.messages,
#                     model=request.query.model,
#                 )
#             return {"response": response, "source_documents": []}
#         else:
#             if not request.collection_name:
#                 raise HTTPException(status_code=400, detail="Collection name is required for RAG queries")

#             query_text = _text_from_query_obj(request.query)
#             [query_embedding] = embed_texts([query_text])
#             global _qdrant
#             client = _qdrant
#             client = QdrantService.ensure_qdrant_ready()
#             search_results = client.search(
#                 collection_name=request.collection_name or QDRANT_COLLECTION,
#                 query_vector=query_embedding,
#                 limit=5,
#             )

#             sources = [
#                 {
#                     "score": hit.score,
#                     "metadata": {k: v for k, v in (hit.payload or {}).items()},
#                 }
#                 for hit in search_results
#             ]

#             context_parts = []
#             for i, src in enumerate(sources):
#                 text = src["metadata"].get("text", "") or src["metadata"].get("chunk_text", "")
#                 if text:
#                     context_parts.append(f"Document {i+1}:\n{text}")
#             context = "\n\n".join(context_parts)

#             prompt = f"""Answer the question based on the provided context.

#                 Context:
#                 {context}

#                 Question: {query_text}

#                 Answer:"""
#             ollama_service = OllamaService()
#             response = await ollama_service.query_llm(prompt)
#             return {"response": response, "source_documents": sources}
#     except Exception as e:
#         raise HTTPException(status_code=500, detail=f"Query failed: {str(e)}")

