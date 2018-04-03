import hashlib


def sha1(*args):
    hash_obj = hashlib.sha1()
    for item in args:
        hash_obj.update(bytes(str(item), "utf-8"))

    return hash_obj.hexdigest()
