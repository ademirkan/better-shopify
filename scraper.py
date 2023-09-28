import os
import requests
import time
import urllib.parse
from collections import defaultdict



def fetchAndStore(src, path, file_name):
    """
    Fetch and store file from src to given path with given file name.
    Only fetches and stores the file if it does not already exist at the path.
    """
    # Creating the folder path if it does not exist
    if not os.path.exists(path):
        os.makedirs(path)

    # Full path to store the file
    file_path = os.path.join(path, file_name)

    # Check if file already exists. If not, download and save it.
    if not os.path.exists(file_path):
        # Fetching the file from the source
        response = requests.get(src, stream=True)
        if response.status_code == 200:
            # Writing the file to the local file system
            with open(file_path, 'wb') as file:
                for chunk in response.iter_content(8192):
                    file.write(chunk)
        else:
            print(f"Failed to fetch {src}, status code: {response.status_code}")
            return False
    return True

LINKS = [
"https://content.cylindo.com/api/v2/4926/products/95-748082020XXX-7-2/frames/5/95-748082020XXX-7-2.JPG?background=FFFFFF&feature=FABRIC:527&feature=POSITION:1",
"https://content.cylindo.com/api/v2/4926/products/543062XXX/frames/5/543062XXX.JPG?background=FFFFFF&feature=FABRIC:538&feature=POSITION:1",
"https://content.cylindo.com/api/v2/4926/products/95-585004020XXX-01-2/frames/5/95-585004020XXX-01-2.JPG?background=FFFFFF&feature=FABRIC:586&feature=POSITION:1",
"https://content.cylindo.com/api/v2/4926/products/95-744002XXX-6-2/frames/5/95-744002XXX-6-2.JPG?background=FFFFFF&feature=FABRIC:527&feature=POSITION:1",
"https://content.cylindo.com/api/v2/4926/products/95-744002020XXX-2/frames/5/95-744002020XXX-2.JPG?background=FFFFFF&feature=FABRIC:521&feature=POSITION:1",
"https://content.cylindo.com/api/v2/4926/products/95-744002XXX-0-2/frames/5/95-744002XXX-0-2.JPG?background=FFFFFF&feature=FABRIC:521&feature=POSITION:1",
"https://content.cylindo.com/api/v2/4926/products/95-74105027XXX-Y-2/frames/5/95-74105027XXX-Y-2.JPG?background=FFFFFF&feature=FABRIC:527&feature=POSITION:1&feature=LEG%20FINISH:5",
"https://content.cylindo.com/api/v2/4926/products/95-742048020XXX-WOOD/frames/5/95-742048020XXX-WOOD.JPG?background=FFFFFF&feature=FABRIC:531&feature=POSITION:1",
"https://content.cylindo.com/api/v2/4926/products/95-543125020XXX-2/frames/5/95-543125020XXX-2.JPG?background=FFFFFF&feature=FABRIC:579&feature=POSITION:1",
"https://content.cylindo.com/api/v2/4926/products/95-543091XXX-2/frames/5/95-543091XXX-2.JPG?background=FFFFFF&feature=FABRIC:579&feature=POSITION:1",
"https://content.cylindo.com/api/v2/4926/products/95-742050XXX-WOOD/frames/5/95-742050XXX-WOOD.JPG?background=FFFFFF&feature=FABRIC:506&feature=POSITION:1",
"https://content.cylindo.com/api/v2/4926/products/95-748260XXX-0-2/frames/5/95-748260XXX-0-2.JPG?background=FFFFFF&feature=FABRIC:534&feature=POSITION:1",
"https://content.cylindo.com/api/v2/4926/products/95-772012XXX-10-3-2/frames/5/95-772012XXX-10-3-2.JPG?background=FFFFFF&feature=FABRIC:595&feature=POSITION:1",
"https://content.cylindo.com/api/v2/4926/products/772001XXX-10-3-2/frames/5/772001XXX-10-3-2.JPG?background=FFFFFF&feature=FABRIC:507&feature=POSITION:1",
"https://content.cylindo.com/api/v2/4926/products/95-543115XXX-2/frames/5/95-543115XXX-2.JPG?background=FFFFFF&feature=FABRIC:586&feature=POSITION:1",
"https://content.cylindo.com/api/v2/4926/products/95-740021XXX-2-19-6/frames/5/95-740021XXX-2-19-6.JPG?background=FFFFFF&feature=FABRIC:554&feature=POSITION:1",
"https://content.cylindo.com/api/v2/4926/products/95-748282XXX-0-2/frames/5/95-748282XXX-0-2.JPG?background=FFFFFF&feature=FABRIC:527&feature=POSITION:1",
"https://content.cylindo.com/api/v2/4926/products/95-748082004XXX-0-2/frames/5/95-748082004XXX-0-2.JPG?background=FFFFFF&feature=FABRIC:538&feature=POSITION:1",
"https://content.cylindo.com/api/v2/4926/products/95-748082004XXX-3-2/frames/5/95-748082004XXX-3-2.JPG?background=FFFFFF&feature=FABRIC:527&feature=POSITION:1",
"https://content.cylindo.com/api/v2/4926/products/95-722081XXX-18-Y-2/frames/5/95-722081XXX-18-Y-2.JPG?background=FFFFFF&feature=FABRIC:583&feature=POSITION:1&feature=LEG%20FINISH:7",
"https://content.cylindo.com/api/v2/4926/products/95-744002XXX-Y-2/frames/5/95-744002XXX-Y-2.JPG?background=FFFFFF&feature=FABRIC:527&feature=POSITION:1&feature=LEG%20FINISH:3",
"https://content.cylindo.com/api/v2/4926/products/95-744029XXX-6-2/frames/5/95-744029XXX-6-2.JPG?background=FFFFFF&feature=FABRIC:521&feature=POSITION:1",
"https://content.cylindo.com/api/v2/4926/products/95-744029020XXX-2/frames/5/95-744029020XXX-2.JPG?background=FFFFFF&feature=FABRIC:527&feature=POSITION:1",
"https://content.cylindo.com/api/v2/4926/products/95-744029XXX-0-2/frames/5/95-744029XXX-0-2.JPG?background=FFFFFF&feature=FABRIC:527&feature=POSITION:1",
"https://content.cylindo.com/api/v2/4926/products/95-744029XXX-Y-2/frames/5/95-744029XXX-Y-2.JPG?background=FFFFFF&feature=FABRIC:521&feature=POSITION:1&feature=LEG%20FINISH:3",
"https://content.cylindo.com/api/v2/4926/products/95-74105144XXX-Y-2/frames/5/95-74105144XXX-Y-2.JPG?background=FFFFFF&feature=FABRIC:521&feature=POSITION:1&feature=LEG%20FINISH:5",
"https://content.cylindo.com/api/v2/4926/products/95-74105144XXX-Y-2/frames/5/95-74105144XXX-Y-2.JPG?background=FFFFFF&feature=FABRIC:527&feature=POSITION:1&feature=LEG%20FINISH:7",
"https://content.cylindo.com/api/v2/4926/products/95-74105043XXX-Y-2/frames/5/95-74105043XXX-Y-2.JPG?background=FFFFFF&feature=FABRIC:506&feature=POSITION:1&feature=LEG%20FINISH:5",
"https://content.cylindo.com/api/v2/4926/products/95-74105043XXX-Y-2/frames/5/95-74105043XXX-Y-2.JPG?background=FFFFFF&feature=FABRIC:527&feature=POSITION:1&feature=LEG%20FINISH:7",
"https://content.cylindo.com/api/v2/4926/products/95-74105126XXX-Y-2/frames/5/95-74105126XXX-Y-2.JPG?background=FFFFFF&feature=FABRIC:527&feature=POSITION:1&feature=LEG%20FINISH:5",
"https://content.cylindo.com/api/v2/4926/products/95-74105126XXX-Y-2/frames/5/95-74105126XXX-Y-2.JPG?background=FFFFFF&feature=FABRIC:506&feature=POSITION:1&feature=LEG%20FINISH:7",
"https://content.cylindo.com/api/v2/4926/products/95-74105027XXX-Y-2/frames/5/95-74105027XXX-Y-2.JPG?background=FFFFFF&feature=FABRIC:527&feature=POSITION:1&feature=LEG%20FINISH:7",
"https://content.cylindo.com/api/v2/4926/products/95-741051XXX-Y-2/frames/5/95-741051XXX-Y-2.JPG?background=FFFFFF&feature=FABRIC:521&feature=POSITION:1&feature=LEG%20FINISH:8",
"https://content.cylindo.com/api/v2/4926/products/95-741050XXX-Y-2/frames/5/95-741050XXX-Y-2.JPG?background=FFFFFF&feature=FABRIC:527&feature=POSITION:1&feature=LEG%20FINISH:8",
"https://content.cylindo.com/api/v2/4926/products/95-74105020XXX-Y-2/frames/5/95-74105020XXX-Y-2.JPG?background=FFFFFF&feature=FABRIC:521&feature=POSITION:1&feature=LEG%20FINISH:8",
"https://content.cylindo.com/api/v2/4926/products/95-741051XXX-10-Y-2/frames/5/95-741051XXX-10-Y-2.JPG?background=FFFFFF&feature=FABRIC:506&feature=POSITION:1&feature=LEG%20FINISH:3",
"https://content.cylindo.com/api/v2/4926/products/95-741050XXX-10-Y-2/frames/5/95-741050XXX-10-Y-2.JPG?background=FFFFFF&feature=FABRIC:527&feature=POSITION:1&feature=LEG%20FINISH:3",
"https://content.cylindo.com/api/v2/4926/products/95-74105020XXX-10-YY/frames/5/95-74105020XXX-10-YY.JPG?background=FFFFFF&feature=FABRIC:506&feature=POSITION:1&feature=LEG%20FINISH:32",
"https://content.cylindo.com/api/v2/4926/products/95-592160XXXY-01-4/frames/5/95-592160XXXY-01-4.JPG?background=FFFFFF&feature=FABRIC:539&feature=POSITION:1",
"https://content.cylindo.com/api/v2/4926/products/742048XXX-10-Y-2/frames/5/742048XXX-10-Y-2.JPG?background=FFFFFF&feature=FABRIC:531&feature=POSITION:1&feature=LEG%20FINISH:3",
"https://content.cylindo.com/api/v2/4926/products/95-742048XXX-10-Y-2/frames/5/95-742048XXX-10-Y-2.JPG?background=FFFFFF&feature=FABRIC:565&feature=POSITION:1&feature=LEG%20FINISH:3",
"https://content.cylindo.com/api/v2/4926/products/95-748190XXX-4/frames/5/95-748190XXX-4.JPG?background=FFFFFF&feature=FABRIC:528&feature=POSITION:1",
"https://content.cylindo.com/api/v2/4926/products/95-748251XXX-3/frames/5/95-748251XXX-3.JPG?background=FFFFFF&feature=FABRIC:538&feature=POSITION:1",
"https://content.cylindo.com/api/v2/4926/products/95-592160XXXY-02-4/frames/5/95-592160XXXY-02-4.JPG?background=FFFFFF&feature=FABRIC:565&feature=POSITION:1",
"https://content.cylindo.com/api/v2/4926/products/95-543127XXX-2-2/frames/5/95-543127XXX-2-2.JPG?background=FFFFFF&feature=FABRIC:590&feature=POSITION:1",
"https://content.cylindo.com/api/v2/4926/products/95-748263XXX-3/frames/5/95-748263XXX-3.JPG?background=FFFFFF&feature=FABRIC:527&feature=POSITION:1",
"https://content.cylindo.com/api/v2/4926/products/742050XXX-10-Y-2/frames/5/742050XXX-10-Y-2.JPG?background=FFFFFF&feature=FABRIC:515&feature=POSITION:1&feature=LEG%20FINISH:3",
"https://content.cylindo.com/api/v2/4926/products/95-748251XXX-0/frames/5/95-748251XXX-0.JPG?background=FFFFFF&feature=FABRIC:534&feature=POSITION:1",
"https://content.cylindo.com/api/v2/4926/products/95-543091020XXX-01-2/frames/5/95-543091020XXX-01-2.JPG?background=FFFFFF&feature=FABRIC:527&feature=POSITION:1",
"https://content.cylindo.com/api/v2/4926/products/95-740021XXX-2-10-Y/frames/5/95-740021XXX-2-10-Y.JPG?background=FFFFFF&feature=FABRIC:554&feature=POSITION:1&feature=LEG%20FINISH:3"
]

