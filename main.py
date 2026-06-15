import json
import uvicorn
from fastapi import FastAPI, Request
from redis_client import redis_client

app = FastAPI(title="Shopify AI Agent Core")


@app.post("/agent/event")
async def agent_event(request: Request):
    raw_payload = await request.json()
    print("\n====== RAW SHOPIFY PAYLOAD ======")
    print(json.dumps(raw_payload, indent=2))
    print("==================================\n")
    topic = request.headers.get("X-Shopify-Topic")

    # 🔎 Normalize event types
    if topic == "products/create":
        event_type = "PRODUCT_UPLOADED"

    elif topic == "orders/updated":
        event_type = "ORDER_STATUS_CHANGED"

    else:
        print("⚠️ Unknown Shopify topic:", topic)
        return {"status": "ignored"}

    wrapped_event = {
        "event_type": event_type,
        "event_data": raw_payload
    }
    print(wrapped_event)
    redis_client.lpush("events", json.dumps(wrapped_event))

    return {"status": "accepted"}

# dev_routes.py or inside main app

@app.post("/dev/product")
def dev_product(payload: dict):
    """
    Simulate Shopify products/create webhook
    """
    redis_client.lpush("events", json.dumps({
        "event_type": "PRODUCT_UPLOADED",
        "event_data": payload
    }))
    return {"status": "queued", "payload": payload}
    
@app.post("/dev/order")
def dev_order(payload: dict):
    """
    Simulate ORDER_STATUS_CHANGED webhook (DEV ONLY)
    """
    redis_client.lpush("events", json.dumps({
        "event_type": "ORDER_STATUS_CHANGED",
        "event_data": payload
    }))
    return {
        "status": "queued",
        "event_type": "ORDER_STATUS_CHANGED",
        "event_data": payload
    }

if __name__ == "__main__":
    uvicorn.run(app, host="0.0.0.0", port=8001)
