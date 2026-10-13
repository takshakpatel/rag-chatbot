export interface SourceChunk {
  source: string;
  chunk_index: number | null;
  snippet: string;
  type?: string;
  page?: number | null;
  image_path?: string | null;
}

export interface QueryResponse {
  answer: string;
  sources: SourceChunk[];
  query: string;
  session_id?: string | null;
  cached?: boolean;
  tokens?: {
    prompt: number;
    completion: number;
    total: number;
    cost_usd: number;
  } | null;
  latency_ms?: number | null;
}

export interface IngestResponse {
  documents_loaded: number;
  chunks_created: number;
  collection_name: string;
  images_extracted?: number;
}

export interface Message {
  id?: string;
  session_id?: string;
  role: "user" | "assistant";
  content: string;
  sources?: SourceChunk[];
  tokens?: {
    prompt: number;
    completion: number;
    total: number;
    cost_usd: number;
  } | null;
  latency_ms?: number | null;
  timestamp?: number;
  created_at?: number;
}

export interface ChatSession {
  id: string;
  title: string;
  created_at: number;
  updated_at: number;
  message_count: number;
  preview?: string | null;
}
