
from fastapi import APIRouter, Depends, HTTPException, status

from sqlalchemy import select
from sqlalchemy.orm import Session

from app.core.database import get_db
from app.core.dependencies import get_current_user

from app.models.user import User
from app.models.conversation import Conversation

from app.schemas.conversation import (
    ConversationCreate,
    ConversationResponse
)


router = APIRouter(
    prefix="/conversations",
    tags=["Conversations"]
)


# =====================================
# 1. CHECK CONVERSATION OWNERSHIP
# =====================================

def get_owned_conversation(
    conversation_id: str,
    db: Session,
    user_id: int
) -> Conversation:

    statement = select(Conversation).where(
        Conversation.id == conversation_id,
        Conversation.user_id == user_id
    )

    conversation = db.scalar(statement)

    if conversation is None:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Conversation not found"
        )

    return conversation


# =====================================
# 2. CREATE CONVERSATION
# =====================================

@router.post(
    "",
    response_model=ConversationResponse,
    status_code=status.HTTP_201_CREATED
)
def create_conversation(
    request: ConversationCreate,
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_user)
):

    title = request.title.strip()

    if not title:
        raise HTTPException(
            status_code=400,
            detail="Conversation title cannot be empty"
        )

    conversation = Conversation(
        user_id=current_user.id,
        title=title
    )

    db.add(conversation)

    db.commit()

    db.refresh(conversation)

    return conversation


# =====================================
# 3. GET USER CONVERSATIONS
# =====================================

@router.get(
    "",
    response_model=list[ConversationResponse]
)
def list_conversations(
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_user)
):

    statement = (
        select(Conversation)
        .where(Conversation.user_id == current_user.id)
        .order_by(Conversation.created_at.desc())
    )

    conversations = db.scalars(statement).all()

    return conversations


# =====================================
# 4. GET ONE CONVERSATION
# =====================================

@router.get(
    "/{conversation_id}",
    response_model=ConversationResponse
)
def read_conversation(
    conversation_id: str,
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_user)
):

    conversation = get_owned_conversation(
        conversation_id=conversation_id,
        db=db,
        user_id=current_user.id
    )

    return conversation
