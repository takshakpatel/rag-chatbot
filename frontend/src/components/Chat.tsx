"use client";

import { useState, useRef, useEffect, useCallback } from "react";
import { Message } from "@/types";
import { queryDocuments, fetchSessionDetail, createSession } from "@/lib/api";
import MessageBubble from "./MessageBubble";

interface ChatProps {
  activeSessionId: string | null;
  onSessionCreated?: (sessionId: string) => void;
  onSessionUpdated?: () => void;
  onToggleSidebar?: () => void;
  isSidebarOpen?: boolean;
}

export default function Chat({
  activeSessionId,
  onSessionCreated,
  onSessionUpdated,
  onToggleSidebar,
  isSidebarOpen,
}: ChatProps) {
  const [messages, setMessages] = useState<Message[]>([]);
  const [input, setInput] = useState("");
  const [loading, setLoading] = useState(false);
  const [historyLoading, setHistoryLoading] = useState(false);
  const [sendPulse, setSendPulse] = useState(0);
  const scrollRef = useRef<HTMLDivElement>(null);

  const scrolling = useCallback(() => {
    scrollRef.current?.scrollTo({
      top: scrollRef.current.scrollHeight,
      behavior: "smooth",
    });
  }, []);

  // Load messages when activeSessionId changes
  useEffect(() => {
    if (!activeSessionId) {
      setMessages([]);
      return;
    }

    let isMounted = true;
    setHistoryLoading(true);

    fetchSessionDetail(activeSessionId)
      .then((data) => {
        if (isMounted) {
          setMessages(data.messages || []);
        }
      })
      .catch((err) => {
        console.error("Failed to load session history:", err);
      })
      .finally(() => {
        if (isMounted) setHistoryLoading(false);
      });

    return () => {
      isMounted = false;
    };
  }, [activeSessionId]);

  useEffect(() => {
    scrolling();
  }, [messages, loading, scrolling]);

  async function handleSend() {
    const text = input.trim();
    if (!text || loading) return;

    let currentSessionId = activeSessionId;

    // If no session exists yet, create one
    if (!currentSessionId) {
      try {
        const newSess = await createSession(text.slice(0, 35));
        currentSessionId = newSess.id;
        if (onSessionCreated) {
          onSessionCreated(currentSessionId);
        }
      } catch (e) {
        console.error("Failed to create session, proceeding with default session", e);
      }
    }

    const userMsg: Message = { role: "user", content: text, timestamp: Date.now() };
    setMessages((prev) => [...prev, userMsg]);
    setInput("");
    setSendPulse((p) => p + 1);
    setLoading(true);

    try {
      const res = await queryDocuments(text, 5, currentSessionId);
      const botMsg: Message = {
        role: "assistant",
        content: res.answer,
        sources: res.sources,
        tokens: res.tokens,
        latency_ms: res.latency_ms,
        timestamp: Date.now(),
      };
      setMessages((prev) => [...prev, botMsg]);
      if (onSessionUpdated) {
        onSessionUpdated();
      }
    } catch (e: any) {
      const isTimeout = e?.name === "AbortError" || /timed? ?out|aborted/i.test(e?.message || "");
      const friendly = isTimeout
        ? "The request took too long. Your local model may have been loading or busy — try asking again."
        : `I couldn't complete that query. ${e?.message ? `${e.message} ` : ""}Please try again or rephrase slightly.`;
      setMessages((prev) => [
        ...prev,
        {
          role: "assistant",
          content: friendly,
          timestamp: Date.now(),
        },
      ]);
    } finally {
      setLoading(false);
    }
  }

  function clearChat() {
    if (loading) return;
    setMessages([]);
    setInput("");
  }

  return (
    <div className="glass mt-3 flex min-h-0 flex-1 flex-col overflow-hidden rounded-2xl">
      {/* Chat header */}
      <div className="flex items-center justify-between border-b border-ink-faint/20 px-4 py-2.5 sm:px-6">
        <div className="flex items-center gap-3">
          {onToggleSidebar && (
            <button
              onClick={onToggleSidebar}
              aria-label={isSidebarOpen ? "Hide sidebar" : "Show chat history"}
              title={isSidebarOpen ? "Hide sidebar" : "Show chat history"}
              className="flex h-7 w-7 items-center justify-center rounded-lg text-ink-dim hover:bg-ink-faint/10 hover:text-ink transition-colors"
            >
              <svg width="15" height="15" viewBox="0 0 16 16" fill="none" aria-hidden="true">
                <path d="M2.5 4h11M2.5 8h11M2.5 12h11" stroke="currentColor" strokeWidth="1.4" strokeLinecap="round" />
              </svg>
            </button>
          )}
          <div className="text-[12px] font-medium text-ink">
            {messages.length === 0 ? "Conversation" : `${messages.length} message${messages.length === 1 ? "" : "s"}`}
          </div>
        </div>

        {messages.length > 0 && (
          <button
            onClick={clearChat}
            disabled={loading}
            aria-label="Clear chat"
            title="Clear chat"
            className="flex items-center gap-1.5 rounded-lg px-2 py-1 text-[11px] font-medium text-ink-dim transition-colors hover:bg-ink-faint/10 hover:text-ink disabled:cursor-not-allowed disabled:opacity-40"
          >
            <svg width="13" height="13" viewBox="0 0 14 14" fill="none" aria-hidden="true">
              <path d="M1.5 3h11M4 3V2a1 1 0 0 1 1-1h4a1 1 0 0 1 1 1v1M5.5 6v3.5M8.5 6v3.5M2.5 3l.5 8.5a1 1 0 0 0 1 .9h6a1 1 0 0 0 1-.9l.5-8.5" stroke="currentColor" strokeWidth="1.2" strokeLinecap="round" />
            </svg>
            Clear view
          </button>
        )}
      </div>

      {/* Messages */}
      <div ref={scrollRef} className="flex-1 overflow-y-auto px-4 py-6 sm:px-6">
        {historyLoading ? (
          <div className="flex h-full items-center justify-center">
            <div className="flex items-center gap-2 text-xs text-ink-dim">
              <span className="h-1.5 w-1.5 rounded-full bg-brand animate-pulse" />
              Loading conversation history...
            </div>
          </div>
        ) : messages.length === 0 ? (
          <div className="flex h-full flex-col items-center justify-center gap-4 text-center">
            <div className="group">
              <div className="brand-tile flex h-14 w-14 items-center justify-center rounded-2xl bg-brand">
                <svg width="26" height="26" viewBox="0 0 24 24" fill="none" aria-hidden="true">
                  <path
                    className="brand-page brand-page-left"
                    d="M12 5.6 C9.1 4.2 5.9 4.9 4 7.4 L4 18 C6.6 16.4 9.3 15.9 12 17.4 Z"
                    fill="#fff"
                    fillOpacity="0.4"
                  />
                  <path
                    className="brand-page brand-page-right"
                    d="M12 5.6 C14.9 4.2 18.1 4.9 20 7.4 L20 18 C17.4 16.4 14.7 15.9 12 17.4 Z"
                    fill="#fff"
                  />
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
            <div>
              <p className="text-[15px] font-medium text-ink">Ask Lumen anything about your documents</p>
              <p className="mt-1 max-w-sm text-[13px] leading-relaxed text-ink-dim">
                Upload a file, then ask a question. Every answer is grounded in
                your sources with inline citations.
              </p>
            </div>
          </div>
        ) : (
          messages.map((msg, i) => (
            <MessageBubble
              key={msg.id || i}
              message={msg}
              enterClass={i === messages.length - 1 ? "dive-enter" : "sink-enter"}
            />
          ))
        )}

        {loading && (
          <div className="mb-4 flex items-center gap-2">
            <span className="h-1.5 w-1.5 rounded-full bg-brand animate-pulse" />
            <span className="digits text-[10px] uppercase tracking-[0.16em] text-ink-dim">
              Retrieving · reading your sources
            </span>
          </div>
        )}
      </div>

      {/* Input dock */}
      <div className="px-4 pb-4 pt-1 sm:px-6">
        <div className="glass-field mx-auto flex max-w-3xl items-stretch gap-3 rounded-2xl p-2">
          <div className="flex-1">
            <textarea
              value={input}
              onChange={(e) => setInput(e.target.value)}
              onKeyDown={(e) => {
                if (e.key === "Enter" && !e.shiftKey) {
                  e.preventDefault();
                  handleSend();
                }
              }}
              placeholder="Ask a question or follow-up…"
              rows={1}
              className="w-full resize-none rounded-xl bg-transparent px-2 py-2 text-sm text-reply placeholder-ink-dim focus:outline-none max-h-40"
            />
          </div>
          <button
            onClick={handleSend}
            disabled={loading || !input.trim()}
            aria-label="Send"
            className="group flex w-10 shrink-0 items-stretch justify-center rounded-xl bg-brand text-white transition-all hover:brightness-110 disabled:cursor-not-allowed disabled:opacity-40"
          >
            <svg
              key={sendPulse}
              width="16"
              height="16"
              viewBox="0 0 16 16"
              fill="none"
              aria-hidden="true"
              className={`m-auto ${sendPulse > 0 ? "nudge" : ""}`}
            >
              <path d="M2 8h11M9 4l4 4-4 4" stroke="currentColor" strokeWidth="1.6" strokeLinecap="round" strokeLinejoin="round" />
            </svg>
          </button>
        </div>
      </div>
    </div>
  );
}
