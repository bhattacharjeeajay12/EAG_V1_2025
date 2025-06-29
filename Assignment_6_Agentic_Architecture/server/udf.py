import json
import os

def get_search_from_cache(key):
    folder = "cache"
    file = "cache.json"
    file_path = os.path.join(folder, file)
    os.makedirs(folder, exist_ok=True)

    # Load cache if file exists, otherwise initialize empty dict
    if os.path.exists(file_path):
        with open(file_path, "r") as f:
            cache = json.load(f)
    else:
        cache = {}

    if key in cache:
        print(f"Found result in cache for key: {key}")
        return cache[key]
    return ""

def add_search_in_cache(key, result):  # fixed typo in function name too
    folder = "cache"
    file = "cache.json"
    file_path = os.path.join(folder, file)

    # Load or initialize cache
    if os.path.exists(file_path):
        with open(file_path, "r") as f:
            cache = json.load(f)
    else:
        cache = {}  # <- missing in your version

    # Add/update the key
    cache[key] = result

    # Save updated cache
    with open(file_path, "w") as f:
        json.dump(cache, f, indent=2)
