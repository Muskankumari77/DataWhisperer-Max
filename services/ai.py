from __future__ import annotations

import os
import re

from openai import OpenAI


# ============================================================
# CODE GENERATION PROMPT
# ============================================================

SYSTEM_PROMPT = """You are DataWhisperer AI, a careful data analyst.

Given a pandas DataFrame named df and the user's question,
produce ONLY executable pandas/matplotlib analysis code.

IMPORTANT RULES:

1. The code must assign the final answer to a variable named result.
2. Use only columns that actually exist in the provided dataset.
3. Never fabricate values.
4. Prefer clear and robust pandas operations.
5. Handle missing values when relevant.
6. For grouped, categorical, or comparison questions, return a
   pandas DataFrame whenever possible instead of a Series.
7. Give the output human-readable column names.
8. Sort grouped results logically, usually from highest to lowest
   when the question asks for counts, totals, rankings, or most/least.
9. For a simple total, average, minimum, maximum, or single value,
   result can be a scalar.
10. For a chart, use matplotlib and leave the current figure open.
    The result variable should briefly describe the chart.
11. Do not import anything.
12. Do not read or write files.
13. Do not use network, shell, subprocess, eval, exec,
    functions, or classes.
14. Keep the generated code concise.
15. Return ONLY executable Python code. No markdown fences.
"""


# ============================================================
# EXPLANATION PROMPT
# ============================================================

EXPLANATION_PROMPT = """You are DataWhisperer AI, an intelligent
data analyst explaining an analysis result to a user.

The user asked a question about their dataset.

Your job is to explain the ACTUAL RESULT clearly and naturally.

Rules:

1. Answer the user's question directly.
2. Use ONLY the values present in the provided result.
3. Never invent, estimate, or assume values.
4. If the result is a grouped table, summarize the important
   findings clearly.
5. Mention the highest or lowest value when relevant.
6. For counts, totals, averages, rankings, comparisons, etc.,
   explain the result in simple business-friendly language.
7. Keep the answer concise: usually 1-3 sentences.
8. Do not mention Python, pandas, generated code, prompts,
   or internal processing.
9. Do not say "according to the data" repeatedly.
10. Do not create a markdown table.
11. Do not use emojis.
12. Return ONLY the natural-language answer.
"""


# ============================================================
# CLIENT
# ============================================================

def _client(provider: str):

    if provider == "groq":

        key = os.getenv("GROQ_API_KEY", "")

        if not key:
            raise RuntimeError(
                "GROQ_API_KEY is missing in .env"
            )

        return OpenAI(
            api_key=key,
            base_url="https://api.groq.com/openai/v1",
        )

    key = os.getenv("OPENAI_API_KEY", "")

    if not key:
        raise RuntimeError(
            "OPENAI_API_KEY is missing in .env"
        )

    return OpenAI(
        api_key=key,
    )


# ============================================================
# MODEL
# ============================================================

def _model(provider: str) -> str:

    if provider == "groq":

        return os.getenv(
            "GROQ_MODEL",
            "openai/gpt-oss-120b",
        )

    return os.getenv(
        "OPENAI_MODEL",
        "gpt-4o-mini",
    )


# ============================================================
# CLEAN GENERATED CODE
# ============================================================

def _clean_code(content: str) -> str:

    content = content.strip()

    # Remove opening markdown code fence
    content = re.sub(
        r"^```(?:python)?\s*",
        "",
        content,
        flags=re.I,
    )

    # Remove closing markdown code fence
    content = re.sub(
        r"\s*```$",
        "",
        content,
    )

    return content.strip()


# ============================================================
# GENERATE PANDAS ANALYSIS CODE
# ============================================================

def generate_code(
    question: str,
    context: str,
    provider: str,
) -> str:

    client = _client(provider)

    prompt = (
        f"DATASET CONTEXT:\n"
        f"{context}\n\n"
        f"USER QUESTION:\n"
        f"{question}"
    )

    response = client.chat.completions.create(
        model=_model(provider),
        temperature=0,
        max_tokens=1200,
        messages=[
            {
                "role": "system",
                "content": SYSTEM_PROMPT,
            },
            {
                "role": "user",
                "content": prompt,
            },
        ],
    )

    content = (
        response.choices[0].message.content
        or ""
    )

    return _clean_code(content)


# ============================================================
# EXPLAIN ACTUAL RESULT
# ============================================================

def explain_result(
    question: str,
    result_preview: str,
    provider: str,
) -> str:

    client = _client(provider)

    prompt = f"""
USER QUESTION:
{question}

ACTUAL ANALYSIS RESULT:
{result_preview}

Explain the actual result to the user now.
"""

    response = client.chat.completions.create(
        model=_model(provider),
        temperature=0.2,
        max_tokens=300,
        messages=[
            {
                "role": "system",
                "content": EXPLANATION_PROMPT,
            },
            {
                "role": "user",
                "content": prompt,
            },
        ],
    )

    answer = (
        response.choices[0].message.content
        or ""
    ).strip()

    return answer