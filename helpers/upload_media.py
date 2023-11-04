import requests
import os
from dotenv import load_dotenv
from .run_shopify_query import run_shopify_query

# Environment variables
load_dotenv()
SHOPIFY_ACCESS_TOKEN = os.getenv("SHOPIFY_ACCESS_TOKEN")
SHOPIFY_STORE_URL = os.getenv("SHOPIFY_STORE_URL")


def upload_media(filepath, filename, alt):
    def get_mimetype_and_resource(path):
        if path.endswith(".jpg"):
            return "image/jpeg", "IMAGE"
        elif path.endswith(".png"):
            return "image/png", "IMAGE"
        elif path.endswith(".gif"):
            return "image/gif", "IMAGE"
        elif path.endswith(".mp4"):
            return "video/mp4", "VIDEO"
        elif path.endswith(".mp3"):
            return "audio/mpeg", "AUDIO"
        else:
            raise Exception("Unsupported file type")
    
    MIMETYPE, RESOURCE = get_mimetype_and_resource(filepath)

    # 1. Stage
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
                "filename": filename,
                "mimeType": MIMETYPE,
                "resource": RESOURCE,
                "httpMethod": "POST",
                "fileSize": str(os.path.getsize(filepath)),
            },
        ]
    }

    stage_response = run_shopify_query(STAGE_QUERY, STAGE_INPUT)


    # 2. Post
    upload_targets = stage_response["data"]["stagedUploadsCreate"]["stagedTargets"]
    target = upload_targets[0]
    payload = {param["name"]: param["value"] for param in target["parameters"]}
    files = {"file": open(filepath, "rb")}
    upload_response = requests.post(target["url"], files=files, data=payload)
    if upload_response.status_code > 299:
        raise Exception(f"Failed to create upload: {filepath, filename}")

    # 3. Create
    CREATE_QUERY = """
    mutation fileCreate($files: [FileCreateInput!]!) {
    fileCreate(files: $files) {
        files {
            id
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
                "originalSource": target["resourceUrl"],
            }
        ]
    }

    create_response = run_shopify_query(CREATE_QUERY, CREATE_VARIABLES)
    if create_response["data"]["fileCreate"]["userErrors"]:
        raise Exception(f"Failed to create upload: {filepath, filename}")
    return create_response["data"]["fileCreate"]["files"][0]["id"]
