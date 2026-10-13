<div align="center">

#  Lumen

**A retrieval-augmented chatbot that answers strictly from your own documents — with hybrid retrieval, cross-encoder re-ranking, inline citations, persistent multi-turn chat, and a frosted-glass UI.**

Local **embeddings + cross-encoder re-ranking** on your machine, generation via the **Groq API** (free tier) — no heavyweight local LLM required.

</div>

---

## Highlights

- **Grounded, cited answers** — every answer references the exact source chunks it was built from, with inline `[1]`, `[2]` citations.
- **Refusal guardrails** — the model is instructed to refuse when the sources genuinely don't contain the answer, instead of hallucinating.
- **Hybrid retrieval** — BM25 keyword search + dense vector search fused with **Reciprocal Rank Fusion**, then re-ranked by a local cross-encoder for precision.
- **Query rewriting** — the LLM generates alternative phrasings of each question to fix the keyword-mismatch problem before retrieval.
- **Multi-turn chat with memory** — conversations are persisted to SQLite; follow-up questions are resolved against the previous turn automatically.
- **Multi-format ingestion** — PDF, DOCX, PPTX, HTML, Markdown, TXT, and images (OCR-friendly parsing via PyMuPDF/Pillow).
- **Reliability hardening** — automatic **retry-with-backoff** for the LLM, and **duplicate-chunk dedup** so re-uploading a file never floods the context with repeat snippets.
- **Observability** — a TTL query cache plus cumulative **token / cost tracking** exposed via `/stats`.
- **Glassmorphism UI** — a responsive "Glass Studio" interface with **light/dark themes**, branded **Lumen**, a **session sidebar** (new / rename / delete), and a **Clear chat** action.
- **Containerised** — one-command startup with Docker Compose.

---

## Tech Stack

| Layer | Technology |
|-------|------------|
| **Backend** | Python 3.11, FastAPI, Uvicorn |
| **Orchestration** | LangChain (`langchain`, `langchain-groq`, `langchain-chroma`, `langchain-text-splitters`) |
| **LLM** | Groq API via `ChatGroq` (default `llama-3.3-70b-versatile`, fully configurable) |
| **Embeddings** | `sentence-transformers/all-MiniLM-L6-v2` (local) |
| **Re-ranker** | `cross-encoder/ms-marco-MiniLM-L-6-v2` (local) |
| **Vector store** | ChromaDB (persistent, `langchain-chroma`) |
| **Keyword search** | BM25 (`rank-bm25` via `BM25Retriever`) |
| **History store** | SQLite (`lumen_history.db`) |
| **Tokenisation** | `tiktoken` |
| **Document parsing** | PyMuPDF, pypdf, python-docx, python-pptx, BeautifulSoup4, Pillow |
| **Frontend** | Next.js 14 (App Router), React 18, TypeScript, Tailwind CSS |
| **Deployment** | Docker / Docker Compose |

---

## Architecture

```
┌─────────────────┐        ┌────────────────────────────────────────────────┐
│  Next.js UI      │        │                  FastAPI Backend                │
│  localhost:3000  │        │                  localhost:8000                 │
│                  │  /api  │                                                │
│  Glass UI        │ ─────▶ │  ┌────────┐  ┌─────────┐  ┌──────────────┐     │
│  light/dark      │ ◀───── │  │Loader  │→ │Chunker  │→ │  Embedder     │     │
│  session sidebar │  JSON   │  │PDF/DOCX│  │Recursive│  │ all-MiniLM    │     │
└─────────────────┘        │  │PPTX/...│  │Semantic │  │ L6 v2 (local) │     │
                            │  └────────┘  └─────────┘  └──────┬────────┘     │
                            │                                   │             │
                            │                     ┌─────────────▼──────┐     │
                            │                     │  ChromaDB           │     │
                            │                     │  Vector store       │     │
                            │                     └─────────────┬──────┘     │
                            │                                   │             │
                            │  ┌────────────────────────────────▼─────────┐  │
                            │  │  Hybrid Retrieval                         │  │
                            │  │  BM25 + Vector → RRF → Cross-Encoder      │  │
                            │  └────────────────────────────────┬─────────┘  │
                            │                                   │             │
                            │  ┌────────────────────────────────▼─────────┐  │
                            │  │  LLM  (Groq API via ChatGroq)             │  │
                            │  │  answer + citations + refusal             │  │
                            │  │  retry-with-backoff                       │  │
                            │  └──────────────────────────────────────────┘  │
                            │                                                │
                            │  ┌──────────┐ ┌───────────────┐ ┌────────────┐ │
                            │  │  Cache    │ │ Token/Cost    │ │ SQLite     │ │
                            │  │  (TTL)    │ │ tracking      │ │ sessions   │ │
                            │  └──────────┘ └───────────────┘ └────────────┘ │
                            └────────────────────────────────────────────────┘
```

**Pipeline:** load → chunk → embed → store → hybrid retrieve (BM25 + vector + RRF) → cross-encoder re-rank → prompt with context + history → Groq LLM → answer with inline citations (or a refusal).

---

##  Quick Start

### Prerequisites

