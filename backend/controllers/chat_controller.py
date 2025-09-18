import os
from fastapi import HTTPException, APIRouter

from services.qdrantService import QdrantService
from services.openAiService import open_ai_service

from helpers.embeding_helper import embed_texts, embed_texts_openai

from qdrant_client import models as qmodels

from models.openai_response import OpenAIChatRequest

from const.env_variables import QDRANT_COLLECTION
from const.variables import qdrant_limit

from helpers.files_helper import load_prompt

router = APIRouter(
    prefix=""
)

@router.post("/open_ai/chat", tags=["Chat"])
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

            [query_vec] = await embed_texts_openai([query])

            client = QdrantService.ensure_qdrant_ready(use_openai=True)

            search_params = {
                "collection_name": QDRANT_COLLECTION,
                "query_vector": query_vec,
                "limit": qdrant_limit,
                "with_payload": True,
            }
            if filter_condition:
                search_params["query_filter"] = filter_condition

            search_results = client.search(**search_params)

            context_chunks = []
            for hit in search_results:
                payload = hit.payload
                if payload and "chunk_text" in payload:
                    text_to_append = f"""
                        =========================
                        filename: {payload["filename"]}
                        page_number: {payload["page_number"]}
                        source_type: {payload["source_type"]}
                        file_extension: {payload["file_extension"]}
                        upload_timestamp: {payload["upload_timestamp"]}
                        chunk_word_count: {payload["chunk_word_count"]}
                        chunk_text: {payload["chunk_text"]}
                        chunk_sentence_count: {payload["chunk_sentence_count"]}
                        ========================="""
                    context_chunks.append(text_to_append)
            context = "\n\n".join(context_chunks)

            context_message = {
                "role": "system",
                "content": f"Relevant context from documents:\n{context}" if context else "No relevant context found."
            }

            rule_messge = {
                "role": "user",
                "content": f"Remember, if you don't have the information, say that you don't have the information. Remember to add also page number and source file in your response. It could be usefull for the user to know the source of the information. Always response in the same language as the user's message."
            }

            messages_without_context = [rule_messge] + messages

            messages_with_context = [context_message] + messages_without_context

            response_without_context = await open_ai_service.query_model(
                model=request.model,
                messages=messages_without_context,
            )

            response = await open_ai_service.query_model(
                model=request.model,
                messages=messages_with_context,
            )

            judge_prompt = load_prompt("llm_as_a_judge_prompt.md")
            # Should return decision, if the response with context is ok or no. If no, return the reason why.
            judge_response = await open_ai_service.query_model(
                model=request.model,
                messages=[{
                    "role": "system",
                    "content": judge_prompt
                }, {
                    "role": "user",
                    "content": f"Response: {response}\n\nResponse without context: {response_without_context}"
                }]
            )

            return {"response": judge_response}
        else:
            response = await open_ai_service.query_model(
                model=request.model,
                messages=messages,
            )
            return {"response": response}
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"OpenAI chat failed: {str(e)}")
