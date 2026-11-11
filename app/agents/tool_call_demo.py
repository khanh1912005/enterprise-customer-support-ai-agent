
import json
import logging
import re

from typing import Any, Callable, TypedDict

from sqlalchemy.orm import Session

from langchain_core.runnables import RunnableConfig
from langgraph.graph import StateGraph, START, END

from app.services.llm_service import get_client, MODEL

from app.tools.order_tools import get_order_status
from app.tools.ticket_tools import create_support_ticket
from app.tools.product_tools import get_product_info
from app.tools.knowledge_tools import search_knowledge_base


logger = logging.getLogger(__name__)


# =====================================
# 1. DEFINE TOOL SCHEMAS
# =====================================

# TOOL 1: ORDER
AGENT_TOOLS = [
    {
        "type": "function",
        "name": "get_order_status",
        "description": (
            "Tra cứu trạng thái đơn hàng của khách hàng "
            "bằng mã đơn hàng. Sử dụng khi khách hỏi về "
            "đơn hàng, giao hàng hoặc gửi mã đơn hàng."
        ),
        "strict": True,
        "parameters": {
            "type": "object",
            "properties": {
                "order_code": {
                    "type": "string",
                    "description": "Mã đơn hàng, ví dụ DH004."
                }
            },
            "required": ["order_code"],
            "additionalProperties": False
        }
    },

    # TOOL 2: TICKET
    {
        "type": "function",
        "name": "create_support_ticket",
        "description": (
            "Tạo yêu cầu hỗ trợ mới cho khách hàng. "
            "Sử dụng khi khách muốn gửi khiếu nại, "
            "báo lỗi sản phẩm hoặc yêu cầu nhân viên hỗ trợ. "
            "Chỉ truyền nội dung vấn đề. "
            "Không truyền user_id, tên hoặc email."
        ),
        "strict": True,
        "parameters": {
            "type": "object",
            "properties": {
                "issue": {
                    "type": "string",
                    "description": (
                        "Nội dung vấn đề khách hàng muốn "
                        "gửi đến bộ phận hỗ trợ."
                    )
                }
            },
            "required": ["issue"],
            "additionalProperties": False
        }
    }
]


# TOOL 3: PRODUCT
PRODUCT_TOOLS = [
    {
        "type": "function",
        "name": "get_product_info",
        "description": (
            "Tìm kiếm thông tin sản phẩm, giá bán, "
            "danh mục và tình trạng còn hàng. "
            "Sử dụng khi khách hỏi về sản phẩm."
        ),
        "strict": True,
        "parameters": {
            "type": "object",
            "properties": {
                "keyword": {
                    "type": "string",
                    "description": (
                        "Tên, mã SKU hoặc danh mục sản phẩm."
                    )
                }
            },
            "required": ["keyword"],
            "additionalProperties": False
        }
    }
]


# TOOL 4: KNOWLEDGE BASE / RAG
KNOWLEDGE_TOOLS = [
    {
        "type": "function",
        "name": "search_knowledge_base",
        "description": (
            "Tìm kiếm thông tin trong Knowledge Base bằng RAG. "
            "Sử dụng khi khách hỏi về chính sách đổi trả, "
            "hoàn tiền, vận chuyển, thanh toán, bảo hành "
            "hoặc các quy trình hỗ trợ khách hàng. "
            "Không tự bịa nội dung chính sách."
        ),
        "strict": True,
        "parameters": {
            "type": "object",
            "properties": {
                "query": {
                    "type": "string",
                    "description": "Câu hỏi cần tra cứu trong tài liệu."
                },
                "top_k": {
                    "type": "integer",
                    "description": (
                        "Số lượng đoạn tài liệu cần tìm. "
                        "Thông thường sử dụng giá trị 3."
                    )
                },
                "category": {
                    "type": ["string", "null"],
                    "description": (
                        "Nhóm tài liệu cần tìm. "
                        "Ví dụ policies. Sử dụng null nếu không lọc."
                    )
                }
            },
            "required": ["query", "top_k", "category"],
            "additionalProperties": False
        }
    }
]


