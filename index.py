import json
from construct_product_media_map import construct_product_media_map
from create_shopify_catalog import create_shopify_catalog

MEDIA_FOLDER_PATH = "./Test Cubed Media"
PRODUCT_MEDIA_MAP_FOLDER_PATH = "./product_media_map.json"
PRODUCT_CATALOG_PATH = "./formatted_catalog.json"

# Construct object mapping product IDs to media objects
product_media_map = construct_product_media_map(MEDIA_FOLDER_PATH)

with open(PRODUCT_MEDIA_MAP_FOLDER_PATH, "w") as file:
    json.dump(product_media_map, file, indent=4)

with open(PRODUCT_CATALOG_PATH, "r") as file:
    product_catalog = json.load(file)

create_shopify_catalog(product_catalog, product_media_map)