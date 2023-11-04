from collections import defaultdict
import json

"""

Goal:

Dublexo Sofa: {
    variants: {
        "colors": [512, 561, 517]
        "size": ["full", "queen]
        "legs": ["wood", "steel"]
    }

    for_sale: [{
        config: {
            ...
        }
        price: 1849
        shipping_range: [7,14]
        }
    ]...

}

"""


with open("innovation_catalog.json") as json_file:
    data = json.load(json_file)


keys = set()
root_keys = set()
non_root_keys = set()

name_to_id = {
    "Dublexo Sofa": [
        "95-741050XXX-10-3-2",
        "95-741050XXX-8-2",
        "95-74105020XXX-10-32",
        "95-74105020XXX-8-2",
        "95-74105027XXX-7-2",
        "95-74105043XXX-7-2",
    ],
    "Dublexo Chair": [
        "95-741051XXX-10-3-2",
        "95-741051XXX-8-2",
        "95-74105126XXX-7-2",
        "95-74105144XXX-7-2",
    ],
}
key_to_products = defaultdict(list)

for product in data:
    if not product["PRODUCTS NAME"]:
        continue
    key = product["ITEM NUMBER"]
    keys.add(key)

    if True:
        root_keys.add(key)
        key_to_products[key].append(
            (product["PRODUCTS NAME"], product["MASTER ITEM NUMBER"])
        )
    else:
        non_root_keys.add(key)


for key in key_to_products:
    names = list(map((lambda x: x[0]), key_to_products[key]))
    keys = list(map((lambda x: x[1]), key_to_products[key]))

    print(names)
    print(keys)
    print("--------------------------------------------")

products = defaultdict(list)
