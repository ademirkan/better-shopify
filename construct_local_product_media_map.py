import os
import json

def construct_local_product_media_map(media_folder_path):
    media_manifesto = {}

    global num_total_files
    global num_processed_files

    # Reset counters
    num_total_files = 0
    num_processed_files = 0

    # Count total files for progress tracking
    for _, _, files in os.walk(media_folder_path):
        num_total_files += len(files)

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
                    media_obj = process_file(file_or_dir_path, file_or_dir)
                    if media_obj:
                        media_manifesto[product_id][variant_sku].append(media_obj)

    return media_manifesto

def process_shared_media(shared_media_path):
    shared_media = {}
    with open(os.path.join(shared_media_path, 'manifesto.json'), 'r') as file:
        shared_media_info = json.load(file)

    for file_name, skus in shared_media_info.items():
        for sku in skus:
            if sku not in shared_media:
                shared_media[sku] = []
            file_path = os.path.join(shared_media_path, file_name)
            media_obj = process_file(file_path, file_name)
            if media_obj:
                shared_media[sku].append(media_obj)
    return shared_media

def process_file(path, name):
    # Determine file type and process accordingly
    if os.path.isdir(path) and name.startswith('360'):
        # Process as 360 image folder
        return process_360_folder(path)
    elif os.path.isfile(path):
        if not name.lower().endswith(('.png', '.jpg', '.jpeg', '.mp4')):
            return None
        if name.lower().endswith(('.png', '.jpg', '.jpeg')):
            return {"type": "IMAGE", "value": path}
        elif name.lower().endswith('.mp4'):
            return {"type": "VIDEO", "value": path}
    return None

def process_360_folder(folder_path):
    images = []
    for img_file in sorted(os.listdir(folder_path)):
        if img_file.lower().endswith(('.png', '.jpg', '.jpeg')):
            img_path = os.path.join(folder_path, img_file)
            images.append(img_path)
    return {"type": "360_IMG", "value": images}
