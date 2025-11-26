import os
import json
from typing import Any, Dict
from .config import settings
from openai import OpenAI

client = OpenAI(api_key=settings.OPENAI_API_KEY)


def summarize_intent(
    nl_policy: str,
    context: Dict[str, Any],
    model: str = "gpt-4o-mini",
) -> str:
    """
    Summarization/confirmation agent.
    Produces a short human-friendly summary of the user's intention.
    No strict schema here — open-ended natural output.
    """
    system = """
You are the Confirmation Agent. Your job is to summarize the user's firewall
policy intent in simple, clear language. Do NOT build rules. Do NOT extract
technical fields. Just describe what the user wants in no more than 5 sentences.
"""
    user_msg = {
        "nl_policy": nl_policy,
        "context": context
    }

    resp = client.chat.completions.create(
        model=model,
        messages=[
            {"role": "system", "content": system},
            {"role": "user", "content": json.dumps(user_msg)}
        ]
    )

    return resp.choices[0].message["content"]
