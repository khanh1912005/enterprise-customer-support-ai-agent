
from pathlib import Path

import chromadb


# =====================================
# 1. DEFINE STORAGE PATH
# =====================================

BASE_DIR = Path(__file__).resolve().parents[2]

CHROMA_DIR = BASE_DIR / "data" / "chroma"

# Tạo thư mục nếu chưa tồn tại
CHROMA_DIR.mkdir(
    parents=True,
    exist_ok=True
)


# =====================================
# 2. INITIALIZE CHROMA CLIENT
# =====================================

chroma_client = chromadb.PersistentClient(
    path=str(CHROMA_DIR)
)


# =====================================
# 3. CREATE KNOWLEDGE COLLECTION
# =====================================

knowledge_collection = (
    chroma_client.get_or_create_collection(
        name="customer_support_knowledge",
        metadata={
            "hnsw:space": "cosine"
        }
    )
)


# =====================================
# 4. GET COLLECTION
# =====================================

def get_knowledge_collection():

    return knowledge_collection
