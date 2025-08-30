from fastapi import HTTPException, APIRouter

from services.qdrantService import QdrantService
from services.openAiService import open_ai_service

from helpers.embeding_helper import embed_texts

from qdrant_client import models as qmodels

from models.openai_response import OpenAIChatRequest

from const.env_variables import QDRANT_COLLECTION

router = APIRouter(
    prefix="",
    tags=[""]
)

@router.post("/open_ai/chat")
async def open_ai_chat(request: OpenAIChatRequest):
    try:
        messages = [message.dict() for message in request.messages]
        
        if request.documents:
            user_messages = [m for m in messages if m.get("role") == "user"]
            if not user_messages:
                raise HTTPException(status_code=400, detail="No user message found for RAG search.")
            query = user_messages[-1]["content"]

            must_conditions = []
            for doc in request.documents:
                must_conditions.append(
                    qmodels.FieldCondition(
                        key="checksum_sha256",
                        match=qmodels.MatchValue(value=doc.checksum_sha256)
                    )
                )
            filter_condition = qmodels.Filter(
                should=must_conditions
            ) if must_conditions else None

            [query_vec] = embed_texts([query])

            client = QdrantService.ensure_qdrant_ready()

            search_params = {
                "collection_name": QDRANT_COLLECTION,
                "query_vector": query_vec,
                "limit": request.max_results or 5,
                "with_payload": True,
            }
            if filter_condition:
                search_params["query_filter"] = filter_condition

            search_results = client.search(**search_params)

            context_chunks = []
            for hit in search_results:
                payload = hit.payload
                if payload and "chunk_text" in payload:
                    context_chunks.append(payload["chunk_text"])
            context = "\n\n".join(context_chunks)

            context_message = {
                "role": "system",
                "content": f"Relevant context from documents:\n{context}" if context else "No relevant context found."
            }
            messages_with_context = [context_message] + messages

            response = await open_ai_service.query_model(
                model=request.model,
                messages=messages_with_context,
            )
        else:
            response = await open_ai_service.query_model(
                model=request.model,
                messages=messages,
            )
        return {"response": response}
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"OpenAI chat failed: {str(e)}")
