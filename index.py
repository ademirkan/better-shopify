from collections import defaultdict
import json
import os
from helpers import CREATE_PRODUCT_QUERY
from helpers import UPDATE_VARIANT_QUERY
from helpers import file_stage
from helpers import file_create
from helpers import run_shopify_query

from construct_local_product_media_map import construct_local_product_media_map

MEDIA_FOLDER_PATH = "./Test Mini Media"
PRODUCT_CATALOG_PATH = "./formatted_catalog.json"

local_product_media_map = construct_local_product_media_map(MEDIA_FOLDER_PATH)
product_catalog = {}

with open(PRODUCT_CATALOG_PATH, "r") as file:
    product_catalog = json.load(file)

for product_key in product_catalog:
    product_config = product_catalog[product_key]
    local_variant_media_map = local_product_media_map[product_key]

    hosted_media_paths = {} # {path: hosted_media_object}

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
            # {
            #     "key": "media_manifesto",
            #     "namespace": "custom",
            #     "type": "json",
            #     "value": json.dumps(staged_variant_media_map),
            # },

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
        local_variant_media = local_variant_media_map[variant_key]
        uploaded_variant_media = []

        for media in local_variant_media:
            media_path = media["value"]
            # Use hosted media if already hosted
            if media_path in hosted_media_paths:
                uploaded_variant_media.append(hosted_media_paths[media_path])
                continue
            
            # Stage
            file_name = os.path.basename(media_path)
            staged_media_resource_url = file_stage(media_path, file_name)

            # Host
            hosted_media_object = {}
            if media["type"] == "IMAGE":
                hosted_media_object = file_create(staged_media_resource_url)
            elif media["type"] == "VIDEO":
                hosted_media_object = file_create(staged_media_resource_url)
            elif media["type"] == "360_IMG":
                for i in range(len(media["value"])):
                    staged_media_resource_url = file_stage(media["value"][i], file_name)
                    hosted_media_object = file_create(staged_media_resource_url)
            
            if not hosted_media_object:
                raise Exception("Failed to host media: {}".format(media_path))

            # Memoize hosted media
            hosted_media_paths[media_path] = hosted_media_object
            uploaded_variant_media.append(hosted_media_object)
        
        # Add variant media to variant metafield
        variant_media_metafield = {
            "key": "media_map",
            "namespace": "custom",
            "type": "json",
            "value": json.dumps(uploaded_variant_media),
        }

        ## TODO: Upload variant media metafield
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
        print("UPDATE_VARIANT_RESPONSE")
        print(update_variant_response)



