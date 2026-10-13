from __future__ import annotations

from typing import Any
from pydantic import BaseModel, Field


class IngestRequest(BaseModel):
    path: str = Field(..., description="File or directory path to ingest")
    collection_name: str = Field(default="documents", description="Vector store collection name")
    chunk_size: int = Field(default=1000, ge=100, le=10000)
    chunk_overlap: int = Field(default=200, ge=0, le=5000)


class IngestResponse(BaseModel):
    documents_loaded: int
    chunks_created: int
    collection_name: str
    images_extracted: int = 0


class SourceChunk(BaseModel):
    source: str
    chunk_index: int | None = None
    snippet: str
    type: str = "text"
    page: int | None = None
    image_path: str | None = None


class QueryRequest(BaseModel):
    query: str = Field(..., min_length=1, max_length=5000)
    k: int = Field(default=5, ge=1, le=20)
    collection_name: str = Field(default="documents")
    session_id: str | None = Field(default=None, description="Chat session ID for multi-turn history")


class QueryResponse(BaseModel):
    answer: str
    sources: list[SourceChunk]
    query: str
    session_id: str | None = None
    cached: bool = False
    tokens: dict[str, Any] | None = None
    latency_ms: float | None = None


class CreateSessionRequest(BaseModel):
    title: str = Field(default="New Chat", max_length=100)


class UpdateSessionRequest(BaseModel):
    title: str = Field(..., min_length=1, max_length=100)


class ChatMessage(BaseModel):
    id: str
    session_id: str
    role: str
    content: str
    sources: list[SourceChunk] = []
    tokens: dict[str, Any] | None = None
    latency_ms: float | None = None
    created_at: float


class ChatSession(BaseModel):
    id: str
    title: str
    created_at: float
    updated_at: float
    message_count: int = 0
    preview: str | None = None
