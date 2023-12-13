import os
import time
import requests
from urllib.parse import urlparse
from .gql import STAGE_QUERY, run_shopify_query
import mimetypes
from urllib.parse import urlparse
import tempfile

# Determine if a string is a URL
def is_url(src):
    try:
        result = urlparse(src)
        return all([result.scheme, result.netloc])
    except ValueError:
        return False

def is_img(src):
    return src.endswith(".jpg") or src.endswith(".png") or src.endswith(".jpeg")

def is_video(src):
    return src.endswith(".mp4") or src.endswith(".mov") or src.endswith(".avi")

# Given a file ID, poll Shopify for the file URL. Return the query.
def fetch_file_by_id(id):
    # GraphQL query to fetch file information
    FILE_QUERY = """
    query($id: ID!) {
        node(id: $id) {
            ... on MediaImage {
                mediaContentType
                image {
                    id
                    url
                    altText
                    width
                    height
                }
            }

            ... on Video {
                mediaContentType
                id
                alt
                preview {
                    image {
                        id
                        url
                        altText
                        width
                        height
                    }
                }
                sources {
                    url
                    mimeType
                    format
                    height
                    width
                }
            }
        }
    }
    """

    formatted_id = id
    sleep_time = 1
    if id.startswith("gid://shopify/Video/"):
        sleep_time = 5

    # Poll Shopify for the file status
    while True:
        # Wait a bit before trying again
        time.sleep(sleep_time)

        data = run_shopify_query(FILE_QUERY, {"id": formatted_id})
        
        # Check for errors
        if 'errors' in data:
            print("Error fetching file:", data['errors'])
            break

        node_data = data.get("data", {}).get("node", {})
        if 'image' in node_data and node_data['image'] is not None:
            return node_data
        elif 'sources' in node_data and node_data['sources']:
            return node_data
        # Add other media types handling here if necessary

# Download a file from a URL to a temporary file. Return the path to the file.
def download_file(url):
    # Make a request to the remote URL
    response = requests.get(url, stream=True)
    if response.status_code != 200:
        raise Exception(f"Failed to download file: Status code {response.status_code}")

    # Try to guess the extension of the file based on the Content-Type header
    content_type = response.headers.get('Content-Type')
    extension = mimetypes.guess_extension(content_type) if content_type else ''

    # If no extension could be guessed, you might want to default to one or raise an error
    if not extension:
        raise Exception(f"Could not determine file extension for MIME type: {content_type}")

    # Parse the filename from the URL or generate a unique name
    parsed_url = urlparse(url)
    filename = os.path.basename(parsed_url.path) or f"downloaded_file{extension}"

    # Ensure the filename ends with the correct extension
    if not filename.endswith(extension):
        filename += extension

    # Create a temporary file path
    temp_path = os.path.join(tempfile.gettempdir(), filename)

    # Write the content to the temporary file
    with open(temp_path, 'wb') as file:
        for chunk in response.iter_content(chunk_size=8192):
            if chunk:  # filter out keep-alive new chunks
                file.write(chunk)

    # Return the path to the temporary file
    return temp_path

# Given a local file, determine the MIME type and Shopify resource type.
def get_mimetype_and_resource(path):
    # Guess the MIME type of the file based on its content.
    # If the path does not have an extension, we assume it is a local file.
    # This is a simplification and may not always be correct.
    mime_type, _ = mimetypes.guess_type(path)
    if mime_type is None:
        raise Exception("Could not determine file type")

    # Map the MIME type to the appropriate resource type for Shopify.
    if mime_type.startswith('image/'):
        return mime_type, "IMAGE"
    elif mime_type.startswith('video/'):
        return mime_type, "VIDEO"
    elif mime_type.startswith('audio/'):
        return mime_type, "AUDIO"
    else:
        raise Exception("Unsupported MIME type: {}".format(mime_type))

# Returns staged url to which src has been uploaded
def file_stage(src, filename):
    # Determine if the src is a URL or a local file path
    is_src_url = is_url(src)

    if is_src_url:
        # If src is a URL, download it to a local temporary file
        filepath = download_file(src)
        MIMETYPE, RESOURCE = get_mimetype_and_resource(filepath)
    else:
        filepath = src
        MIMETYPE, RESOURCE = get_mimetype_and_resource(filepath)

    # Get the size of the file
    file_size = str(os.path.getsize(filepath))

    # GraphQL mutation for staging the file upload
    

    STAGE_INPUT = {
        "input": [
            {
                "filename": os.path.basename(filename),
                "mimeType": MIMETYPE,
                "resource": RESOURCE,
                "fileSize": file_size,
            }
        ]
    }
    
    if RESOURCE == "IMAGE":
        STAGE_INPUT["input"][0]["httpMethod"] = "POST"

    stage_response = run_shopify_query(STAGE_QUERY, STAGE_INPUT)

    if not stage_response.get('data'):
        raise Exception("Failed to get staging URL from Shopify")

    upload_targets = stage_response["data"]["stagedUploadsCreate"]["stagedTargets"]
    target = upload_targets[0]
    resource_url = target["resourceUrl"]
    # Prepare the payload for the file upload
    payload = {param["name"]: param["value"] for param in target["parameters"]}

    # Upload the file to staged URL
    with open(filepath, "rb") as f:
        files = {"file": f}
        upload_response = requests.post(target["url"], files=files, data=payload)
        
    if upload_response.status_code > 299:
        raise Exception(f"Failed to upload file: {upload_response.json()}")

    # Optionally, delete the temporary file if the source was a URL
    if is_src_url:
        os.remove(filepath)
    
    if resource_url.startswith("https://shopify-video-production-core-originals.storage.googleapis.com"):
        # Extract the key from the parameters
        key = next((param["value"] for param in target["parameters"] if param["name"] == "key"), None)
        if key:
            # Append the key and retain the external_video_id query parameter
            video_id_param = resource_url.split("?")[1]  # Extracts 'external_video_id=XXXX'
            resource_url = f"https://storage.googleapis.com/shopify-video-production-core-originals/{key}?{video_id_param}"

    return resource_url
 
# Given a staged URL, create a file in Shopify Admin. Return the media object.
def file_create(staged_src, alt=""):
    # If video, update the resource URL to the video URL
    if staged_src.startswith("https://shopify-video-production-core-originals.storage.googleapis.com"):
        # Extract the key from the parameters
        key = next((param["value"] for param in staged_src["parameters"] if param["name"] == "key"), None)
        if key:
            # Append the key and retain the external_video_id query parameter
            video_id_param = staged_src.split("?")[1]  # Extracts 'external_video_id=XXXX'
            staged_src = f"https://storage.googleapis.com/shopify-video-production-core-originals/{key}?{video_id_param}"
    

    # Create file in Shopify Admin
    CREATE_QUERY = """
    mutation fileCreate($files: [FileCreateInput!]!) {
    fileCreate(files: $files) {
        files {
            id
            fileStatus
            alt
            createdAt
        }
        userErrors {
        field
        message
        }
    }
    }
    """

    CREATE_VARIABLES = {
        "files": [
            {
                "alt": alt,
                "originalSource": staged_src,
            }
        ]
    }

    create_response = run_shopify_query(CREATE_QUERY, CREATE_VARIABLES)
    media_id = create_response["data"]["fileCreate"]["files"][0]["id"]
    if create_response["data"]["fileCreate"]["userErrors"]:
        raise Exception(f"Failed to create upload:", staged_src)
    
    media_obj = fetch_file_by_id(media_id)
    return media_obj
