# logistics_api.py
print("🔥 LOADED logistics_api.py FROM:", __file__)

from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware
from pydantic import BaseModel
import json
from redis_client import redis_client

app = FastAPI()

# 🔓 Allow frontend to talk to backend
app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],  # dev only
    allow_methods=["*"],
    allow_headers=["*"],
)

# Fake in-memory orders for now
ORDERS = {
    "ORD-001": {
        "order_id": "ORD-001",
        "product_name": "LED High Tops",
        "customer_name": "John Doe",
        "customer_phone": "+91XXXXXXXXXX",
        "status": "In Transit",
        "eta": "2025-01-20T14:30:00"
    }
}

class StatusUpdate(BaseModel):
    status: str

@app.get("/orders")
def get_orders():
    return list(ORDERS.values())

@app.post("/orders/{order_id}/status")
def update_status(order_id: str, payload: StatusUpdate):
    order = ORDERS.get(order_id)
    if not order:
        return {"error": "Order not found"}

    prev = order["status"]
    new = payload.status
    order["status"] = new
    
    print("BACKEND redis ping:", redis_client.ping())
    print("BACKEND redis keys BEFORE:", redis_client.keys("*"))

    
    # Emit Redis event
    redis_client.lpush("events", json.dumps({
        "event_type": "ORDER_STATUS_CHANGED",
        "event_data": {
            "order_id": order_id,
            "customer_name": order["customer_name"],
            "customer_phone": order["customer_phone"],
            "previous_status": prev,
            "new_status": new
        }
    }))
    print("BACKEND redis keys AFTER:", redis_client.keys("*"))

    return {"ok": True}

