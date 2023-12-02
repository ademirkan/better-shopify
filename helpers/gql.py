
import os
import requests
from dotenv import load_dotenv

# DUBLEXO_DEMO_QUERY = {
#     "input": {
#         "customProductType": "",
#         "descriptionHtml": "This is a product description in the form of descriptionHtml",
#         "metafields": [
#             {
#                 "key": "signature_variants",
#                 "namespace": "custom",
#                 "type": "json",
#                 "value": '[]',
#             }
#         ],
#         "options": ["Fabric", "Base"],
#         "title": "Dublexo Eik TEST TEST TEST",
#         "variants": [
#             {
#                 "compareAtPrice": "2000",
#                 "inventoryItem": {"cost": "500", "tracked": True},
#                 "inventoryQuantities": [
#                     {
#                         "availableQuantity": 1000,
#                         "locationId": "gid://shopify/Location/85320270117",
#                     }
#                 ],
#                 "metafields": [
#                     {
#                         "key": "variant_images",
#                         "namespace": "custom",
#                         "type": "json",
#                         "value": "",   
#                     }
#                 ],
#                 "options": ["White", "Wood"],
#                 "position": 1,  # make defaults come before customs
#                 "price": "1850",
#                 "requiresShipping": True,
#                 "sku": "sku-1",
#                 "title": "Dublexo Eik Red Wood",
#                 "weight": 1000,
#                 "weightUnit": "POUNDS",
#             },
#             {
#                 "compareAtPrice": "2001",
#                 "inventoryItem": {"cost": "500", "tracked": True},
#                 "inventoryQuantities": [
#                     {
#                         "availableQuantity": 1000,
#                         "locationId": "gid://shopify/Location/85320270117",
#                     }
#                 ],
#                 "metafields": [
#                     {
#                         "key": "variant_media",
#                         "namespace": "custom",
#                         "type": "json",
#                         "value": "", 
#                     }
#                 ],
#                 "options": ["Gray", "Dark wood"],
#                 "position": 1,  # make defaults come before customs
#                 "price": "1850",
#                 "requiresShipping": True,
#                 "sku": "test1",
#                 "title": "Dublexo Eik darkwood",
#                 "weight": 1000,
#                 "weightUnit": "POUNDS",
#             },
#         ],
#         "vendor": "Innovation",
#     },  
#     "media": construct_media(DUBLEXO_DEMO_CONFIG)
# }

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
                variants(first: 250) {
                    edges {
                        node {
                            id
                            title
                            price
                            inventoryQuantity
                            sku
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
