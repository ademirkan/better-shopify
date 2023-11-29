import json
from helpers import run_shopify_query
from helpers import CREATE_PRODUCT_QUERY

# Upload catalog to Shopify
def create_shopify_catalog(catalog_json, media_json):
    for product_key in catalog_json:
        # Create product
        product_config = catalog_json[product_key]
        product_query_input = construct_product_query_input(product_config, media_json[product_key])
        product_response = run_shopify_query(CREATE_PRODUCT_QUERY, product_query_input)
        
        # Error handling
        if product_response["data"]["productCreate"]["userErrors"]:
            print("Error creating product: " + product_key)
            print(product_response["data"]["productCreate"]["userErrors"])
            return


# Construct the product query input
def construct_product_query_input(product_config, media_json):
    output = {"input": {}, "media": []}

    # Add input fields
    output["input"]["title"] = product_config["TITLE"]
    output["input"]["descriptionHtml"] = product_config["DESCRIPTION"]
    output["input"]["vendor"] = product_config["VENDOR"]
    output["input"]["options"] = product_config["OPTIONS"]
    output["input"]["metafields"] = [
        {
            "key": "signature_variants",
            "namespace": "custom",
            "type": "json",
            "value": '[]',
        },
        {
            "key": "media_manifesto",
            "namespace": "custom",
            "type": "json",
            "value": json.dumps(media_json),
        },

    ]
    output["input"]["variants"] = []

    for variant_key in product_config["VARIANTS"]:
        variant = {}
        variant_config = product_config["VARIANTS"][variant_key]
        variant["title"] = variant_config["TITLE"]
        variant["price"] = variant_config["PRICE"]
        variant["compareAtPrice"] = variant_config["COMPARE_AT_PRICE"]
        variant["sku"] = variant_config["SKU"]
        variant["weight"] = variant_config["LBS"]
        variant["weightUnit"] = "POUNDS"
        variant["requiresShipping"] = True
        variant["options"] = variant_config["OPTIONS"]
        variant["position"] = 1
        variant["inventoryItem"] = {
            "cost": variant_config["COST"],
            "tracked": True
        }
        variant["inventoryQuantities"] = [
            {
                "availableQuantity": 100,
                "locationId": "gid://shopify/Location/85320270117",
            }
        ]
        output["input"]["variants"].append(variant)

    return output