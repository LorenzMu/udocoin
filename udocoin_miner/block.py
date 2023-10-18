import datetime
import hashlib
import json
from dataclasses import dataclass

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
    message: str

@dataclass
class BlockData:
    transaction_list: list[TransactionData]

@dataclass
class Block:
    data: BlockData
    proof_of_work: int
    prev_hash: str
    index: int
    block_author_public_key: str
    block_value: float

#print(Block(data=BlockData(origin_address="a",destination_address="b",timestamp="01.01.1970",amount=2),proof=1,prev_hash="no",index=1))