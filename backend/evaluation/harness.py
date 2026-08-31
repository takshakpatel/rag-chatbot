from __future__ import annotations

import json
import os
import re
from pathlib import Path
from dataclasses import dataclass, field, asdict

from app.retriever import naive_retrieve
from app.rag import build_rag_answer
from app.vectorstore import get_embeddings


@dataclass
class EvalQuestion:
    id: int
    question: str
    expected_answer: str
    expected_source_files: list[str]
    expected_keywords: list[str]
    category: str
    unanswerable: bool = False


@dataclass
class RetrievalResult:
    question_id: int
    question: str
    hit: bool
    top_k_sources: list[str]
    expected_sources: list[str]
    rank_of_hit: int | None = None


@dataclass
class FaithfulnessResult:
    question_id: int
    question: str
    answer: str
    keyword_coverage: float
    refused: bool
    expected_refusal: bool


@dataclass
class EvalReport:
    total_questions: int
    retrieval_hit_rate: float
    retrieval_details: list[RetrievalResult]
    faithfulness_details: list[FaithfulnessResult]
    avg_keyword_coverage: float
    refusal_accuracy: float
    config: dict = field(default_factory=dict)


def load_questions(path: str | Path) -> list[EvalQuestion]:
    with open(path) as f:
        raw = json.load(f)
    return [EvalQuestion(**q) for q in raw]


def evaluate_retrieval(
    questions: list[EvalQuestion],
    k: int = 5,
    collection_name: str = "documents",
) -> list[RetrievalResult]:
    results = []
    for q in questions:
        docs = naive_retrieve(q.question, k=k, collection_name=collection_name)
        retrieved_sources = [
            Path(d.metadata.get("source", "")).name for d in docs
        ]

        hit = False
        rank = None
        for expected in q.expected_source_files:
            for i, src in enumerate(retrieved_sources):
                if expected.lower() in src.lower() or src.lower() in expected.lower():
                    hit = True
                    rank = i + 1
                    break
            if hit:
                break

        results.append(RetrievalResult(
            question_id=q.id,
            question=q.question,
            hit=hit,
            top_k_sources=retrieved_sources,
            expected_sources=q.expected_source_files,
            rank_of_hit=rank,
        ))
    return results


def evaluate_faithfulness(
    questions: list[EvalQuestion],
    collection_name: str = "documents",
) -> list[FaithfulnessResult]:
    results = []
    for q in questions:
        result = build_rag_answer(q.question, collection_name=collection_name)
        answer = result["answer"].lower()

        if q.expected_keywords:
            found = sum(1 for kw in q.expected_keywords if kw.lower() in answer)
            coverage = found / len(q.expected_keywords)
        else:
            coverage = 1.0

        refusal_phrases = [
            "i don't have enough",
            "i cannot answer",
            "not enough information",
            "no information",
            "unable to answer",
            "context does not contain",
            "i don't have sufficient",
        ]
        refused = any(phrase in answer for phrase in refusal_phrases)

        results.append(FaithfulnessResult(
            question_id=q.id,
            question=q.question,
            answer=result["answer"],
            keyword_coverage=coverage,
            refused=refused,
            expected_refusal=q.unanswerable,
        ))
    return results


def run_evaluation(
    questions_path: str | Path,
    k: int = 5,
    collection_name: str = "documents",
    config: dict | None = None,
) -> EvalReport:
    questions = load_questions(questions_path)

    retrieval_results = evaluate_retrieval(questions, k=k, collection_name=collection_name)
    faithfulness_results = evaluate_faithfulness(questions, collection_name=collection_name)

    hits = sum(1 for r in retrieval_results if r.hit)
    hit_rate = hits / len(questions) if questions else 0.0

    avg_coverage = (
        sum(r.keyword_coverage for r in faithfulness_results) / len(faithfulness_results)
        if faithfulness_results
        else 0.0
    )

    refusal_correct = sum(
        1 for r in faithfulness_results
        if r.refused == r.expected_refusal
    )
    refusal_acc = refusal_correct / len(faithfulness_results) if faithfulness_results else 0.0

    return EvalReport(
        total_questions=len(questions),
        retrieval_hit_rate=hit_rate,
        retrieval_details=retrieval_results,
        faithfulness_details=faithfulness_results,
        avg_keyword_coverage=avg_coverage,
        refusal_accuracy=refusal_acc,
        config=config or {},
    )


def save_report(report: EvalReport, path: str | Path) -> None:
    with open(path, "w") as f:
        json.dump(asdict(report), f, indent=2)


def print_report(report: EvalReport) -> None:
    print(f"\n{'='*60}")
    print(f"  EVALUATION REPORT")
    print(f"{'='*60}")
    print(f"  Questions:          {report.total_questions}")
    print(f"  Retrieval hit rate: {report.retrieval_hit_rate:.1%}")
    print(f"  Avg keyword cover:  {report.avg_keyword_coverage:.1%}")
    print(f"  Refusal accuracy:   {report.refusal_accuracy:.1%}")
    if report.config:
        print(f"  Config: {report.config}")
    print(f"{'='*60}\n")

    misses = [r for r in report.retrieval_details if not r.hit]
    if misses:
        print(f"  Retrieval misses ({len(misses)}):")
        for r in misses:
            print(f"    Q{r.question_id}: {r.question[:60]}...")
    print()
