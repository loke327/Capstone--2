import hashlib
import json

def sha256_hash(data):
    if isinstance(data, dict):
        data = json.dumps(data, sort_keys=True).encode()

    elif isinstance(data, str):
        data = data.encode()

    elif isinstance(data, bytes):
        pass  # already bytes, do nothing

    else:
        data = str(data).encode()

    return hashlib.sha256(data).hexdigest()
