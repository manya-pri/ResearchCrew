import os
import time
from dotenv import load_dotenv
from langchain_groq import ChatGroq

load_dotenv()

MODEL_NAME = os.getenv("MODEL_NAME", "openai/gpt-oss-120b")
TOKEN_BUDGET = int(os.getenv("TOKEN_BUDGET", "40000"))

class BudgetExceeded(Exception):
    pass

_llm = None

def get_llm():
    global _llm

    if _llm is None:
        _llm = ChatGroq(
            model=MODEL_NAME,
            temperature=0.2
        )

    return _llm

def ask(state, system, user):
    if state["tokens_used"] >= TOKEN_BUDGET:
        raise BudgetExceeded(
            f"Token budget {TOKEN_BUDGET} reached"
        )

    last_error = None

    for attempt in range(3):
        try:
            response = get_llm().invoke([
                ("system", system),
                ("human", user)
            ])

            usage = response.usage_metadata or {}
            tokens = usage.get("total_tokens", 0)

            return response.content, tokens

        except Exception as error:
            last_error = error
            time.sleep(2 * (attempt + 1))

    raise RuntimeError(
        f"LLM failed after 3 tries: {last_error}"
    )
