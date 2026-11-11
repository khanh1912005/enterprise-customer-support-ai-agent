
from app.services.embedding_service import create_embeddings
from app.services.chroma_service import get_knowledge_collection


def main():

    # 1. Văn bản kiểm tra
    texts = [
        "Khách hàng có thể yêu cầu đổi trả khi sản phẩm bị lỗi kỹ thuật.",
        "Đơn hàng đang vận chuyển sẽ được cập nhật trạng thái giao hàng."
    ]

    # 2. Tạo Embeddings
    embeddings = create_embeddings(texts)

    print("SỐ LƯỢNG VĂN BẢN:", len(texts))

    print(
        "KÍCH THƯỚC VECTOR:",
        len(embeddings[0])
    )

    # 3. Lấy ChromaDB Collection
    collection = get_knowledge_collection()

    # 4. Lưu dữ liệu vào ChromaDB
    collection.upsert(
        ids=[
            "test_document_001",
            "test_document_002"
        ],
        documents=texts,
        embeddings=embeddings,
        metadatas=[
            {
                "source": "return_policy.md",
                "category": "return_policy"
            },
            {
                "source": "shipping_policy.md",
                "category": "shipping_policy"
            }
        ]
    )

    print("\nĐÃ LƯU DỮ LIỆU VÀO CHROMADB")

    # 5. Kiểm tra số lượng dữ liệu
    print(
        "SỐ DOCUMENT TRONG COLLECTION:",
        collection.count()
    )


if __name__ == "__main__":
    main()
