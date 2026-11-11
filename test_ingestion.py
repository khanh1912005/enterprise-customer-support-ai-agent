
from pathlib import Path

from app.services.ingestion_service import (
    ingest_markdown_document
)

from app.services.chroma_service import (
    get_knowledge_collection
)


# =====================================
# 1. DEFINE DOCUMENT PATH
# =====================================

BASE_DIR = Path(__file__).resolve().parent

DOCUMENT_PATH = (
    BASE_DIR
    / "app"
    / "knowledge_base"
    / "policies"
    / "return_policy.md"
)


# =====================================
# 2. RUN INGESTION
# =====================================

def main():

    # Đưa tài liệu vào RAG
    result = ingest_markdown_document(
        file_path=DOCUMENT_PATH,
        chunk_size=700,
        chunk_overlap=100
    )

    print("\nINGESTION RESULT:")
    print(result)

    # Lấy Collection
    collection = get_knowledge_collection()

    # Kiểm tra dữ liệu của tài liệu vừa nạp
    documents = collection.get(
        where={
            "source_id": str(DOCUMENT_PATH.resolve())
        },
        include=[
            "documents",
            "metadatas"
        ]
    )

    print("\nDOCUMENTS STORED:", len(documents["ids"]))

    # Hiển thị các Chunk
    for index, document in enumerate(
        documents["documents"]
    ):

        print("\n" + "=" * 50)

        print(f"CHUNK {index + 1}")

        print("CONTENT:")
        print(document)

        print("METADATA:")
        print(documents["metadatas"][index])


if __name__ == "__main__":
    main()
