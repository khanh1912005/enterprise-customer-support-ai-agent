
from sqlalchemy import String, Boolean
from sqlalchemy.orm import Mapped, mapped_column

from app.core.database import Base


class User(Base):

    __tablename__ = "users"

    # ID người dùng
    id: Mapped[int] = mapped_column(
        primary_key=True,
        index=True
    )

    # Họ tên
    full_name: Mapped[str] = mapped_column(
        String(100),
        nullable=False
    )

    # Email đăng nhập, không được trùng
    email: Mapped[str] = mapped_column(
        String(254),
        unique=True,
        index=True,
        nullable=False
    )

    # Mật khẩu đã hash
    hashed_password: Mapped[str] = mapped_column(
        String(255),
        nullable=False
    )

    # Vai trò người dùng
    role: Mapped[str] = mapped_column(
        String(20),
        default="customer",
        nullable=False
    )

    # Tài khoản có đang hoạt động?
    is_active: Mapped[bool] = mapped_column(
        Boolean,
        default=True,
        nullable=False
    )
