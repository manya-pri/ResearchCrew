from dotenv import load_dotenv

load_dotenv()

from app.graph import run_research

TOPICS = [
    "How do vision transformers work?",
    "What is retrieval augmented generation?",
    "Explain gradient descent for beginners",
    "What are the risks of AI agents in production?",
    "How does LangGraph differ from LangChain?"
]

results = []

for topic in TOPICS:
    result = run_research(topic)
    results.append(result)

    print(
        f"Status: {result['status']} | "
        f"Score: {result['score']} | "
        f"Tokens: {result['tokens_used']} | "
        f"Time: {result['seconds']}s"
    )

success = sum(
    1 for result in results
    if result["status"] == "ok"
)

print("\n========== EVALUATION ==========")
print(f"Success: {success}/{len(TOPICS)}")

print(
    "Average tokens:",
    sum(r["tokens_used"] for r in results) // len(results)
)

print(
    "Average time:",
    round(sum(r["seconds"] for r in results) / len(results), 2),
    "seconds"
)
