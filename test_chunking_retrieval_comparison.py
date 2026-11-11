
from pathlib import Path

from app.services.ingestion_service import ingest_markdown_document
from app.services.retrieval_service import retrieve_relevant_chunks


# =====================================
# 1. DOCUMENT
# =====================================

BASE_DIR = Path(__file__).resolve().parent

DOCUMENT_PATH = (
    BASE_DIR
    / "app"
    / "knowledge_base"
    / "policies"
    / "return_policy.md"
)


# =====================================
# 2. TEST DATASET
# =====================================

TEST_CASES = [
    {
        "query": "Điều kiện nào cho phép khách hàng yêu cầu đổi trả?",
        "expected_phrase": "lỗi kỹ thuật",
    },
    {
        "query": "Khách hàng cần cung cấp thông tin gì khi yêu cầu đổi trả?",
        "expected_phrase": "Mã đơn hàng",
    },
    {
        "query": "Quy trình xử lý yêu cầu đổi trả diễn ra như thế nào?",
        "expected_phrase": "Khách hàng gửi yêu cầu hỗ trợ",
    },
    {
        "query": "Chính sách có quy định thời hạn đổi trả cụ thể không?",
        "expected_phrase": "không xác định thời hạn đổi trả",
    },
]


# =====================================
# 3. CHUNKING CONFIGURATIONS
# =====================================

STRATEGIES = [
    {"name": "Small", "size": 300, "overlap": 50},
    {"name": "Medium", "size": 500, "overlap": 75},
    {"name": "Current", "size": 700, "overlap": 100},
    {"name": "Large", "size": 1000, "overlap": 150},
]


# =====================================
# 4. EVALUATION FUNCTION
# =====================================

def evaluate_retrieval():

    hits = 0
    reciprocal_rank_total = 0.0

    for test_case in TEST_CASES:

        result = retrieve_relevant_chunks(
            query=test_case["query"],
            top_k=3,
            category="policies",
        )

        results = result.get("results", [])

        expected_phrase = test_case["expected_phrase"]

        matched_rank = None

        for rank, item in enumerate(results, start=1):

            content = item.get("content", "")

            if expected_phrase.casefold() in content.casefold():

                matched_rank = rank
                break

        if matched_rank is not None:

            hits += 1
            reciprocal_rank_total += 1 / matched_rank

    total = len(TEST_CASES)

    return {
        "hit_rate": hits / total,
        "mrr": reciprocal_rank_total / total,
        "hits": hits,
    }


# =====================================
# 5. COMPARE STRATEGIES
# =====================================

print("=" * 65)
print("CHUNKING + RETRIEVAL COMPARISON")
print("=" * 65)

try:

    for strategy in STRATEGIES:

        print("\nSTRATEGY:", strategy["name"])
        print("-" * 65)

        # Nạp lại tài liệu với cấu hình đang thử
        ingestion_result = ingest_markdown_document(
            DOCUMENT_PATH,
            chunk_size=strategy["size"],
            chunk_overlap=strategy["overlap"],
        )

        if not ingestion_result.get("success"):
            raise RuntimeError(
                f"Ingestion failed: {ingestion_result}"
            )

        print(
            "Chunks:",
            ingestion_result.get("chunk_count")
        )

        # Đánh giá Retrieval
        metrics = evaluate_retrieval()

        print("Successful queries:", metrics["hits"])

        print(
            "Hit Rate@3:",
            round(metrics["hit_rate"], 4)
        )

        print(
            "MRR:",
            round(metrics["mrr"], 4)
        )

finally:

    # Khôi phục cấu hình hiện tại sau thí nghiệm
    print("\nRestoring original configuration: 700/100")

    restore_result = ingest_markdown_document(
        DOCUMENT_PATH,
        chunk_size=700,
        chunk_overlap=100,
    )

    print("Restore result:", restore_result)

print("\nCOMPARISON COMPLETED")
