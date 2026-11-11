
import re


def evaluate_rag_answer(
    context: str,
    answer: str,
    required_facts: list[str],
    unsupported_patterns: dict[str, str] | None = None,
) -> dict:
    """
    Đánh giá câu trả lời RAG bằng phương pháp rule-based.

    context:
        Nội dung tài liệu được Retrieval.

    answer:
        Câu trả lời cần đánh giá.

    required_facts:
        Những thông tin quan trọng cần có trong câu trả lời.

    unsupported_patterns:
        Các mẫu thông tin không được tài liệu hỗ trợ.
    """

    # =====================================
    # 1. VALIDATE INPUT
    # =====================================

    if not isinstance(context, str):
        raise ValueError("Context must be a string.")

    if not isinstance(answer, str) or not answer.strip():
        raise ValueError("Answer cannot be empty.")

    if not isinstance(required_facts, list) or not required_facts:
        raise ValueError("required_facts must be a non-empty list.")

    unsupported_patterns = unsupported_patterns or {}

    # =====================================
    # 2. NORMALIZE TEXT
    # =====================================

    normalized_context = context.casefold()

    normalized_answer = answer.casefold()

    # =====================================
    # 3. CHECK CONTEXT SUPPORT
    # =====================================

    context_facts = [
        fact
        for fact in required_facts
        if fact.casefold() in normalized_context
    ]

    # =====================================
    # 4. CHECK ANSWER FACTS
    # =====================================

    answer_facts = [
        fact
        for fact in required_facts
        if fact.casefold() in normalized_answer
    ]

    # Chỉ tính những thông tin vừa có trong
    # câu trả lời vừa được tài liệu hỗ trợ.
    grounded_facts = [
        fact
        for fact in answer_facts
        if fact.casefold() in normalized_context
    ]

    missing_facts = [
        fact
        for fact in required_facts
        if fact.casefold() not in normalized_answer
    ]

    # =====================================
    # 5. DETECT UNSUPPORTED PATTERNS
    # =====================================

    unsupported_claims = []

    for label, pattern in unsupported_patterns.items():

        matches = re.findall(
            pattern,
            answer,
            flags=re.IGNORECASE
        )

        if matches:

            unsupported_claims.append({
                "label": label,
                "matches": matches
            })

    # =====================================
    # 6. CALCULATE METRICS
    # =====================================

    total_facts = len(required_facts)

    context_recall = len(context_facts) / total_facts

    answer_coverage = len(grounded_facts) / total_facts

    total_checked_items = (
        len(grounded_facts)
        + len(unsupported_claims)
    )

    if total_checked_items:

        faithfulness_heuristic = (
            len(grounded_facts) / total_checked_items
        )

    else:

        faithfulness_heuristic = 0.0

    # =====================================
    # 7. FINAL EVALUATION
    # =====================================

    grounding_pass = (
        len(grounded_facts) > 0
        and len(unsupported_claims) == 0
    )

    return {
        "context_fact_recall": round(context_recall, 4),

        "answer_coverage": round(answer_coverage, 4),

        "faithfulness_heuristic": round(
            faithfulness_heuristic, 4
        ),

        "grounding_pass": grounding_pass,

        "context_facts_found": context_facts,

        "grounded_facts": grounded_facts,

        "missing_facts": missing_facts,

        "unsupported_claims": unsupported_claims,
    }
