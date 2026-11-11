
from app.services.rag_service import prepare_rag_context


def main():

    # 1. Câu hỏi khách hàng
    query = (
        "Sản phẩm của tôi bị hỏng do lỗi kỹ thuật, "
        "tôi có thể đổi trả không?"
    )

    print("CUSTOMER QUESTION:")
    print(query)

    # 2. Chuẩn bị Context
    result = prepare_rag_context(
        query=query,
        top_k=3,
        category="policies"
    )

    # 3. Kiểm tra kết quả
    print("\nSUCCESS:", result["success"])

    print("FOUND:", result["found"])

    print("COUNT:", result.get("count", 0))

    # 4. Hiển thị Context
    print("\nREFERENCE DOCUMENTS:")

    print(result.get("context", ""))

    # 5. Hiển thị nguồn
    print("\nSOURCES:")

    for source in result.get("sources", []):

        print(source)


if __name__ == "__main__":
    main()
