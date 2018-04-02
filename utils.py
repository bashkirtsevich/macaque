import hashlib


def sha1_str(data):
    return hashlib.sha1(data.encode('utf-8')).hexdigest()
