from __future__ import annotations

import os
from pathlib import Path

from langchain_chroma import Chroma
from langchain_core.documents import Document
from langchain_openai import OpenAIEmbeddings
from langchain_community.retrievers import BM25Retriever
from sentence_transformers import CrossEncoder

from app.vectorstore import get_vectorstore
from app.retriever import dedupe_documents


_cross_encoder: CrossEncoder | None = None


def _get_cross_encoder() -> CrossEncoder:
    global _cross_encoder
    if _cross_encoder is None:
        model_name = os.getenv("RERANKER_MODEL", "cross-encoder/ms-marco-MiniLM-L-6-v2")
        _cross_encoder = CrossEncoder(model_name)
    return _cross_encoder


def reciprocal_rank_fusion(
    results_list: list[list[Document]],
    k: int = 60,
) -> list[Document]:
    """Combine multiple result lists using Reciprocal Rank Fusion (RRF).

    Each list is assumed to be in relevance order (best first).
    k=60 is the standard constant from the original RRF paper.
    """
    scores: dict[str, float] = {}
    doc_map: dict[str, Document] = {}

    for results in results_list:
        for rank, doc in enumerate(results):
            doc_id = f"{doc.metadata.get('source', '')}:{doc.page_content[:100]}"
            if doc_id not in scores:
                scores[doc_id] = 0.0
                doc_map[doc_id] = doc
            scores[doc_id] += 1.0 / (k + rank + 1)

    sorted_ids = sorted(scores.keys(), key=lambda x: scores[x], reverse=True)
    return [doc_map[did] for did in sorted_ids]


def hybrid_retrieve(
    query: str,
    k: int = 5,
    collection_name: str = "documents",
    vector_weight: float = 0.6,
    bm25_weight: float = 0.4,
) -> list[Document]:
    """Hybrid retrieval combining vector search and BM25 with RRF fusion."""
    store = get_vectorstore(collection_name=collection_name)

    vector_results = store.similarity_search(query, k=k * 2, filter={"type": {"$ne": "image"}})

    all_docs = store.get(where={"type": {"$ne": "image"}})
    if all_docs and all_docs.get("documents"):
        bm25_docs = [
            Document(page_content=doc, metadata=meta)
            for doc, meta in zip(all_docs["documents"], all_docs["metadatas"])
        ]
        bm25_retriever = BM25Retriever.from_documents(bm25_docs, k=k * 2)
        bm25_results = bm25_retriever.invoke(query)
    else:
        bm25_results = []

    fused = reciprocal_rank_fusion([vector_results, bm25_results])
    return dedupe_documents(fused[:k])


def rerank(
    query: str,
    documents: list[Document],
    top_n: int = 5,
) -> list[Document]:
    """Re-rank documents using a cross-encoder model."""
    if not documents:
        return []

    encoder = _get_cross_encoder()
    pairs = [(query, doc.page_content) for doc in documents]
    scores = encoder.predict(pairs)

    scored_docs = list(zip(documents, scores))
    scored_docs.sort(key=lambda x: x[1], reverse=True)
    return [doc for doc, _ in scored_docs[:top_n]]
