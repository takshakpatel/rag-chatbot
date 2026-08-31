from __future__ import annotations

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


class QueryRequest(BaseModel):
    query: str = Field(..., min_length=1, max_length=5000)
    k: int = Field(default=5, ge=1, le=20)
    collection_name: str = Field(default="documents")


class SourceChunk(BaseModel):
    source: str
    chunk_index: int | None = None
    snippet: str
    type: str = "text"
    page: int | None = None
    image_path: str | None = None


class QueryResponse(BaseModel):
    answer: str
    sources: list[SourceChunk]
    query: str
