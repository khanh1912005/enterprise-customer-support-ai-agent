
from app.services.rag_service import prepare_rag_context

from app.services.rag_evaluation_service import (
    evaluate_rag_answer,
)


# =====================================
# 1. HALLUCINATION DETECTION RULES
# =====================================

UNSUPPORTED_PATTERNS = {
    "Tự bịa thời hạn đổi trả": r"\b30\s*ngày\b",

    "Tự bịa tỷ lệ hoàn tiền": r"hoàn tiền\s*100\s*%",

    "Tự bịa chính sách miễn phí": (
        r"miễn phí\s+(vận chuyển|đổi trả)"
    ),
}


# =====================================
# 2. EVALUATION DATASET
# =====================================

TEST_CASES = [

    {
        "name": "Return conditions",

        "query": (
            "Điều kiện nào cho phép khách hàng yêu cầu đổi trả?"
        ),

        "required_facts": [
            "lỗi kỹ thuật",
            "hư hỏng trong quá trình vận chuyển",
            "giao không đúng với đơn đặt hàng",
        ],

        "answer": (
            "Khách hàng có thể gửi yêu cầu đổi trả khi "
            "sản phẩm bị lỗi kỹ thuật, "
            "bị hư hỏng trong quá trình vận chuyển "
            "hoặc được giao không đúng với đơn đặt hàng."
        ),
    },

    {
        "name": "Return requirements",

        "query": (
            "Khách hàng cần cung cấp thông tin gì khi đổi trả?"
        ),

        "required_facts": [
            "Mã đơn hàng",
            "Mô tả tình trạng sản phẩm",
            "Hình ảnh hoặc video thể hiện lỗi nếu có",
        ],

        "answer": (
            "Khách hàng cần cung cấp mã đơn hàng, "
            "mô tả tình trạng sản phẩm và "
            "hình ảnh hoặc video thể hiện lỗi nếu có."
        ),
    },

    {
        "name": "Return process",

        "query": (
            "Quy trình xử lý yêu cầu đổi trả diễn ra thế nào?"
        ),

        "required_facts": [
            "Khách hàng gửi yêu cầu hỗ trợ",
            "Bộ phận chăm sóc khách hàng tiếp nhận",
            "Nhân viên kiểm tra thông tin đơn hàng",
            "Nhân viên thông báo phương án xử lý",
        ],

        "answer": (
            "Quy trình gồm bốn bước: "
            "Khách hàng gửi yêu cầu hỗ trợ. "
            "Bộ phận chăm sóc khách hàng tiếp nhận. "
            "Nhân viên kiểm tra thông tin đơn hàng "
            "và tình trạng sản phẩm. "
            "Cuối cùng, nhân viên thông báo phương án xử lý."
        ),
    },

    {
        "name": "Missing return deadline",

        "query": (
            "Chính sách có quy định thời hạn đổi trả cụ thể không?"
        ),

        "required_facts": [
            "không xác định thời hạn đổi trả",
            "mức phí",
            "điều kiện hoàn tiền cụ thể",
        ],

        "answer": (
            "Tài liệu mẫu không xác định thời hạn đổi trả, "
            "mức phí hoặc điều kiện hoàn tiền cụ thể."
        ),
    },
]


# =====================================
# 3. EVALUATION CONFIGURATION
# =====================================

TOP_K = 3

CATEGORY = "policies"


# =====================================
# 4. RUN EVALUATION
# =====================================

print("=" * 65)
print("RAG GENERATION EVALUATION")
print("=" * 65)

for index, test_case in enumerate(TEST_CASES, start=1):

    print(f"\nTEST CASE {index}: {test_case['name']}")

    print("-" * 65)

    # Retrieve relevant documents
    retrieval = prepare_rag_context(
        query=test_case["query"],
        top_k=TOP_K,
        category=CATEGORY,
    )

    if not retrieval.get("found"):

        print("SKIPPED: No relevant context found.")

        continue

    # Evaluate the sample answer
    evaluation = evaluate_rag_answer(
        context=retrieval["context"],

        answer=test_case["answer"],

        required_facts=test_case["required_facts"],

        unsupported_patterns=UNSUPPORTED_PATTERNS,
    )

    print("Context Fact Recall:",
          evaluation["context_fact_recall"])

    print("Answer Coverage:",
          evaluation["answer_coverage"])

    print("Faithfulness Heuristic:",
          evaluation["faithfulness_heuristic"])

    print("Grounding Pass:",
          evaluation["grounding_pass"])

    print("\nMissing Facts:")

    for fact in evaluation["missing_facts"]:
        print("-", fact)

    print("\nUnsupported Claims:")

    if evaluation["unsupported_claims"]:

        for claim in evaluation["unsupported_claims"]:
            print("-", claim)

    else:

        print("None detected")


# =====================================
# 5. NEGATIVE TEST
# =====================================

print("\n")
print("=" * 65)
print("HALLUCINATION NEGATIVE TEST")
print("=" * 65)

# Retrieve context for the deadline question
retrieval = prepare_rag_context(
    query="Chính sách có quy định thời hạn đổi trả cụ thể không?",
    top_k=3,
    category="policies",
)

if retrieval.get("found"):

    # Cố tình tạo câu trả lời sai để kiểm tra detector.
    bad_answer = (
        "Khách hàng được đổi trả trong vòng 30 ngày "
        "và được hoàn tiền 100%."
    )

    bad_evaluation = evaluate_rag_answer(
        context=retrieval["context"],

        answer=bad_answer,

        required_facts=[
            "không xác định thời hạn đổi trả",
            "mức phí",
            "điều kiện hoàn tiền cụ thể",
        ],

        unsupported_patterns=UNSUPPORTED_PATTERNS,
    )

    print("Bad answer:", bad_answer)

    print("Faithfulness Heuristic:",
          bad_evaluation["faithfulness_heuristic"])

    print("Grounding Pass:",
          bad_evaluation["grounding_pass"])

    print("Detected unsupported claims:")

    for claim in bad_evaluation["unsupported_claims"]:
        print(claim)


print("\nEVALUATION COMPLETED")
