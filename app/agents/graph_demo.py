
from typing import TypedDict, Annotated
import operator
import re

from sqlalchemy.orm import Session
from langchain_core.runnables import RunnableConfig

from langgraph.graph import StateGraph, START, END
from langgraph.checkpoint.memory import InMemorySaver

from app.services.llm_service import get_client, MODEL
from app.tools.order_tools import get_order_status


# =====================================
# 1. DEFINE STATE
# =====================================

class SupportState(TypedDict):
    user_message: str
    intent: str
    reply: str

    # Lưu lịch sử hội thoại
    history: Annotated[list[dict[str, str]], operator.add]


# =====================================
# 2. HELPER FUNCTIONS
# =====================================

# Regex nhận diện mã đơn hàng
ORDER_CODE_PATTERN = re.compile(
    r"\bDH\d+\b",
    re.IGNORECASE
)


def find_order_code(user_message: str, history: list) -> str | None:

    # 1. Ưu tiên tìm mã trong tin nhắn hiện tại
    match = ORDER_CODE_PATTERN.search(user_message)

    if match:
        return match.group(0).upper()

    # 2. Nếu không có, tìm ngược trong lịch sử
    for item in reversed(history):

        # Chỉ tìm trong tin nhắn của khách hàng
        if item.get("role") == "user":

            old_message = item.get("content", "")

            match = ORDER_CODE_PATTERN.search(old_message)

            if match:
                return match.group(0).upper()

    return None


# =====================================
# 3. DEFINE NODES
# =====================================

# NODE 1: PHÂN LOẠI YÊU CẦU
def classify_request(state: SupportState):

    user_message = state["user_message"]

    history = state.get("history", [])

    # 1. Kiểm tra khách có gửi mã đơn trực tiếp không
    current_order = ORDER_CODE_PATTERN.search(user_message)

    if current_order:
        return {
            "intent": "order"
        }

    # 2. Kiểm tra lịch sử có mã đơn hàng không
    has_previous_order = any(
        item.get("role") == "user"
        and ORDER_CODE_PATTERN.search(item.get("content", ""))
        for item in history
    )

    # 3. Nếu khách dùng từ tham chiếu đến đơn hàng trước đó
    has_reference = re.search(
        r"\b(đó|nó|đơn này|đơn kia|đơn ấy|mã này|mã đó)\b",
        user_message,
        re.IGNORECASE
    )

    has_order_context = re.search(
        r"(đơn|kiểm tra|trạng thái|giao hàng|nhận hàng|bao giờ|khi nào)",
        user_message,
        re.IGNORECASE
    )

    if has_previous_order and has_reference and has_order_context:
        return {
            "intent": "order"
        }

    # 4. Chuẩn bị lịch sử cho LLM đọc
    history_text = "\n".join(
        f"{item['role']}: {item['content']}"
        for item in history[-10:]
    )

    client = get_client()

    # 5. Gọi LLM phân loại
    response = client.responses.create(
        model=MODEL,

        instructions="""
        Bạn là hệ thống phân loại yêu cầu khách hàng.

        Chọn chính xác một trong bốn nhãn:

        greeting:
        Khách hàng chào hỏi.

        order:
        Khách hàng hỏi về đơn hàng, giao hàng,
        mã đơn, trạng thái đơn hàng hoặc thời gian nhận hàng.

        payment:
        Khách hàng hỏi về thanh toán, chuyển khoản,
        bị trừ tiền, thanh toán thất bại hoặc hoàn tiền.

        other:
        Những yêu cầu khác như hỏi sản phẩm,
        giá bán, khuyến mãi hoặc tư vấn mua hàng.

        Hãy đọc cả lịch sử hội thoại và tin nhắn hiện tại
        để hiểu ngữ cảnh.

        Chỉ trả về một nhãn:
        greeting, order, payment hoặc other.

        Không giải thích.
        """,

        input=f"""
        LỊCH SỬ HỘI THOẠI:

        {history_text if history_text else "Chưa có lịch sử."}

        TIN NHẮN HIỆN TẠI:

        {user_message}
        """,

        max_output_tokens=20
    )

    raw_intent = (response.output_text or "").strip().lower()

    print("LLM trả về:", repr(raw_intent))

    raw_intent = raw_intent.replace("`", "")

    intent = (
        raw_intent.split()[0].strip(".,:;!?\"'")
        if raw_intent else ""
    )

    allowed_intents = {
        "greeting",
        "order",
        "payment",
        "other"
    }

    if intent not in allowed_intents:
        intent = "other"

    return {
        "intent": intent
    }


# NODE 2: XỬ LÝ CHÀO HỎI
def greeting_node(state: SupportState):

    return {
        "reply": "Xin chào! Tôi có thể giúp gì cho bạn?"
    }


