import os
import requests
from dotenv import load_dotenv
from twilio_client import send_sms

# Load .env
load_dotenv()

STORE_HANDLE = os.getenv("SHOPIFY_STORE_HANDLE")
ACCESS_TOKEN = os.getenv("SHOPIFY_ACCESS_TOKEN")
API_VERSION = os.getenv("SHOPIFY_API_VERSION", "2024-01")
TWILIO_TO_NUMBER = os.getenv("TWILIO_TO_NUMBER")

BASE_URL = (
    f"https://{STORE_HANDLE}.myshopify.com/admin/api/{API_VERSION}"
)

HEADERS = {
    "X-Shopify-Access-Token": ACCESS_TOKEN,
    "Content-Type": "application/json",
}

def trigger_theme_switch(target_theme_name):
    print(f"--- Connecting to {STORE_HANDLE} ---")

    r = requests.get(f"{BASE_URL}/themes.json", headers=HEADERS)

    if r.status_code != 200:
        print(f"Connection Failed! Status Code: {r.status_code}")
        print(f"Response: {r.text}")
        return

    themes = r.json().get("themes", [])

    for t in themes:
        print(f"ID: {t['id']} | Name: {t['name']} | Role: {t['role']}")

    theme_id = next(
        (t["id"] for t in themes if t["name"].lower() == target_theme_name.lower()),
        None,
    )

    if not theme_id:
        print(f"No match found for '{target_theme_name}'")
        return

    payload = {"theme": {"id": theme_id, "role": "main"}}

    response = requests.put(
        f"{BASE_URL}/themes/{theme_id}.json",
        json=payload,
        headers=HEADERS,
    )

    if response.status_code == 200:
        print("SUCCESS: Theme changed.")
    else:
        print(f"FAILED: {response.status_code}")
        print(response.text)
