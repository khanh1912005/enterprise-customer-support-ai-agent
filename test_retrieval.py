
from app.services.retrieval_service import retrieve_relevant_chunks
from app.services.chroma_service import get_knowledge_collection


def main():

    # 1. Lấy Collection
    collection = get_knowledge_collection()

    # 2. Xóa hai bản ghi thử nghiệm cũ từ test_embedding.py
    # Chỉ xóa đúng hai ID thử nghiệm đã tạo trước đó.
    collection.delete(
        ids=[
            "test_document_001",
            "test_document_002"
        ]
    )

    # 3. Kiểm tra Knowledge Base
    print("TOTAL DOCUMENTS:", collection.count())

    if collection.count() == 0:
        print("Knowledge Base is empty.")
        print("Run: python test_ingestion.py")
        return

    # 4. Câu hỏi kiểm thử
    query = (
        "Sản phẩm của tôi bị hỏng do lỗi kỹ thuật, "
        "tôi có thể đổi trả không?"
    )

    print("\nUSER QUERY:")
    print(query)

    # 5. Semantic Search
    result = retrieve_relevant_chunks(
        query=query,
        top_k=3,
        category="policies"
    )

    print("\nRETRIEVAL RESULT:")
    print("Success:", result["success"])
    print("Found:", result["found"])
    print("Count:", result.get("count", 0))

    # 6. Hiển thị các Chunk tìm được
    for index, item in enumerate(
        result["results"],
        start=1
    ):

        print("\n" + "=" * 60)

        print(f"RESULT {index}")

        print("Similarity:", item["similarity"])

        print("Distance:", item["distance"])

        print("Source:", item["metadata"].get("source"))

        print("Content:")

        print(item["content"])


if __name__ == "__main__":
    main()
