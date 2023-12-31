from app.blockchain_modules.udocoin_dataclasses import TransactionData, SignedTransaction
from json import dumps, loads
from datetime import datetime
from dataclasses import asdict
from cryptography.hazmat.primitives.serialization import load_pem_private_key, load_pem_public_key
from cryptography.hazmat.backends import default_backend
from cryptography.hazmat.primitives import hashes
from cryptography.hazmat.primitives.asymmetric import padding
from cryptography.hazmat.primitives.asymmetric.rsa import RSAPrivateKey, RSAPublicKey
from base64 import decode, b64encode
from cryptography.exceptions import InvalidSignature
import os,re

def sign_transaction(priv_key: RSAPrivateKey, pub_key_bytes: bytes, transaction_data: TransactionData) -> SignedTransaction:

    transaction_data = asdict(transaction_data)
    transaction_data["timestamp"] = str(transaction_data["timestamp"])
    transaction_data = dumps(transaction_data).encode('utf-8')

    signed_transaction_data = priv_key.sign(
        transaction_data,
        padding.PSS(
            mgf=padding.MGF1(hashes.SHA256()),
            salt_length=padding.PSS.MAX_LENGTH
        ),
        hashes.SHA256()
        )

    return SignedTransaction(pub_key_bytes, signed_transaction_data, transaction_data)

#Verifies transaction signature's authenticity
def verify_transaction(signed_transaction: SignedTransaction) -> TransactionData:
    # print("Verifying transaction....")
    # print("=================================")
    # print(signed_transaction.origin_public_key)
    # print("type: " + str(type(signed_transaction.origin_public_key)))
    # print("len: " + str(len(signed_transaction.origin_public_key)))
    # print("---------------------------------")
    # print("transformed:")
    # print(formate_key(signed_transaction.origin_public_key))
    # print("type: " + str(type(formate_key(signed_transaction.origin_public_key))))
    # print("len: " + str(len(formate_key(signed_transaction.origin_public_key))))
    # print("=================================")
    
    pub_key_obj = load_pem_public_key(signed_transaction.origin_public_key, default_backend())

    try:
        pub_key_obj.verify(
            signed_transaction.signature,
            signed_transaction.message,
            padding.PSS(
                mgf=padding.MGF1(hashes.SHA256()),
                salt_length=padding.PSS.MAX_LENGTH
            ),
            hashes.SHA256()
        )

        # print("Message signature was verified, the message is as follows:")
        # print("~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~")
        # print(signed_transaction.message)
        # print("~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~")

        #Check that origin public key in message is the same as the origin public key in the signed_transaction object
        #If this is not done, an attacker could sign a message with their private key, leaving somebody else's public key in tge
        t_data = TransactionData(**loads(signed_transaction.message))
        if type(t_data.origin_public_key) == bytes:
            if t_data.origin_public_key == signed_transaction.origin_public_key:
                return t_data
            
        elif type(t_data.origin_public_key) == str:
            comp_variable = bytes(t_data.origin_public_key, "utf-8")
            if comp_variable == signed_transaction.origin_public_key:
                return t_data
        return None
        
    except InvalidSignature:
        return None  #"Message signature could not be verified!"

def get_priv_key() -> RSAPrivateKey:
    key_str = os.environ["PRIVKEY"]
    key_bytes = bytes(key_str, 'utf-8')
    return load_pem_private_key(key_bytes,None,default_backend)

def get_pub_key() -> RSAPublicKey:
    key_str = os.environ["PUBKEY"]
    key_bytes = bytes(key_str, 'utf-8')
    return load_pem_public_key(key_bytes,default_backend)

def get_pub_key_string() -> str:
    return os.environ["PUBKEY"]

def get_priv_key_from_path(path:str) -> str:
    with open(path, "r") as f:
        return f.read()

def get_pub_key_from_path(path: str) -> str:
    with open(path, "r") as f:
        return f.read()
