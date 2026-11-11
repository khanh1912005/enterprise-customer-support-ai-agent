
import hashlib
import logging

from pathlib import Path

from app.services.document_loader import (
    load_markdown_document,
    split_text
)

from app.services.embedding_service import create_embeddings

from app.services.chroma_service import get_knowledge_collection


logger = logging.getLogger(__name__)


# =====================================
# 1. INGEST MARKDOWN DOCUMENT
# =====================================

def ingest_markdown_document(
    file_path: Path,
    chunk_size: int = 700,
    chunk_overlap: int = 100
) -> dict:

    # 1. Đọc tài liệu
    text, metadata = load_markdown_document(
        file_path
    )

    # 2. Chia tài liệu thành Chunk
    chunks = split_text(
        text=text,
        chunk_size=chunk_size,
        chunk_overlap=chunk_overlap
    )

    if not chunks:
        raise ValueError("Document contains no valid chunks")

    logger.info(
        "Document loaded: %s, chunks=%s",
        file_path.name,
        len(chunks)
    )

    # 3. Tạo Embeddings bằng model local
    embeddings = create_embeddings(chunks)

    # 4. Lấy ChromaDB Collection
    collection = get_knowledge_collection()

    # 5. Tạo định danh nguồn tài liệu
    source_id = str(file_path.resolve())

    # 6. Lấy những Chunk cũ của tài liệu này
    existing = collection.get(
        where={
            "source_id": source_id
        },
        include=["metadatas"]
    )

    old_ids = set(existing["ids"])

    # 7. Tạo ID ổn định cho từng Chunk
    chunk_ids = []

    chunk_metadatas = []

    for index, chunk in enumerate(chunks):

        raw_id = f"{source_id}:{index}:{chunk}"

        chunk_id = hashlib.sha256(
            raw_id.encode("utf-8")
        ).hexdigest()

        chunk_ids.append(chunk_id)

        chunk_metadata = {
            **metadata,
            "source_id": source_id,
            "chunk_index": index
        }

        chunk_metadatas.append(chunk_metadata)

    # 8. Lưu hoặc cập nhật Chunk vào ChromaDB
    collection.upsert(
        ids=chunk_ids,
        documents=chunks,
        embeddings=embeddings,
        metadatas=chunk_metadatas
    )

    # 9. Xóa Chunk cũ không còn được sử dụng
    # khi tài liệu bị thay đổi và số Chunk giảm
    stale_ids = old_ids - set(chunk_ids)

    if stale_ids:

        collection.delete(
            ids=list(stale_ids)
        )

    logger.info(
        "Document ingested successfully: %s",
        file_path.name
    )

    # 10. Trả kết quả
    return {
        "success": True,
        "source": metadata["source"],
        "chunk_count": len(chunks),
        "updated_count": len(set(chunk_ids) & old_ids),
        "new_count": len(set(chunk_ids) - old_ids),
        "removed_count": len(stale_ids)
    }
