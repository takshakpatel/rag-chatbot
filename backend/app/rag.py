from __future__ import annotations

import os
import re
import time

from langchain_core.prompts import ChatPromptTemplate
from langchain_community.llms import Ollama

from app.retriever import naive_retrieve
from app.hybrid_retriever import hybrid_retrieve, rerank
from app.cache import query_cache
from app.token_tracker import token_tracker


_MAX_RETRIES = 3
_RETRY_BACKOFF = 1.5  # seconds, grows per attempt


def _generate_with_retry(chain, context: str, question: str):
    """Invoke the LLM chain, retrying transient Ollama failures with backoff.

    A local Ollama model can stall or fail to (re)load, which surfaces as an
    intermittent "error" even for valid prompts. We retry a few times before
    giving up so equivalent phrasings behave consistently.
    """
    last_err: Exception | None = None
    for attempt in range(_MAX_RETRIES):
        try:
            response = chain.invoke({"context": context, "question": question})
            return response if isinstance(response, str) else response.content
        except Exception as e:  # noqa: BLE001 - retry any transient transport/model error
            last_err = e
            if attempt < _MAX_RETRIES - 1:
                time.sleep(_RETRY_BACKOFF * (attempt + 1))
    raise last_err  # type: ignore[misc]


_SYSTEM_PROMPT = """You are a precise research assistant. You answer questions about a set of documents, using the retrieved context as your source of truth.

Guidelines:
1. Base your answer on the provided context. You may synthesize and organize information across chunks.
2. If you are asked for a summary, overview, or "what is this about", give a clear structured summary of the documents' main points.
3. If the context does NOT contain enough information to answer, say: "I don't have enough information in the provided documents to answer that question."
4. Never invent facts or details not present in the context.
5. Cite supporting sources inline using [1], [2], etc. matching the source numbers below. Cite all sources that support a claim.
6. When a numbered list or structure improves the answer, use it.
7. Be concise and direct.

Context:
{context}"""


def _format_context(docs) -> tuple[str, list[dict]]:
    context_parts = []
    source_map = {}
    for i, doc in enumerate(docs):
        source = doc.metadata.get("source", "unknown")
        label = f"[{i + 1}]"
        if doc.metadata.get("type") == "image":
            page = doc.metadata.get("page", "?")
            caption = doc.metadata.get("caption", "")
            context_parts.append(
                f"{label} (Image — Source: {source}, Page: {page})\n"
                f"{doc.page_content}"
            )
        else:
            context_parts.append(f"{label} (Source: {source})\n{doc.page_content}")
        source_map[i + 1] = {
            "source": source,
            "chunk_index": doc.metadata.get("chunk_index"),
            "snippet": doc.page_content[:200],
            "type": doc.metadata.get("type", "text"),
            "page": doc.metadata.get("page"),
            "image_path": doc.metadata.get("image_path"),
        }
    return "\n\n".join(context_parts), list(source_map.values())


_SUMMARY_PATTERNS = r"(?i)\b(summar(?:ize|ise|y|ies)|overview|what.{0,30}about|main (?:points?|ideas?|topics?)|give me a (?:brief )?summary|tl;?dr|key (?:takeaways?|findings?|points?)|describe (?:the |this )?document|what (?:does|do) (?:this|the) (?:doc|document|paper|file)s?\b)"


def _is_summary_query(q: str) -> bool:
    return bool(re.search(_SUMMARY_PATTERNS, q))


def build_rag_answer(
    query: str,
    k: int = 5,
    collection_name: str = "documents",
    use_hybrid: bool = False,
    use_reranker: bool = False,
    use_cache: bool = True,
) -> dict:
    """Generate a RAG answer with optional hybrid retrieval, re-ranking, and caching."""
    start = time.time()

    # Boost context for summary / overview queries
    is_summary = _is_summary_query(query)
    effective_k = max(k, 12) if is_summary else k

    if use_cache:
        cached = query_cache.get(query, collection_name, k)
        if cached:
            latency = (time.time() - start) * 1000
            token_tracker.record(
                query=query, prompt_tokens=0, completion_tokens=0, cached=True, latency_ms=latency
            )
            return {
                "answer": cached.answer,
                "sources": cached.sources,
                "query": cached.query,
                "cached": True,
                "tokens": {"prompt": 0, "completion": 0, "total": 0, "cost_usd": 0.0},
                "latency_ms": round(latency, 1),
            }

    if use_hybrid:
        docs = hybrid_retrieve(query, k=effective_k * 2 if use_reranker else effective_k, collection_name=collection_name)
    else:
        docs = naive_retrieve(query, k=effective_k * 2 if use_reranker else effective_k, collection_name=collection_name)

    if use_reranker and len(docs) > effective_k:
        docs = rerank(query, docs, top_n=effective_k)

    docs = docs[:effective_k]

    context, sources = _format_context(docs)

    llm_model = os.getenv("LLM_MODEL", "llama3.2")
    # Cap generation length so a vagrant model can't spin for minutes; a local
    # 3B model is slow, and bounding num_predict keeps every phrasing responsive.
    llm = Ollama(model=llm_model, temperature=0, num_predict=512)

    prompt = ChatPromptTemplate.from_messages([
        ("system", _SYSTEM_PROMPT),
        ("human", "{question}"),
    ])

    chain = prompt | llm
    answer_text = _generate_with_retry(chain, context, query)

    prompt_tokens = token_tracker.count_tokens(_SYSTEM_PROMPT + context + query)
    completion_tokens = token_tracker.count_tokens(answer_text)

    usage = token_tracker.record(
        query=query,
        prompt_tokens=prompt_tokens,
        completion_tokens=completion_tokens,
        model=llm_model,
    )

    if use_cache:
        query_cache.set(
            query=query,
            answer=answer_text,
            sources=sources,
            collection=collection_name,
            k=k,
            tokens_used=usage.total_tokens,
        )

    latency = (time.time() - start) * 1000

    return {
        "answer": answer_text,
        "sources": sources,
        "query": query,
        "cached": False,
        "tokens": {
            "prompt": usage.prompt_tokens,
            "completion": usage.completion_tokens,
            "total": usage.total_tokens,
            "cost_usd": round(usage.estimated_cost_usd, 6),
        },
        "latency_ms": round(latency, 1),
    }
