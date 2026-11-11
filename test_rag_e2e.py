
import json

from app.agents.tool_call_demo import (
    AVAILABLE_TOOLS,
    TOOL_HANDLERS,
    execute_tool,
    build_tool_call_graph,
)


# =====================================
# 1. TEST TOOL SCHEMA
# =====================================

print("=" * 65)
print("STEP 1: TEST TOOL SCHEMA")
print("=" * 65)

tool_names = [
    tool["name"]
    for tool in AVAILABLE_TOOLS
]

print("Available Tools:", tool_names)

assert "search_knowledge_base" in tool_names

assert len(tool_names) == len(set(tool_names))

print("PASS: Knowledge Tool Schema registered.")


# =====================================
# 2. TEST TOOL REGISTRY
# =====================================

print("\nSTEP 2: TEST TOOL REGISTRY")
print("=" * 65)

print("Registered Handlers:", list(TOOL_HANDLERS.keys()))

assert "search_knowledge_base" in TOOL_HANDLERS

print("PASS: Knowledge Tool Handler registered.")


# =====================================
# 3. TEST KNOWLEDGE TOOL EXECUTION
# =====================================

print("\nSTEP 3: TEST KNOWLEDGE TOOL")
print("=" * 65)

arguments = {
    "query": (
        "Chính sách có quy định thời hạn "
        "đổi trả cụ thể không?"
    ),
    "top_k": 3,
    "category": "policies",
}

result = execute_tool(
    tool_name="search_knowledge_base",

    arguments=json.dumps(
        arguments,
        ensure_ascii=False
    ),

    # Object giả chỉ dùng cho bài test local.
    # Knowledge Tool không truy vấn PostgreSQL.
    db=object(),

    user_id=1,
)


print("Success:", result.get("success"))

print("Found:", result.get("found"))

print("Count:", result.get("count"))

assert result.get("success") is True

assert result.get("found") is True


# =====================================
# 4. TEST RAG CONTEXT
# =====================================

print("\nSTEP 4: TEST RAG CONTEXT")
print("=" * 65)

context = result.get("context", "")

sources = result.get("sources", [])

print("\nRetrieved Context:")
print(context)

print("\nRetrieved Sources:")
for source in sources:
    print(source)

assert context.strip()

assert sources

assert (
    "không xác định thời hạn đổi trả"
    in context.casefold()
)

print("PASS: Relevant policy context retrieved.")


# =====================================
# 5. TEST LANGGRAPH INITIALIZATION
# =====================================

print("\nSTEP 5: TEST LANGGRAPH")
print("=" * 65)

graph = build_tool_call_graph()

assert graph is not None

print("PASS: LangGraph compiled successfully.")


# =====================================
# 6. FINAL REPORT
# =====================================

print("\n")
print("=" * 65)
print("RAG END-TO-END TEST REPORT")
print("=" * 65)

print("Tool Schema: PASS")

print("Tool Registry: PASS")

print("Knowledge Tool: PASS")

print("ChromaDB Retrieval: PASS")

print("RAG Context: PASS")

print("LangGraph Initialization: PASS")

print("\nALL LOCAL TESTS PASSED.")
print("=" * 65)
