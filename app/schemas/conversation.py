
from datetime import datetime

from pydantic import BaseModel, ConfigDict, Field


class ConversationCreate(BaseModel):

    title: str = Field(
        default="Cuộc trò chuyện mới",
        min_length=1,
        max_length=255
    )


class ConversationResponse(BaseModel):

    model_config = ConfigDict(from_attributes=True)

    id: str
    title: str
    created_at: datetime
