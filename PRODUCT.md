# Product

<!-- impeccable:product-schema 1 -->

## Platform

web

## Stack

Python, FastAPI, LangChain, Groq API (ChatGroq), local sentence-transformers (all-MiniLM-L6-v2 embeddings + ms-marco cross-encoder re-ranker), ChromaDB, BM25, SQLite, Next.js 14 (React 18, TypeScript, Tailwind CSS), Docker

## Users

Developers and builders who want to chat with their own documents — PDFs, DOCX, HTML, Markdown — and get cited, faithful answers rather than hallucinated ones. `[inferred from brief]`

## Product Purpose

A retrieval-augmented generation chatbot that answers questions strictly from a supplied document collection, with inline citations, a refusal mechanism when context is insufficient, and a built-in evaluation harness to measure answer quality.

## Positioning

Unlike a generic LLM chatbot, this system ties every answer to a specific source chunk, refuses to guess when context is absent, and provides measurable retrieval and faithfulness metrics — making it a tool you can trust with real document sets. `[inferred from brief]`

## Operating Context

- Users upload or supply a document collection (PDF, DOCX, HTML, Markdown)
- Documents are ingested, chunked, embedded, and indexed in a vector store
- Users ask questions via a chat UI
- The system retrieves relevant chunks, re-ranks them, generates an answer with inline citations
- Token and cost tracking is visible per query

## Capabilities and Constraints

- Ingestion pipeline supporting PDF, DOCX, HTML, and Markdown
- Chunking with overlap; comparison of at least two chunking strategies
- Vector store with metadata filtering (source, date, section)
- Hybrid retrieval: keyword (BM25) + vector search
- Cross-encoder re-ranking of retrieved candidates
- Answers with inline citations pointing to exact source chunks
- Refusal behaviour when context does not contain the answer
- Evaluation harness: retrieval hit rate + answer faithfulness on a labelled question set (30 questions minimum)
- Token and cost tracking per query
- Caching for repeated queries
- Containerised deployment
- UI: Next.js
- Embedding model: `sentence-transformers/all-MiniLM-L6-v2` (local)
- LLM provider: Groq API via `ChatGroq` (configurable, default `llama-3.3-70b-versatile`)
- Re-ranker: `cross-encoder/ms-marco-MiniLM-L-6-v2` (local)
- Persistent multi-turn chat sessions stored in SQLite

## Brand Commitments

None established. `[inferred]`

## Evidence on Hand

None. All content will come from user-supplied document collections.

## Product Principles

1. **Measure, then improve.** Every change to chunking, retrieval, or ranking is validated against a fixed evaluation set with recorded metrics.
2. **Never hallucinate.** The system refuses to answer when context is insufficient, rather than generating plausible-sounding fabrication.
3. **Every answer is grounded.** Inline citations tie every claim to a specific source chunk.
4. **Start naive, ship real.** Build the simplest working version first, then iterate with measured steps.
5. **Show the cost.** Token usage and cost are tracked per query, not hidden.

## Accessibility & Inclusion

No specific requirements established. `[inferred]`
