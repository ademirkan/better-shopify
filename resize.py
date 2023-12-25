from PIL import Image
import os

def resize_image(input_path, output_path, base_width=1415):
    img = Image.open(input_path)
    w_percent = (base_width / float(img.size[0]))
    h_size = int((float(img.size[1]) * float(w_percent)))
    img = img.resize((base_width, h_size), Image.ANTIALIAS)
    img.save(output_path)

def process_folder(folder_path):
    for subdir, dirs, files in os.walk(folder_path):
        for file in files:
            if file.lower().endswith(('png', 'jpg', 'jpeg')):
                file_path = os.path.join(subdir, file)
                output_path = os.path.join(subdir, "resized_" + file)
                resize_image(file_path, output_path)

folder_path = '1'  # Replace with your folder path
process_folder(folder_path)
