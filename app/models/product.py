
from datetime import datetime

from decimal import Decimal

from sqlalchemy import (
    String,
    Text,
    Integer,
    Numeric,
    Boolean,
    DateTime,
    func
)

from sqlalchemy.orm import Mapped, mapped_column

from app.core.database import Base


class Product(Base):

    # Tên bảng trong PostgreSQL
    __tablename__ = "products"

    # 1. Khóa chính
    id: Mapped[int] = mapped_column(
        Integer,
        primary_key=True,
        autoincrement=True
    )

    # 2. Mã sản phẩm
    sku: Mapped[str] = mapped_column(
        String(50),
        unique=True,
        nullable=False,
        index=True
    )

    # 3. Tên sản phẩm
    name: Mapped[str] = mapped_column(
        String(150),
        nullable=False,
        index=True
    )

    # 4. Mô tả sản phẩm
    description: Mapped[str | None] = mapped_column(
        Text,
        nullable=True
    )

    # 5. Danh mục
    category: Mapped[str | None] = mapped_column(
        String(100),
        nullable=True
    )

    # 6. Giá bán
    price: Mapped[Decimal] = mapped_column(
        Numeric(12, 2),
        nullable=False
    )

    # 7. Số lượng tồn kho
    stock_quantity: Mapped[int] = mapped_column(
        Integer,
        default=0,
        nullable=False
    )

    # 8. Trạng thái kinh doanh
    is_active: Mapped[bool] = mapped_column(
        Boolean,
        default=True,
        nullable=False
    )

    # 9. Thời gian tạo
    created_at: Mapped[datetime] = mapped_column(
        DateTime(timezone=True),
        server_default=func.now(),
        nullable=False
    )
