"""Activity 1: exercise the helpfulness loop on dev (Studio) and production servers.

Sends one query expected to PASS the helpfulness check and one expected to FAIL
(and therefore loop until the message-limit guard fires) to both servers:
- langgraph dev  (http://localhost:2024, traces -> s09-dev-studio)
- langgraph up   (http://localhost:8123, traces -> s09-production)
"""

import asyncio

from langgraph_sdk import get_client

SERVERS = {
    "dev (Studio)": "http://localhost:2024",
    "production (Docker)": "http://localhost:8123",
}

QUERIES = {
    "PASS (first try)": "How often should senior cats see the vet?",
    "RETRY then PASS": "What will the weather be in Zurich exactly 37 days from now at 3:14 pm?",
    "FAIL (loop limit)": "Summarize page 37 of the PDF I uploaded to you yesterday.",
}


async def run(url: str, label: str, kind: str, question: str) -> None:
    client = get_client(url=url)
    verdicts = []
    print(f"\n=== [{label}] {kind}: {question}")
    async for chunk in client.runs.stream(
        None,
        "agent_with_helpfulness",
        input={"messages": [{"role": "human", "content": question}]},
        stream_mode="updates",
    ):
        if chunk.event != "updates" or not isinstance(chunk.data, dict):
            continue
        for node, update in chunk.data.items():
            for msg in (update or {}).get("messages", []):
                content = msg.get("content") or ""
                if isinstance(content, str) and content.startswith("HELPFULNESS:"):
                    verdicts.append(content)
                    print(f"  {node}: {content}")
    print(f"  -> verdicts: {verdicts} ({len(verdicts)} judge round(s))")


async def main() -> None:
    for label, url in SERVERS.items():
        for kind, question in QUERIES.items():
            await run(url, label, kind, question)


asyncio.run(main())