# Danh sách toàn bộ Tool được cung cấp cho LLM
AVAILABLE_TOOLS = (
    AGENT_TOOLS
    + PRODUCT_TOOLS
    + KNOWLEDGE_TOOLS
)


# =====================================
# 2. DEFINE AGENT STATE
# =====================================

class AgentState(TypedDict, total=False):

    user_message: str

    reply: str

    response_id: str

    input_mode: str

    tool_calls: list[dict[str, Any]]

    tool_outputs: list[dict[str, Any]]

    tool_rounds: int


# =====================================
# 3. AGENT INSTRUCTIONS
# =====================================

AGENT_INSTRUCTIONS = """
Bạn là AI Agent hỗ trợ khách hàng thương mại điện tử.

Bạn có bốn công cụ:

1. get_order_status:
Tra cứu trạng thái đơn hàng bằng mã đơn hàng.

2. create_support_ticket:
Tạo yêu cầu hỗ trợ cho khách hàng.

3. get_product_info:
Tìm kiếm thông tin sản phẩm, giá bán,
danh mục và tình trạng còn hàng.

4. search_knowledge_base:
Tìm kiếm thông tin trong tài liệu doanh nghiệp
bằng phương pháp RAG.

QUY TẮC SỬ DỤNG TOOL:

A. ORDER

Khi khách hỏi về đơn hàng, trạng thái giao hàng
hoặc gửi mã đơn, hãy sử dụng get_order_status.

Nếu khách hỏi về đơn hàng nhưng chưa có mã,
hãy yêu cầu cung cấp mã đơn.

Không tự bịa dữ liệu đơn hàng.


B. PRODUCT

Khi khách hỏi về sản phẩm, giá bán,
danh mục hoặc tình trạng còn hàng,
hãy sử dụng get_product_info.

Không tự bịa giá hoặc thông tin sản phẩm.


C. TICKET

Khi khách yêu cầu tạo yêu cầu hỗ trợ,
gửi khiếu nại hoặc báo lỗi sản phẩm,
hãy sử dụng create_support_ticket.

Chỉ tạo Ticket khi khách thể hiện rõ mong muốn
gửi yêu cầu hỗ trợ hoặc khiếu nại.

Nếu nội dung vấn đề chưa rõ ràng,
hãy hỏi thêm thông tin.

Chỉ truyền nội dung vấn đề vào trường issue.

Không yêu cầu hoặc tự tạo user_id, tên hay email.
Backend sẽ lấy thông tin tài khoản.


D. KNOWLEDGE BASE / RAG

Khi khách hỏi về:
- Chính sách đổi trả.
- Điều kiện hoàn tiền.
- Chính sách vận chuyển.
- Phương thức thanh toán.
- Chính sách bảo hành.
- Quy trình hỗ trợ khách hàng.

Hãy sử dụng search_knowledge_base
để tìm kiếm thông tin trong tài liệu.

Đối với câu hỏi về chính sách, hãy ưu tiên category="policies"
khi phù hợp với tài liệu cần tìm.

Sử dụng top_k=3 trong trường hợp thông thường.

Chỉ trả lời dựa trên nội dung tài liệu được truy xuất.

Không tự bịa thời hạn đổi trả, phí vận chuyển,
điều kiện hoàn tiền hoặc nội dung chính sách.

Nếu Knowledge Base không tìm được tài liệu phù hợp
hoặc tài liệu không chứa đủ thông tin,
hãy thông báo rõ rằng hiện chưa có đủ thông tin
để xác nhận và đề nghị khách liên hệ bộ phận hỗ trợ.

Không được tự xác nhận rằng yêu cầu đổi trả
hoặc hoàn tiền đã được phê duyệt.


E. CONVERSATION MEMORY

1. Sử dụng lịch sử hội thoại hiện tại để hiểu
   các câu hỏi tiếp nối của khách hàng.

2. Khi khách sử dụng những cách nói như:
   - Đơn hàng đó.
   - Sản phẩm này.
   - Trường hợp trên.
   - Còn trường hợp đó thì sao?

   Hãy dựa vào những tin nhắn trước trong cùng cuộc hội thoại
   để xác định đối tượng mà khách đang nhắc đến.

3. Nếu khách hỏi tiếp về đơn hàng,
   hãy sử dụng mã đơn hàng đã xuất hiện trong hội thoại
   để gọi get_order_status.

   Không được lấy kết quả tra cứu cũ thay cho việc
   kiểm tra trạng thái đơn hàng hiện tại.

4. Nếu khách hỏi tiếp về chính sách,
   hãy chuyển câu hỏi thành một truy vấn đầy đủ,
   có chứa ngữ cảnh cần thiết từ các lượt trước,
   rồi sử dụng search_knowledge_base.

   Không chỉ dựa vào câu trả lời chính sách cũ
   nếu cần xác minh lại thông tin trong tài liệu.

5. Chỉ sử dụng lịch sử của cuộc hội thoại hiện tại.
   Không được sử dụng dữ liệu của cuộc hội thoại khác.

6. Nếu không đủ ngữ cảnh để xác định khách đang đề cập
   đến sản phẩm hoặc đơn hàng nào, hãy hỏi lại khách.

QUY TẮC CHUNG:

1. Nếu khách chỉ chào hỏi,
   hãy trả lời trực tiếp, không cần gọi Tool.

2. Không tự bịa dữ liệu đơn hàng.

3. Không tự bịa dữ liệu sản phẩm.

4. Không tự tạo mã Ticket.

5. Chỉ thông báo tạo Ticket thành công
   khi kết quả Tool có success=true.

6. Nếu Tool trả success=false,
   phải thông báo rằng thao tác chưa thành công.

7. Không tự nhận đã thực hiện thao tác
   mà Backend chưa thực hiện.

8. Không tiết lộ dữ liệu của khách hàng khác.

9. Không tự bịa thông tin từ Knowledge Base.
"""


