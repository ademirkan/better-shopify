import json
import os
from media import Image, Video, Image360


class MediaManager:
    def __init__(self, media_folder_path):
        self.product_media_map = {}

        def process_shared_media(shared_media_path):
            shared_media = {}
            path_to_media_obj_map = {}

            with open(os.path.join(shared_media_path, 'manifesto.json'), 'r') as file:
                shared_media_info = json.load(file)

            for file_name, skus in shared_media_info.items():
                for sku in skus:
                    if sku not in shared_media:
                        shared_media[sku] = []

                    file_path = os.path.join(shared_media_path, file_name)
                    if file_path in path_to_media_obj_map:
                        media_obj = path_to_media_obj_map[file_path]
                    else:
                        media_obj = process_file(file_path, file_name)
                        path_to_media_obj_map[file_path] = media_obj
                    if media_obj:
                        shared_media[sku].append(media_obj)
            return shared_media
        def process_file(path, name):
            if os.path.isdir(path):
                if name.startswith('360'):
                    return Image360(path)

                return None
            elif os.path.isfile(path):
                if not name.lower().endswith(('.png', '.jpg', '.jpeg', '.mp4')):
                    return None
                if name.lower().endswith(('.png', '.jpg', '.jpeg')):
                    return Image(path)
                elif name.lower().endswith('.mp4'):
                    return Video(path)
            return None
        def construct_local_product_media_map(media_folder_path):
            media_manifesto = {}
            path_to_media_obj_map = {}

            for product_id in os.listdir(media_folder_path):
                product_path = os.path.join(media_folder_path, product_id)

                # Skip if not a directory
                if not os.path.isdir(product_path):
                    continue

                media_manifesto[product_id] = {}
                shared_media_path = os.path.join(product_path, "Shared Media")
                shared_media = {}

                # Process shared media if exists
                if os.path.exists(shared_media_path):
                    shared_media = process_shared_media(shared_media_path)

                # Process individual variant folders
                for variant_sku in os.listdir(product_path):
                    variant_path = os.path.join(product_path, variant_sku)
                    if os.path.isdir(variant_path) and variant_sku != "Shared Media":
                        media_manifesto[product_id][variant_sku] = shared_media.get(variant_sku, [])
                        for file_or_dir in os.listdir(variant_path):
                            file_or_dir_path = os.path.join(variant_path, file_or_dir)
                            if file_or_dir_path in path_to_media_obj_map:
                                media_obj = path_to_media_obj_map[file_or_dir_path]
                            else:
                                media_obj = process_file(file_or_dir_path, file_or_dir)
                                path_to_media_obj_map[file_or_dir_path] = media_obj
                            if media_obj:
                                media_manifesto[product_id][variant_sku].append(media_obj)

            return media_manifesto
        
        self.product_media_map = construct_local_product_media_map(media_folder_path)
    
    def get_product_media_map(self):
        return self.product_media_map
