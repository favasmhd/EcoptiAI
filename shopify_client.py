import os
import requests
from dotenv import load_dotenv

# Load environment variables from .env
load_dotenv()

STORE_HANDLE = os.getenv("SHOPIFY_STORE_HANDLE")
ACCESS_TOKEN = os.getenv("SHOPIFY_ACCESS_TOKEN")
API_VERSION = os.getenv("SHOPIFY_API_VERSION", "2024-01")  # Default if not set

BASE_URL = (
    f"https://{STORE_HANDLE}.myshopify.com/admin/api/{API_VERSION}"
)

HEADERS = {
    "X-Shopify-Access-Token": ACCESS_TOKEN,
    "Content-Type": "application/json",
}

# =====================================================
# THEME MANAGEMENT
# =====================================================

def switch_theme_by_name(theme_name: str) -> bool:
    """
    Publish a theme by its name.
    Requires scopes: read_themes, write_themes
    """

    resp = requests.get(f"{BASE_URL}/themes.json", headers=HEADERS)
    resp.raise_for_status()

    themes = resp.json().get("themes", [])

    theme_id = next(
        (t["id"] for t in themes if t["name"].lower() == theme_name.lower()),
        None
    )

    if not theme_id:
        raise ValueError(f"Theme '{theme_name}' not found")

    payload = {"theme": {"id": theme_id, "role": "main"}}

    publish_resp = requests.put(
        f"{BASE_URL}/themes/{theme_id}.json",
        json=payload,
        headers=HEADERS,
    )
    publish_resp.raise_for_status()

    return True


# =====================================================
# PRODUCT MANAGEMENT
# =====================================================

def update_product_description(
    product_id: str,
    description_html: str
) -> bool:
    """
    Update product description (body_html).
    Requires scopes: read_products, write_products
    """

    payload = {
        "product": {
            "id": product_id,
            "body_html": description_html
        }
    }

    resp = requests.put(
        f"{BASE_URL}/products/{product_id}.json",
        json=payload,
        headers=HEADERS,
    )
    resp.raise_for_status()

    return True

