import requests
import json

# Shopify store details
SHOPIFY_STORE_URL = "https://dc2434-2.myshopify.com/admin/api/2023-10/graphql.json"
SHOPIFY_ACCESS_TOKEN = "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"


# Function to run GraphQL queries
def run_query(query, variables={}):
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


def extract_options(variants_dict):
    return [{"name": key.capitalize()} for key in variants_dict.keys()]


# Your product data
products = [
    {
        "shopify_product_id": 91230412,
        "product_name": "Dublexo Sofa II",
        "variants": {
            "color": [512, 561, 517],
            "size": ["full", "queen"],
            "legs": ["wood", "steel"],
        },
        "for_sale": [
            {
                "config": {"color": 512, "size": "full", "legs": "wood"},
                "price": 1849,
                "shipping_range": [7, 14],
            },
            {
                "config": {"color": 517, "size": "queen", "legs": "steel"},
                "price": 1800,
                "shipping_range": [7, 14],
            },
            {
                "config": {"color": 512, "size": "queen", "legs": "steel"},
                "price": 2000,
                "shipping_range": [21, 28],
            },
        ],
    },
    {
        "shopify_product_id": 99129314,
        "product_name": "Dublexo Sofa III",
        "variants": {
            "color": [512, 561, 517],
            "size": ["full", "queen"],
            "legs": ["wood", "steel"],
        },
        "for_sale": [
            {
                "config": {"color": 512, "size": "full", "legs": "wood"},
                "price": 1849,
                "shipping_range": [7, 14],
            },
            {
                "config": {"color": 517, "size": "queen", "legs": "steel"},
                "price": 1800,
                "shipping_range": [7, 14],
            },
            {
                "config": {"color": 512, "size": "queen", "legs": "steel"},
                "price": 2000,
                "shipping_range": [21, 28],
            },
        ],
    },
]

# Creating a product with options and variants
for product in products:
    product_query = """
    mutation productCreate($input: ProductInput!) {
        productCreate(input: $input) {
        product {
          id
          title
          options {
            name
            values
          }
        }
        userErrors {
          field
          message
        }
      }
    }
    """

    product_options = ["Color", "Size", "Legs"]
    product_query_config = {
        "input": {
            # "customProductType": "",
            # "descriptionHtml": "",
            # "metafields": [
            #     {
            #         "description": "",
            #         "id": "",
            #         "key": "",
            #         "namespace": "",
            #         "type": "",
            #         "value": "",
            #     }
            # ],
            # "options": [""],
            # "title": "",
            "variants": [
                {
                    # "compareAtPrice": "",
                    # "inventoryItem": {"cost": "", "tracked": True},
                    # "inventoryQuantities": [{"availableQuantity": 1000, "locationId": "85320270117"}],
                    # "mediaId": "",
                    # "mediaSrc": [""],
                    # "metafields": [
                    #     {
                    #         "description": "",
                    #         "id": "",
                    #         "key": "",
                    #         "namespace": "",
                    #         "type": "",
                    #         "value": "",
                    #     }
                    # ],
                    # "options": [""],
                    # "position": 1,    # make defaults come before customs
                    # "price": "",
                    # "privateMetafields": [
                    #     {
                    #         "key": "",
                    #         "namespace": "",
                    #         "owner": "",
                    #         "valueInput": {"value": "", "valueType": ""},
                    #     }
                    # ],
                    # "requiresShipping": true,
                    # "sku": "",
                    # "title": "",
                    # "weight": 1.1 ,
                    # "weightUnit": "lbs",
                },
            ],
            # "vendor": "",
        },
        # "media": [{"alt": "", "mediaContentType": "", "originalSource": ""}],
    }

    product_response = run_query(
        product_query, {"input": product_query_config["input"]}
    )
    print(product_response)
    product_id = product_response["data"]["productCreate"]["product"]["id"]
