from cryptography import fernet
import tasks

def generate_key():
    key = fernet.Fernet.generate_key()
    return key

def encode(file, key):
    '''
    Encodes file
    :param file: a file (stream)
    :param key:
    :return:
    '''
    while(file):
        yield file.read()
    return file


def decode(file, key):
    '''
    Decodes file with a given key
    :param file:
    :param key:
    :return:
    '''

