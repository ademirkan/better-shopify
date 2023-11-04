import os
import base64
import requests
import json
import mimetypes


# Shopify store details
SHOPIFY_STORE_URL = "https://dc2434-2.myshopify.com/admin/api/2023-10/graphql.json"
SHOPIFY_ACCESS_TOKEN = "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"

# Shopify Query
PRODUCT_QUERY = """
    mutation CreateProductWithNewMedia($input: ProductInput!, $media: [CreateMediaInput!]) {
        productCreate(input: $input, media: $media) {
        product {
          id
          title
          options {
            name
            values
          }
          media(first: 10) {
            nodes {
                alt
                mediaContentType
                preview {
                    status
                }
            }
        }
        }
        userErrors {
          field
          message
        }
      }
    }
    """


# Functions
def run_query(query, variables={}):
    headers = {
        "Content-Type": "application/json",
        "X-Shopify-Access-Token": SHOPIFY_ACCESS_TOKEN,
    }
    response = requests.post(
        SHOPIFY_STORE_URL,
        json={"query": query, "variables": variables},
        headers=headers,
    )
    return response.json()


def get_resource_and_mime(filename):
    mime_type, _ = mimetypes.guess_type(filename)
    if mime_type:
        if "image" in mime_type:
            return "IMAGE", mime_type
        elif "video" in mime_type:
            return "VIDEO", mime_type
        # Add more conditions here for other file types like 3D models, etc.
    # Default to a generic BLOB type or handle unknown types as needed
    return "BLOB", "application/octet-stream"


def get_staged_upload_urls(file_paths):
    # GraphQL mutation for staged uploads
    STAGED_UPLOADS_CREATE = """
    mutation stagedUploadsCreate($input: [StagedUploadInput!]!) {
      stagedUploadsCreate(input: $input) {
        stagedTargets {
          resourceUrl
          parameters {
            name
            value
          }
        }
        userErrors {
          field
          message
        }
      }
    }
    """

    # Construct the input for the mutation
    inputs = []
    for path in file_paths:
        resource, mime_type = get_resource_and_mime(path)
        input_data = {
            "filename": os.path.basename(path),
            "mimeType": mime_type,
            "resource": resource,
        }
        # If fileSize is required for some resources like VIDEO, calculate and add it here.
        if resource == "VIDEO":
            input_data["fileSize"] = str(os.path.getsize(path))
        inputs.append(input_data)

    # Headers for the GraphQL request
    headers = {
        "Content-Type": "application/json",
        "X-Shopify-Access-Token": SHOPIFY_ACCESS_TOKEN,
    }

    # Run the mutation
    response = requests.post(
        SHOPIFY_STORE_URL,
        json={"query": STAGED_UPLOADS_CREATE, "variables": {"input": inputs}},
        headers=headers,
    )
    response_json = response.json()
    staged_uploads = response_json["data"]["stagedUploadsCreate"]["stagedTargets"]

    return staged_uploads


def create_files_with_staged_urls(staged_urls):
    # The fileCreate GraphQL mutation
    FILE_CREATE_MUTATION = """
    mutation fileCreate($files: [FileCreateInput!]!) {
        fileCreate(files: $files) {
            files {
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

    # Construct the files input for the mutation
    files_input = [
        {
            "alt": "Description for the image",
            "mediaContentType": "IMAGE",
            "originalSource": staged_url,
        }
        for staged_url in staged_urls
    ]

    # Run the mutation
    response = run_query(FILE_CREATE_MUTATION, variables={"files": files_input})

    # Check the response
    if "errors" in response:
        print(f"GraphQL error: {response['errors']}")
    else:
        files_created = response["data"]["fileCreate"]["files"]
        user_errors = response["data"]["fileCreate"]["userErrors"]

        if user_errors:
            print("Errors occurred:")
            for error in user_errors:
                print(f"Field: {error['field']}, Message: {error['message']}")
            return []
        else:
            print("Files created successfully:")
            for file in files_created:
                print(f"Alt: {file['alt']}, Created At: {file['createdAt']}")

    return files_input


# Function to construct media
def construct_media(folder_path):
    # Get the full paths of all files in the specified folder
    file_paths = [
        os.path.join(folder_path, f)
        for f in os.listdir(folder_path)
        if os.path.isfile(os.path.join(folder_path, f))
    ]

    # Use the get_staged_upload_urls function to get the upload URLs for these images
    staged_uploads = get_staged_upload_urls(file_paths)

    # Extract the resource URLs from the staged uploads
    staged_urls = [staged["resourceUrl"] for staged in staged_uploads]

    # Use the create_files_with_staged_urls function to upload the files to Shopify
    files_created = create_files_with_staged_urls(staged_urls)

    # Construct the media array using the file data returned from Shopify
    return files_created


DUBLEXO_DEMO_CONFIG = {
    "input": {
        "customProductType": "",
        "descriptionHtml": "This is a product description in the form of descriptionHtml",
        "metafields": [
            {
                "key": "signature_variants",
                "namespace": "custom",
                "type": "json",
                "value": '{"some_key": "some_value"}',
            }
        ],
        "options": ["Fabric", "Base"],
        "title": "Dublexo Eik",
        "variants": [
            {
                "compareAtPrice": "2000",
                "inventoryItem": {"cost": "500", "tracked": True},
                "inventoryQuantities": [
                    {
                        "availableQuantity": 1000,
                        "locationId": "gid://shopify/Location/85320270117",
                    }
                ],
                # "mediaId": "",
                # "mediaSrc": [""],
                # "metafields": [
                #     {
                #         "key": "",
                #         "namespace": "",
                #         "type": "",
                #         "value": "",
                #     }
                # ],
                "options": ["Red", "Wood"],
                "position": 1,  # make defaults come before customs
                "price": "1850",
                "requiresShipping": True,
                "sku": "test1",
                "title": "Dublexo Eik Red Wood",
                "weight": 1000,
                "weightUnit": "POUNDS",
            },
            {
                "compareAtPrice": "2001",
                "inventoryItem": {"cost": "500", "tracked": True},
                "inventoryQuantities": [
                    {
                        "availableQuantity": 1000,
                        "locationId": "gid://shopify/Location/85320270117",
                    }
                ],
                # "mediaId": "",
                # "mediaSrc": [""],
                # "metafields": [
                #     {
                #         "key": "",
                #         "namespace": "",
                #         "type": "",
                #         "value": "",
                #     }
                # ],
                "options": ["Red", "Dark wood"],
                "position": 1,  # make defaults come before customs
                "price": "1850",
                "requiresShipping": True,
                "sku": "test1",
                "title": "Dublexo Eik Red darkwood",
                "weight": 1000,
                "weightUnit": "POUNDS",
            },
        ],
        "vendor": "Innovation",
    },
    "media": [
        # {
        #     "alt": "test",
        #     "mediaContentType": "IMAGE",
        #     "originalSource": "https://upload.wikimedia.org/wikipedia/commons/thumb/2/2f/Google_2015_logo.svg/1200px-Google_2015_logo.svg.png",
        # }
    ],
}

# Generate media for product
DUBLEXO_DEMO_CONFIG["media"] = construct_media("./media/dublexo_eik/")
# Upload base product
product_response = run_query(PRODUCT_QUERY, DUBLEXO_DEMO_CONFIG)


print(product_response)
