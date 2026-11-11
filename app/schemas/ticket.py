from typing import Literal

from pydantic import BaseModel, ConfigDict, Field


class TicketCreate(BaseModel):
    customer_name: str = Field(min_length=2, max_length=100)
    email: str = Field(min_length=5, max_length=254)
    issue: str = Field(min_length=5, max_length=2000)


class TicketReplace(BaseModel):
    customer_name: str = Field(min_length=2, max_length=100)
    email: str = Field(min_length=5, max_length=254)
    issue: str = Field(min_length=5, max_length=2000)
    status: Literal["pending", "in_progress", "resolved"]


class TicketResponse(BaseModel):
    model_config = ConfigDict(from_attributes=True)

    id: int
    customer_name: str
    email: str
    issue: str
    status: Literal["pending", "in_progress", "resolved"]
