import json
from .schemas import RequestContext
from .config import settings
from openai import OpenAI

client = OpenAI(api_key=settings.OPENAI_API_KEY)


def summarize_intent(
    nl_policy: str,
    context: RequestContext,
    model: str = "gpt-4o-mini",
) -> str:
    """
    Summarization/confirmation agent.
    Produces a short human-friendly summary of the user's intention and provided context.
    No strict schema here — open-ended natural output.
    """
    system = """
You are the Confirmation Agent for a firewall policy assistant.

Your job is to:
1) First, summarize the CONTEXT the user provided (network description, objects, zones, etc.) in simple, clear language.
2) Then, summarize what the USER IS ASKING FOR as a firewall policy intent, also in simple, clear language.
3) At the end, explicitly ask the user: "Is this what you meant?"

Constraints:
- Do NOT build or describe firewall rules.
- Do NOT output JSON or any technical schema.
- Do NOT invent additional context that was not provided.
- The final sentence must be a confirmation question to the user.
"""

    user_msg = {
        "nl_policy": nl_policy,
        "context": {
            "description": context.description,
            "details": context.details,
        }
    }

    resp = client.chat.completions.create(
        model=model,
        messages=[
            {"role": "system", "content": system},
            {"role": "user", "content": json.dumps(user_msg)}
        ]
    )

    return resp.choices[0].message.content
