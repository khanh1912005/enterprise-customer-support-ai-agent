
import logging

from sqlalchemy import select, or_
from sqlalchemy.exc import SQLAlchemyError
from sqlalchemy.orm import Session

from app.models.product import Product


logger = logging.getLogger(__name__)


def get_product_info(
    keyword: str,
    db: Session
) -> dict:

    # 1. Kiểm tra từ khóa
    if not isinstance(keyword, str) or not keyword.strip():
        return {
            "success": False,
            "found": False,
            "error": "invalid_keyword",
            "message": "Từ khóa tìm kiếm không hợp lệ."
        }

    keyword = keyword.strip()

    if len(keyword) > 100:
        return {
            "success": False,
            "found": False,
            "error": "keyword_too_long",
            "message": "Từ khóa tìm kiếm quá dài."
        }

    try:

        # 2. Tạo từ khóa tìm kiếm
        search_pattern = f"%{keyword}%"

        # 3. Truy vấn sản phẩm
        statement = (
            select(Product)
            .where(
                Product.is_active.is_(True),
                or_(
                    Product.name.ilike(search_pattern),
                    Product.sku.ilike(search_pattern),
                    Product.category.ilike(search_pattern)
                )
            )
            .order_by(Product.name)
            .limit(5)
        )

        products = db.scalars(statement).all()

        # 4. Không tìm thấy sản phẩm
        if not products:
            return {
                "success": True,
                "found": False,
                "products": [],
                "message": "Không tìm thấy sản phẩm phù hợp."
            }

        # 5. Chuẩn hóa dữ liệu trả về
        product_results = []

        for product in products:

            product_results.append({
                "sku": product.sku,
                "name": product.name,
                "description": product.description,
                "category": product.category,
                "price": str(product.price),
                "availability": (
                    "Còn hàng"
                    if product.stock_quantity > 0
                    else "Hết hàng"
                )
            })

        # 6. Trả kết quả
        return {
            "success": True,
            "found": True,
            "count": len(product_results),
            "products": product_results
        }

    except SQLAlchemyError:

        logger.exception(
            "Failed to search products: %s",
            keyword
        )

        return {
            "success": False,
            "found": False,
            "error": "product_lookup_unavailable",
            "message": "Dịch vụ tìm kiếm sản phẩm đang gặp sự cố."
        }
