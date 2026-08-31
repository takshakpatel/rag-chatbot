from __future__ import annotations

import tiktoken
from dataclasses import dataclass, field


@dataclass
class TokenUsage:
    prompt_tokens: int = 0
    completion_tokens: int = 0
    total_tokens: int = 0
    estimated_cost_usd: float = 0.0


@dataclass
class QueryStats:
    query: str
    tokens: TokenUsage
    cached: bool = False
    latency_ms: float = 0.0


class TokenTracker:
    """Track token usage and estimated cost per query.

    Cost estimates based on OpenAI pricing (as of 2024):
    - gpt-4o-mini: $0.15/1M input, $0.60/1M output
    - text-embedding-3-small: $0.02/1M tokens
    """

    COST_TABLE = {
        "gpt-4o-mini": {"input": 0.15 / 1_000_000, "output": 0.60 / 1_000_000},
        "gpt-4o": {"input": 2.50 / 1_000_000, "output": 10.00 / 1_000_000},
        "gpt-3.5-turbo": {"input": 0.50 / 1_000_000, "output": 1.50 / 1_000_000},
    }

    EMBEDDING_COST = 0.02 / 1_000_000  # per token

    def __init__(self):
        self._history: list[QueryStats] = []
        try:
            self._enc = tiktoken.get_encoding("cl100k_base")
        except Exception:
            self._enc = None

    def count_tokens(self, text: str) -> int:
        if self._enc:
            return len(self._enc.encode(text))
        return len(text) // 4

    def estimate_llm_cost(
        self,
        prompt_tokens: int,
        completion_tokens: int,
        model: str = "gpt-4o-mini",
    ) -> float:
        rates = self.COST_TABLE.get(model, self.COST_TABLE["gpt-4o-mini"])
        return prompt_tokens * rates["input"] + completion_tokens * rates["output"]

    def record(
        self,
        query: str,
        prompt_tokens: int,
        completion_tokens: int,
        model: str = "gpt-4o-mini",
        cached: bool = False,
        latency_ms: float = 0.0,
    ) -> TokenUsage:
        cost = 0.0 if cached else self.estimate_llm_cost(prompt_tokens, completion_tokens, model)
        usage = TokenUsage(
            prompt_tokens=prompt_tokens,
            completion_tokens=completion_tokens,
            total_tokens=prompt_tokens + completion_tokens,
            estimated_cost_usd=cost,
        )
        stats = QueryStats(query=query, tokens=usage, cached=cached, latency_ms=latency_ms)
        self._history.append(stats)
        return usage

    def cumulative_stats(self) -> dict:
        if not self._history:
            return {"total_queries": 0, "total_tokens": 0, "total_cost_usd": 0.0}
        total_prompt = sum(s.tokens.prompt_tokens for s in self._history)
        total_completion = sum(s.tokens.completion_tokens for s in self._history)
        total_cost = sum(s.tokens.estimated_cost_usd for s in self._history)
        cached_count = sum(1 for s in self._history if s.cached)
        return {
            "total_queries": len(self._history),
            "total_prompt_tokens": total_prompt,
            "total_completion_tokens": total_completion,
            "total_tokens": total_prompt + total_completion,
            "total_cost_usd": round(total_cost, 6),
            "cached_queries": cached_count,
            "avg_latency_ms": round(
                sum(s.latency_ms for s in self._history) / len(self._history), 1
            ),
        }


# Global singleton
token_tracker = TokenTracker()
