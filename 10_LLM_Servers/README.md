<p align = "center" draggable="false" ><img src="https://github.com/AI-Maker-Space/LLM-Dev-101/assets/37101144/d1343317-fa2f-41e1-8af1-1dbb18399719"
     width="200px"
     height="auto"/>
</p>

## <h1 align="center" id="heading">Session 10: LLM Servers</h1>

| 📰 Session Sheet                                  | ⏺️ Recording                           | 🖼️ Slides                                   | 👨‍💻 Repo       | 📝 Homework                                              | 📁 Feedback                        |
| ------------------------------------------------- | -------------------------------------- | ------------------------------------------- | ------------- | -------------------------------------------------------- | ---------------------------------- |
| [LLM Servers](../00_Docs/Session_Sheets/16_LLM_Servers) |[Recording!](https://us02web.zoom.us/rec/share/HDunij9p7eCXeP_OgsRDRjTdWUqiEhDBGWrFJEn1bwWR1wz1jKX6EHXSOM45d0sC.rHiyo_znZ-R8Jh6S) <br> passcode: `D80X^YjL`| [Session 10 Slides](https://www.canva.com/design/DAG-EBu7B5A/POcowC5rDLENSPcSVpbf8g/edit?utm_content=DAG-EBu7B5A&utm_campaign=designshare&utm_medium=link2&utm_source=sharebutton) | You are here! | [Session 10 Assignment: LLM Servers](https://forms.gle/Riqvwf6KrZcCRKV86) <br><br> [Demo Day Submission (3/12)](https://forms.gle/7xyuBUn69GX4v6K98)  | [Feedback 3/5](https://forms.gle/W28QFWJXpSS4ZAR6A) |

**⚠️!!! PLEASE BE SURE TO SHUTDOWN YOUR DEDICATED ENDPOINT ON FIREWORKS AI WHEN YOU'RE FINISHED YOUR ASSIGNMENT !!!⚠️**

# Build 🏗️

In today's assignment, we'll be creating Fireworks AI endpoints, and then building a RAG application.

- 🤝 Breakout Room #1
  - Set-up Open Source Endpoint (Instructions [here](./ENDPOINT_SETUP.md)) ((This process may take 15-20min.))
  - Test Endpoint and Embeddings with the `endpoint_slammer.ipynb` notebook.

- 🤝 Breakout Room #2
  - Use the Open Source Endpoints to build a RAG LangGraph application

# Ship 🚢

The completed notebook and your RAG app/notebook!

### Deliverables

- A short Loom of either:
  - the notebook and the RAG application you built for the Main Homework Assignment; or
  - the notebook you created for the Advanced Build

# Share 🚀

Make a social media post about your final application!

### Deliverables

- Make a post on any social media platform about what you built!

Here's a template to get you started:

```
🚀 Exciting News! 🚀

I am thrilled to announce that I have just built and shipped a RAG application powered by open-source endpoints! 🎉🤖

🔍 Three Key Takeaways:
1️⃣
2️⃣
3️⃣

Let's continue pushing the boundaries of what's possible in the world of AI and question-answering. Here's to many more innovations! 🚀
Shout out to @AIMakerspace !

#LangChain #QuestionAnswering #RetrievalAugmented #Innovation #AI #TechMilestone

Feel free to reach out if you're curious or would like to collaborate on similar projects! 🤝🔥
```

# Submitting You Homework

## Main Homework Assignment

Follow these steps to prepare and submit your homework assignment:

1. Follow the instructions in `ENDPOINT_SETUP.md`
2. Replace both `model` values in `endpoint_slammer.ipynb` with the `gpt-oss` endpoint you created in Step 1
3. Run the code cells in `endpoint_slammer.ipynb`
4. Respond to the questions in the section below
5. Build a sample RAG
6. Record a Loom video reviewing what you have learned from this session

**⚠️!!! PLEASE BE SURE TO SHUTDOWN YOUR DEDICATED ENDPOINT ON FIREWORKS AI WHEN YOU HAVE FINISHED YOUR ASSIGNMENT !!!⚠️**

## Questions

### ❓ Question #1:

What is the difference between serverless and dedicated endpoints?

#### ✅ Answer:

A **serverless endpoint** runs on shared, multi-tenant infrastructure: you pay **per token**, there's nothing to provision or shut down, and you can start calling the model immediately (e.g. `accounts/fireworks/models/gpt-oss-20b`). The trade-off is that capacity is shared — you're subject to rate limits, and latency/throughput can vary with other tenants' load.

A **dedicated (on-demand) endpoint** provisions GPUs reserved exclusively for you. You pay **per GPU-hour** whether or not requests are flowing, but in exchange you get guaranteed capacity, predictable latency, higher throughput ceilings, and control over the deployment (hardware, quantization, replicas, autoscaling/scale-to-zero). Serverless fits low or spiky traffic and experimentation; dedicated fits production workloads with sustained volume or strict latency SLOs — and you must remember to shut it down to avoid burning money while idle.

### ❓ Question #2:

Why is it important to consider token throughput and latency when choosing an LLM for user-facing applications?

#### ✅ Answer:

Because they directly determine the **user's perceived experience** and the **app's capacity**:

- **Latency** — especially *time-to-first-token* — is what the user feels. In a chat UI, a response that takes seconds before anything appears feels broken; streaming with a fast first token feels instant even if the full answer takes a while.
- **Token throughput** (tokens/sec, both per-stream and aggregate) determines how fast responses render and how many **concurrent users** the endpoint can serve. The `endpoint_slammer` notebook demonstrates this: firing 24 concurrent requests at an endpoint reveals whether it queues, throttles, or degrades under load.

For agentic or RAG apps the effect compounds — a single user query may trigger several sequential LLM calls (tool selection, retrieval-grounded generation, judging), so per-call latency multiplies. Choosing a model/endpoint is therefore a balance of quality vs. speed vs. cost: a slightly weaker but much faster open-source model on a well-provisioned endpoint often beats a stronger-but-slower one for interactive use.

## Activity 1: RAGAS Evaluation with Cost Analysis

Use RAGAS to evaluate your open-source Fireworks AI powered RAG app against an OpenAI `gpt-4.1-mini` powered equivalent. Compare retrieval quality, answer faithfulness, and end-to-end accuracy across both providers.

Additionally, instrument both pipelines with **LangSmith** to capture token usage and cost per query. Use LangSmith's tracing and cost dashboards to compare the total cost of running each provider at scale. Include your evaluation results, cost breakdown, and analysis in your Loom video.

### ✅ Results

All code, the eval dataset, and raw outputs live in [`activity1/`](./activity1/). Both pipelines share identical chunks (42 chunks of `data/cat-health-guide.pdf`), prompt, retriever settings (k=4), and temperature (0), so the comparison isolates the provider stack:

| | Fireworks (open source) | OpenAI |
|---|---|---|
| Chat model | `gpt-oss-20b` (serverless) | `gpt-4.1-mini` |
| Embeddings | `qwen3-embedding-8b` | `text-embedding-3-small` |

The eval set is 8 questions with ground truths written from the PDF (the 2021 AAHA/AAFP Feline Life Stage Guidelines). Judge model for RAGAS is OpenAI `gpt-4.1` — a non-contestant — for both providers.

#### RAGAS scores (mean over 8 questions)

| Metric | Fireworks | OpenAI | What it measures |
|---|---|---|---|
| context_precision | 0.955 | 0.969 | retrieval quality (signal vs. noise in retrieved chunks) |
| context_recall | 1.000 | 1.000 | retrieval quality (did we fetch everything needed) |
| faithfulness | 0.917 | 1.000 | is the answer grounded in the retrieved context |
| answer_correctness | 0.846 | 0.837 | end-to-end accuracy vs. ground truth |

**Retrieval quality is effectively tied.** Both embedding models achieved perfect recall and near-perfect precision on this corpus. **Faithfulness** favors `gpt-4.1-mini` slightly: `gpt-oss-20b` occasionally embellishes with details not strictly in the context (e.g., describing BCS as "a standardized 9-point scale" — true, but not in the retrieved chunks). **Answer correctness is a wash** — the open-source stack actually edged ahead, mostly because its fuller answers overlap more with the ground truths than `gpt-4.1-mini`'s terse one-liners.

#### Token usage, latency, and cost (8 queries, measured 2026-07-05)

| | Fireworks | OpenAI |
|---|---|---|
| Input tokens | 21,238 | 21,238 |
| Output tokens | 7,622 | 376 |
| Median generation latency | 1.8 s | 1.3 s |
| Max generation latency | 73.0 s | 2.8 s |
| Price (per 1M tokens in/out) | $0.07 / $0.30 | $0.40 / $1.60 |
| **Cost per query** | **$0.00047** | **$0.00114** |
| **Cost per 1M queries** | **~$472** | **~$1,137** |

#### Analysis

- **The open-source stack is ~2.4× cheaper per query** at comparable answer quality, despite `gpt-oss-20b` emitting **20× more output tokens**. Why so many? `gpt-oss-20b` is a reasoning model — most of those tokens are hidden chain-of-thought billed as output. One question burned 6,536 output tokens (73 s) to produce a ~150-token visible answer, and the size of that reasoning burst varied run to run. If Fireworks didn't bill reasoning tokens so cheaply, the cost advantage would shrink.
- **Latency is the real trade-off, not quality.** `gpt-4.1-mini` was consistently fast (max 2.8 s); `gpt-oss-20b`'s reasoning made latency spiky (median 1.8 s but a 73 s worst case). For a user-facing chat app, that p100 matters more than the median — exactly the throughput/latency consideration from Question #2.
- **Serverless rate limits bite under load.** The `endpoint_slammer` run saw 6 of 24 concurrent requests rejected with 429s on the serverless endpoint, and the eval pipeline itself hit an embeddings rate limit once (fixed with retries). At production concurrency you'd need a dedicated deployment — which flips the cost math from per-token to per-GPU-hour.
- **LangSmith instrumentation:** each provider traces to its own project — `s10-rag-fireworks` and `s10-rag-openai` at [smith.langchain.com](https://smith.langchain.com). Open a project → **Stats** to see token totals and latency percentiles, and set per-model prices under **Settings → Usage & Billing → Model pricing** to get the cost dashboards; the traces carry full token counts per run.

Reproduce with: `uv run python activity1/run_pipelines.py`, then `uv run --no-project activity1/eval_ragas.py`, then `uv run python activity1/analyze_costs.py` (see [`activity1/README.md`](./activity1/README.md)).

## Advanced Activity: Local Models

Swap out the Fireworks AI endpoints for **locally-running open-source models** using [Ollama](https://ollama.com/) or another local inference server of your choice. Run both your embedding model and your chat model locally, and rebuild the RAG pipeline on top of them.

- Compare quality and latency between the local setup and your Fireworks AI hosted endpoint.
- Reflect: what are the trade-offs of local models vs. managed endpoints in a production setting?

Include your findings and a demo in your Loom video.
