#!/usr/bin/env python3
"""Run the evaluation harness.

Usage:
    python -m evaluation.run_eval --questions evaluation/questions.json
    python -m evaluation.run_eval --questions evaluation/questions.json --k 10
    python -m evaluation.run_eval --questions evaluation/questions.json --config '{"chunk_size": 500}'
"""
from __future__ import annotations

import argparse
import json
import sys
from pathlib import Path

sys.path.insert(0, str(Path(__file__).resolve().parent.parent))

from evaluation.harness import run_evaluation, save_report, print_report


def main():
    parser = argparse.ArgumentParser(description="Run RAG evaluation")
    parser.add_argument("--questions", required=True, help="Path to questions JSON")
    parser.add_argument("--k", type=int, default=5, help="Top-k retrieval")
    parser.add_argument("--collection", default="documents", help="Collection name")
    parser.add_argument("--config", default=None, help="JSON config string for the report")
    parser.add_argument("--output", default=None, help="Save report to this path")
    args = parser.parse_args()

    config = json.loads(args.config) if args.config else {}

    report = run_evaluation(
        questions_path=args.questions,
        k=args.k,
        collection_name=args.collection,
        config=config,
    )

    print_report(report)

    if args.output:
        save_report(report, args.output)
        print(f"Report saved to {args.output}")


if __name__ == "__main__":
    main()
