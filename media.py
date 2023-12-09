from abc import ABC, abstractmethod 
import os
from helpers import file_stage
from helpers.file import file_create
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
    def get_staged_media(self):
        pass

    @abstractmethod
    def get_hosted_media(self):
        pass


class Image(Media):
    def __init__(self, local_image_path):
        self.local_image_path = local_image_path
        self.staged_media = None
        self.hosted_media = None
        self.media_type = "IMAGE"
    
    def get_media_type(self):
        return self.media_type
    
    def get_staged_media(self):
        if self.staged_media:
            return self.staged_media
        
        file_name = os.path.basename(self.local_image_path)
        staged_media_resource_url = file_stage(self.local_image_path, file_name)
        self.staged_media = staged_media_resource_url
        return self.staged_media

    def get_hosted_media(self):
        if self.hosted_media:
            return self.hosted_media

        if self.local_image_path in HOSTED_MEDIA_CACHE:
            self.hosted_media = HOSTED_MEDIA_CACHE[self.local_image_path]
            return self.hosted_media
        
        print("hosting", self.local_image_path)
        staged_media_resource_url = self.get_staged_media()
        hosted_media_object = file_create(staged_media_resource_url)
        HOSTED_MEDIA_CACHE[self.local_image_path] = hosted_media_object

        with open("./cache/__hosted_media_cache.json", "w") as file:
            json.dump(HOSTED_MEDIA_CACHE, file)

        self.hosted_media = hosted_media_object

        return self.hosted_media
    

class Video(Media):
    def __init__(self, local_video_path):
        self.local_path = local_video_path
        self.staged_media = None
        self.hosted_media = None
        self.media_type = "VIDEO"
    
    def get_media_type(self):
        return self.media_type
    
    def get_staged_media(self):
        if self.staged_media:
            return self.staged_media
        
        file_name = os.path.basename(self.local_path)
        staged_media_resource_url = file_stage(self.local_path, file_name)
        self.staged_media = staged_media_resource_url
        return self.staged_media

    def get_hosted_media(self):
        if self.hosted_media:
            return self.hosted_media

        if self.local_path in HOSTED_MEDIA_CACHE:
            self.hosted_media = HOSTED_MEDIA_CACHE[self.local_path]
            return self.hosted_media
        
        staged_media_resource_url = self.get_staged_media()
        print("hosting", self.local_path)
        hosted_media_object = file_create(staged_media_resource_url)
        HOSTED_MEDIA_CACHE[self.local_path] = hosted_media_object

        with open("./cache/__hosted_media_cache.json", "w") as file:
            json.dump(HOSTED_MEDIA_CACHE, file)

        self.hosted_media = hosted_media_object
        return self.hosted_media

class Image360(Media):
    def __init__(self, folder_path):
        self.local_media = []
        self.staged_media = []
        self.hosted_media = []
        self.media_type = "360_IMG"

        # Sort by removing extension, non-digit characters, then sort by that number
        for img_file in sorted(os.listdir(folder_path), key=lambda x: int(''.join(filter(str.isdigit, os.path.splitext(x)[0])))):
            print(img_file)
            if img_file.lower().endswith(('.png', '.jpg', '.jpeg')):
                img_path = os.path.join(folder_path, img_file)
                self.local_media.append(Image(img_path))
            else:
                raise Exception("360 image folder contains non-image files")
    
    def get_media_type(self):
        return self.media_type
    
    def get_staged_media(self):
        if self.staged_media:
            return self.staged_media
        
        staged_media_resource_url = []
        for i in range(len(self.local_media)):
            staged_media_resource_url.append(self.local_media[i].get_staged_media())

        self.staged_media = staged_media_resource_url
        return self.staged_media

    def get_hosted_media(self):
        if self.hosted_media:
            return self.hosted_media
        
        hosted_media_object = {"mediaContentType": self.media_type, "sources": []}
        for i in range(len(self.local_media)):
            hosted_media_object["sources"].append(self.local_media[i].get_hosted_media())
        
        self.hosted_media = hosted_media_object
        return self.hosted_media