from __future__ import annotations

from langchain_chroma import Chroma
from langchain_core.documents import Document

from app.vectorstore import get_vectorstore


def dedupe_documents(docs: list[Document]) -> list[Document]:
    """Strip duplicate chunks caused by re-ingesting the same file.

    Keeps the first (highest-ranked) occurrence of each logical chunk. The key
    uses the file *name* (not the full path) so the same document uploaded into
    different temp directories also collapses to a single entry. Without this,
    re-uploading a PDF floods the context with identical snippets and makes
    answers degrade or look inconsistent across phrasings.
    """
    seen: set[tuple] = set()
    result: list[Document] = []
    for doc in docs:
        name = (doc.metadata.get("source") or "").split("/")[-1].split("\\")[-1]
        ci = doc.metadata.get("chunk_index")
        key = (name, ci, doc.page_content[:120])
        if key in seen:
            continue
        seen.add(key)
        result.append(doc)
    return result


def naive_retrieve(
    query: str,
    k: int = 5,
    persist_dir: str | None = None,
    collection_name: str = "documents",
) -> list[Document]:
    """Retrieve the top-k text chunks by vector similarity (excludes image documents)."""
    store = get_vectorstore(persist_dir, collection_name)
    results = store.similarity_search(
        query,
        k=k,
        filter={"type": {"$ne": "image"}},
    )
    return dedupe_documents(results)
