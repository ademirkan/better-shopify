import os
import json
import requests
from urllib.parse import urlparse
from .gql import run_shopify_query
import mimetypes
from urllib.parse import urlparse
import tempfile
from .gql import run_shopify_query


# Determine if a string is a URL
def is_url(src):
    try:
        result = urlparse(src)
        return all([result.scheme, result.netloc])
    except ValueError:
        return False

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

# Given a local or external file, stage the file upload. Return the resource URL.
def file_stage(src, filename):
    # Import media_cache.json
    media_cache = {}
    with open(os.path.join(os.path.dirname(__file__), "media_cache.json")) as f:
        media_cache = json.load(f)

    # Check if src is in media_cache.json
    if src in media_cache:
        return media_cache[src]
    

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
    STAGE_QUERY = """
    mutation stagedUploadsCreate($input: [StagedUploadInput!]!) {
        stagedUploadsCreate(input: $input) {
            stagedTargets {
                url
                resourceUrl
                parameters {
                    name
                    value
                }
            }
        }
    }
    """

    STAGE_INPUT = {
        "input": [
            {
                "filename": os.path.basename(filename),
                "mimeType": MIMETYPE,
                "resource": RESOURCE,
                "httpMethod": "POST",
                "fileSize": file_size,
            }
        ]
    }

    stage_response = run_shopify_query(STAGE_QUERY, STAGE_INPUT)

    if not stage_response.get('data'):
        raise Exception("Failed to get staging URL from Shopify")

    upload_targets = stage_response["data"]["stagedUploadsCreate"]["stagedTargets"]
    target = upload_targets[0]

    # Prepare the payload for the file upload
    payload = {param["name"]: param["value"] for param in target["parameters"]}
    with open(filepath, "rb") as f:
        files = {"file": f}
        upload_response = requests.post(target["url"], files=files, data=payload)

    if upload_response.status_code > 299:
        raise Exception(f"Failed to upload file: {upload_response.json()}")

    # Optionally, delete the temporary file if the source was a URL
    if is_src_url:
        os.remove(filepath)

    # Add the URL to media_cache.json
    media_cache[src] = target["resourceUrl"]
    with open(os.path.join(os.path.dirname(__file__), "media_cache.json"), "w") as f:
        json.dump(media_cache, f)
    
    return target["resourceUrl"]
 
# Given a local or external file, create a Shopify file. Return the file ID and URL.
def file_stage_and_create(src, filename, alt):

    # Stage the file upload
    resource_url = file_stage(src, filename)
    

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
                "originalSource": resource_url,
            }
        ]
    }

    create_response = run_shopify_query(CREATE_QUERY, CREATE_VARIABLES)
    if create_response["data"]["fileCreate"]["userErrors"]:
        raise Exception(f"Failed to create upload: {src, filename}")
    
    return {"id":create_response["data"]["fileCreate"]["files"][0]["id"], "url": resource_url}
