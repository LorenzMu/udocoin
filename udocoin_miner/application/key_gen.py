from cryptography.hazmat.backends import default_backend
from cryptography.hazmat.primitives.asymmetric import rsa
from cryptography.hazmat.primitives.serialization import Encoding, NoEncryption, PrivateFormat, PublicFormat

from cryptography.hazmat.primitives import hashes
from cryptography.hazmat.primitives.asymmetric import padding

import os,sys

directory_name = ".udocoin"
private_key_file_name = "priv_key"
public_key_file_name = "pub_key.pub"

def get_directory()->str:
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

def get_filenames(key_directory_path,n=None):
    if n is None:
        private_key_path = os.path.join(key_directory_path,private_key_file_name)
        public_key_path = os.path.join(key_directory_path,public_key_file_name)
        
        if os.path.exists(private_key_path) or os.path.exists(public_key_path):
            return get_filenames(key_directory_path,1)
        return private_key_path,public_key_path
    
    n += 1
    private_key_path = os.path.join(key_directory_path,private_key_file_name + f" ({n})")
    public_key_path = os.path.join(key_directory_path,public_key_file_name + f" ({n})")

    if os.path.exists(private_key_path) or os.path.exists(public_key_path):
        return get_filenames(key_directory_path,n)
    return private_key_path,public_key_path
    
def get_keys():
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

def main():
    key_directory_path = get_directory()
    private_key_path,public_key_path = get_filenames(key_directory_path)
    priv_key,pub_key = get_keys()
    save_keys(
        private_key_path=private_key_path,
        priv_key=priv_key,
        public_key_path=public_key_path,
        pub_key=pub_key)

main()