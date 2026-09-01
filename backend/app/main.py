from __future__ import annotations

import os
import shutil
import tempfile
from pathlib import Path

from dotenv import load_dotenv
load_dotenv()

from fastapi import FastAPI, File, HTTPException, UploadFile
from fastapi.middleware.cors import CORSMiddleware

from app.loader import load_documents, load_uploaded_files, SUPPORTED_EXTENSIONS
from app.chunker import chunk_documents
from app.semantic_chunker import chunk_documents_semantic
from app.vectorstore import add_documents_to_store, reset_store, get_vectorstore
from app.rag import build_rag_answer
from app.cache import query_cache
from app.token_tracker import token_tracker
from app.schemas import (
    IngestRequest,
    IngestResponse,
    QueryRequest,
    QueryResponse,
    SourceChunk,
)

app = FastAPI(
    title="Lumen",
    description="Lumen — retrieval-augmented generation over your own documents.",
    version="0.1.0",
)

app.add_middleware(
    CORSMiddleware,
    allow_origins=["http://localhost:3000", "http://localhost:3001"],
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
    """Ingest documents uploaded directly from the browser.

    Accepts any number of files; only supported extensions (PDF, DOCX, HTML,
    MD, TXT) are processed. Files are written to a temp directory so the
    existing loaders handle them identically to local files.
    """
    if not files:
        raise HTTPException(status_code=400, detail="No files uploaded.")

    saved: list[Path] = []
    temp_dir = Path(tempfile.mkdtemp(prefix="rag_upload_"))
    try:
        for up in files:
            suffix = Path(up.filename or "").suffix.lower()
            if suffix not in SUPPORTED_EXTENSIONS:
                # Reject unsupported files early with a clear message.
                raise HTTPException(
                    status_code=415,
                    detail=f"Unsupported file type: {up.filename or 'unknown'}. Accepted: {', '.join(sorted(SUPPORTED_EXTENSIONS))}",
                )
            # Sanitize filename to avoid path traversal
            safe_name = Path(up.filename or "upload").name
            dest = temp_dir / safe_name
            with dest.open("wb") as f:
                shutil.copyfileobj(up.file, f)
            saved.append(dest)

        docs = load_uploaded_files(saved)
    finally:
        shutil.rmtree(temp_dir, ignore_errors=True)

    return _ingest_docs(docs, collection_name, chunk_size, chunk_overlap)


@app.post("/query", response_model=QueryResponse)
def query(req: QueryRequest):
    store = get_vectorstore(collection_name=req.collection_name)
    if store._collection.count() == 0:
        raise HTTPException(status_code=400, detail="No documents ingested yet. Call /ingest first.")

    result = build_rag_answer(
        query=req.query,
        k=req.k,
        collection_name=req.collection_name,
        use_hybrid=False,
        use_reranker=False,
    )

    return QueryResponse(
        answer=result["answer"],
        sources=[SourceChunk(**s) for s in result["sources"]],
        query=result["query"],
    )


@app.post("/query/hybrid")
def query_hybrid(req: QueryRequest):
    store = get_vectorstore(collection_name=req.collection_name)
    if store._collection.count() == 0:
        raise HTTPException(status_code=400, detail="No documents ingested yet. Call /ingest first.")

    result = build_rag_answer(
        query=req.query,
        k=req.k,
        collection_name=req.collection_name,
        use_hybrid=True,
        use_reranker=True,
        use_cache=True,
    )

    return {
        "answer": result["answer"],
        "sources": [SourceChunk(**s) for s in result["sources"]],
        "query": result["query"],
        "cached": result["cached"],
        "tokens": result["tokens"],
        "latency_ms": result["latency_ms"],
    }


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
