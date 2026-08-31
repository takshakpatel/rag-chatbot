"use client";

import { useState, useRef, useEffect, useCallback } from "react";
import { Message } from "@/types";
import { queryDocuments } from "@/lib/api";
import MessageBubble from "./MessageBubble";

export default function Chat() {
  const [messages, setMessages] = useState<Message[]>([]);
  const [input, setInput] = useState("");
  const [loading, setLoading] = useState(false);
  const [sendPulse, setSendPulse] = useState(0);
  const scrollRef = useRef<HTMLDivElement>(null);

  const scrolling = useCallback(() => {
    scrollRef.current?.scrollTo({
      top: scrollRef.current.scrollHeight,
      behavior: "smooth",
    });
  }, []);

  useEffect(() => {
    scrolling();
  }, [messages, loading, scrolling]);

  async function handleSend() {
    const text = input.trim();
    if (!text || loading) return;

    const userMsg: Message = { role: "user", content: text, timestamp: Date.now() };
    setMessages((prev) => [...prev, userMsg]);
    setInput("");
    setSendPulse((p) => p + 1);
    setLoading(true);

    try {
      const res = await queryDocuments(text);
      const botMsg: Message = {
        role: "assistant",
        content: res.answer,
        sources: res.sources,
        timestamp: Date.now(),
      };
      setMessages((prev) => [...prev, botMsg]);
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
        <div className="text-[12px] font-medium text-ink">
          {messages.length === 0 ? "Conversation" : `${messages.length} message${messages.length === 1 ? "" : "s"}`}
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
            Clear chat
          </button>
        )}
      </div>

      {/* Messages */}
      <div ref={scrollRef} className="flex-1 overflow-y-auto px-4 py-6 sm:px-6">
        {messages.length === 0 && (
          <div className="flex h-full flex-col items-center justify-center gap-4 text-center">
            <div className="flex h-14 w-14 items-center justify-center rounded-2xl bg-brand shadow-glass-glow">
              <svg width="24" height="24" viewBox="0 0 24 24" fill="none" aria-hidden="true">
                <path
                  d="M12 2.5c2.1 2.1 6 3.9 6 7.8 0 3.9-2.6 6.6-6 7.7-3.4-1.1-6-3.8-6-7.7 0-3.9 3.9-5.7 6-7.8Z"
                  fill="#fff"
                  fillOpacity="0.9"
                />
                <circle cx="12" cy="10.6" r="1.8" fill="#8b7cf6" />
              </svg>
            </div>
            <div>
              <p className="text-[15px] font-medium text-ink">Ask Lumen anything about your documents</p>
              <p className="mt-1 max-w-sm text-[13px] leading-relaxed text-ink-dim">
                Upload a file, then ask a question. Every answer is grounded in
                your sources with inline citations.
              </p>
            </div>
          </div>
        )}
        {messages.map((msg, i) => (
          <MessageBubble
            key={i}
            message={msg}
            enterClass={i === messages.length - 1 ? "dive-enter" : "sink-enter"}
          />
        ))}
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
              placeholder="Ask a question…"
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
