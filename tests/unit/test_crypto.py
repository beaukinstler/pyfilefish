import base64
import os
from pathlib import Path

abspath = os.path.abspath(__file__)
dname = Path(abspath).parent


# os.chdir(dname)
from cryptography.fernet import Fernet
from cryptography.hazmat.backends import default_backend
from cryptography.hazmat.primitives import hashes
from cryptography.hazmat.primitives.kdf.pbkdf2 import PBKDF2HMAC
from pyfi_util.pyfish_util import get_md5
from hashlib import md5

from settings import *
from pyfi_util.pyfi_crypto import *

try:
    import gpg
    from pyfi_util import pyfi_crypto_gpg as pfgpg
except ImportError as e:
    logger.warning(msg=str(e))
import pytest
import sys
from hashlib import sha3_512 as sha


@pytest.mark.skipif(sys.platform != "linux", reason="only supported on linux")
@pytest.mark.crypto
def test_gpg_encrypt():
    a_key = GPG_PUBLIC_ID
    filename = "tests/test_files/test.wav"
    pfgpg.encrypt_file_with_gpg(file_name=filename, key=a_key)
    assert Path(f"{filename}.asc").exists()


@pytest.mark.crypto
@pytest.mark.skipif(sys.platform != "linux", reason="only supported on linux")
def test_gpg_decrypt():
    a_key = GPG_PUBLIC_ID
    filename = "tests/test_files/test.wav"
    pfgpg.decrypt_file_with_gpg(file_name=filename, key=GPG_PASS)
    assert Path(f"{filename}.asc").exists()


@pytest.mark.crypto
def test_basic_encryption():
    """Ensure basic test files and utilities are in place, attempt
    encryption and decryption with third party tools, before and instead of 
    testing the pyfish abstractions. If this test fails, the the rest are sure to.
    """
    password = b"password"
    salt = os.urandom(16)
    kdf = PBKDF2HMAC(
        algorithm=hashes.SHA256(),
        length=32,
        salt=salt,
        iterations=100000,
        backend=default_backend(),
    )
    key = base64.urlsafe_b64encode(kdf.derive(password))
    f = Fernet(key)
    token = f.encrypt(b"Secret message!")
    print(token)
    print(f.decrypt(token))


@pytest.mark.crypto
def test_encrypting_test_files():
    """Ensure basic test files and utilities are in place, attempt
    encryption and decryption with third party tools, before and instead of 
    testing the pyfish abstractions. If this test fails, the the rest are sure to.
    """
    password = b"password"
    salt = os.urandom(16)
    kdf = PBKDF2HMAC(
        algorithm=hashes.SHA256(),
        length=32,
        salt=salt,
        iterations=100000,
        backend=default_backend(),
    )
    data = bytes
    md5_sum_before = ""
    md5sAfter = ""
    with open("tests/test_files/test.wav", "rb") as file_to_read:
        data = file_to_read.read()
        md5_sum_before = md5(data).hexdigest()
        print(f"md5before: {md5_sum_before}")

    key = base64.urlsafe_b64encode(kdf.derive(password))
    f = Fernet(key)
    token = f.encrypt(data)
    with open("tests/test_files/test.wav.encrypted", "wb") as file_to_write:
        file_to_write.write(token)
    # print(token)
    with open("tests/test_files/test.wav.encrypted", "rb") as file_to_decrypt:
        token = file_to_decrypt.read()

    f2 = Fernet(key)
    # print(f2.decrypt(token))

    with open(
        "tests/test_files/test.wav_un-encrypted", "wb"
    ) as decrypt_file_to_write:
        decrypt_file_to_write.write(f2.decrypt(token))

    with open(
        "tests/test_files/test.wav_un-encrypted", "rb"
    ) as decrypt_file_to_read:
        data = decrypt_file_to_read.read()
        md5sAfter = md5(data).hexdigest()

    assert md5sAfter == md5_sum_before


@pytest.mark.crypto
def test_decrypt_function():
    """use pyfi util crypt to decrypt an encrypted file, and make sure the
    md5 hash is as expected.
    """
    password = PYFI_S3_ENCRYPTION_KEY
    salt = PYFI_S3_SALT
    kdf = PBKDF2HMAC(
        algorithm=hashes.SHA256(),
        length=32,
        salt=salt,
        iterations=100000,
        backend=default_backend(),
    )
    data = bytes
    md5_sum_before = ""
    md5sAfter = ""
    with open("tests/test_files/test.wav", "rb") as file_to_read:
        data = file_to_read.read()
        md5_sum_before = md5(data).hexdigest()
        print(f"md5before: {md5_sum_before}")

    key = base64.urlsafe_b64encode(kdf.derive(password))
    f = Fernet(key)
    token = f.encrypt(data)
    encrypted_file = "tests/test_files/test.wav.encrypted"
    with open(encrypted_file, "wb") as file_to_write:
        file_to_write.write(token)
    decrypted_data = convert_encrypted_file_into_decrypted_data(
        encpryted_file_path=encrypted_file
    )

    md5sAfter = md5(decrypted_data).hexdigest()

    assert md5sAfter == md5_sum_before


@pytest.mark.crypto
def test_decrypt_and_decompress_function():
    """use pyfi util crypt to decrypt an encrypted file, and make sure the
    md5 hash is as expected.
    """
    password = PYFI_S3_ENCRYPTION_KEY
    salt = PYFI_S3_SALT
    kdf = PBKDF2HMAC(
        algorithm=hashes.SHA256(),
        length=32,
        salt=salt,
        iterations=100000,
        backend=default_backend(),
    )
    data = bytes
    md5_sum_before = ""
    md5sAfter = ""
    with open("tests/test_files/test.wav", "rb") as file_to_read:
        data = file_to_read.read()
        md5_sum_before = md5(data).hexdigest()
        print(f"md5before: {md5_sum_before}")

    key = base64.urlsafe_b64encode(kdf.derive(password))
    f = Fernet(key)
    token = f.encrypt(data)
    encrypted_file = "tests/test_files/test.wav.encrypted"
    with open(encrypted_file, "wb") as file_to_write:
        file_to_write.write(token)
    decrypted_data = convert_encrypted_file_into_decrypted_data(
        encpryted_file_path=encrypted_file
    )

    md5sAfter = md5(decrypted_data).hexdigest()

    assert md5sAfter == md5_sum_before


@pytest.mark.crypto
def test_encrypt_and_compress_function():
    """use pyfi util crypt to encrypt a file, and make sure the
    md5 hash is as expected after it is also decrypted.
    """
    password = PYFI_S3_ENCRYPTION_KEY
    salt = PYFI_S3_SALT
    kdf = PBKDF2HMAC(
        algorithm=hashes.SHA256(),
        length=32,
        salt=salt,
        iterations=100000,
        backend=default_backend(),
    )
    key = base64.urlsafe_b64encode(kdf.derive(password))
    f = Fernet(key)
    file_to_encrypt = "tests/test_files/test.wav"

    encrypted_data = convert_file_into_encrypted_data(
        file_path_to_encrypt=file_to_encrypt, compression=True
    )
    recovered_data = convert_encrypted_data_into_decrypted_data(
        encrypted_data, compression=True
    )
    dd1 = gzip.decompress(f.decrypt(encrypted_data))
    dd2 = recovered_data

    md51 = md5(dd1).hexdigest()
    md52 = md5(dd2).hexdigest()

    assert md51 == md52


if __name__ == "__main__":
    pass
