# Given product media path, update the media for its variants.
# 
# Product Media Folder
# ├── Variant Folder
# │   ├── Media 1
# │   ├── Media 2 
# ├── Variant Folder
# │   ├── Media 1
# │   ├── Media 2
#

import json
from helpers.gql import run_shopify_query


def get_product_variant_ids(product_id):
    # Construct Query
    query = """
    query {
        product(id: "gid://shopify/Product/%s") {
            variants(first: 10) {
                edges {
                    node {
                        id
                    }
                }
            }
        }
    }
    """ % product_id

    # Run Query
    response = run_shopify_query(query)
    variant_ids = []
    for edge in response["data"]["product"]["variants"]["edges"]:
        # Extract Variant ID from "gid://shopify/ProductVariant/48638178656549"
        variant_ids.append(edge["node"]["id"].split("/")[-1])
    
    return variant_ids

def update_variant_media_by_id(parent_product_media_folder_path, variant_id):
    # Construct media metadata
    media_metadata_json = {}

    # Product Media Folder
    # ├── Variant Folder
    # │   ├── Media 1
    # │   ├── Media 2
    






    # Update variant media metafield
    # -- Fetch metafield ID
    query = """
        query {
            productVariant(id: "gid://shopify/ProductVariant/%s") {
                metafield(namespace: "custom", key: "media_map"){
                    id
                    value
                }
            }
        }
    """ % variant_id
    response = run_shopify_query(query)
    # Get metafield ID from gid://shopify/Metafield/36295264043301
    metafield_id = response["data"]["productVariant"]["metafield"]["id"].split("/")[-1]


    # -- Construct Query
    query = """
        mutation {
            productVariantUpdate(
                input: {
                id: "gid://shopify/ProductVariant/%s",
                metafields: [
                    {
                    id: "gid://shopify/Metafield/%s",
                    value: "%s"
                    }
                ]
                }
            ) {
                productVariant {
                id
                metafields(first: 10) {
                    edges {
                    node {
                        id
                        namespace
                        key
                        value
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

    """ % (variant_id, metafield_id, json.dumps(media_metadata_json).replace("\"", "\\\""))


    response = run_shopify_query(query)
    return response



def update_variant_media_by_sku(variant_media_folder_path, variant_sku):
    pass

# ------------------------------------------------------------------------------
print(update_variant_media_by_id("", 48638178656549))
