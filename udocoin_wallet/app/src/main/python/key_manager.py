from cryptography.hazmat.backends import default_backend
from cryptography.hazmat.primitives.asymmetric import rsa
from cryptography.hazmat.primitives.serialization import Encoding, NoEncryption, PrivateFormat, PublicFormat

from cryptography.hazmat.primitives import hashes
from cryptography.hazmat.primitives.asymmetric import padding

import os

directory_name = ".udocoin"
private_key_file_name = "priv_key"
public_key_file_name = "pub_key.pub"

def get_directory()->str:
    global directory_name
    if os.name == 'nt':  # Windows
        key_directory_path = os.path.join(os.path.expanduser("~"), directory_name)
    else:  # Unix-based Systeme (Linux, macOS)
        key_directory_path = os.path.join(os.path.expanduser(f"~/{directory_name}"))

    if not os.path.exists(key_directory_path):
        try:
            os.makedirs(key_directory_path)
        except:
            print(f'Error at creating directory "{key_directory_path}".')
            print(f'Please create directory "{key_directory_path}".')
            exit(1)
    return key_directory_path

default_path = get_directory()

private_key_path = os.path.join(default_path,private_key_file_name)
public_key_path = os.path.join(default_path,public_key_file_name)
    
def generate_keys():
    private_key = rsa.generate_private_key(
        public_exponent=65537,
        key_size=512,
        backend=default_backend())

    priv_key = private_key.private_bytes(encoding=Encoding.PEM, encryption_algorithm=NoEncryption(), format=PrivateFormat.TraditionalOpenSSL)
    pub_key = private_key.public_key().public_bytes(encoding=Encoding.PEM, format=PublicFormat.SubjectPublicKeyInfo)

    return priv_key,pub_key

def save_keys(private_key_path,priv_key,public_key_path,pub_key):
    print("==========================================")
    with open(private_key_path, "wb") as binary_file:
        binary_file.write(priv_key)
        print(f'Your private key has been saved to "{private_key_path}"')

    with open(public_key_path, "wb") as binary_file:
        binary_file.write(pub_key)
        print(f'Your public key has been saved to "{public_key_path}"')
    print("==========================================")
    
def create_keys():
    global private_key_path
    global public_key_path
    priv_key,pub_key = generate_keys()
    save_keys(
        private_key_path=private_key_path,
        priv_key=priv_key,
        public_key_path=public_key_path,
        pub_key=pub_key)
    return [priv_key,pub_key]

def get_keys():
    privkey = ""
    pubkey = ""
    if not has_keys():
        return [privkey,pubkey]
    
    global private_key_path
    with open(private_key_path, "r") as file:
        privkey = file.read()
    global public_key_path
    with open(public_key_path, "r") as file:
        pubkey = file.read()

    return [privkey,pubkey]

def get_private_key():
    global private_key_path
    if not os.path.exists(private_key_path):
        return ""
    with open(private_key_path, "r") as file:
        return file.read()
    
def get_public_key():
    global public_key_path
    if not os.path.exists(public_key_path):
        return ""
    with open(public_key_path, "r") as file:
        return file.read()

def has_keys():
    global public_key_path
    global private_key_path
    return os.path.exists(public_key_path) and os.path.exists(private_key_path)
    