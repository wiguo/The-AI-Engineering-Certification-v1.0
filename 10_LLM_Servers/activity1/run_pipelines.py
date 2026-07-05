"""Activity 1, phase 1: run the same RAG pipeline on two providers and capture results.

Providers:
- fireworks: qwen3-embedding-8b + gpt-oss-20b (the open-source stack from this session)
- openai:    text-embedding-3-small + gpt-4.1-mini

Both use identical chunks, prompt, and retriever settings so the comparison isolates
the provider. Each provider traces to its own LangSmith project so token usage and
cost can be compared in the LangSmith dashboards.

Run from 10_LLM_Servers/:  uv run python activity1/run_pipelines.py
"""

from __future__ import annotations

import json
import os
import time
from pathlib import Path

from dotenv import load_dotenv

load_dotenv(Path(__file__).resolve().parents[1] / ".env")

import tiktoken
from langchain_community.document_loaders import DirectoryLoader, PyMuPDFLoader
from langchain_core.tracers.context import tracing_v2_enabled
from langchain_core.prompts import ChatPromptTemplate
from langchain_openai import ChatOpenAI
from langchain_openai.embeddings import OpenAIEmbeddings
from langchain_qdrant import QdrantVectorStore

FIREWORKS_BASE_URL = "https://api.fireworks.ai/inference/v1"

HUMAN_TEMPLATE = (
    "\n#CONTEXT:\n{context}\n\nQUERY:\n{query}\n\n"
    "Use the provide context to answer the provided user query. "
    "Only use the provided context to answer the query. If you do not know the answer, "
    'or it\'s not contained in the provided context respond with "I don\'t know"'
)

PROVIDERS = {
    "fireworks": {
        "langsmith_project": "s10-rag-fireworks",
        "chat": dict(
            model="accounts/fireworks/models/gpt-oss-20b",
            openai_api_key=os.environ["FIREWORKS_API_KEY"],
            openai_api_base=FIREWORKS_BASE_URL,
        ),
        "embeddings": dict(
            model="accounts/fireworks/models/qwen3-embedding-8b",
            openai_api_key=os.environ["FIREWORKS_API_KEY"],
            openai_api_base=FIREWORKS_BASE_URL,
            check_embedding_ctx_length=False,
            dimensions=4096,
            max_retries=10,
        ),
    },
    "openai": {
        "langsmith_project": "s10-rag-openai",
        "chat": dict(model="gpt-4.1-mini"),
        "embeddings": dict(model="text-embedding-3-small"),
    },
}


def load_chunks() -> list:
    enc = tiktoken.encoding_for_model("gpt-4o")
    from langchain_text_splitters import RecursiveCharacterTextSplitter

    splitter = RecursiveCharacterTextSplitter(
        chunk_size=750, chunk_overlap=0, length_function=lambda t: len(enc.encode(t))
    )
    data_dir = Path(__file__).resolve().parents[1] / "data"
    documents = DirectoryLoader(
        str(data_dir), glob="**/*.pdf", loader_cls=PyMuPDFLoader
    ).load()
    return splitter.split_documents(documents)


def run_provider(name: str, cfg: dict, chunks: list, questions: list[dict]) -> list[dict]:
    store = QdrantVectorStore.from_documents(
        documents=chunks,
        embedding=OpenAIEmbeddings(**cfg["embeddings"]),
        location=":memory:",
        collection_name=f"activity1_{name}",
    )
    retriever = store.as_retriever()
    prompt = ChatPromptTemplate.from_messages([("human", HUMAN_TEMPLATE)])
    llm = ChatOpenAI(temperature=0, **cfg["chat"])

    rows = []
    for item in questions:
        q = item["question"]
        with tracing_v2_enabled(project_name=cfg["langsmith_project"]):
            t0 = time.perf_counter()
            docs = retriever.invoke(q)
            t_retrieve = time.perf_counter() - t0

            context = "\n\n".join(d.page_content for d in docs)
            t0 = time.perf_counter()
            msg = llm.invoke(prompt.format_messages(query=q, context=context))
            t_generate = time.perf_counter() - t0

        usage = msg.usage_metadata or {}
        rows.append(
            {
                "question": q,
                "ground_truth": item["ground_truth"],
                "answer": msg.content,
                "contexts": [d.page_content for d in docs],
                "input_tokens": usage.get("input_tokens", 0),
                "output_tokens": usage.get("output_tokens", 0),
                "retrieve_seconds": round(t_retrieve, 3),
                "generate_seconds": round(t_generate, 3),
            }
        )
        print(
            f"[{name}] {q[:60]}... "
            f"({usage.get('input_tokens', 0)} in / {usage.get('output_tokens', 0)} out, "
            f"{t_generate:.1f}s)"
        )
    return rows


def main() -> None:
    here = Path(__file__).resolve().parent
    questions = json.loads((here / "eval_questions.json").read_text(encoding="utf-8"))
    chunks = load_chunks()
    print(f"{len(chunks)} chunks loaded")

    results = {}
    for name, cfg in PROVIDERS.items():
        print(f"\n=== provider: {name} (LangSmith project: {cfg['langsmith_project']}) ===")
        results[name] = run_provider(name, cfg, chunks, questions)

    out = here / "results" / "pipeline_results.json"
    out.parent.mkdir(exist_ok=True)
    out.write_text(json.dumps(results, indent=2, ensure_ascii=False), encoding="utf-8")
    print(f"\nsaved -> {out}")


if __name__ == "__main__":
    main()
