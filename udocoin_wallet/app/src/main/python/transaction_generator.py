import datetime
from dataclasses import dataclass,asdict
from json import dumps, loads
from cryptography.hazmat.primitives import hashes
from cryptography.hazmat.primitives.asymmetric import padding

@dataclass
class TransactionData:
    origin_public_key: str
    destination_public_key: str
    timestamp: datetime.datetime
    amount: float

#message is a json dump of a TransactionData object
@dataclass
class SignedTransaction:
    origin_public_key: str
    signature: str
    #message may not be passed in the final implementation as it is redundant; the message is encoded in the signature
    message: str

def sign_transaction(priv_key, pub_key_bytes, transaction_data: TransactionData) -> SignedTransaction:

    transaction_data = asdict(transaction_data)
    transaction_data["timestamp"] = str(transaction_data["timestamp"])
    transaction_data["origin_public_key"] = transaction_data["origin_public_key"]
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