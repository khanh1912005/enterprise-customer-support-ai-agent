
from datetime import datetime, timezone
from uuid import uuid4

from sqlalchemy import String, ForeignKey, DateTime
from sqlalchemy.orm import Mapped, mapped_column

from app.core.database import Base


class Conversation(Base):

    __tablename__ = "conversations"

    # Mã cuộc trò chuyện
    id: Mapped[str] = mapped_column(
        String(36),
        primary_key=True,
        default=lambda: str(uuid4())
    )

    # Chủ sở hữu cuộc trò chuyện
    user_id: Mapped[int] = mapped_column(
        ForeignKey("users.id", ondelete="CASCADE"),
        nullable=False,
        index=True
    )

    # Tiêu đề cuộc trò chuyện
    title: Mapped[str] = mapped_column(
        String(255),
        nullable=False,
        default="Cuộc trò chuyện mới"
    )

    # Thời gian tạo
    created_at: Mapped[datetime] = mapped_column(
        DateTime(timezone=True),
        nullable=False,
        default=lambda: datetime.now(timezone.utc)
    )