fetchAndStore("https://content.cylindo.com/api/v2/4926/products/95-740021XXX-2-10-Y/frames/5/95-740021XXX-2-10-Y.JPG?background=FFFFFF&feature=FABRIC:554&feature=POSITION:1&feature=LEG%20FINISH:3"
, "./test", "imgName.jpeg")

FABRICS = [216, 316, 317, 318, 506, 507, 515, 521, 525, 527, 528, 531, 534, 538, 554, 558, 563, 565, 571, 573, 574, 575, 577, 578, 579, 580, 581, 583, 584, 585, 586, 587, 590, 595]
MAX_NUM_POSITIONS = 4
NUM_FRAMES = 33
BACKGROUND_COLOR = "FFFFFF"

product_dict = {}

for link in LINKS:
    # Parse the URL
    parsed_url = urllib.parse.urlparse(link)
    # Extract the key from the path
    product_key = parsed_url.path.split("/")[5]
    # Extract and parse the query string
    query_params = urllib.parse.parse_qs(parsed_url.query)


    if not product_key in product_dict:
        product_dict[product_key] = defaultdict(set)

    # Iterate over query parameters
    for feature_str in query_params['feature']:
        # delimit
        feature_key, feature_val = feature_str.split(':')
        # If the key is 'fabric', or 'position', it's a custom feature
        if feature_key.upper() not in ['FABRIC', 'POSITION']:
            # Add the custom feature to the dictionary
            feature_key = feature_key.replace(' ', '_')
            product_dict[product_key][feature_key].add(feature_val)

        

