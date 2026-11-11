
from pathlib import Path

from app.services.document_loader import (
    load_markdown_document,
    split_text
)


# =====================================
# 1. DOCUMENT PATH
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
# 2. RUN TEST
# =====================================

def main():

    # Load document
    text, metadata = load_markdown_document(
        DOCUMENT_PATH
    )

    print("DOCUMENT LOADED SUCCESSFULLY")

    print("Metadata:", metadata)

    print("Original length:", len(text))

    # Split document
    chunks = split_text(
        text,
        chunk_size=700,
        chunk_overlap=100
    )

    print("\nTOTAL CHUNKS:", len(chunks))

    # Hiển thị từng Chunk
    for index, chunk in enumerate(chunks):

        print("\n" + "=" * 50)

        print(f"CHUNK {index + 1}")

        print("Length:", len(chunk))

        print(chunk)


if __name__ == "__main__":
    main()
