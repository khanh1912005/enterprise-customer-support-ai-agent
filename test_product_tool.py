
from app.core.database import get_db
from app.tools.product_tools import get_product_info


if __name__ == "__main__":

    # Lấy Database Session
    db_generator = get_db()
    db = next(db_generator)

    try:

        # Kiểm tra tìm kiếm sản phẩm
        result = get_product_info(
            keyword="iPhone 16 Pro",
            db=db
        )

        print("\nKẾT QUẢ PRODUCT TOOL:")
        print(result)

    finally:

        # Đóng Database Session
        db_generator.close()
