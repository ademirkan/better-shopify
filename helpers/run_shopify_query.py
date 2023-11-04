import os
import requests
from dotenv import load_dotenv

# Environment variables
load_dotenv()
SHOPIFY_ACCESS_TOKEN = os.getenv("SHOPIFY_ACCESS_TOKEN")
SHOPIFY_STORE_URL = os.getenv("SHOPIFY_STORE_URL")


def run_shopify_query(query, variables={}):
    headers = {
        "Content-Type": "application/json",
        "X-Shopify-Access-Token": SHOPIFY_ACCESS_TOKEN,
    }
    response = requests.post(
        SHOPIFY_STORE_URL,
        json={"query": query, "variables": variables},
        headers=headers,
    )
    return response.json()
