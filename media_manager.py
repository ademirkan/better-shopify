import json
import os
from media import Image, Video, Image360
import re

class MediaManager:
    def __init__(self, media_folder_path):
        self.product_media_map = {}

        def extract_number(filename):
            match = re.search(r'(\d+)', filename)
            return int(match.group()) if match else 0       
        
        def process_file(path, name):
            if os.path.isdir(path):
                ## Load index.json 
                index = {}
                with open(os.path.join(path, 'index.json'), 'r') as file:
                    index = json.load(file)
                
                if not index:
                    return None
                
                media_type = index['mediaType']
                match media_type:
                    case "360_IMG":
                        return Image360(path)
                    case _:
                        return None

            elif os.path.isfile(path):
                if not name.lower().endswith(('.png', '.jpg', '.jpeg', '.mp4')):
                    return None
                if name.lower().endswith(('.png', '.jpg', '.jpeg')):
                    return Image(path)
                elif name.lower().endswith('.mp4'):
                    return Video(path)
            return None
        
        def construct_product_media_map(media_folder_path):
            product_media_object_map = {}
            path_to_media_cache = {}
            ordered_product_media_path_map = {}

            ## Construct ordered_product_media_path_map
            for product_id in os.listdir(media_folder_path):
                product_path = os.path.join(media_folder_path, product_id)

                # Skip if not a directory
                if not os.path.isdir(product_path):
                    continue

                ordered_product_media_path_map[product_id] = {}
                shared_media_folder_path = os.path.join(product_path, "Shared Media")

                # Process shared media if exists
                shared_media_paths = {}
                if os.path.exists(shared_media_folder_path):
                    with open(os.path.join(shared_media_folder_path, 'manifesto.json'), 'r') as file:
                        shared_media_info = json.load(file)

                    for file_name, skus in shared_media_info.items():
                        for sku in skus:
                            if sku not in shared_media_paths:
                                shared_media_paths[sku] = []

                            file_path = os.path.join(shared_media_folder_path, file_name)
                            shared_media_paths[sku].append(file_path)
                    
                    ## Sort by removing extension, non-digit characters, then sort by that number
                    for sku in shared_media_paths:
                        shared_media_paths[sku] = sorted(
                            shared_media_paths[sku], 
                            key=lambda x: extract_number(os.path.basename(x))
                        )

                # Process individual variant folders
                for variant_sku in os.listdir(product_path):
                    variant_path = os.path.join(product_path, variant_sku)
                    if not os.path.isdir(variant_path) or variant_sku == "Shared Media":
                        continue

                    ## Populate paths for variant
                    ordered_product_media_path_map[product_id][variant_sku] = []
                    for file_or_dir in os.listdir(variant_path):
                        file_or_dir_path = os.path.join(variant_path, file_or_dir)
                        ordered_product_media_path_map[product_id][variant_sku].append(file_or_dir_path)
                    
                    ordered_product_media_path_map[product_id][variant_sku] = sorted(
                        ordered_product_media_path_map[product_id][variant_sku], 
                        key=lambda x: extract_number(os.path.basename(x)))
                    

                    ## Add any shared media to ordered_product_media_path_map[product_id][variant_sku]
                    shared_media_for_variant = shared_media_paths.get(variant_sku, [])
                    for path in shared_media_for_variant:
                        ordered_product_media_path_map[product_id][variant_sku].append(path)
    
            ## Using ordered_product_media_path_map, populate product_media_object_map
            ## TODO: Implement
            path_to_media_cache = {}
            for product_id in ordered_product_media_path_map:
                product_media_object_map[product_id] = {}
                for variant_sku in ordered_product_media_path_map[product_id]:
                    product_media_object_map[product_id][variant_sku] = []
                    for path in ordered_product_media_path_map[product_id][variant_sku]:
                        if path in path_to_media_cache:
                            product_media_object_map[product_id][variant_sku].append(path_to_media_cache[path])
                            continue
                        media_object = process_file(path, os.path.basename(path))
                        if media_object:
                            path_to_media_cache[path] = media_object
                            product_media_object_map[product_id][variant_sku].append(media_object)
            return product_media_object_map
        
        self.product_media_map = construct_product_media_map(media_folder_path)
    
    def get_product_media_map(self):
        return self.product_media_map
