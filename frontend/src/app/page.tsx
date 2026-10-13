"use client";

import { useEffect, useState, useCallback } from "react";
import IngestPanel from "@/components/IngestPanel";
import Chat from "@/components/Chat";
import Sidebar from "@/components/Sidebar";
import { ChatSession } from "@/types";
import { fetchSessions, renameSession, deleteSession } from "@/lib/api";

function BrandMark() {
  return (
    <div className="group relative">
      <div className="brand-tile flex h-9 w-9 items-center justify-center rounded-xl bg-brand">
        <svg width="19" height="19" viewBox="0 0 24 24" fill="none" aria-hidden="true">
          {/* left page */}
          <path
            className="brand-page brand-page-left"
            d="M12 5.6 C9.1 4.2 5.9 4.9 4 7.4 L4 18 C6.6 16.4 9.3 15.9 12 17.4 Z"
            fill="#fff"
            fillOpacity="0.4"
          />
          {/* right page */}
          <path
            className="brand-page brand-page-right"
            d="M12 5.6 C14.9 4.2 18.1 4.9 20 7.4 L20 18 C17.4 16.4 14.7 15.9 12 17.4 Z"
            fill="#fff"
          />
          {/* spine crease */}
          <path
            className="brand-spine"
            d="M12 5.6 L12 17.4"
            stroke="#fff"
            strokeOpacity="0.75"
            strokeWidth="1.4"
            strokeLinecap="round"
          />
        </svg>
      </div>
    </div>
  );
}

function ThemeToggle() {
  const [theme, setTheme] = useState<"dark" | "light">("dark");

  useEffect(() => {
    const saved = (localStorage.getItem("rag-deepdive-theme") as "dark" | "light") || "dark";
    setTheme(saved);
    document.documentElement.classList.toggle("theme-light", saved === "light");
  }, []);

  const toggle = () => {
    const next = theme === "dark" ? "light" : "dark";
    setTheme(next);
    localStorage.setItem("rag-deepdive-theme", next);
    document.documentElement.classList.toggle("theme-light", next === "light");
  };

  return (
    <button
      onClick={toggle}
      aria-label={theme === "dark" ? "Switch to light mode" : "Switch to dark mode"}
      title={theme === "dark" ? "Switch to light" : "Switch to dark"}
      className="glass flex h-9 w-9 items-center justify-center rounded-lg text-ink-dim transition-colors hover:text-ink"
    >
      {theme === "dark" ? (
        <svg width="17" height="17" viewBox="0 0 17 17" fill="none" aria-hidden="true">
          <path
            d="M6.3 2.6a5.4 5.4 0 1 0 7.6 6.5A4.4 4.4 0 0 1 6.3 2.6Z"
            stroke="currentColor"
            strokeWidth="1.4"
            strokeLinejoin="round"
          />
        </svg>
      ) : (
        <svg width="17" height="17" viewBox="0 0 17 17" fill="none" aria-hidden="true">
          <circle cx="8.5" cy="8.5" r="3.4" stroke="currentColor" strokeWidth="1.4" />
          <path
            d="M8.5 1.8v1.8M8.5 13.4v1.8M1.8 8.5h1.8M13.4 8.5h1.8M3.6 3.6l1.3 1.3M12.1 12.1l1.3 1.3M13.4 3.6l-1.3 1.3M4.9 12.1l-1.3 1.3"
            stroke="currentColor"
            strokeWidth="1.4"
            strokeLinecap="round"
          />
        </svg>
      )}
    </button>
  );
}

export default function Home() {
  const [status, setStatus] = useState<string | null>(null);
  const [sessions, setSessions] = useState<ChatSession[]>([]);
  const [activeSessionId, setActiveSessionId] = useState<string | null>(null);
  const [isSidebarOpen, setIsSidebarOpen] = useState(true);

  const loadSessions = useCallback(async () => {
    try {
      const data = await fetchSessions();
      setSessions(data);
    } catch (e) {
      console.error("Failed to fetch chat sessions:", e);
    }
  }, []);

  useEffect(() => {
    loadSessions();
  }, [loadSessions]);

  const handleNewChat = () => {
    setActiveSessionId(null);
  };

  const handleSelectSession = (id: string) => {
    setActiveSessionId(id);
  };

  const handleRenameSession = async (id: string, newTitle: string) => {
    try {
      await renameSession(id, newTitle);
      loadSessions();
    } catch (e) {
      console.error("Failed to rename session:", e);
    }
  };

  const handleDeleteSession = async (id: string) => {
    try {
      await deleteSession(id);
      if (activeSessionId === id) {
        setActiveSessionId(null);
      }
      loadSessions();
    } catch (e) {
      console.error("Failed to delete session:", e);
    }
  };

  const handleSessionCreated = (id: string) => {
    setActiveSessionId(id);
    loadSessions();
  };

  return (
    <div className="depth-canvas relative flex h-screen flex-col">
      {/* Header */}
      <header className="relative z-10 px-4 pt-4 sm:px-6">
        <div className="glass mx-auto flex max-w-7xl items-center justify-between rounded-2xl px-4 py-2.5">
          <div className="flex items-center gap-3">
            <button
              onClick={() => setIsSidebarOpen((v) => !v)}
              aria-label="Toggle chat history"
              title="Toggle chat history"
              className="flex h-8 w-8 items-center justify-center rounded-lg text-ink-dim hover:bg-ink-faint/10 hover:text-ink transition-colors"
            >
              <svg width="17" height="17" viewBox="0 0 16 16" fill="none" aria-hidden="true">
                <path d="M2.5 4h11M2.5 8h11M2.5 12h11" stroke="currentColor" strokeWidth="1.4" strokeLinecap="round" />
              </svg>
            </button>
            <BrandMark />
            <div>
              <h1 className="text-[14px] font-semibold tracking-tight text-ink">
                Lumen
              </h1>
              <p className="text-[11px] text-ink-dim">
                Ask your documents · cited multi-turn answers
              </p>
            </div>
          </div>
          <ThemeToggle />
        </div>
      </header>

      {/* Main Workspace with Sidebar & Chat */}
      <main className="relative z-10 mx-auto flex w-full max-w-7xl min-h-0 flex-1 gap-3 overflow-hidden px-4 pb-4 pt-3 sm:px-6">
        <Sidebar
          sessions={sessions}
          activeSessionId={activeSessionId}
          onSelectSession={handleSelectSession}
          onNewChat={handleNewChat}
          onRenameSession={handleRenameSession}
          onDeleteSession={handleDeleteSession}
          isOpen={isSidebarOpen}
          onToggle={() => setIsSidebarOpen((v) => !v)}
        />

        <div className="flex min-w-0 flex-1 flex-col overflow-hidden">
          <IngestPanel onIngested={setStatus} />
          {status && (
            <div className="glass mt-3 flex flex-none items-center gap-2 rounded-lg px-4 py-2 text-xs text-ink">
              <span className="h-1.5 w-1.5 rounded-full bg-verified" />
              {status}
            </div>
          )}
          <Chat
            activeSessionId={activeSessionId}
            onSessionCreated={handleSessionCreated}
            onSessionUpdated={loadSessions}
            onToggleSidebar={() => setIsSidebarOpen((v) => !v)}
            isSidebarOpen={isSidebarOpen}
          />
        </div>
      </main>
    </div>
  );
}
