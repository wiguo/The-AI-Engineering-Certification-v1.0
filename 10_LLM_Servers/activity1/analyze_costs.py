"""Activity 1, phase 3: token usage, latency, and cost-per-query comparison.

Prices (USD per 1M tokens, verified 2026-07-05):
- Fireworks gpt-oss-20b serverless: $0.07 input / $0.30 output (fireworks.ai/models/fireworks/gpt-oss-20b)
- Fireworks qwen3-embedding-8b:     $0.10 (fireworks.ai/pricing)
- OpenAI gpt-4.1-mini:              $0.40 input / $1.60 output (developers.openai.com/api/docs/pricing)
- OpenAI text-embedding-3-small:    $0.02 (developers.openai.com/api/docs/pricing)

Run from 10_LLM_Servers/:  uv run python activity1/analyze_costs.py
"""

from __future__ import annotations

import json
import statistics
from pathlib import Path

PRICES = {  # USD per 1M tokens
    "fireworks": {"input": 0.07, "output": 0.30},
    "openai": {"input": 0.40, "output": 1.60},
}

HERE = Path(__file__).resolve().parent


def main() -> None:
    results = json.loads(
        (HERE / "results" / "pipeline_results.json").read_text(encoding="utf-8")
    )

    lines = []
    for provider, rows in results.items():
        p = PRICES[provider]
        tokens_in = sum(r["input_tokens"] for r in rows)
        tokens_out = sum(r["output_tokens"] for r in rows)
        cost = tokens_in / 1e6 * p["input"] + tokens_out / 1e6 * p["output"]
        latencies = [r["generate_seconds"] for r in rows]
        lines.append(
            {
                "provider": provider,
                "queries": len(rows),
                "input_tokens": tokens_in,
                "output_tokens": tokens_out,
                "total_cost_usd": round(cost, 6),
                "cost_per_query_usd": round(cost / len(rows), 6),
                "cost_per_1M_queries_usd": round(cost / len(rows) * 1e6, 2),
                "median_gen_seconds": round(statistics.median(latencies), 2),
                "max_gen_seconds": round(max(latencies), 2),
            }
        )

    out = HERE / "results" / "cost_summary.json"
    out.write_text(json.dumps(lines, indent=2), encoding="utf-8")
    for row in lines:
        print(json.dumps(row, indent=2))
    print(f"\nsaved -> {out}")


if __name__ == "__main__":
    main()
