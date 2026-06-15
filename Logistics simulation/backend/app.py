import os
import sqlite3
from datetime import datetime, timedelta, timezone
from typing import List, Optional

from fastapi import FastAPI, HTTPException, Request
from fastapi.middleware.cors import CORSMiddleware
from pydantic import BaseModel

DB_PATH = os.getenv("ECOPTI_DB_PATH", "/home/favas/EcoptiAI/database/ecoptiai.db")

app = FastAPI(title="EcoptiAI Logistics API")

app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)


class Shipment(BaseModel):
    order_id: str
    product_name: str
    customer_name: str
    status: str
    eta: Optional[str] = None


class StatusUpdate(BaseModel):
    order_id: str
    status: str


def get_conn() -> sqlite3.Connection:
    conn = sqlite3.connect(DB_PATH)
    conn.row_factory = sqlite3.Row
    return conn


def init_db() -> None:
    with get_conn() as conn:
        conn.execute(
            """
            CREATE TABLE IF NOT EXISTS shipments (
                id INTEGER PRIMARY KEY AUTOINCREMENT,
                order_id TEXT UNIQUE,
                product_name TEXT,
                customer_name TEXT,
                status TEXT,
                eta TEXT,
                created_at DATETIME DEFAULT CURRENT_TIMESTAMP,
                updated_at DATETIME DEFAULT CURRENT_TIMESTAMP
            );
            """
        )


@app.on_event("startup")
async def startup() -> None:
    init_db()


def _parse_customer_name(payload: dict) -> str:
    customer = payload.get("customer") or {}
    first = (customer.get("first_name") or "").strip()
    last = (customer.get("last_name") or "").strip()
    if first or last:
        return (first + " " + last).strip()

    shipping = payload.get("shipping_address") or {}
    name = (shipping.get("name") or "").strip()
    if name:
        return name

    return "Unknown"


def _parse_product(payload: dict) -> tuple[str, Optional[str]]:
    line_items = payload.get("line_items") or []
    if line_items:
        item = line_items[0] or {}
        title = (item.get("title") or "").strip() or "Unknown Product"
        handle = (item.get("handle") or "").strip() or None
        return title, handle
    return "Unknown Product", None


def _parse_order_id(payload: dict) -> str:
    return (
        payload.get("name")
        or payload.get("order_number")
        or payload.get("id")
        or "unknown"
    )


def _default_eta_iso(days: int = 3) -> str:
    eta = datetime.now(timezone.utc) + timedelta(days=days)
    return eta.isoformat()


@app.get("/shipments", response_model=List[Shipment])
def list_shipments() -> List[Shipment]:
    with get_conn() as conn:
        rows = conn.execute(
            """
            SELECT order_id, product_name, customer_name, status, eta
            FROM shipments
            ORDER BY created_at DESC
            """
        ).fetchall()

    return [Shipment(**dict(row)) for row in rows]


@app.post("/update_status")
def update_status(payload: StatusUpdate):
    with get_conn() as conn:
        row = conn.execute(
            "SELECT id FROM shipments WHERE order_id = ?",
            (payload.order_id,),
        ).fetchone()

        if not row:
            raise HTTPException(status_code=404, detail="Order not found")

        conn.execute(
            """
            UPDATE shipments
            SET status = ?, updated_at = CURRENT_TIMESTAMP
            WHERE order_id = ?
            """,
            (payload.status, payload.order_id),
        )

    return {"ok": True}


@app.post("/webhooks/order_created")
async def webhook_order_created(request: Request):
    payload = await request.json()

    order_id = str(_parse_order_id(payload))
    product_name, product_handle = _parse_product(payload)
    customer_name = _parse_customer_name(payload)

    status = "On the Way"
    eta = _default_eta_iso(days=3)

    with get_conn() as conn:
        conn.execute(
            """
            INSERT INTO orders (order_id, product_handle, customer_name)
            VALUES (?, ?, ?)
            ON CONFLICT(order_id) DO UPDATE SET
                product_handle = excluded.product_handle,
                customer_name = excluded.customer_name
            """,
            (order_id, product_handle, customer_name),
        )

        conn.execute(
            """
            INSERT INTO shipments (order_id, product_name, customer_name, status, eta)
            VALUES (?, ?, ?, ?, ?)
            ON CONFLICT(order_id) DO UPDATE SET
                product_name = excluded.product_name,
                customer_name = excluded.customer_name,
                status = excluded.status,
                eta = excluded.eta,
                updated_at = CURRENT_TIMESTAMP
            """,
            (order_id, product_name, customer_name, status, eta),
        )

    return {"ok": True, "order_id": order_id}
