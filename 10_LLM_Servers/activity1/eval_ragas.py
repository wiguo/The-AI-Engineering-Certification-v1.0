# /// script
# requires-python = ">=3.11"
# dependencies = [
#     "ragas==0.2.15",
#     "langchain-openai==0.3.18",
#     "datasets>=3.0",
#     "pandas",
#     "python-dotenv",
# ]
# ///
"""Activity 1, phase 2: score both providers' RAG outputs with RAGAS.

Runs in its own environment because ragas pins an older langchain than the app uses:
    uv run --no-project activity1/eval_ragas.py

Metrics:
- context_precision / context_recall -> retrieval quality
- faithfulness                       -> is the answer grounded in retrieved context
- answer_correctness                 -> end-to-end accuracy vs ground truth

Judge model is OpenAI gpt-4.1 (a non-contestant) for both providers.
"""

from __future__ import annotations

import json
import os
from pathlib import Path

from dotenv import load_dotenv

HERE = Path(__file__).resolve().parent
load_dotenv(HERE.parent / ".env")
os.environ["LANGSMITH_TRACING"] = "false"  # judge calls should not pollute cost traces

import pandas as pd
from datasets import Dataset
from langchain_openai import ChatOpenAI, OpenAIEmbeddings
from ragas import RunConfig, evaluate
from ragas.embeddings import LangchainEmbeddingsWrapper
from ragas.llms import LangchainLLMWrapper
from ragas.metrics import (
    answer_correctness,
    context_precision,
    context_recall,
    faithfulness,
)


def main() -> None:
    results = json.loads(
        (HERE / "results" / "pipeline_results.json").read_text(encoding="utf-8")
    )

    judge = LangchainLLMWrapper(ChatOpenAI(model="gpt-4.1", temperature=0))
    judge_embeddings = LangchainEmbeddingsWrapper(
        OpenAIEmbeddings(model="text-embedding-3-small")
    )
    metrics = [context_precision, context_recall, faithfulness, answer_correctness]

    summary = {}
    per_question = {}
    for provider, rows in results.items():
        ds = Dataset.from_dict(
            {
                "question": [r["question"] for r in rows],
                "answer": [r["answer"] for r in rows],
                "contexts": [r["contexts"] for r in rows],
                "ground_truth": [r["ground_truth"] for r in rows],
            }
        )
        print(f"\n=== scoring {provider} ===")
        scores = evaluate(
            ds,
            metrics=metrics,
            llm=judge,
            embeddings=judge_embeddings,
            run_config=RunConfig(timeout=600, max_workers=4),
        )
        df = scores.to_pandas()
        per_question[provider] = df
        summary[provider] = {
            m.name: round(float(df[m.name].mean()), 4) for m in metrics
        }

    print("\n=== summary (mean over 8 questions) ===")
    summary_df = pd.DataFrame(summary)
    print(summary_df)

    out_dir = HERE / "results"
    summary_df.to_csv(out_dir / "ragas_summary.csv")
    for provider, df in per_question.items():
        df.to_csv(out_dir / f"ragas_{provider}_per_question.csv", index=False)
    print(f"\nsaved -> {out_dir}\\ragas_summary.csv and per-question CSVs")


if __name__ == "__main__":
    main()
