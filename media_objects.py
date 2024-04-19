from abc import ABC, abstractmethod 
import os
from helpers import file_stage
from helpers.cache import embed_shopify_id_in_file, fetch_shopify_id_from_file
from helpers.file import fetch_file_by_id, file_create
import json

# import __hosted_media_cache.json as MEDIA_CACHE
HOSTED_MEDIA_CACHE = {}
with open("./cache/__hosted_media_cache.json", "r") as file:
    HOSTED_MEDIA_CACHE = json.load(file)


class Media(ABC):

    @abstractmethod
    def __init__(self):
        pass

    @abstractmethod
    def get_media_type(self):
        pass

    @abstractmethod
    def stage(self):
        ## Stage
        pass

    @abstractmethod
    def create(self):
        ## Stage
        ## Create
        ## Process
        pass


class Image(Media):
    def __init__(self, local_image_path):
        self.local_image_path = local_image_path
        self.staged_url = None
        self.shopify_image = None
        self.media_type = "IMAGE"

        shopify_id = fetch_shopify_id_from_file(self.local_image_path)

        ## Check if cached
        if shopify_id and shopify_id in HOSTED_MEDIA_CACHE:
            self.shopify_image = HOSTED_MEDIA_CACHE[shopify_id]
        elif shopify_id:
            self.shopify_image = fetch_file_by_id(shopify_id)
            HOSTED_MEDIA_CACHE[shopify_id] = self.shopify_image
            

    def get_media_type(self):
        return self.media_type
    
    def stage(self):
        ## Check if already staged
        if self.staged_url:
            return self.staged_url
        
        if self.shopify_image:
            raise Exception("Image already hosted")
        
        ## Stage
        file_name = os.path.basename(self.local_image_path)
        staged_media_resource_url = file_stage(self.local_image_path, file_name)

        ## Store
        self.staged_url = staged_media_resource_url
        return self.staged_url

    def create(self):
        ## Check if already created this runtime
        if self.shopify_image:
            return self.shopify_image
        
        ## Stage
        print("hosting", self.local_image_path)
        staged_media_resource_url = self.stage()

        ## Create
        create_response = file_create(staged_media_resource_url)
        shopify_id = create_response["data"]["fileCreate"]["files"][0]["id"]
        file_response = fetch_file_by_id(shopify_id)

        ## Cache processed media object
        embed_shopify_id_in_file(self.local_image_path, shopify_id)
        HOSTED_MEDIA_CACHE[shopify_id] = file_response
        with open("./cache/__hosted_media_cache.json", "w") as file:
            json.dump(HOSTED_MEDIA_CACHE, file)

        ## Store
        self.shopify_image = file_response
        return self.shopify_image
    

class Video(Media):
    def __init__(self, local_path):
        self.local_path = local_path
        self.staged_url = None
        self.shopify_video = None
        self.media_type = "VIDEO"

        shopify_id = fetch_shopify_id_from_file(self.local_path)

        ## Check if cached
        if shopify_id and shopify_id in HOSTED_MEDIA_CACHE:
            self.shopify_video = HOSTED_MEDIA_CACHE[shopify_id]
        elif shopify_id:
            self.shopify_video = fetch_file_by_id(shopify_id)
            HOSTED_MEDIA_CACHE[shopify_id] = self.shopify_video
    
    def get_media_type(self):
        return self.media_type
    
    def stage(self):
        ## Check if already staged
        if self.staged_url:
            return self.staged_url
        
        ## Stage
        file_name = os.path.basename(self.local_path)
        staged_media_resource_url = file_stage(self.local_path, file_name)

        ## Store
        self.staged_url = staged_media_resource_url

        return self.staged_url

    def create(self):
        ## Check if already created this runtime
        if self.shopify_video:
            return self.shopify_video

        ## Stage
        print("hosting", self.local_path)
        staged_media_resource_url = self.stage()

        ## Create
        create_response = file_create(staged_media_resource_url)
        shopify_id = create_response["data"]["fileCreate"]["files"][0]["id"]
        file_response = fetch_file_by_id(shopify_id)


        ## Cache
        embed_shopify_id_in_file(self.local_path, shopify_id)
        HOSTED_MEDIA_CACHE[shopify_id] = file_response
        with open("./cache/__hosted_media_cache.json", "w") as file:
            json.dump(HOSTED_MEDIA_CACHE, file)

        ## Store
        self.shopify_video = file_response
        return self.shopify_video

class Image360(Media):
    def __init__(self, folder_path):
        self.local_media = []
        self.staged_urls = []
        self.hosted_images = []
        self.preview_index = 0
        self.media_type = "360_IMG"

        # Sort by removing extension, non-digit characters, then sort by that number
        for img_file in sorted(os.listdir(folder_path), key=lambda x: int(''.join(filter(str.isdigit, os.path.splitext(x)[0]))) if any(char.isdigit() for char in x) else float('inf')):
            if img_file.lower().endswith(('.png', '.jpg', '.jpeg')):
                img_path = os.path.join(folder_path, img_file)
                self.local_media.append(Image(img_path))
            else:
                continue
        
        ## Open index.json
        index = {}
        with open(os.path.join(folder_path, 'index.json'), 'r') as file:
            index = json.load(file)
        
        if not index or not index["previewIndex"]:
            raise Exception("360 image folder does not contain index.json or previewIndex")
        
        self.preview_index = index["previewIndex"]
    
    def get_media_type(self):
        return self.media_type
    
    def stage(self):
        ## Check if already staged
        if self.staged_urls:
            return self.staged_urls
        
        ## Stage each image
        staged_media_resource_url = []
        for i in range(len(self.local_media)):
            staged_media_resource_url.append(self.local_media[i].stage())

        ## Store
        self.staged_urls = staged_media_resource_url

        return self.staged_urls

    def create(self):
        ## Check if already created this runtime
        if self.hosted_images:
            return self.hosted_images
        
        ## Create
        sources = []
        for i in range(len(self.local_media)):
            sources.append(self.local_media[i].create())
        ## Process (create the object front-end needs)
        processed_media_object = {"mediaContentType": self.media_type, "previewIndex": self.preview_index, "sources": sources}

        self.hosted_images = processed_media_object
        return self.hosted_images
    

def process_file(path):
    name = os.path.basename(path)
    if os.path.isdir(path):
        ## Load index.json 
        index = {}
        with open(os.path.join(path, 'index.json'), 'r') as file:
            index = json.load(file)
        
        if not index:
            return None
        
        media_type = index['mediaType']
        match media_type:
            case "360_IMG":
                return Image360(path)
            case _:
                return None

    elif os.path.isfile(path):
        if name.lower().endswith(('.png', '.jpg', '.jpeg')):
            return Image(path)
        elif name.lower().endswith('.mp4'):
            return Video(path)
        else:
            return None
        
    return None