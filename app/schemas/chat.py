
from pydantic import BaseModel, Field


class ChatRequest(BaseModel):

    conversation_id: str = Field(
        min_length=36,
        max_length=36
    )

    message: str = Field(
        min_length=1,
        max_length=2000
    )


class ChatResponse(BaseModel):

    reply: str
