"use client";

import { SourceChunk } from "@/types";

interface CitationsProps {
  sources: SourceChunk[];
}

export default function Citations({ sources }: CitationsProps) {
  if (!sources.length) return null;

  return (
    <div className="mt-3 flex flex-wrap gap-2">
      {sources.map((src, i) => (
        <div
          key={i}
          className="group relative rounded-md border border-border bg-surface-2 px-2.5 py-1.5 text-xs font-mono text-muted transition-colors hover:border-accent hover:text-accent-light cursor-default"
        >
          <span className="font-semibold text-accent-light mr-1">[{i + 1}]</span>
          {src.source.split(/[/\\]/).pop()}
          <div className="pointer-events-none absolute bottom-full left-1/2 z-10 mb-2 -translate-x-1/2 whitespace-normal rounded-lg border border-border bg-surface-3 p-3 text-xs text-gray-300 opacity-0 shadow-xl transition-opacity group-hover:opacity-100 w-72">
            <div className="mb-1 font-semibold text-accent-light text-[10px] uppercase tracking-wider">
              Source Chunk
            </div>
            <div className="line-clamp-4 leading-relaxed">{src.snippet}</div>
          </div>
        </div>
      ))}
    </div>
  );
}
