
import json

from app.agents.tool_call_demo import (
    AVAILABLE_TOOLS,
    TOOL_HANDLERS,
    execute_tool,
)


# =====================================
# 1. KIỂM TRA DANH SÁCH TOOLS
# =====================================

print("DANH SÁCH TOOLS")
print("=" * 50)

for tool in AVAILABLE_TOOLS:
    print("-", tool["name"])


# =====================================
# 2. KIỂM TRA TOOL REGISTRY
# =====================================

print("\nTOOL REGISTRY")
print("=" * 50)

for tool_name in TOOL_HANDLERS:
    print("-", tool_name)


# =====================================
# 3. KIỂM TRA RAG QUA EXECUTE_TOOL
# =====================================

arguments = {
    "query": "Sản phẩm bị lỗi kỹ thuật thì có được đổi trả không?",
    "top_k": 3,
    "category": "policies",
}

result = execute_tool(
    tool_name="search_knowledge_base",
    arguments=json.dumps(arguments, ensure_ascii=False),

    # Knowledge Tool không truy vấn PostgreSQL.
    # Dùng object giả để thỏa điều kiện kiểm tra context
    # trong Generic Tool Executor.
    db=object(),
    user_id=1,
)


# =====================================
# 4. HIỂN THỊ KẾT QUẢ
# =====================================

print("\nKẾT QUẢ THỰC THI KNOWLEDGE TOOL")
print("=" * 50)

print("Success:", result.get("success"))
print("Found:", result.get("found"))
print("Count:", result.get("count"))

print("\nCONTEXT:")
print(result.get("context"))

print("\nSOURCES:")
for source in result.get("sources", []):
    print(source)
