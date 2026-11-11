
from functools import lru_cache

from sentence_transformers import SentenceTransformer


# =====================================
# 1. MODEL CONFIGURATION
# =====================================

EMBEDDING_MODEL = (
    "sentence-transformers/"
    "paraphrase-multilingual-MiniLM-L12-v2"
)


# =====================================
# 2. LOAD MODEL
# =====================================

@lru_cache(maxsize=1)
def get_embedding_model():

    return SentenceTransformer(
        EMBEDDING_MODEL,
        device="cpu"
    )


# =====================================
# 3. CREATE EMBEDDINGS
# =====================================

def create_embeddings(
    texts: list[str]
) -> list[list[float]]:

    if not texts:
        raise ValueError("Texts cannot be empty")

    for text in texts:

        if not isinstance(text, str) or not text.strip():
            raise ValueError(
                "Each text must be a non-empty string"
            )

    # Lấy model local
    model = get_embedding_model()

    # Chuyển văn bản thành vector
    embeddings = model.encode(
        texts,
        convert_to_numpy=True,
        normalize_embeddings=True,
        show_progress_bar=False
    )

    return embeddings.tolist()
