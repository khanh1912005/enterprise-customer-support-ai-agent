
import logging

from sqlalchemy import select
from sqlalchemy.exc import SQLAlchemyError
from sqlalchemy.orm import Session

from app.models.order import Order


logger = logging.getLogger(__name__)


def get_order_status(
    order_code: str,
    db: Session,
    user_id: int
) -> dict:

    # 1. Kiểm tra mã đơn hàng
    if not isinstance(order_code, str) or not order_code.strip():
        return {
            "found": False,
            "message": "Invalid order code"
        }

    # 2. Chuẩn hóa mã đơn hàng
    order_code = order_code.strip().upper()

    try:

        # 3. Truy vấn theo mã đơn hàng và chủ sở hữu
        statement = select(Order).where(
            Order.order_code == order_code,
            Order.user_id == user_id
        )

        order = db.scalar(statement)

        # 4. Không tìm thấy đơn hàng thuộc tài khoản này
        if order is None:
            return {
                "found": False,
                "message": (
                    "Không tìm thấy đơn hàng "
                    "hoặc bạn không có quyền truy cập."
                )
            }

        # 5. Trả thông tin đơn hàng
        return {
            "success": True,
            "found": True,
            "order_code": order.order_code,
            "status": order.status,
            "carrier": order.carrier,
            "estimated_delivery": (
                order.estimated_delivery.isoformat()
                if order.estimated_delivery
                else None
            )
        }

    except SQLAlchemyError:

        # 6. Ghi nhận lỗi database
        logger.exception(
            "Failed to query order: %s",
            order_code
        )

        return {
            "success": False,
            "found": False,
            "error": "order_lookup_unavailable",
            "message": "Order lookup service unavailable"
        }
