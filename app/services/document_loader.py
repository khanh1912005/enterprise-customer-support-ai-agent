
from pathlib import Path


# =====================================
# 1. LOAD MARKDOWN DOCUMENT
# =====================================

def load_markdown_document(
    file_path: Path
) -> tuple[str, dict]:

    # Kiểm tra file tồn tại
    if not file_path.exists():
        raise FileNotFoundError(
            f"Document not found: {file_path}"
        )

    # Kiểm tra phần mở rộng
    if file_path.suffix.lower() != ".md":
        raise ValueError(
            "Only Markdown files are supported"
        )

    # Đọc nội dung UTF-8
    text = file_path.read_text(
        encoding="utf-8"
    )

    if not text.strip():
        raise ValueError(
            "Document is empty"
        )

    # Metadata mô tả nguồn tài liệu
    metadata = {
        "source": file_path.name,
        "category": file_path.parent.name,
        "file_type": "markdown"
    }

    return text, metadata


# =====================================
# 2. SPLIT TEXT INTO CHUNKS
# =====================================

def split_text(
    text: str,
    chunk_size: int = 700,
    chunk_overlap: int = 100
) -> list[str]:

    if chunk_size <= 0:
        raise ValueError(
            "chunk_size must be positive"
        )

    if chunk_overlap < 0 or chunk_overlap >= chunk_size:
        raise ValueError(
            "chunk_overlap must be smaller than chunk_size"
        )

    if not text.strip():
        return []

    chunks = []

    start = 0
    text_length = len(text)

    while start < text_length:

        # Xác định điểm kết thúc dự kiến
        end = min(
            start + chunk_size,
            text_length
        )

        # Ưu tiên cắt ở ranh giới đoạn,
        # dòng hoặc câu thay vì cắt giữa từ.
        if end < text_length:

            search_start = start + chunk_size // 2

            boundaries = [
                text.rfind("\n\n", search_start, end),
                text.rfind("\n", search_start, end),
                text.rfind(". ", search_start, end),
                text.rfind(" ", search_start, end)
            ]

            boundary = max(boundaries)

            if boundary > start:

                if text.startswith("\n\n", boundary):
                    end = boundary + 2

                elif text.startswith(". ", boundary):
                    end = boundary + 1

                else:
                    end = boundary + 1

        # Lấy nội dung Chunk
        chunk = text[start:end].strip()

        if chunk:
            chunks.append(chunk)

        if end >= text_length:
            break

        # Tạo phần overlap
        next_start = end - chunk_overlap

        # Điều chỉnh để không bắt đầu giữa một từ
        while (
            next_start < end
            and text[next_start].isspace()
        ):
            next_start += 1

        start = max(
            next_start,
            start + 1
        )

    return chunks
