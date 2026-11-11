
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
# 2. EVALUATION CONFIGURATION
# =====================================

TOP_K = 3
CATEGORY = "policies"


# =====================================
# 3. EVALUATION METRICS
# =====================================

total_queries = len(TEST_CASES)

hit_count = 0

reciprocal_rank_total = 0.0


# =====================================
# 4. RUN EVALUATION
# =====================================

print("=" * 60)
print("RAG RETRIEVAL EVALUATION")
print("=" * 60)

for index, test_case in enumerate(TEST_CASES, start=1):

    query = test_case["query"]

    expected_phrase = test_case["expected_phrase"]

    result = retrieve_relevant_chunks(
        query=query,
        top_k=TOP_K,
        category=CATEGORY
    )

    results = result.get("results", [])

    # Tìm vị trí kết quả chứa cụm từ mong đợi
    matched_rank = None

    for rank, item in enumerate(results, start=1):

        content = item.get("content", "")

        if expected_phrase.casefold() in content.casefold():

            matched_rank = rank

            break

    # Tính Hit Rate và Reciprocal Rank
    if matched_rank is not None:

        hit_count += 1

        reciprocal_rank_total += 1 / matched_rank

        status = "HIT"

    else:

        status = "MISS"

    # Hiển thị kết quả từng câu hỏi
    print(f"\nTEST CASE {index}")
    print("-" * 60)

    print("Query:", query)

    print("Expected phrase:", expected_phrase)

    print("Status:", status)

    print("Matched rank:", matched_rank)

    print("Retrieved documents:", len(results))


# =====================================
# 5. CALCULATE FINAL METRICS
# =====================================

hit_rate = hit_count / total_queries

mrr = reciprocal_rank_total / total_queries


# =====================================
# 6. DISPLAY FINAL REPORT
# =====================================

print("\n")
print("=" * 60)
print("FINAL EVALUATION REPORT")
print("=" * 60)

print(f"Total queries: {total_queries}")

print(f"Successful queries: {hit_count}")

print(f"Hit Rate@{TOP_K}: {hit_rate:.4f}")

print(f"MRR: {mrr:.4f}")

print("=" * 60)
