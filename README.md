<div align="center">

# 🔦 Lumen

**A local-first RAG chatbot that answers strictly from your own documents — with hybrid retrieval, cross-encoder re-ranking, inline citations, and a frosted-glass UI.**

Fully free & private: embeddings, retrieval, re-ranking and generation all run **on your machine** with no cloud API keys.

</div>

---

## ✨ Highlights

- **100% local & private** — `all-MiniLM-L6-v2` embeddings, `llama3.2` LLM via [Ollama](https://ollama.com), and a local cross-encoder re-ranker. No API keys, no data leaves your machine.
- **Hybrid retrieval** — BM25 keyword search + dense vector search fused with **Reciprocal Rank Fusion**, then re-ranked by a cross-encoder for precision.
- **Inline citations** — every answer references the exact source chunks it was built from.
- **Refusal guardrails** — the model is instructed to refuse when the sources genuinely don't contain the answer, instead of hallucinating.
- **Reliability hardening** — automatic **retry-with-backoff** for the local LLM, and **duplicate-chunk dedup** so re-uploading a file never floods the context with repeat snippets.
- **Multi-format ingestion** — PDF, DOCX, HTML, Markdown, and images (with OCR-friendly parsing via PyMuPDF/Pillow).
- **Glassmorphism UI** — a responsive "Glass Studio" interface with **light/dark themes**, branded **Lumen**, plus a **Clear chat** action.

---

## 🧱 Architecture

```
┌─────────────────┐        ┌──────────────────────────────────────────────┐
│  Next.js UI      │        │                FastAPI Backend               │
│  localhost:3000  │        │                localhost:8000                │
│                  │  /api  │                                              │
│  Glass UI        │ ─────▶ │  ┌────────┐  ┌─────────┐  ┌──────────────┐  │
│  light/dark      │ ◀───── │  │Loader  │→ │Chunker  │→ │  Embedder     │  │
│  clear chat      │  JSON   │  │PDF/DOCX│  │Recursive│  │ all-MiniLM    │  │
└─────────────────┘        │  │HTML/MD  │  │Semantic │  │ L6 v2 (local) │  │
                           │  └────────┘  └─────────┘  └──────┬───────┘  │
                           │                                  │          │
                           │                    ┌─────────────▼──────┐   │
                           │                    │  ChromaDB           │   │
                           │                    │  Vector store       │   │
                           │                    └─────────────┬──────┘   │
                           │                                 │          │
                           │  ┌──────────────────────────────▼──────┐   │
                           │  │  Hybrid Retrieval                    │   │
                           │  │  BM25 + Vector → RRF → Cross-Encoder │   │
                           │  └──────────────────────────────┬──────┘   │
                           │                                 │          │
                           │  ┌──────────────────────────────▼──────┐   │
                           │  │  LLM  llama3.2 (local, via Ollama)   │   │
                           │  │  answer + citations + refusal        │   │
                           │  │  retry-with-backoff                  │   │
                           │  └─────────────────────────────────────┘   │
                           │                                             │
                           │  ┌──────────┐  ┌────────────────────────┐  │
                           │  │  Cache    │  │  Token/Cost tracking   │  │
                           │  └──────────┘  └────────────────────────┘  │
                           └─────────────────────────────────────────────┘
```

---

## 🚀 Quick Start

### Prerequisites

- **Python 3.11+**
- **Node.js 18+**
- **Ollama** ([download](https://ollama.com/download)) — with the model pulled:
  ```bash
  ollama pull llama3.2
  ```

### 1. Backend

```bash
cd backend
python -m venv .venv
# Windows:
.venv\Scripts\activate
# macOS/Linux:
source .venv/bin/activate

pip install -r requirements.txt
cp .env.example .env     # defaults already point at local models — no changes needed

uvicorn app.main:app --reload
```

The API is live at `http://localhost:8000`. Verify: `curl http://localhost:8000/health`.

### 2. Ingest your documents

Drop files into `backend/documents/`, then either:

- **Run the UI** (step 3) and use the **Upload** panel, or
- **Via the API**:

```bash
curl -X POST http://localhost:8000/ingest/upload \
  -F "file=@backend/documents/my-file.pdf"
```

### 3. Frontend

```bash
cd frontend
npm install
npm run dev
```

Open **http://localhost:3000** — the UI proxy forwards `/api` → `localhost:8000` automatically.

---

## ⚙️ Configuration (`backend/.env`)

| Variable | Default | Description |
|----------|---------|-------------|
| `LLM_MODEL` | `llama3.2` | Local LLM served by Ollama (`localhost:11434`) |
| `EMBEDDING_MODEL` | `all-MiniLM-L6-v2` | Local embedding model |
| `RERANKER_MODEL` | `cross-encoder/ms-marco-MiniLM-L-6-v2` | Local re-ranking model |
| `CHROMA_PERSIST_DIR` | `./chroma_db` | Chroma persistence directory |
| `CHUNK_SIZE` | `1000` | Default chunk size |
| `CHUNK_OVERLAP` | `200` | Default chunk overlap |
| `OPENAI_API_KEY` | — | *Optional* — only if you switch `LLM_MODEL`/`EMBEDDING_MODEL` to OpenAI-hosted models |

---

## 🔌 API Endpoints

| Method | Path | Description |
|--------|------|-------------|
| `GET` | `/health` | Health check |
| `POST` | `/ingest` | Ingest all documents from a server-side path |
| `POST` | `/ingest/upload` | Upload and ingest a single file |
| `POST` | `/query` | RAG query (hybrid retrieval + re-rank + citations) |
| `POST` | `/query/hybrid` | Explicit hybrid query |
| `GET` | `/stats` | Cache stats and cumulative token usage |
| `DELETE` | `/collection/{name}` | Delete a collection |

---

## 🗺️ Project Structure

```
.
├── backend/
│   ├── app/
│   │   ├── main.py              # FastAPI application (routes)
│   │   ├── loader.py            # Document loaders (PDF, DOCX, HTML, MD, images)
│   │   ├── chunker.py           # Recursive character splitting
│   │   ├── semantic_chunker.py  # Sentence-aware semantic chunking
│   │   ├── vectorstore.py       # Chroma vector store
│   │   ├── retriever.py         # Vector retrieval + duplicate-chunk dedup
│   │   ├── hybrid_retriever.py  # BM25 + Vector + RRF + cross-encoder re-rank
│   │   ├── rag.py               # RAG chain: citations, refusal, retry-with-backoff
│   │   ├── cache.py             # Query cache with TTL
│   │   ├── token_tracker.py     # Token usage / cost tracking
│   │   └── schemas.py           # Pydantic models
│   ├── documents/               # Your document collection
│   ├── requirements.txt
│   └── .env.example
├── frontend/
│   ├── src/
│   │   ├── app/                 # page.tsx, layout.tsx, globals.css
│   │   ├── components/          # Chat, MessageBubble, SourcePins, IngestPanel
│   │   └── lib/api.ts           # API client (with request timeout)
│   ├── package.json
│   └── next.config.js           # /api → localhost:8000 proxy
├── docker-compose.yml
├── DESIGN.md                    # UI design system ("Glass Studio")
├── PRODUCT.md
└── README.md
```

---

## 🔒 Privacy & Security

- Everything runs locally — nothing is sent to a cloud provider by default.
- Retrieval **dedupes duplicate chunks** and the LLM call uses **retry-with-backoff** for stability.
- The request from the browser has a **timeout + friendly retry** message, so transient local-model slowness never hangs the UI.

---

## 📄 License

MIT
