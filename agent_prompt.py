# agent_prompt.py

import json
from langchain_core.prompts import PromptTemplate
from rag_core import retrieve_similar_products


# =====================================================
# PROMPT TEMPLATE
# =====================================================
prompt_template = PromptTemplate(
	input_variables=["event_type", "event_data", "retrieved_context"],
	template="""\
You are a JSON-only automation agent.
Output EXACTLY one JSON object. Nothing else.
No markdown. No code blocks. No backticks. No explanations. No examples. No questions.
Stop immediately after the closing brace.

Event Type:
{event_type}

Current Event Type is {event_type}.
Ignore all other event types. 

Event Data:
{event_data}

Reference Description (STYLE & STRUCTURE TO FOLLOW):
{retrieved_context}

Rules:
- Use only the information provided above.
- Do not invent details.
- If information is missing, be conservative.

Actions:
- GENERATE_PRODUCT_DESCRIPTION
- SEND_ORDER_NOTIFICATION
- NO_ACTION

If event_type is PRODUCT_UPLOADED:
- Generate a product description that mirrors the sentence structure, tone, and feature density of the reference description.
- Adapt it naturally to the new product title.
- You may generate plausible but realistic product features appropriate for the product type.
- Do not mention vendor or brand.
- Keep similar rhythm and sentence count.

If event_type is ORDER_STATUS_CHANGED:
- Send an SMS ONLY if new_status is Delayed and previous_status was not Delayed.
- Otherwise return NO_ACTION.

JSON formats:
Product: {{ "action": "GENERATE_PRODUCT_DESCRIPTION", "reasoning": "brief", "response": "description text" }} Order with SMS: {{ "action": "SEND_ORDER_NOTIFICATION", "reasoning": "brief", "response": {{ "message": "sms text" }} }} No action: {{ "action": "NO_ACTION", "reasoning": "brief" }}

Now output the single correct JSON object for the event type {event_type} and nothing else
""" 
)

# =====================================================
# PROMPT BUILDER
# =====================================================
def build_prompt(inputs: dict) -> str:
    event_type = inputs["event_type"]
    event_data = inputs["event_data"]

    # -------- RAG --------
    results = retrieve_similar_products(
        event_data.get("product_name", "")
    )

    if results:
        retrieved_context = "\n".join(
            f"- {r['product_name']}: {r['description']} "
            f"(similarity {r['similarity_score']:.2f})"
            for r in results
        )
    else:
        retrieved_context = "No relevant products found."

    return prompt_template.format(
        event_type=event_type,
        event_data=json.dumps(event_data, indent=2),
        retrieved_context=retrieved_context
    )

