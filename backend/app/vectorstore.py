from __future__ import annotations

import os
from pathlib import Path

from langchain_chroma import Chroma
from langchain_core.documents import Document
from langchain_community.embeddings import HuggingFaceEmbeddings


_DEFAULT_PERSIST_DIR = os.getenv("CHROMA_PERSIST_DIR", "./chroma_db")


def get_embeddings(model: str | None = None) -> HuggingFaceEmbeddings:
    model = model or os.getenv("EMBEDDING_MODEL", "all-MiniLM-L6-v2")
    return HuggingFaceEmbeddings(model_name=model)


def get_vectorstore(
    persist_dir: str | Path | None = None,
    collection_name: str = "documents",
    embedding_model: str | None = None,
) -> Chroma:
    persist_dir = str(persist_dir or _DEFAULT_PERSIST_DIR)
    Path(persist_dir).mkdir(parents=True, exist_ok=True)
    return Chroma(
        collection_name=collection_name,
        embedding_function=get_embeddings(embedding_model),
        persist_directory=persist_dir,
    )


def add_documents_to_store(
    chunks: list[Document],
    persist_dir: str | Path | None = None,
    collection_name: str = "documents",
) -> int:
    """Add chunks to the vector store. Returns the number of chunks added."""
    store = get_vectorstore(persist_dir, collection_name)
    store.add_documents(chunks)
    return len(chunks)


def reset_store(
    persist_dir: str | Path | None = None,
    collection_name: str = "documents",
) -> None:
    """Delete the collection and recreate it."""
    store = get_vectorstore(persist_dir, collection_name)
    store.delete_collection()
