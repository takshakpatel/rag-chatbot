"use client";

import { useEffect, useState } from "react";
import IngestPanel from "@/components/IngestPanel";
import Chat from "@/components/Chat";

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
