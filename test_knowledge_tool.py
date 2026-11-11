
from app.tools.knowledge_tools import search_knowledge_base


result = search_knowledge_base(
    query="Sản phẩm bị lỗi kỹ thuật thì có được đổi trả không?",
    top_k=3,
    category="policies",
)

print("KẾT QUẢ KNOWLEDGE TOOL")
print("=" * 50)

print("Success:", result["success"])
print("Found:", result["found"])
print("Số đoạn tìm được:", result.get("count", 0))

print("\nNỘI DUNG TÌM ĐƯỢC:")
print(result["context"])

print("\nNGUỒN TÀI LIỆU:")
for source in result["sources"]:
    print(source)
