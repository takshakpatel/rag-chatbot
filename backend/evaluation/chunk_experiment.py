#!/usr/bin/env python3
"""Compare two chunking strategies by measuring retrieval hit rate.

Usage:
    python -m evaluation.chunk_experiment --docs ./documents --questions evaluation/questions.json
"""
from __future__ import annotations

import argparse
import json
import sys
from pathlib import Path

sys.path.insert(0, str(Path(__file__).resolve().parent.parent))

from app.loader import load_documents
from app.chunker import chunk_documents
from app.semantic_chunker import chunk_documents_semantic
from app.vectorstore import add_documents_to_store, reset_store, get_vectorstore
from evaluation.harness import run_evaluation, print_report


def run_experiment(
    docs_path: str,
    questions_path: str,
    chunk_sizes: list[int] = [500, 1000, 1500],
    overlaps: list[int] = [100, 200],
):
    docs = load_documents(docs_path)
    if not docs:
        print("No documents found.")
        return

    results_table = []

    for strategy_name, chunk_fn in [
        ("recursive", chunk_documents),
        ("semantic", chunk_documents_semantic),
    ]:
        for size in chunk_sizes:
            for overlap in overlaps:
                if overlap >= size:
                    continue

                collection = f"{strategy_name}_s{size}_o{overlap}"
                reset_store(collection_name=collection)

                chunks = chunk_fn(docs, chunk_size=size, chunk_overlap=overlap)
                add_documents_to_store(chunks, collection_name=collection)

                report = run_evaluation(
                    questions_path=questions_path,
                    collection_name=collection,
                    config={"strategy": strategy_name, "chunk_size": size, "chunk_overlap": overlap},
                )

                results_table.append({
                    "strategy": strategy_name,
                    "chunk_size": size,
                    "chunk_overlap": overlap,
                    "num_chunks": len(chunks),
                    "retrieval_hit_rate": report.retrieval_hit_rate,
                    "avg_keyword_coverage": report.avg_keyword_coverage,
                    "refusal_accuracy": report.refusal_accuracy,
                })

                reset_store(collection_name=collection)

                print(f"  {strategy_name:10s} | size={size:4d} | overlap={overlap:3d} | chunks={len(chunks):4d} | hit_rate={report.retrieval_hit_rate:.1%}")

    print(f"\n{'='*90}")
    print(f"  {'Strategy':<12} {'Size':>6} {'Overlap':>8} {'Chunks':>7} {'Hit Rate':>10} {'Coverage':>10} {'Refusal':>10}")
    print(f"  {'-'*12} {'-'*6} {'-'*8} {'-'*7} {'-'*10} {'-'*10} {'-'*10}")
    for r in results_table:
        print(
            f"  {r['strategy']:<12} {r['chunk_size']:>6} {r['chunk_overlap']:>8} "
            f"{r['num_chunks']:>7} {r['retrieval_hit_rate']:>9.1%} "
            f"{r['avg_keyword_coverage']:>9.1%} {r['refusal_accuracy']:>9.1%}"
        )
    print(f"{'='*90}\n")

    output_path = Path("evaluation") / "chunk_experiment_results.json"
    with open(output_path, "w") as f:
        json.dump(results_table, f, indent=2)
    print(f"Results saved to {output_path}")


def main():
    parser = argparse.ArgumentParser(description="Compare chunking strategies")
    parser.add_argument("--docs", required=True, help="Path to documents directory")
    parser.add_argument("--questions", required=True, help="Path to questions JSON")
    args = parser.parse_args()

    run_experiment(args.docs, args.questions)


if __name__ == "__main__":
    main()
