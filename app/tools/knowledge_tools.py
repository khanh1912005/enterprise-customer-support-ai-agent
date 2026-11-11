
from app.services.rag_service import prepare_rag_context


def search_knowledge_base(
    query: str,
    top_k: int = 3,
    category: str | None = None,
    db=None,
    user_id=None,
) -> dict:
    """
    Tìm kiếm tài liệu trong Knowledge Base bằng RAG.

    Args:
        query: Câu hỏi hoặc nội dung cần tra cứu.
        top_k: Số lượng đoạn tài liệu cần tìm.
        category: Nhóm tài liệu, ví dụ policies.
        db: Giữ tương thích với Tool Registry hiện tại.
        user_id: Giữ tương thích với Tool Registry hiện tại.

    Returns:
        Kết quả tìm kiếm và các đoạn tài liệu liên quan.
    """

    if not isinstance(query, str) or not query.strip():
        return {
            "success": False,
            "found": False,
            "message": "Câu truy vấn không được để trống.",
            "context": "",
            "sources": [],
        }

    result = prepare_rag_context(
        query=query,
        top_k=top_k,
        category=category,
    )

    return {
        "success": result.get("success", False),
        "found": result.get("found", False),
        "context": result.get("context", ""),
        "sources": result.get("sources", []),
        "count": result.get("count", 0),
        "message": result.get("message"),
    }