# =====================================
# 4. AGENT NODE
# =====================================

def agent_node(state: AgentState):

    client = get_client()

    # Xác định đầu vào là tin nhắn khách
    # hay kết quả trả về từ Tool
    input_mode = state.get("input_mode", "user")

    previous_response_id = state.get("response_id")

    if input_mode == "tool":

        input_payload = state.get("tool_outputs", [])

    else:

        input_payload = state.get("user_message", "")

    # Chuẩn bị request gửi đến LLM
    request_data = {
        "model": MODEL,

        "instructions": AGENT_INSTRUCTIONS,

        "input": input_payload,

        # Cung cấp đầy đủ 4 Tool
        "tools": AVAILABLE_TOOLS,

        "tool_choice": "auto",

        "max_output_tokens": 500
    }

    # Tiếp tục Responses API nếu có response trước
    if previous_response_id:

        request_data["previous_response_id"] = previous_response_id

    # DEBUG: Kiểm tra các Tool gửi tới LLM
    logger.info(
        "AVAILABLE TOOLS: %s",
        [
            tool["name"]
            for tool in AVAILABLE_TOOLS
        ]
    )

    response = client.responses.create(**request_data)

    # Kiểm tra trạng thái response
    if response.status != "completed":

        raise RuntimeError(
            f"LLM response was not completed: {response.status}"
        )

    # DEBUG: Kiểm tra loại output
    logger.info(
        "LLM OUTPUT TYPES: %s",
        [
            item.type
            for item in response.output
        ]
    )

    # Tìm Function Calls
    function_calls = [
        item
        for item in response.output
        if item.type == "function_call"
    ]

    tool_calls = []

    for call in function_calls:

        tool_calls.append({
            "name": call.name,
            "arguments": call.arguments,
            "call_id": call.call_id
        })

    logger.info(
        "Agent yêu cầu Tool: %s",
        tool_calls
    )

    return {
        "response_id": response.id,

        "tool_calls": tool_calls,

        "tool_outputs": [],

        "input_mode": "user",

        "reply": response.output_text or ""
    }


