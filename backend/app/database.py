from __future__ import annotations

import json
import sqlite3
import time
import uuid
from pathlib import Path
from typing import Any

DB_PATH = Path(__file__).resolve().parent.parent / "lumen_history.db"


def get_db_connection() -> sqlite3.Connection:
    conn = sqlite3.connect(str(DB_PATH), check_same_thread=False)
    conn.row_factory = sqlite3.Row
    conn.execute("PRAGMA journal_mode=WAL;")
    conn.execute("PRAGMA foreign_keys=ON;")
    return conn


def init_db() -> None:
    conn = get_db_connection()
    try:
        with conn:
            conn.executescript("""
                CREATE TABLE IF NOT EXISTS sessions (
                    id TEXT PRIMARY KEY,
                    title TEXT NOT NULL,
                    created_at REAL NOT NULL,
                    updated_at REAL NOT NULL
                );

                CREATE TABLE IF NOT EXISTS messages (
                    id TEXT PRIMARY KEY,
                    session_id TEXT NOT NULL,
                    role TEXT NOT NULL,
                    content TEXT NOT NULL,
                    sources TEXT,
                    tokens TEXT,
                    latency_ms REAL,
                    created_at REAL NOT NULL,
                    FOREIGN KEY (session_id) REFERENCES sessions(id) ON DELETE CASCADE
                );

                CREATE INDEX IF NOT EXISTS idx_messages_session_id ON messages(session_id);
                CREATE INDEX IF NOT EXISTS idx_sessions_updated_at ON sessions(updated_at DESC);
            """)
    finally:
        conn.close()


def create_session(title: str = "New Chat", session_id: str | None = None) -> dict[str, Any]:
    sid = session_id or str(uuid.uuid4())
    now = time.time()
    conn = get_db_connection()
    try:
        with conn:
            conn.execute(
                "INSERT INTO sessions (id, title, created_at, updated_at) VALUES (?, ?, ?, ?)",
                (sid, title, now, now),
            )
        return {"id": sid, "title": title, "created_at": now, "updated_at": now, "message_count": 0}
    finally:
        conn.close()


def list_sessions() -> list[dict[str, Any]]:
    conn = get_db_connection()
    try:
        cur = conn.cursor()
        cur.execute("""
            SELECT s.id, s.title, s.created_at, s.updated_at,
                   COUNT(m.id) AS message_count,
                   (SELECT content FROM messages WHERE session_id = s.id ORDER BY created_at ASC LIMIT 1) AS preview
            FROM sessions s
            LEFT JOIN messages m ON s.id = m.session_id
            GROUP BY s.id
            ORDER BY s.updated_at DESC
        """)
        rows = cur.fetchall()
        return [dict(row) for row in rows]
    finally:
        conn.close()


def get_session(session_id: str) -> dict[str, Any] | None:
    conn = get_db_connection()
    try:
        cur = conn.cursor()
        cur.execute("SELECT id, title, created_at, updated_at FROM sessions WHERE id = ?", (session_id,))
        row = cur.fetchone()
        return dict(row) if row else None
    finally:
        conn.close()


def update_session_title(session_id: str, title: str) -> dict[str, Any] | None:
    now = time.time()
    conn = get_db_connection()
    try:
        with conn:
            cur = conn.execute(
                "UPDATE sessions SET title = ?, updated_at = ? WHERE id = ?",
                (title, now, session_id),
            )
            if cur.rowcount == 0:
                return None
        return get_session(session_id)
    finally:
        conn.close()


def delete_session(session_id: str) -> bool:
    conn = get_db_connection()
    try:
        with conn:
            cur = conn.execute("DELETE FROM sessions WHERE id = ?", (session_id,))
            return cur.rowcount > 0
    finally:
        conn.close()


def add_message(
    session_id: str,
    role: str,
    content: str,
    sources: list[dict[str, Any]] | None = None,
    tokens: dict[str, Any] | None = None,
    latency_ms: float | None = None,
) -> dict[str, Any]:
    now = time.time()
    mid = str(uuid.uuid4())
    conn = get_db_connection()
    try:
        with conn:
            cur = conn.execute("SELECT id, title FROM sessions WHERE id = ?", (session_id,))
            session = cur.fetchone()
            if not session:
                initial_title = content[:35] + ("..." if len(content) > 35 else "") if role == "user" else "New Chat"
                conn.execute(
                    "INSERT INTO sessions (id, title, created_at, updated_at) VALUES (?, ?, ?, ?)",
                    (session_id, initial_title, now, now),
                )
            else:
                if session["title"] == "New Chat" and role == "user":
                    new_title = content[:35] + ("..." if len(content) > 35 else "")
                    conn.execute("UPDATE sessions SET title = ?, updated_at = ? WHERE id = ?", (new_title, now, session_id))
                else:
                    conn.execute("UPDATE sessions SET updated_at = ? WHERE id = ?", (now, session_id))

            sources_json = json.dumps(sources) if sources else None
            tokens_json = json.dumps(tokens) if tokens else None

            conn.execute(
                """
                INSERT INTO messages (id, session_id, role, content, sources, tokens, latency_ms, created_at)
                VALUES (?, ?, ?, ?, ?, ?, ?, ?)
                """,
                (mid, session_id, role, content, sources_json, tokens_json, latency_ms, now),
            )

        return {
            "id": mid,
            "session_id": session_id,
            "role": role,
            "content": content,
            "sources": sources or [],
            "tokens": tokens,
            "latency_ms": latency_ms,
            "created_at": now,
        }
    finally:
        conn.close()


def get_session_messages(session_id: str) -> list[dict[str, Any]]:
    conn = get_db_connection()
    try:
        cur = conn.cursor()
        cur.execute(
            """
            SELECT id, session_id, role, content, sources, tokens, latency_ms, created_at
            FROM messages
            WHERE session_id = ?
            ORDER BY created_at ASC
            """,
            (session_id,),
        )
        rows = cur.fetchall()
        messages = []
        for row in rows:
            m = dict(row)
            m["sources"] = json.loads(m["sources"]) if m["sources"] else []
            m["tokens"] = json.loads(m["tokens"]) if m["tokens"] else None
            messages.append(m)
        return messages
    finally:
        conn.close()


init_db()
