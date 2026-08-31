import { QueryResponse, IngestResponse } from "@/types";

const API_BASE = "/api";

export async function ingestDocuments(
  path: string,
  chunkSize = 1000,
  chunkOverlap = 200
): Promise<IngestResponse> {
  const res = await fetch(`${API_BASE}/ingest`, {
    method: "POST",
    headers: { "Content-Type": "application/json" },
    body: JSON.stringify({
      path,
      chunk_size: chunkSize,
      chunk_overlap: chunkOverlap,
    }),
  });
  if (!res.ok) {
    const err = await res.json().catch(() => ({ detail: res.statusText }));
    throw new Error(err.detail || "Ingestion failed");
  }
  return res.json();
}

export async function uploadDocuments(
  files: File[],
  chunkSize = 1000,
  chunkOverlap = 200
): Promise<IngestResponse> {
  const formData = new FormData();
  files.forEach((f) => formData.append("files", f));
  formData.append("collection_name", "documents");
  formData.append("chunk_size", String(chunkSize));
  formData.append("chunk_overlap", String(chunkOverlap));

  const res = await fetch(`${API_BASE}/ingest/upload`, {
    method: "POST",
    body: formData,
  });
  if (!res.ok) {
    const err = await res.json().catch(() => ({ detail: res.statusText }));
    throw new Error(err.detail || "Upload ingestion failed");
  }
  return res.json();
}

export async function queryDocuments(
  query: string,
  k = 5,
  timeoutMs = 120000
): Promise<QueryResponse> {
  const controller = new AbortController();
  const timer = setTimeout(() => controller.abort(), timeoutMs);
  try {
    const res = await fetch(`${API_BASE}/query`, {
      method: "POST",
      headers: { "Content-Type": "application/json" },
      body: JSON.stringify({ query, k }),
      signal: controller.signal,
    });
    if (!res.ok) {
      const err = await res.json().catch(() => ({ detail: res.statusText }));
      throw new Error(err.detail || "Query failed");
    }
    return res.json();
  } finally {
    clearTimeout(timer);
  }
}