# =====================================
# 5. TOOL HANDLERS
# =====================================

# TOOL HANDLER 1: ORDER

def get_order_status_handler(
    args: dict[str, Any],
    db: Session,
    user_id: int
) -> dict[str, Any]:

    order_code = args.get("order_code")

    if not isinstance(order_code, str) or not order_code.strip():

        return {
            "success": False,
            "error": "invalid_order_code"
        }

    order_code = order_code.strip().upper()

    if not re.fullmatch(r"DH\d+", order_code):

        return {
            "success": False,
            "error": "invalid_order_code"
        }

    return get_order_status(
        order_code=order_code,
        db=db,
        user_id=user_id
    )


# TOOL HANDLER 2: TICKET

def create_support_ticket_handler(
    args: dict[str, Any],
    db: Session,
    user_id: int
) -> dict[str, Any]:

    issue = args.get("issue")

    if not isinstance(issue, str) or not issue.strip():

        return {
            "success": False,
            "error": "invalid_issue",
            "message": "Nội dung yêu cầu hỗ trợ không hợp lệ."
        }

    return create_support_ticket(
        issue=issue.strip(),
        db=db,
        user_id=user_id
    )


# TOOL HANDLER 3: PRODUCT

def get_product_info_handler(
    args: dict[str, Any],
    db: Session,
    user_id: int
) -> dict[str, Any]:

    keyword = args.get("keyword")

    if not isinstance(keyword, str) or not keyword.strip():

        return {
            "success": False,
            "error": "invalid_keyword"
        }

    return get_product_info(
        keyword=keyword.strip(),
        db=db
    )


# TOOL HANDLER 4: KNOWLEDGE BASE / RAG

def search_knowledge_base_handler(
    args: dict[str, Any],
    db: Session,
    user_id: int
) -> dict[str, Any]:

    query = args.get("query")

    top_k = args.get("top_k", 3)

    category = args.get("category")

    if not isinstance(query, str) or not query.strip():

        return {
            "success": False,
            "error": "invalid_query",
            "message": "Câu truy vấn không hợp lệ."
        }

    if (
        not isinstance(top_k, int)
        or isinstance(top_k, bool)
        or not 1 <= top_k <= 10
    ):

        return {
            "success": False,
            "error": "invalid_top_k",
            "message": "top_k phải nằm trong khoảng từ 1 đến 10."
        }

    if category is not None and not isinstance(category, str):

        return {
            "success": False,
            "error": "invalid_category"
        }

    return search_knowledge_base(
        query=query.strip(),
        top_k=top_k,
        category=category,
        db=db,
        user_id=user_id
    )


# =====================================
# 6. TOOL REGISTRY
# =====================================

ToolHandler = Callable[
    [dict[str, Any], Session, int],
    dict[str, Any]
]


TOOL_HANDLERS: dict[str, ToolHandler] = {

    "get_order_status": get_order_status_handler,

    "create_support_ticket": create_support_ticket_handler,

    "get_product_info": get_product_info_handler,

    "search_knowledge_base": search_knowledge_base_handler

}


# =====================================
# 7. GENERIC TOOL EXECUTOR
# =====================================

