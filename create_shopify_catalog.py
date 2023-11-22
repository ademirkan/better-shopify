from helpers import run_shopify_query
from helpers import CREATE_PRODUCT_QUERY
from helpers import CREATE_VARIANT_QUERY

def construct_product_query_input(product_config, media_json):
    output = {"input": {}, "media": []}

    # Add input fields
    output["input"]["title"] = product_config["TITLE"]
    output["input"]["descriptionHtml"] = product_config["DESCRIPTION"]
    output["input"]["vendor"] = product_config["VENDOR"]
    output["input"]["options"] = product_config["OPTIONS"]
    output["input"]["variants"] = []
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
            "value": media_json.dumps(),
        },

    ]

    return output

def construct_variant_query_input(product_id, variant_config):
    output = {"input": {}}

    # Add input fields
    output["input"]["productId"] = product_id
    output["input"]["title"] = variant_config["TITLE"]
    output["input"]["price"] = variant_config["PRICE"]
    output["input"]["compareAtPrice"] = variant_config["COMPARE_AT_PRICE"]
    output["input"]["sku"] = variant_config["SKU"]
    output["input"]["weight"] = variant_config["LBS"]
    output["input"]["weightUnit"] = "POUNDS"
    output["input"]["requiresShipping"] = True
    output["input"]["options"] = variant_config["OPTIONS"]
    output["input"]["position"] = 1
    output["input"]["inventoryItem"] = {
        "cost": variant_config["COST"],
        "tracked": True
    }
    output["input"]["inventoryQuantities"] = [
        {
            "availableQuantity": 1000,
            "locationId": "gid://shopify/Location/85320270117",
        }
    ]

    return output

# Upload catalog to Shopify
def create_shopify_catalog(catalog_json, media_json):
    for product_key in catalog_json:
        # Create product
        product_config = catalog_json[product_key]
        product_query_input = construct_product_query_input(product_config, media_json[product_key])
        product_response = run_shopify_query(CREATE_PRODUCT_QUERY, product_query_input)

        # Error handling
        if product_response["productCreate"]["userErrors"]:
            print("Error creating product: " + product_key)
            print(product_response["productCreate"]["userErrors"])
            return
        
        product_id = product_response["productCreate"]["product"]["id"]

        # Create variants
        for variant_config in product_config["VARIANTS"]:
            variant_input = construct_variant_query_input(product_id, variant_config)
            variant_response = run_shopify_query(CREATE_VARIANT_QUERY, variant_input)

            # Error handling
            if variant_response["productVariantCreate"]["userErrors"]:
                print("Error creating variant for product: " + product_key)
                print(variant_response["productVariantCreate"]["userErrors"])
                return