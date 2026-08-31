"use client";

import { Message } from "@/types";
import SourcePins from "./SourcePins";

interface MessageBubbleProps {
  message: Message;
  enterClass?: string;
}

function RefusalMark() {
  return (
    <svg width="13" height="13" viewBox="0 0 13 13" fill="none" aria-hidden="true">
      <path
        d="M6.5 1.5v6M6.5 10.5h.01"
        stroke="currentColor"
        strokeWidth="1.6"
        strokeLinecap="round"
      />
    </svg>
  );
}

function AssistantMark() {
  return (
    <svg width="13" height="13" viewBox="0 0 13 13" fill="none" aria-hidden="true">
      <path
        d="M6.5 1.5c1.3 1.3 3.7 2.4 3.7 4.8A3.7 3.7 0 0 1 6.5 9.7 3.7 3.7 0 0 1 2.8 6.3c0-2.4 2.4-3.5 3.7-4.8Z"
        fill="url(#assistg)"
      />
      <defs>
        <linearGradient id="assistg" x1="2.8" y1="1.5" x2="2.8" y2="9.7" gradientUnits="userSpaceOnUse">
          <stop stopColor="#8b7cf6" />
          <stop offset="1" stopColor="#4cc9f0" />
        </linearGradient>
      </defs>
    </svg>
  );
}

export default function MessageBubble({ message, enterClass = "sink-enter" }: MessageBubbleProps) {
  const isUser = message.role === "user";
  const isRefusal =
    !isUser &&
    message.content.length < 160 &&
    /(don't have enough|cannot answer|no information|not enough|unable to answer|context does not contain)/i.test(
      message.content
    );

  if (isUser) {
    return (
      <div className={`mb-3 flex justify-end ${enterClass}`}>
        <div className="bubble-user max-w-[80%] rounded-2xl rounded-br-md px-4 py-2.5">
          <p className="text-[14px] leading-relaxed text-white">{message.content}</p>
        </div>
      </div>
    );
  }

  return (
    <div className={`mb-5 ${enterClass}`}>
      <div className="mb-1.5 flex items-center gap-2">
        <AssistantMark />
        <span className="digits text-[10px] uppercase tracking-[0.16em] text-ink-dim">
          {isRefusal ? "Could not answer" : "Answer"}
        </span>
      </div>
      <div
        className={`glass-tile overflow-hidden rounded-2xl px-4 py-3.5 ${
          isRefusal ? "border-refusal/40" : ""
        }`}
      >
        <p className={`text-[15px] leading-relaxed ${isRefusal ? "text-refusal" : "text-reply"}`}>
          {isRefusal && <RefusalMark />} {message.content}
        </p>
        {message.sources && <SourcePins sources={message.sources} />}
      </div>
    </div>
  );
}
