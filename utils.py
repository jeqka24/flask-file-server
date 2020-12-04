import secrets
from itertools import cycle


def generate_key():
    key = secrets.token_bytes(16)
    return key


def encode(byte_in, key):
    '''
    Encodes file (simple XORing)
    :param byte_in: bytearray
    :param key: bytearray (shorter)
    :return: bytearray
    '''
    return bytearray(b ^ c for b, c in zip(byte_in, cycle(key)))


def decode(byte_in, key):
    '''
    Decodes file with a given key
    :param byte_in: bytearray
    :param key: bytearray (shorter)
    :return: bytearray
    '''
    return encode(byte_in, key)
