import json
import os
from helpers import construct_base_product_query_input, run_shopify_query
from helpers import CREATE_PRODUCT_QUERY

# Shopify store details
MEDIA_FOLDER_PATH = "./media"
CATALOG_FOLDER_PATH = "./demo_catalog.json"

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

# Load demo_catalog.json
catalog = []
with open(os.path.join(os.path.dirname(__file__), CATALOG_FOLDER_PATH)) as f:
    catalog = json.load(f)


for product_key in catalog:
    product_config = catalog[product_key]

    product_query_input = construct_base_product_query_input(product_config, MEDIA_FOLDER_PATH + "/" + product_key)
    product_response = run_shopify_query(CREATE_PRODUCT_QUERY, product_query_input)
    product_id = product_response["data"]["productCreate"]["product"]["id"]
    

    for variant_config in product_config["VARIANTS"]:
        variant_query_input = construct_variant_query_input(product_id, variant_config, MEDIA_FOLDER_PATH + "/" + product_key + "/" + variant_config["SKU"])
        variant_response = run_shopify_query(CREATE_VARIANT_QUERY, variant_query_input)




# Sample media JSON
# sample_variant_media_json = [{
#                                 "media_type": "360_IMAGE", 
#                                     "value" : {
#                                                 "type": "innovation", 
#                                                 "value": {"src": "https://content.cylindo.com/api/v2/4926/products/95-74105043XXX-Y-2/frames/5/95-74105043XXX-Y-2.JPG?background=DDDDDD&feature=FABRIC:527&feature=POSITION:1&feature=LEG%20FINISH:5", 
#                                                 "positions": [1,3,4]}
#                                              }
#                             },
#                             {
#                                 "media_type": "IMAGE",
#                                     "value": {"src": "", "id": ""}
#                             },
#                             {
#                                 "media_type": "VIDEO",
#                                     "value": {"src": "", "id": ""}
#                             }]

# # Upload base product
# product_response = run_shopify_query(CREATE_PRODUCT_QUERY, DUBLEXO_DEMO_CONFIG)

# print(product_response)