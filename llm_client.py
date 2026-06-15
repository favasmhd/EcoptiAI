from groq import Groq
from dotenv import load_dotenv
import os

# Load variables from .env
load_dotenv()

client = Groq(
    api_key=os.getenv("GROQ_API_KEY")
)

MODEL_NAME = "llama-3.1-8b-instant"

'''DEMO_MODE = False  # <-- turn ON for recording

# ── MOCK LLM ──────────────────────────────────────────────────────────────────
# Set USE_MOCK_LLM = True to use the mock instead of the real LLM.
# Delete this entire block (and flip the flag) to remove it cleanly.
USE_MOCK_LLM = False

def _mock_call_llm(prompt_text: str, max_new_tokens: int = 512) -> str:
    """
    Mock LLM that returns hardcoded JSON responses based on keywords in the prompt.
    Safe to delete along with USE_MOCK_LLM without touching any other logic.
    """
    import json
    prompt_lower = prompt_text.lower()

    if "order" in prompt_lower or "notification" in prompt_lower or "delay" in prompt_lower:
        return json.dumps({
            "action": "SEND_ORDER_NOTIFICATION",
            "reasoning": "Received event that order is delayed",
            "response": {
                "message": "We are sorry for the delay, we are working on it."
            }
        })

    if "product" in prompt_lower or "description" in prompt_lower:
        return json.dumps({
            "action": "GENERATE_PRODUCT_DESCRIPTION",
            "reasoning": "Mock: detected product description request.",
            "response": "This is a mock product description."
        })

    return json.dumps({
        "action": "NO_ACTION",
        "reasoning": "Mock: no matching intent found."
    })
# ── END MOCK LLM ──────────────────────────────────────────────────────────────'''


def call_llm(prompt: str) -> str:
    response = client.chat.completions.create(
        model=MODEL_NAME,
        messages=[
            {
                "role": "user",
                "content": prompt
            }
        ],
        temperature=0.2,
        max_completion_tokens=300
    )

    return response.choices[0].message.content


def parse_llm_output(raw_text: str) -> dict:
    import json
    import re

    # Strip markdown code fences first
    cleaned = re.sub(r"```(?:json)?", "", raw_text).strip()

    def parse_error(reason):
        return {
            "action": "PARSE_ERROR",
            "reasoning": reason,
            "response": raw_text.strip()
        }

    try:
        data = json.loads(cleaned)
    except json.JSONDecodeError:
        candidates = re.findall(r"\{[\s\S]*\}", cleaned)
        data = None
        for block in reversed(candidates):
            try:
                parsed = json.loads(block)
                if (
                    isinstance(parsed, dict)
                    and "action" in parsed
                    and parsed["action"] in {
                        "GENERATE_PRODUCT_DESCRIPTION",
                        "SEND_ORDER_NOTIFICATION",
                        "NO_ACTION",
                    }
                ):
                    data = parsed
                    break
            except Exception:
                continue
        if data is None:
            return parse_error("No valid agent JSON found")

    action = data.get("action")
    reasoning = data.get("reasoning", "")
    response = data.get("response")

    if action == "GENERATE_PRODUCT_DESCRIPTION":
        if not isinstance(response, str):
            return parse_error("Product description response must be string")
        return {"action": action, "reasoning": reasoning, "response": response}

    if action == "SEND_ORDER_NOTIFICATION":
        if not isinstance(response, dict):
            return parse_error("Notification response must be object")
        if "message" not in response:
            return parse_error("Notification missing 'message'")
        return {"action": action, "reasoning": reasoning, "response": response}

    if action == "NO_ACTION":
        return {"action": action, "reasoning": reasoning}

    return parse_error(f"Unknown action: {action}")