def execute_tool(
    tool_name: str,
    arguments: str,
    db: Session | None,
    user_id: int | None
) -> dict[str, Any]:

    # 1. Chuyển JSON thành Dictionary
    try:

        args = json.loads(arguments)

    except (json.JSONDecodeError, TypeError):

        return {
            "success": False,
            "error": "invalid_arguments"
        }

    # 2. Kiểm tra kiểu dữ liệu
    if not isinstance(args, dict):

        return {
            "success": False,
            "error": "arguments_must_be_object"
        }

    # 3. Lấy Handler từ Registry
    handler = TOOL_HANDLERS.get(tool_name)

    if handler is None:

        return {
            "success": False,
            "error": "unknown_tool"
        }

    # 4. Kiểm tra ngữ cảnh thực thi
    if db is None or user_id is None:

        return {
            "success": False,
            "error": "missing_execution_context"
        }

    # 5. Thực thi Handler
    try:

        return handler(
            args=args,
            db=db,
            user_id=user_id
        )

    except Exception:

        logger.exception(
            "Tool execution failed: %s",
            tool_name
        )

        return {
            "success": False,
            "error": "tool_execution_failed",
            "message": "Không thể thực hiện yêu cầu lúc này."
        }


# =====================================
# 8. TOOL EXECUTOR NODE
# =====================================

def tool_executor_node(
    state: AgentState,
    config: RunnableConfig
):

    configurable = config.get("configurable", {})

    db = configurable.get("db")

    # user_id phải đến từ JWT
    user_id = configurable.get("user_id")

    tool_outputs = []

    for tool_call in state.get("tool_calls", []):

        result = execute_tool(
            tool_name=tool_call["name"],
            arguments=tool_call["arguments"],
            db=db,
            user_id=user_id
        )

        logger.info(
            "Tool %s returned success=%s",
            tool_call["name"],
            result.get("success")
        )

        # Gửi kết quả theo call_id tương ứng
        tool_outputs.append({
            "type": "function_call_output",

            "call_id": tool_call["call_id"],

            "output": json.dumps(
                result,
                ensure_ascii=False,
                default=str
            )
        })

    return {
        "tool_outputs": tool_outputs,

        "tool_calls": [],

        "tool_rounds": state.get("tool_rounds", 0) + 1,

        "input_mode": "tool"
    }


# =====================================
# 9. ROUTING
# =====================================

MAX_TOOL_ROUNDS = 3


def route_after_agent(state: AgentState):

    # Không có Tool cần gọi
    if not state.get("tool_calls"):

        return "end"

    # Giới hạn số vòng gọi Tool
    if state.get("tool_rounds", 0) >= MAX_TOOL_ROUNDS:

        return "limit"

    return "execute_tool"


# =====================================
# 10. MAX TOOL NODE
# =====================================

def max_tool_node(state: AgentState):

    return {
        "reply": (
            "Yêu cầu cần quá nhiều lần sử dụng công cụ. "
            "Bạn vui lòng thử lại với yêu cầu cụ thể hơn."
        ),

        "tool_calls": []
    }


# =====================================
# 11. BUILD GRAPH
# =====================================

def build_tool_call_graph(checkpointer=None):

    builder = StateGraph(AgentState)

    builder.add_node("agent", agent_node)

    builder.add_node(
        "tool_executor",
        tool_executor_node
    )

    builder.add_node(
        "max_tool",
        max_tool_node
    )

    # Bắt đầu từ Agent
    builder.add_edge(START, "agent")

    # Agent quyết định có gọi Tool hay không
    builder.add_conditional_edges(
        "agent",
        route_after_agent,
        {
            "execute_tool": "tool_executor",
            "end": END,
            "limit": "max_tool"
        }
    )

    # Thực thi xong quay lại Agent
    builder.add_edge("tool_executor", "agent")

    builder.add_edge("max_tool", END)

    if checkpointer is not None:

        return builder.compile(
            checkpointer=checkpointer
        )

    return builder.compile()


# =====================================
# 12. RUN DEMO
# =====================================

if __name__ == "__main__":

    agent_graph = build_tool_call_graph()

    result = agent_graph.invoke({

        "user_message": "Xin chào shop!",

        "input_mode": "user",

        "tool_calls": [],

        "tool_outputs": [],

        "tool_rounds": 0

    })

    print("\nKẾT QUẢ:")

    print(result["reply"])
