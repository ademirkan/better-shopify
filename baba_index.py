
import os
from update_media_map import bulk_update_variant_media_map

print("Paste product id here: ")
product_id = input().strip()

print("Paste product media folder path here: ")
product_media_folder_path = input().strip()


dict_variant_folder_path_to_variant_id = {}
# Assume the directory structure is:
# product_id
#   variant_id

# for variant_id in os.listdir(product_media_folder_path):
#     variant_path = os.path.join(product_media_folder_path, variant_id)
#     if not os.path.isdir(variant_path):
#         continue
    
#     if variant_path in dict_variant_folder_path_to_variant_id:
#         raise Exception("Duplicate variant id found in media folder path")
#     dict_variant_folder_path_to_variant_id[variant_path] = variant_id

def sorting_function(variant_media_path_list):
    return

bulk_update_variant_media_map(product_media_folder_path, dict_variant_folder_path_to_variant_id, sorting_function)
print("Media maps updated successfully")