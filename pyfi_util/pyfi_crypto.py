from settings import *
from cryptography.fernet import Fernet
from cryptography.hazmat.backends import default_backend
from cryptography.hazmat.primitives import hashes
from cryptography.hazmat.primitives.kdf.pbkdf2 import PBKDF2HMAC

# from pyfi_util.pyfish_util import get_md5
from hashlib import md5
import base64
import os
from pathlib import Path
import gzip

from settings import *


def convert_encrypted_file_into_decrypted_data(
    encpryted_file_path="",
    salt=PYFI_S3_SALT,
    password=PYFI_S3_ENCRYPTION_KEY,
    message="",
    compression=False,
):
    kdf = PBKDF2HMAC(
        algorithm=hashes.SHA256(),
        length=32,
        salt=salt,
        iterations=100000,
        backend=default_backend(),
    )
    data = bytes()
    with open(encpryted_file_path, "rb") as file_to_read:
        data = file_to_read.read()

    key = base64.urlsafe_b64encode(kdf.derive(password))
    f = Fernet(key)
    decrypted_data = f.decrypt(data)

    return_data = bytes()
    if compression:
        try:
            return_data = gzip.decompress(decrypted_data)
        except OSError as e:
            print("data not compressed")
            print(e)
            return_data = decrypted_data
    else:
        return_data = decrypted_data
    return return_data


def convert_encrypted_data_into_decrypted_data(
    bdata,
    salt=PYFI_S3_SALT,
    password=PYFI_S3_ENCRYPTION_KEY,
    message="",
    compression=False,
):
    kdf = PBKDF2HMAC(
        algorithm=hashes.SHA256(),
        length=32,
        salt=salt,
        iterations=100000,
        backend=default_backend(),
    )
    decrypted_data = bytes()
    data = bytes()
    key = base64.urlsafe_b64encode(kdf.derive(password))
    f = Fernet(key)
    decrypted_data = f.decrypt(bdata)

    data = bytes()
    if compression:
        try:
            data = gzip.decompress(decrypted_data)
        except OSError as e:
            print("data not compressed")
            print(e)
            data = decrypted_data
    else:
        data = decrypted_data
    return data


def convert_file_into_encrypted_data(
    file_path_to_encrypt="",
    salt=PYFI_S3_SALT,
    password=PYFI_S3_ENCRYPTION_KEY,
    message="",
    compression=False,
):
    """Encrypt a file
    
    Keyword Arguments:
        salt {bytes} -- 16 bit bytes object (default: {PYFI_S3_SALT environment variable})
        password {bytes} -- utf-8 encoded password (default: {PYFI_S3_ENCRYPTION_KEY})
        message {str} -- add a message to the encrypted file (default: {""})
        encpryted_file_path {str} -- string representation of the path to encrypt (default: {""})
    
    Returns:
        bytes -- returns encrypted data blob to be used or written to file
    """
    kdf = PBKDF2HMAC(
        algorithm=hashes.SHA256(),
        length=32,
        salt=salt,
        iterations=100000,
        backend=default_backend(),
    )

    data = bytes()
    with open(file_path_to_encrypt, "rb") as file_to_read:
        if compression:
            data = gzip.compress(file_to_read.read())
        else:
            data = file_to_read.read()

    key = base64.urlsafe_b64encode(kdf.derive(password))
    f = Fernet(key)
    encrypted_data = f.encrypt(data)
    return encrypted_data


def convert_bdata_into_encrypted_data(
    bdata,
    salt=PYFI_S3_SALT,
    password=PYFI_S3_ENCRYPTION_KEY,
    message="",
    compression=False,
):
    """Encrypt binary data
    
    Keyword Arguments:
        salt {bytes} -- 16 bit bytes object (default: {PYFI_S3_SALT environment variable})
        password {bytes} -- utf-8 encoded password (default: {PYFI_S3_ENCRYPTION_KEY})
        message {str} -- add a message to the encrypted file (default: {""})
        encpryted_file_path {str} -- string representation of the path to encrypt (default: {""})
    
    Returns:
        bytes -- returns encrypted data blob to be used or written to file
    """
    kdf = PBKDF2HMAC(
        algorithm=hashes.SHA256(),
        length=32,
        salt=salt,
        iterations=100000,
        backend=default_backend(),
    )
    if compression:
        data = gzip.compress(bdata)
    else:
        data = bdata
    encrypted_data = bytes()
    key = base64.urlsafe_b64encode(kdf.derive(password))
    f = Fernet(key)
    encrypted_data = f.encrypt(data)
    return encrypted_data
