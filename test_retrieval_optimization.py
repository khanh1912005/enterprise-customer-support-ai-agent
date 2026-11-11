
from app.services.retrieval_service import retrieve_relevant_chunks


# =====================================
# 1. TEST DATASET
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
# 2. TEST CONFIGURATIONS
# =====================================

TOP_K_VALUES = [1, 3, 5]

SIMILARITY_THRESHOLDS = [
    None,
    0.30,
    0.40,
    0.50,
]


# =====================================
# 3. EVALUATION FUNCTION
# =====================================

def evaluate_retrieval(top_k, threshold):

    hits = 0

    reciprocal_rank_total = 0.0

    total_returned = 0

    for test_case in TEST_CASES:

        result = retrieve_relevant_chunks(
            query=test_case["query"],
            top_k=top_k,
            category="policies",
            min_similarity=threshold,
        )

        results = result.get("results", [])

        total_returned += len(results)

        expected_phrase = test_case["expected_phrase"]

        matched_rank = None

        for rank, item in enumerate(results, start=1):

            content = item["content"]

            if expected_phrase.casefold() in content.casefold():

                matched_rank = rank

                break

        if matched_rank is not None:

            hits += 1

            reciprocal_rank_total += 1 / matched_rank

    total_queries = len(TEST_CASES)

    return {
        "hits": hits,

        "hit_rate": hits / total_queries,

        "mrr": reciprocal_rank_total / total_queries,

        "average_results": total_returned / total_queries,
    }


# =====================================
# 4. RUN EXPERIMENTS
# =====================================

print("=" * 70)
print("RETRIEVAL OPTIMIZATION EVALUATION")
print("=" * 70)

for top_k in TOP_K_VALUES:

    for threshold in SIMILARITY_THRESHOLDS:

        metrics = evaluate_retrieval(
            top_k=top_k,
            threshold=threshold,
        )

        threshold_label = (
            "Disabled"
            if threshold is None
            else str(threshold)
        )

        print("\nTOP_K:", top_k)

        print("SIMILARITY THRESHOLD:", threshold_label)

        print("Successful queries:", metrics["hits"])

        print(
            "Hit Rate:",
            round(metrics["hit_rate"], 4)
        )

        print(
            "MRR:",
            round(metrics["mrr"], 4)
        )

        print(
            "Average retrieved chunks:",
            round(metrics["average_results"], 2)
        )

        print("-" * 70)


print("\nEVALUATION COMPLETED")
