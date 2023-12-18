from base64 import b64decode, b64encode
import datetime
from dataclasses import dataclass

#Dataclasses to more easily and stably use the required data structures

@dataclass
class TransactionData:
    origin_public_key: str
    destination_public_key: str
    timestamp: datetime.datetime
    amount: float

#message is a json dump of a TransactionData object
@dataclass
class SignedTransaction:
    origin_public_key: bytes
    signature: bytes
    message: bytes

@dataclass
class SerializableSignedTransaction:
    origin_public_key: str
    signature: str
    message: str

@dataclass
class BlockData:
    transaction_list: list[SignedTransaction]

@dataclass
class SerializableBlockData:
    transaction_list: list[SerializableSignedTransaction]

@dataclass
class Block:
    data: BlockData
    proof_of_work: int
    prev_hash: str
    index: int
    block_author_public_key: str=None
    block_value: float=None

@dataclass
class SerializableBlock:
    data: SerializableBlockData
    proof_of_work: int
    prev_hash: str
    index: int
    block_author_public_key: str=None
    block_value: float=None

@dataclass
class AccountBalance:
    public_key: str
    balance: float

#To be able to use cryptography functions, bytes objects are required
def deserialize_signed_transaction(serializable_signed_transaction: SerializableSignedTransaction) -> SignedTransaction:
    origin_public_key = serializable_signed_transaction.origin_public_key.encode('utf-8')
    signature = b64decode(serializable_signed_transaction.signature)
    message = serializable_signed_transaction.message.encode('utf-8')

    return SignedTransaction(origin_public_key=origin_public_key, signature=signature, message=message)

#To send JSON, bytes objects need to be converted to strings
def serialize_signed_transaction(signed_transaction: SignedTransaction) -> SerializableSignedTransaction:
    origin_public_key = signed_transaction.origin_public_key.decode("utf-8")
    signature = b64encode(signed_transaction.signature).decode('utf-8')
    message = signed_transaction.message.decode("utf-8")

    return SerializableSignedTransaction(origin_public_key=origin_public_key, signature=signature, message=message)
