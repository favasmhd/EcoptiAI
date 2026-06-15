# agent.py

from langchain_core.runnables import RunnableLambda

from agent_prompt import build_prompt
from llm_client import call_llm, parse_llm_output


# =====================================================
# LANGCHAIN RUNNABLES
# =====================================================

# Step 1: Build prompt (RAG + instructions)
prompt_runnable = RunnableLambda(build_prompt)


# Step 2: Call LLM and parse structured output
def llm_step(prompt_text: str) -> dict:
    print("🧠 Calling LLM...")
    raw_output = call_llm(prompt_text)
    print("🧠 LLM responded")
    print("🔎 RAW OUTPUT:")
    print(raw_output)
    return parse_llm_output(raw_output)


llm_runnable = RunnableLambda(llm_step)

# Full pipeline
pipeline = prompt_runnable | llm_runnable


# =====================================================
# CONTEXT ENRICHMENT
# =====================================================
def enrich_context(event_type: str, event_data: dict) -> dict:
    enriched = dict(event_data)

    if event_type == "ORDER_STATUS_CHANGED":
        enriched["severity"] = (
            "high" if event_data.get("delay_minutes", 0) > 120 else "medium"
        )

        enriched["customer_risk"] = (
            "repeat_issue"
            if event_data.get("customer_history", 0) >= 2
            else "normal"
        )

    return enriched


# =====================================================
# PUBLIC AGENT ENTRY POINT
# =====================================================
def handle_event(event_type: str, event_data: dict) -> dict:
    """
    Main entry point for the agent.
    Used by tests and FastAPI webhook.
    """
    enriched_data = enrich_context(event_type, event_data)

    return pipeline.invoke({
        "event_type": event_type,
        "event_data": enriched_data
    })
    
def execute_action(decision: dict, event_data: dict):
    action = decision["action"]

    if action == "SEND_ORDER_NOTIFICATION":
        # call sms api
        print("📩 Sending SMS")

    elif action == "ISSUE_COUPON":
        print("🎁 Issuing coupon")

    elif action == "ESCALATE_SUPPORT":
        print("📞 Escalating to support")

    elif action == "GENERATE_PRODUCT_DESCRIPTION":
        print("📝 Saving generated description")

    return decision
