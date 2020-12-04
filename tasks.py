from huey import SqliteHuey
from entities import db_name

from utils import encode, decode
from os import rename, remove
import logging

huey = SqliteHuey(filename=db_name)
CHUNK_SIZE = 4096


@huey.task()
def encode_file(filename, key):
    with open(filename, "rb") as fi, open(filename + ".enc", "wb") as fo:
        while fi.readable():
            chunk = fi.read(CHUNK_SIZE)
            if len(chunk) == 0:
                break
            fo.write(encode(chunk, key))
    remove(filename)
    rename(filename + ".enc", filename)


