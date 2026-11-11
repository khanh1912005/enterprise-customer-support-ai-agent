
import os
import json
import logging

from pathlib import Path
from dotenv import load_dotenv
from openai import OpenAI, OpenAIError
from sqlalchemy.orm import Session

from app.tools.order_tools import get_order_status
from app.prompts.support_prompt import SUPPORT_ASSISTANT_INSTRUCTIONS


# ==========================================
# 1. CONFIGURATION
# ==========================================

BASE_DIR = Path(__file__).resolve().parents[2]

load_dotenv(BASE_DIR / ".env")

logger = logging.getLogger(__name__)

MODEL = os.getenv("OPENAI_MODEL", "gpt-6-luna")


class LLMConfigurationError(Exception):
    pass


class LLMProviderError(Exception):
    pass
def get_client():

    api_key = os.getenv("OPENAI_API_KEY")

    if not api_key:
        raise LLMConfigurationError(
            "OPENAI_API_KEY is missing"
        )

    return OpenAI(api_key=api_key)

# ==========================================
# 2. DEFINE TOOLS
# ==========================================

ORDER_TOOLS = [
    {
        "type": "function",
        "name": "get_order_status",
        "description": (
            "Tra cứu trạng thái đơn hàng bằng mã đơn hàng. "
            "Sử dụng khi khách hàng hỏi về trạng thái "
            "hoặc tình trạng giao hàng."
        ),
        "strict": True,
        "parameters": {
            "type": "object",
            "properties": {
                "order_code": {
                    "type": "string",
                    "description": "Mã đơn hàng, ví dụ DH001 hoặc DH004"
                }
            },
            "required": ["order_code"],
            "additionalProperties": False
        }
    }
]


# ==========================================
# 3. FIND FUNCTION CALLS
# ==========================================

def find_function_calls(response):

    return [
        item
        for item in response.output
        if item.type == "function_call"
    ]


# ==========================================
# 4. EXECUTE TOOL
# ==========================================

def execute_tool(
    tool_name: str,
    arguments: str,
    db: Session,
    user_id: int
) -> dict:

    # Chuyển JSON thành Python Dictionary
    try:
        args = json.loads(arguments)

    except (json.JSONDecodeError, TypeError):
        return {
            "success": False,
            "error": "Invalid tool arguments"
        }

    # Kiểm tra arguments phải là Dictionary
    if not isinstance(args, dict):
        return {
            "success": False,
            "error": "Arguments must be an object"
        }

    # Chỉ thực thi tool đã đăng ký
    if tool_name == "get_order_status":

        # Lấy đúng tên tham số order_code
        order_code = args.get("order_code")

        if (
            not isinstance(order_code, str)
            or not order_code.strip()
        ):
            return {
                "success": False,
                "error": "Invalid order code"
            }

        # Truy vấn PostgreSQL
        return get_order_status(
            order_code=order_code.strip(),
            db=db,
            user_id=user_id
        )

    return {
        "success": False,
        "error": "Unknown tool"
    }


# ==========================================
# 5. GENERATE RESPONSE WITH TOOL CALLING
# ==========================================

def generate_response(
    user_message: str,
    db: Session,
    user_id: int
) -> str:

    client = get_client()
    try:

        # REQUEST 1:
        # Gửi câu hỏi và danh sách tools đến LLM

        response = client.responses.create(
            model=MODEL,
            instructions=SUPPORT_ASSISTANT_INSTRUCTIONS,
            input=user_message,
            tools=ORDER_TOOLS,
            tool_choice="auto",
            max_output_tokens=500
        )

        # Cho phép tối đa 3 vòng thực thi tool
        for _ in range(3):

            # Tìm function call trong response
            function_calls = find_function_calls(response)

            # Nếu không có function call:
            # Trả câu trả lời cuối cùng
            if not function_calls:

                return response.output_text or (
                    "Xin lỗi, tôi chưa thể tạo câu trả lời."
                )

            tool_outputs = []

            # Thực thi từng function call
            for tool_call in function_calls:

                logger.info(
                    "AI requested tool: %s",
                    tool_call.name
                )

                try:

                    result = execute_tool(
                        tool_name=tool_call.name,
                        arguments=tool_call.arguments,
                        db=db,
                        user_id=user_id
                    )

                except Exception:

                    logger.exception(
                        "Tool execution failed: %s",
                        tool_call.name
                    )

                    result = {
                        "success": False,
                        "error": "Tool execution failed"
                    }

                # Đóng gói kết quả tool
                tool_outputs.append({
                    "type": "function_call_output",
                    "call_id": tool_call.call_id,
                    "output": json.dumps(
                        result,
                        ensure_ascii=False,
                        default=str
                    )
                })

            # REQUEST TIẾP THEO:
            # Gửi kết quả tool trở lại LLM

            response = client.responses.create(
                model=MODEL,
                instructions=SUPPORT_ASSISTANT_INSTRUCTIONS,
                previous_response_id=response.id,
                input=tool_outputs,
                tools=ORDER_TOOLS,
                tool_choice="auto",
                max_output_tokens=500
            )

        # Tránh lặp tool vô hạn
        if find_function_calls(response):
            logger.warning("Maximum tool execution rounds reached")

            return (
                "Xin lỗi, tôi chưa thể hoàn thành yêu cầu. "
                "Vui lòng thử lại."
            )

        return response.output_text or (
            "Xin lỗi, tôi chưa thể tạo câu trả lời."
        )

    except OpenAIError as exc:

        logger.exception("OpenAI API request failed")

        raise LLMProviderError(
            "Could not get a response from the AI provider"
        ) from exc
