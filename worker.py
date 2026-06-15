# worker.py

import json
from redis_client import redis_client
from agent import handle_event
from shopify_client import update_product_description
from twilio_client import send_sms
import time
#from db_logger import log_agent_action


print("🟢 Worker started. Waiting for events...")
print("Redis ping:", redis_client.ping())


while True:
	queue, raw_event = redis_client.brpop("events")
	payload = json.loads(raw_event)

	# ✅ TRUST the event
	event_type = payload["event_type"]
	event_data = payload["event_data"]

	print("📥 Received event:", event_type)
	print("🧠 Sending event to agent...")
	output = handle_event(event_type, event_data)
	print("✅ Agent returned response")

	# ✅ GLOBAL decision logging (Phase 1 + Phase 2)
	'''log_agent_action(
		action=output.get("action"),
		details=f"{event_type} | {event_data.get('order_id') or event_data.get('product_id')}",
		result=output
	)'''
	DEV_MODE = False

	# ✅ ROUTE BY ACTION (never by assumptions)
	if output["action"] == "GENERATE_PRODUCT_DESCRIPTION":
		product_id = event_data.get("id")  # Shopify product ID
		if not product_id:
			print("⚠️ Missing product_id, skipping Shopify update")
			continue

		if DEV_MODE:
			print("🧪 DEV MODE — skipping Shopify update")
			print("🆔 Product ID:", product_id)
			print("📝 Description:")
			print(output["response"])
		else:
			update_product_description(
				product_id=product_id,
				description_html=output["response"]
			)

	elif output["action"] == "SEND_ORDER_NOTIFICATION":
		if DEV_MODE:
			print("🧪 DEV MODE — SMS skipped")
			print("📩 SMS would be sent:", output["response"]["message"])
		else:
			time.sleep(100)
			print("📩 SMS would be sent:", output["response"]["message"])
			send_sms(
			to=event_data["customer_phone"],
			message=output["response"]["message"]
			)
			print("📩 SMS sent successfully")

	else:
		print("⚠️ Unknown action:", output["action"])

