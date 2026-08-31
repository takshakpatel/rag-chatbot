from __future__ import annotations

from langchain_core.documents import Document
from langchain_text_splitters import RecursiveCharacterTextSplitter


def chunk_documents(
    documents: list[Document],
    chunk_size: int = 1000,
    chunk_overlap: int = 200,
) -> list[Document]:
    """Split documents into overlapping chunks using recursive character splitting.

    Image documents (metadata.type == "image") are passed through as-is.
    """
    text_docs = [d for d in documents if d.metadata.get("type") != "image"]
    image_docs = [d for d in documents if d.metadata.get("type") == "image"]

    splitter = RecursiveCharacterTextSplitter(
        chunk_size=chunk_size,
        chunk_overlap=chunk_overlap,
        length_function=len,
        add_start_index=True,
    )
    chunks = splitter.split_documents(text_docs)
    for i, chunk in enumerate(chunks):
        chunk.metadata["chunk_index"] = i

    # Append image docs (unsplit) after text chunks
    for img_doc in image_docs:
        img_doc.metadata["chunk_index"] = len(chunks)
        chunks.append(img_doc)

    return chunks
