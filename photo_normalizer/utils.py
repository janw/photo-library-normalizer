import hashlib


BUF_SIZE = 65536 * 1024


def hash_file(filename):
    hashsum = hashlib.md5()

    with open(filename, "rb") as f:
        data = f.read(BUF_SIZE)
        while data:
            hashsum.update(data)
            data = f.read(BUF_SIZE)

    return hashsum.hexdigest()
