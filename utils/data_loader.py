import json
import os
from config import CONTENT_DIR

_cache = {}

def load(filename: str) -> dict:
    if filename in _cache:
        return _cache[filename]
    path = os.path.join(CONTENT_DIR, filename)
    with open(path, "r", encoding="utf-8") as f:
        data = json.load(f)
    _cache[filename] = data
    return data
