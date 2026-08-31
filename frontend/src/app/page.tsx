"use client";

import { useEffect, useState } from "react";
import IngestPanel from "@/components/IngestPanel";
import Chat from "@/components/Chat";

function BrandMark() {
  return (
    <div className="flex h-9 w-9 items-center justify-center rounded-xl bg-brand shadow-glass-glow">
      <svg width="18" height="18" viewBox="0 0 18 18" fill="none" aria-hidden="true">
        <path
          d="M9 1.5c1.6 1.6 4.6 3 4.6 6 0 2.9-2 5-4.6 5.8-2.6-.8-4.6-2.9-4.6-5.8 0-3 3-4.4 4.6-6Z"
          fill="#fff"
          fillOpacity="0.95"
        />
        <circle cx="9" cy="8" r="1.4" fill="#8b7cf6" />
      </svg>
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

  return (
    <div className="depth-canvas relative flex h-screen flex-col">
      {/* Header — the surface line */}
      <header className="relative z-10 px-4 pt-4 sm:px-6">
        <div className="glass mx-auto flex max-w-6xl items-center justify-between rounded-2xl px-4 py-2.5">
          <div className="flex items-center gap-3">
            <BrandMark />
            <div>
              <h1 className="text-[14px] font-semibold tracking-tight text-ink">
                Lumen
              </h1>
              <p className="text-[11px] text-ink-dim">
                Ask your documents · cited answers
              </p>
            </div>
          </div>
          <ThemeToggle />
        </div>
      </header>

      {/* Body */}
      <main className="relative z-10 flex min-h-0 flex-1 flex-col overflow-hidden px-4 pb-4 sm:px-6">
        <IngestPanel onIngested={setStatus} />
        {status && (
          <div className="glass mt-3 flex flex-none items-center gap-2 rounded-lg px-4 py-2 text-xs text-ink">
            <span className="h-1.5 w-1.5 rounded-full bg-verified" />
            {status}
          </div>
        )}
        <Chat />
      </main>
    </div>
  );
}