# fetch from all links, add to folder in /product_key/(?custom_feature)/fabric/bg/pos...
for product_key in product_dict:
    custom_features = product_dict[product_key]

    for fabric in FABRICS:
        for position in range(MAX_NUM_POSITIONS):

            # SLEEP to avoid rejection
            time.sleep(1.1)
            if custom_features != {}:
                # /product_key/fabric/bg/position
                print(custom_features)

                # NOTE: THIS IS ASSUMING CUSTOM KEYS ARE MUTUALLY EXCLUSIVE
                for custom_key, custom_val in custom_features.items():
                    for value in custom_val:
                        features = {"FABRIC": fabric, "POSITION": position, custom_key: value}
                        folder_path = f"./{product_key}/{custom_key}_{value}/{BACKGROUND_COLOR}/{position}"
                        for frame in range(NUM_FRAMES):
                            src = f"https://content.cylindo.com/api/v2/4926/products/{product_key}/frames/{frame}/{product_key}.JPG?background={BACKGROUND_COLOR}"
                            img_name = f"{product_key}_{frame}.jpeg"

                            fetchAndStore(src, folder_path, img_name)

                                
                            
            
            else:
                features = {"FABRIC": fabric, "POSITION": position}
                folder_path = f"./{product_key}/{BACKGROUND_COLOR}/{position}"
                for frame in range(NUM_FRAMES):
                    src = f"https://content.cylindo.com/api/v2/4926/products/{product_key}/frames/{frame}/{product_key}.JPG?background={BACKGROUND_COLOR}"
                    img_name = f"{product_key}_{frame}.jpeg"
                    fetchAndStore(src, folder_path, img_name)