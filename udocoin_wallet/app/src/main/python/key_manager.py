from cryptography.hazmat import backends
from cryptography.hazmat.primitives.asymmetric import rsa
from cryptography.hazmat.primitives import serialization
import os

def get_base_path():
    directory_name = ".udocoin"
    return os.path.join(os.path.expanduser("~"), directory_name) if os.name == 'nt' else os.path.join(os.path.expanduser(f"~/{directory_name}"))

def get_public_key_path():
    return os.path.join(get_base_path(),"pub_key.pub")

def get_private_key_path():
    return os.path.join(get_base_path(),"priv_key")

def generate_private_key()->bytes:
    private_key_obj = rsa.generate_private_key(
        public_exponent=65537,
        key_size=512,
        backend=backends.default_backend()
    )
    private_key_bytes = private_key_obj.private_bytes(
        encoding=serialization.Encoding.PEM, 
        encryption_algorithm=serialization.NoEncryption(), 
        format=serialization.PrivateFormat.TraditionalOpenSSL)
    return private_key_bytes

def generate_private_key_string()->str:
    return str(generate_private_key())
        
def generate_public_key_from_private_key(private_key:bytes)->bytes:
    private_key_obj = serialization.load_pem_private_key(
        data=private_key,
        password=None,
        backend=backends.default_backend())
    public_key_obj = private_key_obj.public_key()
    public_key_bytes = public_key_obj.public_bytes(
        encoding=serialization.Encoding.PEM, 
        format=serialization.PublicFormat.SubjectPublicKeyInfo)
    return public_key_bytes

def generate_public_key_from_private_key_string(private_key:str)->bytes:
    private_key = bytes(private_key, 'utf-8')
    return generate_public_key_from_private_key(private_key)

def generate_public_key_string_from_private_key_string(private_key:str)->str:
    return str(generate_public_key_from_private_key_string(private_key))

def safe_public_key_from_private_key_string(private_key:str)->str:
    private_key = bytes(private_key, 'utf-8')
    public_key = generate_public_key_from_private_key(private_key)
    safe_public_key_to_file(public_key)
    return str(public_key)

def is_valid_key_pair(private_key:bytes,public_key:bytes)->bool:
    public_key_bytes = generate_public_key_from_private_key(private_key)
    return (public_key_bytes == public_key)

def is_valid_key_pair_strings(private_key:str,public_key:str)->bool:
    private_key_bytes = bytes(private_key, 'utf-8')
    public_key_bytes = bytes(public_key, 'utf-8')
    return is_valid_key_pair(private_key_bytes,public_key_bytes)

def is_valid_public_key(public_key:bytes)->bool:
    try:
        serialization.load_pem_public_key(
            data=public_key,
            backend=backends.default_backend()
        )
    except:
        return False
    return True

def is_valid_public_key_string(public_key:str)->bool:
    public_key_bytes = bytes(public_key, 'utf-8')
    return is_valid_public_key(public_key_bytes)

def is_valid_private_key(private_key:bytes)->bool:
    try:
        generate_public_key_from_private_key(private_key)
    except:
        return False
    return True

def is_valid_private_key_string(private_key:str)->bool:
    private_key_bytes = bytes(private_key, 'utf-8')
    return is_valid_private_key(private_key_bytes)

def get_public_key_from_file()->bytes:
    public_key = get_public_key_from_file_string()
    return bytes(public_key, 'utf-8')

def get_public_key_from_file_string()->str:
    path = get_public_key_path()
    with open(path,"r") as file:
        return file.read()

def get_private_key_from_file()->bytes:
    private_key = get_private_key_from_file_string()
    return bytes(private_key, 'utf-8')

def get_private_key_from_file_string()->str:
    path = get_private_key_path()
    with open(path,"r") as file:
        return file.read()
    
def write_binary_file(base_path:str,path:str,content:bytes):
    if not os.path.exists(base_path):
        os.makedirs(base_path)
    with open(path,"wb") as binary_file:
        binary_file.write(content)
    
def safe_public_key_to_file(public_key:bytes):
    write_binary_file(
        base_path=get_base_path(),
        path=get_public_key_path(),
        content=public_key)

def safe_public_key_to_file_string(public_key:str):
    public_key_bytes = bytes(public_key, 'utf-8')
    safe_public_key_to_file(public_key_bytes)

def safe_private_key_to_file(private_key:bytes):
    write_binary_file(
        base_path=get_base_path(),
        path=get_private_key_path(),
        content=private_key)

def safe_private_key_to_file_string(private_key:str):
    private_key_bytes = bytes(private_key, 'utf-8')
    safe_private_key_to_file(private_key_bytes)

def has_valid_keys()->bool:
    print("Searching for vaild keys...")
    try:
        private_key = get_private_key_from_file()
        print("Private key: " + str(private_key))
        public_key = get_public_key_from_file()
        print("Public key: " + str(public_key))
        print("Private key is valid: " + str(is_valid_private_key(private_key)))
        print("Keypair is valid: " + str(is_valid_key_pair(private_key,public_key)))
        return is_valid_private_key(private_key) and is_valid_key_pair(private_key,public_key)
    except:
        return False
    
def generate_and_safe_new_key_pair():
    private_key_bytes = generate_private_key()
    public_key_bytes = generate_public_key_from_private_key(private_key_bytes)
    safe_private_key_to_file(private_key_bytes)
    safe_public_key_to_file(public_key_bytes)