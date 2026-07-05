# Activity 1: RAGAS Evaluation with Cost Analysis

Compares the same RAG pipeline on two providers over 8 questions grounded in
`data/cat-health-guide.pdf` (2021 AAHA/AAFP Feline Life Stage Guidelines):

| | Fireworks (open source) | OpenAI |
|---|---|---|
| Chat model | `gpt-oss-20b` (serverless) | `gpt-4.1-mini` |
| Embeddings | `qwen3-embedding-8b` | `text-embedding-3-small` |

Chunks, prompt, retriever settings (k=4), and temperature (0) are identical, so the
comparison isolates the provider stack.

## Files

- `eval_questions.json` — 8 questions + ground truths written from the PDF
- `run_pipelines.py` — runs both pipelines, captures answers/contexts/tokens/latency,
  traces each provider to its own LangSmith project (`s10-rag-fireworks`, `s10-rag-openai`)
- `eval_ragas.py` — scores both result sets with RAGAS (context precision/recall,
  faithfulness, answer correctness); judge = OpenAI `gpt-4.1` for both
- `analyze_costs.py` — token totals, latency, and cost per query at current prices
- `results/` — pipeline outputs, RAGAS scores, cost summary

## Run

From `10_LLM_Servers/` (needs `FIREWORKS_API_KEY`, `OPENAI_API_KEY`, `LANGSMITH_API_KEY` in `.env`):

```bash
uv run python activity1/run_pipelines.py     # phase 1: generate
uv run --no-project activity1/eval_ragas.py  # phase 2: RAGAS scoring (own env — ragas pins older langchain)
uv run python activity1/analyze_costs.py     # phase 3: cost/latency summary
```

Results and analysis are written up in the main session README under "Activity 1".
