from __future__ import annotations

import os
import re
import time
from typing import Any

from dotenv import load_dotenv
load_dotenv(override=True)

from langchain_core.prompts import ChatPromptTemplate
from langchain_groq import ChatGroq

from app.retriever import naive_retrieve
from app.hybrid_retriever import hybrid_retrieve, rerank
from app.cache import query_cache
from app.token_tracker import token_tracker


_MAX_RETRIES = 3
_RETRY_BACKOFF = 1.5  # seconds, grows per attempt


def _get_llm() -> ChatGroq:
    """Return a ChatGroq LLM instance using env config."""
    model_name = os.getenv("LLM_MODEL", "qwen/qwen3.8-27b")
    return ChatGroq(
        model=model_name,
        temperature=0,
        max_tokens=1024,
        api_key=os.getenv("GROQ_API_KEY"),
    )


def _generate_with_retry(chain, inputs: dict[str, Any]):
    """Invoke the LLM chain, retrying transient failures with backoff."""
    last_err: Exception | None = None
    for attempt in range(_MAX_RETRIES):
        try:
            response = chain.invoke(inputs)
            return response if isinstance(response, str) else response.content
        except Exception as e:  # noqa: BLE001
            last_err = e
            if attempt < _MAX_RETRIES - 1:
                time.sleep(_RETRY_BACKOFF * (attempt + 1))
    raise last_err  # type: ignore[misc]


def _rewrite_query(query: str) -> list[str]:
    """Use the LLM to generate alternative phrasings of the query.

    This fixes the keyword-mismatch problem: BM25 only finds exact words,
    so if a user asks 'budget' and the doc says 'expenditure', nothing is found.
    By generating 3 variations we cast a wider semantic net before retrieval.
    """
    llm = _get_llm()
    prompt = (
        "You are a search query assistant. Given the user's question, generate "
        "3 alternative phrasings that mean the same thing but use different words. "
        "These will be used to search a document database. "
        "Output ONLY the 3 alternatives, one per line, no numbering, no explanation.\n\n"
        f"Original question: {query}"
    )
    try:
        response = llm.invoke(prompt)
        text = response.content if hasattr(response, "content") else str(response)
        alternatives = [line.strip() for line in text.strip().splitlines() if line.strip()]
        # Return original + up to 3 alternatives
        return [query] + alternatives[:3]
    except Exception:  # noqa: BLE001
        # If rewriting fails, fall back to original query only
        return [query]


_SYSTEM_PROMPT = """You are a precise research assistant. You answer questions about a set of documents, using the retrieved context as your source of truth.

Guidelines:
1. Base your answer on the provided context and prior conversation history. You may synthesize and organize information across chunks.
2. If you are asked for a summary, overview, or "what is this about", give a clear structured summary of the documents' main points.
3. If the context and conversation history do NOT contain enough information to answer, say: "I don't have enough information in the provided documents to answer that question."
4. Never invent facts or details not present in the context.
5. Cite supporting sources inline using [1], [2], etc. matching the source numbers below. Cite all sources that support a claim.
6. When a numbered list or structure improves the answer, use it.
7. Be concise and direct.

Context:
{context}"""

_FOLLOWUP_PATTERNS = r"(?i)\b(it|its|they|them|their|these|those|this|that|he|she|him|her|the above|previous|and\?|what about|how about|more details|explain further)\b"


def _format_context(docs) -> tuple[str, list[dict]]:
    context_parts = []
    source_map = {}
    for i, doc in enumerate(docs):
        source = doc.metadata.get("source", "unknown")
        label = f"[{i + 1}]"
        if doc.metadata.get("type") == "image":
            page = doc.metadata.get("page", "?")
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


def _resolve_retrieval_query(query: str, chat_history: list[dict[str, Any]] | None) -> str:
    """Enhance query retrieval if the query is an ambiguous follow-up turn."""
    if not chat_history:
        return query

    # Find the last user question in history
    last_user_query = None
    for msg in reversed(chat_history):
        if msg.get("role") == "user":
            last_user_query = msg.get("content")
            break

    if last_user_query and (len(query.split()) <= 4 or re.search(_FOLLOWUP_PATTERNS, query)):
        return f"{last_user_query} {query}"

    return query


def build_rag_answer(
    query: str,
    k: int = 5,
    collection_name: str = "documents",
    use_hybrid: bool = False,
    use_reranker: bool = False,
    use_cache: bool = True,
    chat_history: list[dict[str, Any]] | None = None,
) -> dict:
    """Generate a RAG answer with optional hybrid retrieval, re-ranking, history awareness, and caching."""
    start = time.time()

    # Determine retrieval query with multi-turn context
    retrieval_query = _resolve_retrieval_query(query, chat_history)

    is_summary = _is_summary_query(query)
    effective_k = max(k, 12) if is_summary else k

    # Use cache only for first-turn standalone queries to avoid state collision
    if use_cache and not chat_history:
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

    # --- Query rewriting: generate alternative phrasings to fix keyword-mismatch ---
    query_variants = _rewrite_query(retrieval_query)

    # Retrieve docs for each query variant and merge, then deduplicate
    from app.retriever import dedupe_documents
    all_docs = []
    seen_ids: set[str] = set()
    for variant in query_variants:
        if use_hybrid:
            variant_docs = hybrid_retrieve(variant, k=effective_k * 2 if use_reranker else effective_k, collection_name=collection_name)
        else:
            variant_docs = naive_retrieve(variant, k=effective_k * 2 if use_reranker else effective_k, collection_name=collection_name)
        for doc in variant_docs:
            doc_id = f"{doc.metadata.get('source', '')}:{doc.page_content[:100]}"
            if doc_id not in seen_ids:
                seen_ids.add(doc_id)
                all_docs.append(doc)

    docs = dedupe_documents(all_docs)

    if use_reranker and len(docs) > effective_k:
        docs = rerank(retrieval_query, docs, top_n=effective_k)

    docs = docs[:effective_k]
    context, sources = _format_context(docs)

    llm_model = os.getenv("LLM_MODEL", "qwen/qwen3.8-27b")
    llm = _get_llm()

    messages = [("system", _SYSTEM_PROMPT)]

    # Add conversation history turns (up to last 6 turns)
    if chat_history:
        for msg in chat_history[-6:]:
            role = "human" if msg.get("role") == "user" else "ai"
            messages.append((role, msg.get("content", "")))

    messages.append(("human", "{question}"))

    prompt = ChatPromptTemplate.from_messages(messages)
    chain = prompt | llm

    answer_text = _generate_with_retry(chain, {"context": context, "question": query})

    history_text = " ".join([m.get("content", "") for m in (chat_history or [])[-6:]])
    prompt_tokens = token_tracker.count_tokens(_SYSTEM_PROMPT + context + history_text + query)
    completion_tokens = token_tracker.count_tokens(answer_text)

    usage = token_tracker.record(
        query=query,
        prompt_tokens=prompt_tokens,
        completion_tokens=completion_tokens,
        model=llm_model,
    )

    if use_cache and not chat_history:
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
