
import logging

from app.services.embedding_service import create_embeddings
from app.services.chroma_service import get_knowledge_collection


logger = logging.getLogger(__name__)


def retrieve_relevant_chunks(
    query: str,
    top_k: int = 3,
    category: str | None = None,
    min_similarity: float | None = 0.3,
) -> dict:
    """
    Tìm kiếm các đoạn tài liệu liên quan trong ChromaDB.

    Args:
        query: Câu hỏi cần tìm kiếm.
        top_k: Số lượng kết quả tối đa lấy từ ChromaDB.
        category: Nhóm tài liệu cần tìm.
        min_similarity: Ngưỡng tương đồng tối thiểu từ 0 đến 1.
                        None nghĩa là không lọc theo ngưỡng.

    Returns:
        Kết quả tìm kiếm cùng similarity và metadata.
    """

    # =====================================
    # 1. VALIDATE INPUT
    # =====================================

    if not isinstance(query, str) or not query.strip():

        raise ValueError("Query cannot be empty.")

    if (
        not isinstance(top_k, int)
        or isinstance(top_k, bool)
        or not 1 <= top_k <= 10
    ):

        raise ValueError("top_k must be between 1 and 10.")

    if category is not None and (
        not isinstance(category, str) or not category.strip()
    ):

        raise ValueError("Category must be a non-empty string or None.")

    if min_similarity is not None:

        if (
            isinstance(min_similarity, bool)
            or not isinstance(min_similarity, (int, float))
            or not 0 <= min_similarity <= 1
        ):

            raise ValueError(
                "min_similarity must be between 0 and 1."
            )

    query = query.strip()

    # =====================================
    # 2. GET COLLECTION
    # =====================================

    collection = get_knowledge_collection()

    total_documents = collection.count()

    if total_documents == 0:

        return {
            "success": True,
            "found": False,
            "count": 0,
            "results": [],
        }

    # =====================================
    # 3. CREATE QUERY EMBEDDING
    # =====================================

    query_embedding = create_embeddings([query])[0]

    # =====================================
    # 4. METADATA FILTERING
    # =====================================

    where_filter = None

    if category is not None:

        where_filter = {
            "category": category
        }

    # =====================================
    # 5. VECTOR SEARCH
    # =====================================

    search_results = collection.query(
        query_embeddings=[query_embedding],

        n_results=min(top_k, total_documents),

        where=where_filter,

        include=[
            "documents",
            "metadatas",
            "distances",
        ],
    )

    ids = search_results["ids"][0]

    documents = search_results["documents"][0]

    metadatas = search_results["metadatas"][0]

    distances = search_results["distances"][0]

    # =====================================
    # 6. PROCESS RESULTS
    # =====================================

    results = []

    for index, document_id in enumerate(ids):

        content = documents[index]

        metadata = metadatas[index] or {}

        distance = float(distances[index])

        # Với cosine distance:
        # similarity = 1 - distance
        similarity = 1.0 - distance

        # =================================
        # 7. SIMILARITY THRESHOLD
        # =================================

        if (
            min_similarity is not None
            and similarity < min_similarity
        ):

            continue

        results.append({

            "id": document_id,

            "content": content,

            "metadata": metadata,

            "distance": distance,

            "similarity": similarity,

        })

    # =====================================
    # 8. RETURN RESULT
    # =====================================

    logger.info(
        "Retrieval completed: query=%s, top_k=%s, "
        "category=%s, threshold=%s, found=%s",
        query,
        top_k,
        category,
        min_similarity,
        len(results),
    )

    return {
        "success": True,

        "found": len(results) > 0,

        "count": len(results),

        "results": results,
    }
