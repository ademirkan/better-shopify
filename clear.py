import os
from PIL import Image
import piexif
import subprocess

def clear_metadata_from_file(file_path):
    image_extensions = ['.jpg', '.jpeg', '.png', '.gif', '.bmp']
    video_extensions = ['.mp4', '.avi', '.mov', '.wmv', '.flv']

    if any(file_path.lower().endswith(ext) for ext in image_extensions):
        clear_image_metadata(file_path)
    elif any(file_path.lower().endswith(ext) for ext in video_extensions):
        clear_video_metadata(file_path)
    else:
        print(f"Unsupported file type for file {file_path}")

def clear_image_metadata(image_path):
    try:
        img = Image.open(image_path)
        data = list(img.getdata())
        image_without_exif = Image.new(img.mode, img.size)
        image_without_exif.putdata(data)

        image_without_exif.save(image_path)
        print(f"Cleared metadata from image {image_path}")
    except Exception as e:
        print(f"Failed to clear metadata from image: {e}")

def clear_video_metadata(video_path):
    temp_video_path = video_path + ".nometa.mp4"  # Temporary file

    try:
        command = [
            'ffmpeg',
            '-i', video_path,
            '-map_metadata', '-1',  # Remove metadata
            '-codec', 'copy',
            temp_video_path
        ]

        subprocess.run(command, check=True)
        os.replace(temp_video_path, video_path)
        print(f"Cleared metadata from video {video_path}")
    except subprocess.CalledProcessError as e:
        print(f"Failed to clear metadata from video: {e}")
        if os.path.exists(temp_video_path):
            os.remove(temp_video_path)


def clear_metadata_in_directory(directory):
    for root, dirs, files in os.walk(directory):
        for file in files:
            file_path = os.path.join(root, file)
            clear_metadata_from_file(file_path)

# Example usage: 
clear_metadata_in_directory('/Users/arifd/Desktop/Code/Projects/LaContempo/shopify_db/Media/Test Cubed Media original')
