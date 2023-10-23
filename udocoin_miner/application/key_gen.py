from cryptography.hazmat.backends import default_backend
from cryptography.hazmat.primitives.asymmetric import rsa
from cryptography.hazmat.primitives.serialization import Encoding, NoEncryption, PrivateFormat, PublicFormat

from cryptography.hazmat.primitives import hashes
from cryptography.hazmat.primitives.asymmetric import padding

import os,pathlib

public_key_path = os.path.join(pathlib.Path(__file__).parent,"app","blockchain_modules","blockchain_secrets","pub_key.pub")
private_key_path = os.path.join(pathlib.Path(__file__).parent,"app","blockchain_modules","blockchain_secrets","priv_key")

private_key = rsa.generate_private_key(
    public_exponent=65537,
    key_size=512,
    backend=default_backend())

priv_key = private_key.private_bytes(encoding=Encoding.PEM, encryption_algorithm=NoEncryption(), format=PrivateFormat.TraditionalOpenSSL)
pub_key = private_key.public_key().public_bytes(encoding=Encoding.PEM, format=PublicFormat.SubjectPublicKeyInfo)

with open(private_key_path, "wb") as binary_file:
    binary_file.write(priv_key)
    print(f"Your private key has been saved to {private_key_path}")

with open(public_key_path, "wb") as binary_file:
    binary_file.write(pub_key)
    print(f"Your public key has been saved to {public_key_path}")
