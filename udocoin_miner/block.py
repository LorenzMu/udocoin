import datetime
import hashlib
import json
from dataclasses import dataclass

@dataclass
class TransactionData:
    origin_address: str
    destination_address: str
    timestamp: str
    amount: float

@dataclass
class BlockData:
    transaction_list: list[TransactionData]

@dataclass
class Block:
    data: BlockData
    proof: int
    prev_hash: str
    index: int

#print(Block(data=BlockData(origin_address="a",destination_address="b",timestamp="01.01.1970",amount=2),proof=1,prev_hash="no",index=1))