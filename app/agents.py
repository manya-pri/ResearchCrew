import json
import os
import re

from tavily import TavilyClient
from .llm import ask


def parse_json(text, opener, closer, fallback):
    """Extract JSON from the LLM response."""
    match = re.search(
        re.escape(opener) + r".*?" + re.escape(closer),
        text,
        re.S
    )

    if not match:
        return fallback

    try:
        return json.loads(match.group(0))
    except json.JSONDecodeError:
        return fallback


# AGENT 1: PLANNER
def planner(state):
    text, used = ask(
        state,
        "You are a research planner. Reply with ONLY a JSON list of "
        "3 short web-search questions.",
        f"Topic: {state['topic']}"
    )

    questions = parse_json(
        text, "[", "]", [state["topic"]]
    )[:3]

    return {
        "questions": questions,
        "tokens_used": state["tokens_used"] + used,
        "trace": state["trace"] + [
            f"Planner created {len(questions)} questions"
        ]
    }


# AGENT 2: RESEARCHER
def researcher(state):
    client = TavilyClient(
        api_key=os.getenv("TAVILY_API_KEY")
    )

    findings = []
    tokens = state["tokens_used"]

    for question in state["questions"]:

        results = client.search(
            question,
            max_results=3
        ).get("results", [])

        context = "\n".join(
            f"- {r.get('content', '')[:500]}"
            for r in results
        )

        sources = [
            r["url"] for r in results if r.get("url")
        ]

        summary, used = ask(
            {"tokens_used": tokens},
            "Summarise the notes in 3-4 factual sentences. "
            "Use only the notes. If there is insufficient evidence, "
            "say so.",
            f"Question: {question}\nNotes:\n{context}"
        )

        tokens += used

        findings.append({
            "question": question,
            "summary": summary,
            "sources": sources
        })

    return {
        "findings": findings,
        "tokens_used": tokens,
        "trace": state["trace"] + [
            f"Researcher collected {len(findings)} findings"
        ]
    }


# AGENT 3: WRITER
def writer(state):
    notes = "\n\n".join(
        f"Question: {f['question']}\n"
        f"Answer: {f['summary']}\n"
        f"Sources: {', '.join(f['sources'])}"
        for f in state["findings"]
    )

    feedback = state.get("feedback", "")

    text, used = ask(
        state,
        "You are a professional research report writer. "
        "Write a clear Markdown report with a title, "
        "introduction, sections, conclusion and Sources list. "
        "Use only the research notes. Do not invent facts or sources.",
        f"Topic: {state['topic']}\n\n"
        f"Research notes:\n{notes}\n\n"
        f"Reviewer feedback: {feedback}"
    )

    return {
        "draft": text,
        "revisions": state["revisions"] + 1,
        "tokens_used": state["tokens_used"] + used,
        "trace": state["trace"] + [
            f"Writer created draft #{state['revisions'] + 1}"
        ]
    }


# AGENT 4: CRITIC
def critic(state):
    text, used = ask(
        state,
        "You are a strict research report reviewer. "
        "Evaluate accuracy, clarity and source usage. "
        'Reply ONLY with JSON: {"score": 8, "feedback": "..."}. '
        "Score must be between 1 and 10.",
        state["draft"]
    )

    result = parse_json(
        text,
        "{",
        "}",
        {"score": 7, "feedback": "Review completed."}
    )

    score = max(1, min(10, int(result.get("score", 7))))
    feedback = str(result.get("feedback", ""))

    return {
        "score": score,
        "feedback": feedback,
        "tokens_used": state["tokens_used"] + used,
        "trace": state["trace"] + [
            f"Critic evaluated report: {score}/10"
        ]
    }
