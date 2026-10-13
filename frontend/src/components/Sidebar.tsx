"use client";

import { useState } from "react";
import { ChatSession } from "@/types";

interface SidebarProps {
  sessions: ChatSession[];
  activeSessionId: string | null;
  onSelectSession: (id: string) => void;
  onNewChat: () => void;
  onRenameSession: (id: string, newTitle: string) => void;
  onDeleteSession: (id: string) => void;
  isOpen: boolean;
  onToggle: () => void;
}

export default function Sidebar({
  sessions,
  activeSessionId,
  onSelectSession,
  onNewChat,
  onRenameSession,
  onDeleteSession,
  isOpen,
  onToggle,
}: SidebarProps) {
  const [editingId, setEditingId] = useState<string | null>(null);
  const [editTitle, setEditTitle] = useState("");

  function startEditing(s: ChatSession, e: React.MouseEvent) {
    e.stopPropagation();
    setEditingId(s.id);
    setEditTitle(s.title);
  }

  function handleRename(id: string) {
    if (editTitle.trim()) {
      onRenameSession(id, editTitle.trim());
    }
    setEditingId(null);
  }

  function formatTime(timestamp: number) {
    const d = new Date(timestamp * 1000);
    const now = new Date();
    const isToday = d.toDateString() === now.toDateString();
    if (isToday) {
      return d.toLocaleTimeString([], { hour: "2-digit", minute: "2-digit" });
    }
    return d.toLocaleDateString([], { month: "short", day: "numeric" });
  }

  return (
    <>
      {/* Mobile backdrop */}
      {isOpen && (
        <div
          className="fixed inset-0 z-30 bg-black/40 backdrop-blur-xs md:hidden"
          onClick={onToggle}
        />
      )}

      {/* Sidebar container */}
      <aside
        className={`glass fixed md:relative z-40 flex h-full flex-col rounded-2xl transition-all duration-300 ease-in-out ${
          isOpen ? "w-64 sm:w-72" : "w-0 p-0 overflow-hidden border-none opacity-0 md:w-0"
        } ${isOpen ? "opacity-100" : ""}`}
      >
        {/* Top bar: New Chat + Close */}
        <div className="flex items-center justify-between border-b border-ink-faint/20 p-3">
          <button
            onClick={onNewChat}
            className="flex flex-1 items-center justify-center gap-2 rounded-xl bg-brand py-2 px-3 text-xs font-medium text-white transition-all hover:brightness-110 shadow-xs"
          >
            <svg width="14" height="14" viewBox="0 0 14 14" fill="none" aria-hidden="true">
              <path d="M7 2.5v9M2.5 7h9" stroke="currentColor" strokeWidth="1.5" strokeLinecap="round" />
            </svg>
            <span>New Chat</span>
          </button>
          <button
            onClick={onToggle}
            aria-label="Collapse sidebar"
            title="Collapse sidebar"
            className="ml-2 flex h-8 w-8 items-center justify-center rounded-lg text-ink-dim hover:bg-ink-faint/10 hover:text-ink transition-colors"
          >
            <svg width="15" height="15" viewBox="0 0 16 16" fill="none" aria-hidden="true">
              <path d="M11 3L5 8L11 13" stroke="currentColor" strokeWidth="1.5" strokeLinecap="round" strokeLinejoin="round" />
            </svg>
          </button>
        </div>

        {/* Sessions list */}
        <div className="flex-1 overflow-y-auto p-2 space-y-1">
          {sessions.length === 0 ? (
            <div className="p-4 text-center text-xs text-ink-dim">
              No conversations yet. Start asking questions to save chats.
            </div>
          ) : (
            sessions.map((s) => {
              const isActive = s.id === activeSessionId;
              const isEditing = editingId === s.id;

              return (
                <div
                  key={s.id}
                  onClick={() => onSelectSession(s.id)}
                  className={`group relative flex cursor-pointer items-center justify-between rounded-xl px-3 py-2 text-xs transition-all ${
                    isActive
                      ? "bg-brand/15 text-ink font-medium border border-brand/30 shadow-xs"
                      : "text-ink-dim hover:bg-ink-faint/10 hover:text-ink"
                  }`}
                >
                  <div className="flex min-w-0 flex-1 items-center gap-2">
                    <svg
                      width="14"
                      height="14"
                      viewBox="0 0 16 16"
                      fill="none"
                      aria-hidden="true"
                      className={`shrink-0 ${isActive ? "text-brand" : "text-ink-dim"}`}
                    >
                      <path
                        d="M2.5 4.5A1.5 1.5 0 0 1 4 3h8a1.5 1.5 0 0 1 1.5 1.5v6A1.5 1.5 0 0 1 12 12H5l-3 2.5V4.5Z"
                        stroke="currentColor"
                        strokeWidth="1.3"
                        strokeLinejoin="round"
                      />
                    </svg>

                    {isEditing ? (
                      <input
                        type="text"
                        value={editTitle}
                        autoFocus
                        onClick={(e) => e.stopPropagation()}
                        onChange={(e) => setEditTitle(e.target.value)}
                        onBlur={() => handleRename(s.id)}
                        onKeyDown={(e) => {
                          if (e.key === "Enter") handleRename(s.id);
                          if (e.key === "Escape") setEditingId(null);
                        }}
                        className="w-full rounded bg-black/20 px-1 py-0.5 text-xs text-ink focus:outline-none focus:ring-1 focus:ring-brand"
                      />
                    ) : (
                      <div className="min-w-0 flex-1">
                        <div className="truncate">{s.title}</div>
                        <div className="text-[10px] text-ink-dim/70">
                          {formatTime(s.updated_at)} · {s.message_count} msg{s.message_count === 1 ? "" : "s"}
                        </div>
                      </div>
                    )}
                  </div>

                  {/* Action buttons (Rename & Delete) on hover */}
                  {!isEditing && (
                    <div className="flex items-center gap-1 opacity-0 group-hover:opacity-100 transition-opacity ml-1">
                      <button
                        onClick={(e) => startEditing(s, e)}
                        title="Rename"
                        className="rounded p-1 text-ink-dim hover:text-ink hover:bg-ink-faint/20"
                      >
                        <svg width="12" height="12" viewBox="0 0 14 14" fill="none" aria-hidden="true">
                          <path
                            d="M9.5 2.5L11.5 4.5M2 12L2 9.5L9.5 2L12 4.5L4.5 12L2 12Z"
                            stroke="currentColor"
                            strokeWidth="1.2"
                            strokeLinecap="round"
                            strokeLinejoin="round"
                          />
                        </svg>
                      </button>
                      <button
                        onClick={(e) => {
                          e.stopPropagation();
                          if (confirm(`Delete "${s.title}"?`)) {
                            onDeleteSession(s.id);
                          }
                        }}
                        title="Delete chat"
                        className="rounded p-1 text-ink-dim hover:text-red-400 hover:bg-ink-faint/20"
                      >
                        <svg width="12" height="12" viewBox="0 0 14 14" fill="none" aria-hidden="true">
                          <path
                            d="M2 3.5h10M4.5 3.5V2.5a1 1 0 0 1 1-1h3a1 1 0 0 1 1 1v1M3 3.5l.8 8.5a1 1 0 0 0 1 .9h4.4a1 1 0 0 0 1-.9l.8-8.5"
                            stroke="currentColor"
                            strokeWidth="1.2"
                            strokeLinecap="round"
                          />
                        </svg>
                      </button>
                    </div>
                  )}
                </div>
              );
            })
          )}
        </div>
      </aside>
    </>
  );
}
