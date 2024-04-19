# Given product media path, update the media for its variants.
# 
# Product Media Folder
# ├── Variant Folder
# │   ├── Media 1
# │   ├── Media 2 
# ├── Variant Folder
# │   ├── Media 1
# │   ├── Media 2

import json
import os
from helpers.gql import run_shopify_query
from media_objects import process_file


def construct_variant_media_map(variant_media_folder_path, sorting_function):
    # Variant_media_folder_path = a/b/c/d
    # Parent_product_media_folder_path = a/b/c
    # Shared_media_folder_path = a/b/c/Shared Media
    # Variant_id = d
    parent_product_media_folder_path = os.path.dirname(variant_media_folder_path)
    shared_media_folder_path = os.path.join(parent_product_media_folder_path, "Shared Media")
    variant_id = os.path.basename(variant_media_folder_path)
    files_to_ignore = ["manifesto.json", ".DS_Store"]

    # Construct variant_media_path_list
    #|- Add media unique to variant
    #|- Add shared media
    variant_media_path_list = []
    for file_or_dir in os.listdir(variant_media_folder_path):
        if file_or_dir in files_to_ignore:
            continue
        file_or_dir_path = os.path.join(variant_media_folder_path, file_or_dir)
        variant_media_path_list.append(file_or_dir_path)
    
    if os.path.exists(shared_media_folder_path):
        shared_media_dict = {}
        with open(os.path.join(shared_media_folder_path, 'manifesto.json'), 'r') as file:
            shared_media_dict = json.load(file)
        for file_or_dir in shared_media_dict:
            if file_or_dir in files_to_ignore:
                continue
            if variant_id in shared_media_dict[file_or_dir]:
                file_or_dir_path = os.path.join(shared_media_folder_path, file_or_dir)
                variant_media_path_list.append(file_or_dir_path)
    
    # Sort variant_media_path_list
    sorting_function(variant_media_path_list)

    # Create sorted list of media objects
    sorted_media_objects = [
        process_file(media_path)
        for media_path in variant_media_path_list
        if os.path.exists(media_path)
    ]
    

    # Upload media objects to Shopify and return 
    return [media_object.create() for media_object in sorted_media_objects]


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

def update_variant_media(variant_media_map, variant_id, sorting_function):
    # Construct media_map
    variant_media_map = construct_variant_media_map(variant_media_map, sorting_function)

    # Product Media Folder
    # ├── Variant Folder
    # │   ├── Media 1
    # │   ├── Media 2
    # ├── Other Variant Folders
    # │   ├── ...
    # ├── Shared Media

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

    """ % (variant_id, metafield_id, json.dumps(variant_media_map).replace("\"", "\\\""))
    
    response = run_shopify_query(query)
    return response

def bulk_update_variant_media_map(product_media_folder_path, dict_path_to_variant_id, sorting_function):
    for file_or_dir in os.listdir(product_media_folder_path):
        if file_or_dir in ["Shared Media", ".DS_Store"]:
            continue
        variant_media_folder_path = os.path.join(product_media_folder_path, file_or_dir)
        if not os.path.isdir(variant_media_folder_path):
            continue
        variant_id = dict_path_to_variant_id[variant_media_folder_path]
        update_variant_media(variant_media_folder_path, variant_id, sorting_function)
    pass

# ------------------------------------------------------------------------------
# Test
# ------------------------------------------------------------------------------
def sorting_function(variant_media_path_list):
    return

print(json.dumps(construct_variant_media_map("/Users/arifd/Desktop/Code/Projects/LaContempo/shopify_db/Media/Test Cubed Media original/Cubed/95-744002521-6-2", sorting_function)))



