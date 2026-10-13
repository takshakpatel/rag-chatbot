import { QueryResponse, IngestResponse, ChatSession, Message } from "@/types";

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
  sessionId?: string | null,
  timeoutMs = 120000
): Promise<QueryResponse> {
  const controller = new AbortController();
  const timer = setTimeout(() => controller.abort(), timeoutMs);
  try {
    const res = await fetch(`${API_BASE}/query`, {
      method: "POST",
      headers: { "Content-Type": "application/json" },
      body: JSON.stringify({
        query,
        k,
        session_id: sessionId || null,
      }),
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

export async function fetchSessions(): Promise<ChatSession[]> {
  const res = await fetch(`${API_BASE}/sessions`);
  if (!res.ok) {
    throw new Error("Failed to fetch sessions");
  }
  return res.json();
}

export async function createSession(title = "New Chat"): Promise<ChatSession> {
  const res = await fetch(`${API_BASE}/sessions`, {
    method: "POST",
    headers: { "Content-Type": "application/json" },
    body: JSON.stringify({ title }),
  });
  if (!res.ok) {
    throw new Error("Failed to create session");
  }
  return res.json();
}

export async function fetchSessionDetail(
  sessionId: string
): Promise<{ session: ChatSession; messages: Message[] }> {
  const res = await fetch(`${API_BASE}/sessions/${sessionId}`);
  if (!res.ok) {
    throw new Error("Failed to load conversation history");
  }
  return res.json();
}

export async function renameSession(
  sessionId: string,
  title: string
): Promise<ChatSession> {
  const res = await fetch(`${API_BASE}/sessions/${sessionId}`, {
    method: "PATCH",
    headers: { "Content-Type": "application/json" },
    body: JSON.stringify({ title }),
  });
  if (!res.ok) {
    throw new Error("Failed to rename session");
  }
  return res.json();
}

export async function deleteSession(sessionId: string): Promise<void> {
  const res = await fetch(`${API_BASE}/sessions/${sessionId}`, {
    method: "DELETE",
  });
  if (!res.ok) {
    throw new Error("Failed to delete session");
  }
}
