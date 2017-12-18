import hashlib


def is_valid_message(message, type):
    return True


def name_hash(s):
    return hashlib.md5(bytes(s.lower(), 'utf-8')).hexdigest()
