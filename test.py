from helpers.file import fetch_file_by_id

id = "gid://shopify/ImageSource/36614361252133"
id2 = "gid://shopify/MediaImage/36604413411621"
print(fetch_file_by_id(id2))
print(fetch_file_by_id(id))
