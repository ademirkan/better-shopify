import json 
from helpers import CREATE_PRODUCT_QUERY
from helpers import UPDATE_VARIANT_QUERY
from helpers import run_shopify_query
from media_manager import MediaManager

MEDIA_FOLDER_PATH = "./Test Cubed Media"
PRODUCT_CATALOG_PATH = "./formatted_catalog.json"

product_media_map = MediaManager(MEDIA_FOLDER_PATH).get_product_media_map()
product_catalog = {}

with open(PRODUCT_CATALOG_PATH, "r") as file:
    product_catalog = json.load(file)

for product_key in product_catalog:
    product_config = product_catalog[product_key]

    ## CREATE PRODUCT
    # Construct the product query input
    def construct_product_create_query_input(product_config):
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
                "key": "additional_info",
                "namespace": "custom",
                "type": "json",
                "value": json.dumps(product_config["ADDITIONAL_INFO"]),
            },
            {
                "key": "shipping",
                "namespace": "custom",
                "type": "json",
                "value": json.dumps(product_config["SHIPPING"]),
            }
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
    

    product_query_input = construct_product_create_query_input(product_config)
    product_response = run_shopify_query(CREATE_PRODUCT_QUERY, product_query_input)

    ## HOST MEDIA
    for variant_key in product_config["VARIANTS"]:

        variant_config = product_config["VARIANTS"][variant_key]
        variant_media_map = product_media_map[product_key][variant_key]

        hosted_variant_media = []
        for media in variant_media_map:
            hosted_variant_media.append(media.create())
        
        print(hosted_variant_media)
        # Add variant media to variant metafield
        variant_media_metafield = {
            "key": "media_map",
            "namespace": "custom",
            "type": "json",
            "value": json.dumps(hosted_variant_media),
        }

        ## Upload variant media metafield
        variant_sku_to_id_map = {}
        for variant_edge in product_response["data"]["productCreate"]["product"]["variants"]["edges"]:
            variant = variant_edge["node"]
            variant_sku_to_id_map[variant["sku"]] = variant["id"]
        
        variant_id = variant_sku_to_id_map[variant_config["SKU"]]
        variables = {
            "input": {
                "id": variant_id,
                "metafields": [variant_media_metafield],
            }
        }

        update_variant_response = run_shopify_query(UPDATE_VARIANT_QUERY, variables)



