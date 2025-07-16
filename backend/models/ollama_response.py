from pydantic import BaseModel
from typing import Optional, Dict, Any

class OllamaMessage(BaseModel):
    role: str
    content: str

class OllamaResponse(BaseModel):
    model: str
    created_at: str
    message: OllamaMessage
    done_reason: Optional[str] = None
    done: bool
    total_duration: Optional[int] = None
    load_duration: Optional[int] = None
    prompt_eval_count: Optional[int] = None
    prompt_eval_duration: Optional[int] = None
    eval_count: Optional[int] = None
    eval_duration: Optional[int] = None
