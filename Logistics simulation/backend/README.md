EcoptiAI Logistics API

Run locally:

1. Install deps:
   python -m venv .venv
   . .venv/bin/activate
   pip install -r requirements.txt

2. Set DB path (optional):
   export ECOPTI_DB_PATH=/home/favas/EcoptiAI/database/ecoptiai.db

3. Start server:
   uvicorn app:app --host 0.0.0.0 --port 8000 --reload

Webhook endpoint:
- POST /webhooks/order_created

Dashboard endpoints:
- GET /shipments
- POST /update_status  {"order_id": "...", "status": "Delayed"}