- **Python 3.11+**
- **Node.js 18+**
- A **Groq API key** (free) — create one at [console.groq.com](https://console.groq.com/keys)

### 1. Backend

```bash
cd backend
python -m venv .venv
# Windows:
.venv\Scripts\activate
# macOS/Linux:
source .venv/bin/activate

pip install -r requirements.txt
cp .env.example .env
# then open .env and set GROQ_API_KEY to your key

uvicorn app.main:app --reload
```

The API is live at `http://localhost:8000`. Verify: `curl http://localhost:8000/health`.

> The first request downloads the local embedding and cross-encoder models, so it may take a little longer.

### 2. Ingest your documents

Drop files into `backend/documents/`, then either:

- **Run the UI** (step 3) and use the **Upload** panel, or
- **Via the API**:

```bash
curl -X POST http://localhost:8000/ingest/upload \
  -F "files=@backend/documents/my-file.pdf"
```

### 3. Frontend

Run these two commands (from the `frontend` directory):

```bash
cd frontend
npm install
npm run dev
```

- **`npm install`** — installs the frontend's dependencies (run once).
- **`npm run dev`** — starts the Next.js dev server.

> Use `npm.cmd` instead of `npm` if you're on Windows and `npm` isn't resolving. Don't run a production build (`npm run build`) while the dev server is running — they share the `.next` cache and can corrupt it.

Open **http://localhost:3000** — the UI proxy forwards `/api` → `localhost:8000` automatically (`next.config.js`).

### 4. Docker (alternative)

```bash
docker compose up --build
```

`docker-compose.yml` builds both services, waits for the backend health check, and mounts `backend/documents` plus a named `chroma_data` volume.

---

##  Configuration (`backend/.env`)

| Variable | Default | Description |
|----------|---------|-------------|
| `GROQ_API_KEY` | — | **Required.** Your Groq API key |
| `LLM_MODEL` | `llama-3.3-70b-versatile` | Chat model served by the Groq API |
| `EMBEDDING_MODEL` | `all-MiniLM-L6-v2` | Local embedding model |
| `RERANKER_MODEL` | `cross-encoder/ms-marco-MiniLM-L-6-v2` | Local re-ranking cross-encoder |
| `CHROMA_PERSIST_DIR` | `./chroma_db` | Chroma persistence directory |
| `CHUNK_SIZE` | `1000` | Default chunk size |
| `CHUNK_OVERLAP` | `200` | Default chunk overlap |

---

##  API Endpoints

| Method | Path | Description |
|--------|------|-------------|
| `GET` | `/health` | Health check |
| `POST` | `/ingest` | Ingest all documents from a server-side path |
| `POST` | `/ingest/upload` | Upload and ingest one or more files |
| `POST` | `/query` | RAG query (hybrid retrieval + re-rank + citations) |
| `POST` | `/query/hybrid` | Explicit hybrid query |
| `GET` | `/stats` | Cache stats and cumulative token usage |
| `GET` | `/sessions` | List chat sessions |
| `POST` | `/sessions` | Create a chat session |
| `GET` | `/sessions/{id}` | Fetch a session and its messages |
| `PATCH` | `/sessions/{id}` | Rename a session |
| `DELETE` | `/sessions/{id}` | Delete a session |
| `DELETE` | `/collection/{name}` | Delete a collection |

---

## Project Structure

```
.
├── backend/
│   ├── app/
│   │   ├── main.py              # FastAPI application (routes)
│   │   ├── loader.py            # Document loaders (PDF, DOCX, PPTX, HTML, MD, images)
│   │   ├── chunker.py           # Recursive character splitting
│   │   ├── semantic_chunker.py  # Sentence-aware semantic chunking (experimental)
│   │   ├── vectorstore.py       # Chroma vector store
│   │   ├── retriever.py         # Vector retrieval + duplicate-chunk dedup
│   │   ├── hybrid_retriever.py  # BM25 + Vector + RRF + cross-encoder re-rank
│   │   ├── rag.py               # RAG chain: query rewrite, citations, refusal, retry
│   │   ├── cache.py             # Query cache with TTL
│   │   ├── token_tracker.py     # Token usage / cost tracking
│   │   ├── database.py          # SQLite chat sessions & messages
│   │   ├── image_extractor.py   # PDF image extraction
│   │   └── schemas.py           # Pydantic models
│   ├── evaluation/              # Retrieval + faithfulness evaluation harness
│   ├── documents/               # Your document collection (gitignored)
│   ├── requirements.txt
│   └── .env.example
├── frontend/
│   ├── src/
│   │   ├── app/                 # page.tsx, layout.tsx, globals.css
│   │   ├── components/          # Chat, MessageBubble, SourcePins, IngestPanel, Sidebar
│   │   └── lib/api.ts           # API client (with request timeout)
│   ├── package.json
│   └── next.config.js           # /api → localhost:8000 proxy
├── docker-compose.yml
├── DESIGN.md                    # UI design system ("Glass Studio")
├── PRODUCT.md
└── README.md
```

---

##  Reliability & Privacy

- Retrieval **dedupes duplicate chunks** and the LLM call uses **retry-with-backoff** for stability.
- The browser request has a **timeout + friendly retry** message, so transient slowness never hangs the UI.
- **Embeddings and re-ranking run locally.** Retrieved context (not your whole corpus) is sent to the Groq API to generate the answer — so treat the hosted LLM as an external processor when your documents are sensitive.

---

##  Evaluation

`backend/evaluation/` contains a small harness (`run_eval.py`, `harness.py`, `chunk_experiment.py`, `questions_template.json`) for measuring **retrieval hit rate** and **answer faithfulness** against a labelled question set.

---

##  License

MIT
