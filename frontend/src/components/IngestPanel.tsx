"use client";

import { useRef, useState } from "react";
import { uploadDocuments } from "@/lib/api";

const ACCEPTED = ".pdf,.docx,.html,.htm,.md,.txt,.pptx";
const ACCEPTED_LABEL = "PDF · DOCX · PPTX · HTML · MD · TXT";

interface IngestPanelProps {
  onIngested: (info: string) => void;
}

export default function IngestPanel({ onIngested }: IngestPanelProps) {
  const [files, setFiles] = useState<File[]>([]);
  const [dragging, setDragging] = useState(false);
  const [loading, setLoading] = useState(false);
  const [error, setError] = useState<string | null>(null);
  const inputRef = useRef<HTMLInputElement>(null);

  function addFiles(list: FileList | File[]) {
    setError(null);
    const next = Array.from(list);
    if (!next.length) return;
    setFiles((prev) => {
      const seen = new Set(prev.map((f) => f.name + f.size));
      const fresh = next.filter((f) => !seen.has(f.name + f.size));
      return [...prev, ...fresh];
    });
  }

  async function handleUpload() {
    if (!files.length || loading) return;
    setLoading(true);
    setError(null);
    try {
      const res = await uploadDocuments(files);
      const imgText = res.images_extracted ? ` · ${res.images_extracted} images extracted` : "";
      onIngested(
        `Uploaded ${res.documents_loaded} · carved ${res.chunks_created} chunks into ${res.collection_name}${imgText}`
      );
      setFiles([]);
      if (inputRef.current) inputRef.current.value = "";
    } catch (e: any) {
      setError(e.message || "Upload ingestion failed");
    } finally {
      setLoading(false);
    }
  }

  return (
    <div className="glass-tile mt-3 rounded-2xl px-4 py-3">
      <div className="flex flex-col gap-2.5">
        <div className="flex items-stretch gap-3">
          {/* Dropzone / picker */}
          <label
            onDragOver={(e) => {
              e.preventDefault();
              setDragging(true);
            }}
            onDragLeave={(e) => {
              e.preventDefault();
              setDragging(false);
            }}
            onDrop={(e) => {
              e.preventDefault();
              setDragging(false);
              if (e.dataTransfer.files?.length) addFiles(e.dataTransfer.files);
            }}
            className={`flex flex-1 cursor-pointer items-center gap-3 rounded-xl border border-dashed px-4 py-2.5 transition-colors ${
              dragging
                ? "border-thermo bg-thermo/10"
                : "border-ink-faint/40 hover:border-thermo/70"
            }`}
          >
            <svg width="20" height="20" viewBox="0 0 20 20" fill="none" aria-hidden="true" className="shrink-0 text-thermo">
              <path
                d="M10 13V3M6.5 6.5 10 3l3.5 3.5M3 12v3a2 2 0 0 0 2 2h10a2 2 0 0 0 2-2v-3"
                stroke="currentColor"
                strokeWidth="1.5"
                strokeLinecap="round"
                strokeLinejoin="round"
              />
            </svg>
            <span className="flex-1 text-sm text-ink-dim">
              <span className="font-medium text-ink">Choose files</span> or drop them here — from anywhere on your system
            </span>
            <input
              ref={inputRef}
              type="file"
              multiple
              accept={ACCEPTED}
              className="sr-only"
              onChange={(e) => e.target.files && addFiles(e.target.files)}
            />
            <span className="digits hidden shrink-0 text-[10px] uppercase tracking-[0.14em] text-ink-faint sm:block">
              {files.length} file{files.length === 1 ? "" : "s"} · {ACCEPTED_LABEL}
            </span>
          </label>

          {/* Upload action */}
          <button
            onClick={handleUpload}
            disabled={loading || !files.length}
            className="flex shrink-0 items-stretch rounded-xl bg-brand px-5 text-sm font-medium text-white transition-all hover:brightness-110 disabled:cursor-not-allowed disabled:opacity-40"
          >
            <span className="m-auto">{loading ? "Uploading…" : "Upload"}</span>
          </button>
        </div>

        {/* Selected files */}
        {files.length > 0 && (
          <div className="flex flex-wrap gap-1.5">
            {files.map((f, i) => (
              <span
                key={`${f.name}-${i}`}
                className="glass-tile flex items-center gap-1.5 rounded-full px-2.5 py-1 text-[11px] text-ink"
              >
                <span className="h-1.5 w-1.5 rounded-full bg-thermo/70" />
                <span className="max-w-[180px] truncate">{f.name}</span>
                <button
                  type="button"
                  aria-label={`Remove ${f.name}`}
                  onClick={() => setFiles((prev) => prev.filter((_, j) => j !== i))}
                  className="text-ink-faint transition-colors hover:text-refusal"
                >
                  ×
                </button>
              </span>
            ))}
          </div>
        )}

        {error && (
          <div className="rounded-lg border border-refusal/40 bg-refusal/10 px-3 py-2 text-xs text-refusal">
            {error}
          </div>
        )}
      </div>
    </div>
  );
}
