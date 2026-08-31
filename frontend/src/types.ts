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
}

export interface IngestResponse {
  documents_loaded: number;
  chunks_created: number;
  collection_name: string;
  images_extracted?: number;
}

export interface Message {
  role: "user" | "assistant";
  content: string;
  sources?: SourceChunk[];
  timestamp: number;
}
