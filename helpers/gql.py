
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

# Shopify GraphQL API query for creating a product with media
CREATE_PRODUCT_QUERY = """
    mutation CreateProduct($input: ProductInput!, $media: [CreateMediaInput!]) {
        productCreate(input: $input, media: $media) {
        product {
          id
          title
          options {
            name
            values
          }
          media(first: 10) {
            nodes {
                alt
                mediaContentType
                preview {
                    status
                }
            }
        }
        }
        userErrors {
          field
          message
        }
      }
    }
    """

# Shopify GraphQL API query for creating a variant
CREATE_VARIANT_QUERY = """
  mutation productVariantCreate($input: ProductVariantInput!) {
    productVariantCreate(input: $input) {
      product {
        id
        title
      }
      productVariant {
        createdAt
        displayName
        id
        inventoryItem {
          unitCost {
            amount
          }
          tracked
        }
        inventoryPolicy
        inventoryQuantity
        price
        product {
          id
        }
        title
      }
      userErrors {
        field
        message
      }
    }
  }
"""
