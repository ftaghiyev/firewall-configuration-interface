
import os
import json
from typing import Any, Dict

from openai import OpenAI

from .prompts import RESOLVER_SYSTEM_PROMPT, IR_BUILDER_SYSTEM_PROMPT
from .schemas import ResolverOutput, IRBuilderOutput
from ..config import settings


client = OpenAI(api_key=settings.OPENAI_API_KEY)


def summarize_intent(
    nl_policy: str,
    context: Dict[str, Any],
    model: str = "gpt-4o-mini",
) -> str:
    """
    Summarization/confirmation agent.
    Produces a short human-friendly summary of the user's intention and provided context.
    No strict schema here — open-ended natural output.
    """
    system = """
You are the Confirmation Agent for a firewall policy assistant.

Your tasks:
1) First, summarize the CONTEXT the user provided (network description, objects, zones, etc.) using clear, simple language.
2) Then summarize WHAT YOU ARE ASKING FOR — always address the user directly using “you”, never “the user”, “they”, or third-person phrasing.
3) End by telling them that you will begin building the firewall rules based on their intent.

Communication Requirements:
- ALWAYS speak directly to the user (“you are asking…”, “you want…”).
- NEVER use third-person phrasing like “the user wants”, “the user asked”.
- Do NOT generate or describe firewall rules.
- Do NOT output JSON, XML, or structured schemas.
- Do NOT invent context that was not explicitly provided.

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

    return resp.choices[0].message.content



def resolve_policy(nl_policy: str, context: dict, model: str = "gpt-4o-mini") -> ResolverOutput:
    response = client.responses.parse(
        model=model,
        input=[
            {"role": "system", "content": RESOLVER_SYSTEM_PROMPT},
            {
                "role": "user",
                "content": json.dumps({
                    "nl_policy": nl_policy,
                    "context": context,
                }),
            },
        ],
        text_format=ResolverOutput,
    )

    return response.output_parsed 


def build_ir(resolver_output: ResolverOutput, context: dict, model: str = "gpt-4o-mini") -> IRBuilderOutput:
    response = client.responses.parse(
        model=model,
        input=[
            {"role": "system", "content": IR_BUILDER_SYSTEM_PROMPT},
            {
                "role": "user",
                "content": json.dumps({
                    "resolver": resolver_output.model_dump(),
                    "context": context,
                }),
            },
        ],
        text_format=IRBuilderOutput,
    )

    return response.output_parsed 