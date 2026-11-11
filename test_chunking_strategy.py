
from pathlib import Path

from app.services.document_loader import (
    load_markdown_document,
    split_text,
)


# =====================================
# 1. LOAD DOCUMENT
# =====================================

BASE_DIR = Path(__file__).resolve().parent

DOCUMENT_PATH = (
    BASE_DIR
    / "app"
    / "knowledge_base"
    / "policies"
    / "return_policy.md"
)

text, metadata = load_markdown_document(DOCUMENT_PATH)


# =====================================
# 2. DEFINE CHUNKING STRATEGIES
# =====================================

STRATEGIES = [
    {
        "name": "Small",
        "chunk_size": 300,
        "chunk_overlap": 50,
    },
    {
        "name": "Medium",
        "chunk_size": 500,
        "chunk_overlap": 75,
    },
    {
        "name": "Current",
        "chunk_size": 700,
        "chunk_overlap": 100,
    },
    {
        "name": "Large",
        "chunk_size": 1000,
        "chunk_overlap": 150,
    },
]


# =====================================
# 3. COMPARE CHUNKING
# =====================================

print("=" * 60)
print("CHUNKING STRATEGY EVALUATION")
print("=" * 60)

print("Document:", metadata["source"])
print("Original length:", len(text))


for strategy in STRATEGIES:

    chunks = split_text(
        text,
        chunk_size=strategy["chunk_size"],
        chunk_overlap=strategy["chunk_overlap"],
    )

    lengths = [len(chunk) for chunk in chunks]

    average_length = (
        sum(lengths) / len(lengths)
        if lengths else 0
    )

    print("\nSTRATEGY:", strategy["name"])
    print("-" * 60)

    print("Chunk size:", strategy["chunk_size"])
    print("Overlap:", strategy["chunk_overlap"])
    print("Number of chunks:", len(chunks))
    print("Average chunk length:", round(average_length, 2))
    print("Chunk lengths:", lengths)


print("\nEVALUATION COMPLETED")
