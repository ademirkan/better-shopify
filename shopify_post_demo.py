import os
from dotenv import load_dotenv
from helpers import upload_media

# Environment variables
load_dotenv()
SHOPIFY_ACCESS_TOKEN = os.getenv("SHOPIFY_ACCESS_TOKEN")
SHOPIFY_STORE_URL = os.getenv("SHOPIFY_STORE_URL")
TEST_FILE_PATH = "./media/dublexo_eik/test_dublexo_eik_e1 copy.jpg"


print(upload_media(TEST_FILE_PATH, "test_dublexo.jpg", "image of dublexo eik e1"))
