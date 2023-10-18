from block import TransactionData, SignedTransaction
from json import dumps, loads
from datetime import datetime
from dataclasses import asdict
from cryptography.hazmat.primitives.serialization import load_pem_private_key, load_pem_public_key
from cryptography.hazmat.backends import default_backend
from cryptography.hazmat.primitives import hashes
from cryptography.hazmat.primitives.asymmetric import padding
from base64 import decode, b64encode
from cryptography.exceptions import InvalidSignature


def sign_transaction(priv_key, pub_key_bytes, transaction_data: TransactionData) -> SignedTransaction:

    transaction_data = asdict(transaction_data)
    transaction_data["timestamp"] = str(transaction_data["timestamp"])
    transaction_data["origin_public_key"] = b64encode(transaction_data["origin_public_key"]).decode("utf-8")
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

def verify_transaction(signed_transaction: SignedTransaction) -> TransactionData:
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
        return TransactionData(**loads(signed_transaction.message))
    except InvalidSignature:
        return "Message signature could not be verified!"

def get_priv_key(path: str):
    with open(path, "rb") as f:
        pemlines = f.read()
        return load_pem_private_key(pemlines, None, default_backend())

def get_pub_key(path: str):
    with open(path, "rb") as f:
        pemlines = f.read()
        return load_pem_public_key(pemlines, default_backend())

def get_pub_key_string(path: str) -> str:
    with open(path, "rb") as f:
        return f.read()


my_transaction_data = TransactionData(get_pub_key_string("pub_key.txt"), "schmarn", timestamp=datetime.now(), amount=50)

signed_trans = sign_transaction(get_priv_key("priv_key.txt"), get_pub_key_string("pub_key.txt"), my_transaction_data)



print(verify_transaction(signed_trans))


signed_trans.message = signed_trans.message + b"ich bin ein kleiner hacker"

print(verify_transaction(signed_trans))

# print(signed_trans.origin_public_key)
# print("~~~~~~~~~~~~~~")
# print(signed_trans.signed_transaction)

# print(type(signed_trans.origin_public_key))
# print(type(signed_trans.signed_transaction))


