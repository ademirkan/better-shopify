import subprocess
import os
from PIL import Image
import piexif

# Helper function to determine if the file is an image
def is_image_file(file_path):
    image_extensions = ['.jpg', '.jpeg', '.png', '.gif', '.bmp']
    return any(file_path.lower().endswith(ext) for ext in image_extensions)

# Helper function to determine if the file is a video
def is_video_file(file_path):
    video_extensions = ['.mp4', '.avi', '.mov', '.wmv', '.flv']
    return any(file_path.lower().endswith(ext) for ext in video_extensions)

# Function to embed the ID string in image metadata
def embed_id_in_image(image_path, id_str):
    # Load the image
    img = Image.open(image_path)

    # Check if the image has EXIF data, if not, create an empty EXIF dict
    if "exif" in img.info:
        exif_dict = piexif.load(img.info['exif'])
    else:
        exif_dict = {"0th": {}, "Exif": {}, "GPS": {}, "1st": {}, "thumbnail": None}

    # Embed the ID string in the ImageDescription field
    exif_dict['0th'][piexif.ImageIFD.ImageDescription] = id_str.encode()

    # Dump the new EXIF data
    exif_bytes = piexif.dump(exif_dict)

    # Overwrite the image with new EXIF data
    img.save(image_path, exif=exif_bytes, quality=95)

# Function to fetch the ID from image metadata
def fetch_id_from_image_metadata(image_path):
    # Open the image
    img = Image.open(image_path)

    # Check if the image has EXIF data
    if "exif" in img.info:
        # Load EXIF data
        exif_dict = piexif.load(img.info['exif'])

        # Check if the ImageDescription field exists and has data
        if piexif.ImageIFD.ImageDescription in exif_dict['0th']:
            id_str = exif_dict['0th'][piexif.ImageIFD.ImageDescription]

            # Decode the ID string if it's in bytes format
            if isinstance(id_str, bytes):
                id_str = id_str.decode()

            return id_str
        else:
            print("No ID stored in the ImageDescription field.")
    else:
        print("No EXIF data found in the image.")

    return None

def embed_metadata_in_video(video_path, metadata_id):
    temp_video_path = video_path + ".temp.mp4"  # Temporary file

    try:
        # Construct the FFmpeg command for embedding metadata
        command = [
            'ffmpeg',
            '-i', video_path,
            '-metadata', f'title={metadata_id}',
            '-codec', 'copy',
            '-y',  # Overwrite the output file if it exists
            temp_video_path  # Write to a temporary file
        ]

        # Execute the command
        subprocess.run(command, check=True)
        print(f"Metadata embedded successfully in temporary file {temp_video_path}")

        # Replace original file with temporary file
        os.replace(temp_video_path, video_path)
        print(f"Original file {video_path} updated successfully.")
    except subprocess.CalledProcessError as e:
        print(f"An error occurred: {e}")
        if os.path.exists(temp_video_path):
            os.remove(temp_video_path)

def fetch_metadata_from_video(video_path):
    try:
        command = ['ffmpeg', '-i', video_path]
        result = subprocess.run(command, text=True, stderr=subprocess.PIPE, stdout=subprocess.PIPE)

        # Look for the line containing the title metadata
        for line in result.stderr.split('\n'):
            if "title" in line:
                # Extract the title value
                title_line = line.split("title",1)[1].strip()
                # Remove possible leading characters like ':' or '='
                title_value = title_line.lstrip(':=').strip()
                return title_value
    except subprocess.CalledProcessError as e:
        # Handle specific errors if needed
        pass

    return None


def embed_shopify_id_in_file(path, id):
    if is_image_file(path):
        embed_id_in_image(path, id)
    elif is_video_file(path):
        embed_metadata_in_video(path, id)
    else:
        print("Unsupported file type.")

def fetch_shopify_id_from_file(path):
    if is_image_file(path):
        return fetch_id_from_image_metadata(path)
    elif is_video_file(path):
        return fetch_metadata_from_video(path)
    else:
        print("Unsupported file type.")
        return None


# Example Usage
# path = 'somefile.mp4'  # or 'somefile.jpg'
# shopify_id = 'gid://shopify/ImageSource/36520545583397'

# embed_shopify_id_in_file(path, shopify_id)
# fetched_id = fetch_shopify_id_from_file(path)
# if fetched_id:
#     print(f"Fetched ID: {fetched_id}")
# else:
#     print("No Shopify ID found.")