# NODE 3: XỬ LÝ ĐƠN HÀNG
def order_node(
    state: SupportState,
    config: RunnableConfig
):

    user_message = state["user_message"]

    history = state.get("history", [])

    # 1. Tìm mã đơn trong tin nhắn hiện tại
    # Nếu không có thì tìm lại trong lịch sử
    order_code = find_order_code(
        user_message,
        history
    )

    # 2. Nếu không tìm thấy mã đơn
    if not order_code:
        return {
            "reply": (
                "Bạn vui lòng cung cấp mã đơn hàng "
                "(ví dụ DH001) để tôi kiểm tra nhé."
            )
        }

    # 3. Lấy DB và user_id từ config
    configurable = config.get("configurable", {})

    db: Session = configurable.get("db")

    user_id = configurable.get("user_id")

    # 4. Kiểm tra cấu hình
    if db is None or user_id is None:
        return {
            "reply": (
                "Hệ thống chưa được cấu hình "
                "kết nối tra cứu đơn hàng."
            )
        }

    # 5. Gọi công cụ truy vấn PostgreSQL
    result = get_order_status(
        order_code=order_code,
        db=db,
        user_id=user_id
    )

    # 6. Xử lý lỗi database
    if result.get("error") == "order_lookup_unavailable":
        return {
            "reply": (
                "Hệ thống tra cứu đơn hàng đang gặp sự cố. "
                "Bạn vui lòng thử lại sau."
            )
        }

    # 7. Không tìm thấy đơn hàng
    if not result.get("found"):
        return {
            "reply": result.get(
                "message",
                "Không tìm thấy đơn hàng."
            )
        }

    # 8. Trả kết quả
    return {
        "reply": (
            f"Đơn hàng {result['order_code']} của bạn:\n"
            f"- Trạng thái: {result['status']}\n"
            f"- Đơn vị vận chuyển: "
            f"{result.get('carrier') or 'Chưa cập nhật'}\n"
            f"- Dự kiến giao hàng: "
            f"{result.get('estimated_delivery') or 'Chưa có thông tin'}"
        )
    }


# NODE 4: XỬ LÝ THANH TOÁN
def payment_node(state: SupportState):

    return {
        "reply": (
            "Tôi có thể hỗ trợ bạn về các vấn đề thanh toán."
        )
    }


# NODE 5: XỬ LÝ CÁC YÊU CẦU KHÁC
def other_node(state: SupportState):

    return {
        "reply": (
            "Bạn vui lòng mô tả rõ hơn vấn đề cần hỗ trợ."
        )
    }


# NODE 6: LƯU LỊCH SỬ HỘI THOẠI
def save_conversation(state: SupportState):

    return {
        "history": [
            {
                "role": "user",
                "content": state["user_message"]
            },
            {
                "role": "assistant",
                "content": state["reply"]
            }
        ]
    }


# =====================================
# 4. DEFINE ROUTING
# =====================================

def route_request(state: SupportState):

    if state["intent"] == "greeting":
        return "greeting"

    elif state["intent"] == "order":
        return "order"

    elif state["intent"] == "payment":
        return "payment"

    return "other"


# =====================================
# 5. BUILD GRAPH
# =====================================

builder = StateGraph(SupportState)

# Đăng ký các Node
builder.add_node("classify", classify_request)

builder.add_node("greeting", greeting_node)

builder.add_node("order", order_node)

builder.add_node("payment", payment_node)

builder.add_node("other", other_node)

builder.add_node("save_conversation", save_conversation)


# Điểm bắt đầu
builder.add_edge(START, "classify")


# Điều hướng
builder.add_conditional_edges(
    "classify",
    route_request,
    {
        "greeting": "greeting",
        "order": "order",
        "payment": "payment",
        "other": "other"
    }
)


# Tất cả nhánh đi qua Node lưu lịch sử
builder.add_edge("greeting", "save_conversation")

builder.add_edge("order", "save_conversation")

builder.add_edge("payment", "save_conversation")

builder.add_edge("other", "save_conversation")


# Kết thúc Graph
builder.add_edge("save_conversation", END)


# =====================================
# 6. ENABLE MEMORY
# =====================================

def build_support_graph(checkpointer):

    return builder.compile(
        checkpointer=checkpointer
    )

# =====================================
# 7. RUN GRAPH DEMO
# =====================================

if __name__ == "__main__":

    demo_config = {
        "configurable": {
            "thread_id": "demo-thread-001"
        }
    }
    demo_checkpointer = InMemorySaver()

    support_graph = build_support_graph(
    demo_checkpointer
)
    messages = [
        "Xin chào",
        "Tôi gặp vấn đề khi thanh toán",
        "Tôi vẫn chưa nhận được tiền"
    ]

    for index, message in enumerate(messages, start=1):

        result = support_graph.invoke(
            {
                "user_message": message,
                "intent": "",
                "reply": "",
                "history": []
            },
            config=demo_config
        )

        print(f"\nLƯỢT {index}")

        print("Khách hàng:", message)

        print("Intent:", result["intent"])

        print("Agent:", result["reply"])

        print("Lịch sử:", result["history"])

        print(
            "Số tin nhắn đã lưu:",
            len(result["history"])
        )

        print("-" * 50)
