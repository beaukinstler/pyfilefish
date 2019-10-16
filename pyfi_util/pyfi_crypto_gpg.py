from settings import *
from pathlib import Path
import gpg
from dotenv import load_dotenv
from os import getenv

load_dotenv(dotenv_path=".env")


def encrypt_file_with_gpg(file_name, key):
    fl = Path(file_name)
    if fl.exists():
        with open(file_name, "rb") as afile:
            text = afile.read()
        c = gpg.core.Context(armor=True)
        rkey = list(c.keylist(pattern=key, secret=False))
        ciphertext, result, sign_result = c.encrypt(
            text,
            recipients=rkey,
            always_trust=True,
            add_encrypt_to=True,
            sign=False,
        )
        with open("{0}.asc".format(file_name), "wb") as bfile:
            bfile.write(ciphertext)


def decrypt_file_with_gpg(file_name, key=""):
    if not key:
        pass
        # TODO
        # key = ui.prompt_for_key
    encrypted_file = Path(file_name)
    output_name = f"new--{encrypted_file.name}"
    with open(f"{str(encrypted_file)}.asc", "rb") as cfile:
        plaintext, result, verify_result = gpg.Context().decrypt(
            cfile, passphrase=GPG_PASS
        )
    with open(encrypted_file.parent.joinpath(output_name), "wb") as dfile:
        dfile.write(plaintext)
