import hashlib

from dateutil.parser import parse


def sha1(*args):
    hash_obj = hashlib.sha1()
    for item in args:
        hash_obj.update(bytes(str(item), "utf-8"))

    return hash_obj.hexdigest()


def parse_datetime(s):
    if s:
        return parse(s)
    else:
        return None
