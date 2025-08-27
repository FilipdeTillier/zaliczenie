import uvicorn
from fastapi import HTTPException

from services.openAiService import open_ai_service
from models.openai_response import OpenAIChatRequest

from const.server import app

@app.post("/open_ai/chat")
async def open_ai_chat(request: OpenAIChatRequest):
    try:
        response = await open_ai_service.query_model(
            model=request.model,
            messages=[message.dict() for message in request.messages],
        )
        return {"response": response}
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"OpenAI chat failed: {str(e)}")


if __name__ == "__main__":
    uvicorn.run("app:app", host="0.0.0.0", port=8080, reload=True)
