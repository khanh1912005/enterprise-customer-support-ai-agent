
import logging

from sqlalchemy.orm import Session
from sqlalchemy.exc import SQLAlchemyError

from app.models.ticket import Ticket
from app.models.user import User


logger = logging.getLogger(__name__)


def create_support_ticket(
    issue: str,
    db: Session,
    user_id: int
) -> dict:

    # 1. Kiểm tra nội dung yêu cầu
    if not isinstance(issue, str) or not issue.strip():
        return {
            "success": False,
            "error": "invalid_issue",
            "message": "Nội dung yêu cầu không hợp lệ."
        }

    issue = issue.strip()

    # 2. Giới hạn độ dài nội dung
    if len(issue) > 5000:
        return {
            "success": False,
            "error": "issue_too_long",
            "message": "Nội dung yêu cầu quá dài."
        }

    try:

        # 3. Lấy thông tin người dùng từ PostgreSQL
        user = db.get(User, user_id)

        if user is None or not user.is_active:
            return {
                "success": False,
                "error": "user_not_found",
                "message": "Không tìm thấy tài khoản hợp lệ."
            }

        # 4. Tạo Ticket
        ticket = Ticket(
            user_id=user.id,
            customer_name=user.full_name,
            email=user.email,
            issue=issue,
            status="pending"
        )

        # 5. Lưu vào PostgreSQL
        db.add(ticket)

        db.commit()

        db.refresh(ticket)

        # 6. Trả kết quả
        return {
            "success": True,
            "ticket_id": ticket.id,
            "status": ticket.status,
            "message": "Yêu cầu hỗ trợ đã được tạo thành công."
        }

    except SQLAlchemyError:

        # 7. Rollback nếu database gặp lỗi
        db.rollback()

        logger.exception(
            "Failed to create support ticket for user_id=%s",
            user_id
        )

        return {
            "success": False,
            "error": "ticket_creation_unavailable",
            "message": "Không thể tạo yêu cầu hỗ trợ lúc này."
        }
