from __future__ import annotations

import os
import shutil
import tempfile
from pathlib import Path

from dotenv import load_dotenv
load_dotenv(override=True)

from fastapi import FastAPI, File, HTTPException, UploadFile
from fastapi.middleware.cors import CORSMiddleware

from app.loader import load_documents, load_uploaded_files, SUPPORTED_EXTENSIONS
from app.chunker import chunk_documents
from app.semantic_chunker import chunk_documents_semantic
from app.vectorstore import add_documents_to_store, reset_store, get_vectorstore
from app.rag import build_rag_answer
from app.cache import query_cache
from app.token_tracker import token_tracker
from app.database import (
    create_session,
    list_sessions,
    get_session,
    update_session_title,
    delete_session,
    add_message,
    get_session_messages,
)
from app.schemas import (
    IngestRequest,
    IngestResponse,
    QueryRequest,
    QueryResponse,
    SourceChunk,
    ChatSession,
    ChatMessage,
    CreateSessionRequest,
    UpdateSessionRequest,
)

app = FastAPI(
    title="Lumen",
    description="Lumen — retrieval-augmented generation over your own documents.",
    version="0.2.0",
)

app.add_middleware(
    CORSMiddleware,
    allow_origins=["http://localhost:3000", "http://localhost:3001", "http://127.0.0.1:3000", "*"],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)


@app.get("/health")
def health():
    return {"status": "ok"}


def _ingest_docs(docs, collection_name: str, chunk_size: int, chunk_overlap: int) -> IngestResponse:
    if not docs:
        raise HTTPException(status_code=400, detail="No supported documents found in the upload.")
    image_count = sum(1 for d in docs if d.metadata.get("type") == "image")
    chunks = chunk_documents(docs, chunk_size=chunk_size, chunk_overlap=chunk_overlap)
    added = add_documents_to_store(chunks, collection_name=collection_name)
    return IngestResponse(
        documents_loaded=len(docs),
        chunks_created=added,
        collection_name=collection_name,
        images_extracted=image_count,
    )


@app.post("/ingest", response_model=IngestResponse)
def ingest(req: IngestRequest):
    try:
        docs = load_documents(req.path)
    except FileNotFoundError as e:
        raise HTTPException(status_code=404, detail=str(e))

    if not docs:
        raise HTTPException(status_code=400, detail="No supported documents found at the given path.")

    return _ingest_docs(docs, req.collection_name, req.chunk_size, req.chunk_overlap)


@app.post("/ingest/upload", response_model=IngestResponse)
async def ingest_upload(
    files: list[UploadFile] = File(...),
    collection_name: str = "documents",
    chunk_size: int = 1000,
    chunk_overlap: int = 200,
):
    if not files:
        raise HTTPException(status_code=400, detail="No files uploaded.")

    saved: list[Path] = []
    temp_dir = Path(tempfile.mkdtemp(prefix="rag_upload_"))
    try:
        for up in files:
            suffix = Path(up.filename or "").suffix.lower()
            if suffix not in SUPPORTED_EXTENSIONS:
                raise HTTPException(
                    status_code=415,
                    detail=f"Unsupported file type: {up.filename or 'unknown'}. Accepted: {', '.join(sorted(SUPPORTED_EXTENSIONS))}",
                )
            safe_name = Path(up.filename or "upload").name
            dest = temp_dir / safe_name
            with dest.open("wb") as f:
                shutil.copyfileobj(up.file, f)
            saved.append(dest)

        docs = load_uploaded_files(saved)
        result = _ingest_docs(docs, collection_name, chunk_size, chunk_overlap)
    finally:
        shutil.rmtree(temp_dir, ignore_errors=True)

    return result


# --- Sessions & History Endpoints ---

@app.get("/sessions", response_model=list[ChatSession])
def get_sessions():
    return list_sessions()


@app.post("/sessions", response_model=ChatSession)
def create_new_session(req: CreateSessionRequest | None = None):
    title = req.title if req else "New Chat"
    return create_session(title=title)


@app.get("/sessions/{session_id}")
def get_session_detail(session_id: str):
    sess = get_session(session_id)
    if not sess:
        raise HTTPException(status_code=404, detail="Session not found")
    messages = get_session_messages(session_id)
    return {"session": sess, "messages": messages}


@app.patch("/sessions/{session_id}", response_model=ChatSession)
def rename_session(session_id: str, req: UpdateSessionRequest):
    updated = update_session_title(session_id, req.title)
    if not updated:
        raise HTTPException(status_code=404, detail="Session not found")
    return updated


@app.delete("/sessions/{session_id}")
def remove_session(session_id: str):
    deleted = delete_session(session_id)
    if not deleted:
        raise HTTPException(status_code=404, detail="Session not found")
    return {"status": "deleted", "session_id": session_id}


# --- Query Endpoints ---

@app.post("/query", response_model=QueryResponse)
def query(req: QueryRequest):
    store = get_vectorstore(collection_name=req.collection_name)
    if store._collection.count() == 0:
        raise HTTPException(status_code=400, detail="No documents ingested yet. Call /ingest first.")

    chat_history: list[dict] = []
    if req.session_id:
        chat_history = get_session_messages(req.session_id)
        # Record user question
        add_message(session_id=req.session_id, role="user", content=req.query)

    result = build_rag_answer(
        query=req.query,
        k=req.k,
        collection_name=req.collection_name,
        use_hybrid=True,
        use_reranker=True,
        use_cache=True,
        chat_history=chat_history,
    )

    if req.session_id:
        # Record assistant answer with citations and tokens
        add_message(
            session_id=req.session_id,
            role="assistant",
            content=result["answer"],
            sources=result["sources"],
            tokens=result["tokens"],
            latency_ms=result["latency_ms"],
        )

    return QueryResponse(
        answer=result["answer"],
        sources=[SourceChunk(**s) for s in result["sources"]],
        query=result["query"],
        session_id=req.session_id,
        cached=result.get("cached", False),
        tokens=result.get("tokens"),
        latency_ms=result.get("latency_ms"),
    )


@app.post("/query/hybrid", response_model=QueryResponse)
def query_hybrid(req: QueryRequest):
    return query(req)


@app.get("/stats")
def stats():
    return {
        "cache": query_cache.stats(),
        "tokens": token_tracker.cumulative_stats(),
    }


@app.delete("/collection/{name}")
def delete_collection(name: str):
    reset_store(collection_name=name)
    return {"status": "deleted", "collection": name}
