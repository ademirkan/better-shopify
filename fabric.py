import os
from media_objects import Image
from media_manager import MediaManager


LARGE_SWATCHES_FOLDER = "./Swatches/Innovation/Large/"
SMALL_SWATCHES_FOLDER = "./Swatches/Innovation/Small/"

FABRICS = [
    216,
    316,
    317,
    318,
    506,
    507,
    515,
    521,
    525,
    527,
    528,
    531,
    534,
    538,
    554,
    558,
    563,
    565,
    571,
    573,
    574,
    575,
    577,
    578,
    579,
    580,
    581,
    583,
    584,
    585,
    586,
    587,
    590,
    595,
]

fabrics_dict = {}

for fabric_id in FABRICS:
    fabric_id = str(fabric_id)
    fabric_file_name = fabric_id + ".jpg"

    fabric_large_swatch_path = os.path.join(LARGE_SWATCHES_FOLDER, fabric_file_name)
    fabric_small_swatch_path = os.path.join(SMALL_SWATCHES_FOLDER, fabric_file_name)
    
    large_fabric_media = Image(fabric_large_swatch_path)
    small_fabric_media = Image(fabric_small_swatch_path)

    fabrics_dict[fabric_id] = {
        "smallImage": small_fabric_media.create(),
        "largeImage": large_fabric_media.create(),
    }

    print(fabric_id, "done")

print(fabrics_dict)





