import dataclasses 
import datetime
import json
import base64
from cryptography.hazmat import primitives,backends
from cryptography.hazmat.primitives import asymmetric,serialization
from cryptography.exceptions import InvalidSignature

#This file implements the same functions used in the wallet app to create transactions
#This lets you create transaction requests using your PC if you do not wish to use the wallet app

print("INITIALIZING")

@dataclasses.dataclass
class TransactionData:
    origin_public_key: str
    destination_public_key: str
    timestamp: datetime.datetime
    amount: float

@dataclasses.dataclass
class SignedTransaction:
    origin_public_key: str
    signature: str
    message: str

def sign_transaction(private_key, public_key:bytes, transaction_data: TransactionData) -> SignedTransaction:

    transaction_data = dataclasses.asdict(transaction_data)
    transaction_data["timestamp"] = str(transaction_data["timestamp"])
    transaction_data["origin_public_key"] = transaction_data["origin_public_key"]
    transaction_data = json.dumps(transaction_data).encode('utf-8')

    signed_transaction_data = private_key.sign(
        transaction_data,
        asymmetric.padding.PSS(
            mgf=asymmetric.padding.MGF1(primitives.hashes.SHA256()),
            salt_length=asymmetric.padding.PSS.MAX_LENGTH
        ),
        primitives.hashes.SHA256()
        )

    return SignedTransaction(public_key, signed_transaction_data, transaction_data)

def verify_transaction(signed_transaction: SignedTransaction) -> TransactionData:
    pub_key_obj = serialization.load_pem_public_key(signed_transaction.origin_public_key, backends.default_backend())

    try:
        pub_key_obj.verify(
            signed_transaction.signature,
            signed_transaction.message,
            asymmetric.padding.PSS(
                mgf=asymmetric.padding.MGF1(primitives.hashes.SHA256()),
                salt_length=asymmetric.padding.PSS.MAX_LENGTH
            ),
            primitives.hashes.SHA256()
        )
        return TransactionData(**json.loads(signed_transaction.message))
        
    except InvalidSignature:
        return "Message signature could not be verified!"

def create_transaction(private_key:str,public_key:str,destination_public_key:str,amount:float)->dict:
    private_key_obj = serialization.load_pem_private_key(
        data=bytes(private_key,'utf-8'),
        password=None,
        backend=backends.default_backend()
    )
    transaction = TransactionData(
        origin_public_key=str(public_key),
        destination_public_key=destination_public_key,
        timestamp=datetime.datetime.now(),
        amount=amount
    )
    signed_transaction = sign_transaction(
        private_key=private_key_obj,
        public_key=bytes(public_key,'utf-8'),
        transaction_data=transaction
    )
    verify_transaction(signed_transaction)
    return export_signed_transaction(signed_transaction)

#Makes binary data serializable
def export_signed_transaction(signed_transaction:SignedTransaction)->str:
    signed_transaction.origin_public_key = signed_transaction.origin_public_key.decode("utf-8")
    signed_transaction.signature = base64.b64encode(signed_transaction.signature).decode('utf-8')
    signed_transaction.message = signed_transaction.message.decode("utf-8")
    return json.dumps(signed_transaction,cls=EnhancedJSONEncoder) 


#This is required for dataclass object json serialization
#Taken from https://stackoverflow.com/questions/51286748/make-the-python-json-encoder-support-pythons-new-dataclasses
class EnhancedJSONEncoder(json.JSONEncoder):
    def default(self, o):
        if dataclasses.is_dataclass(o):
            return dataclasses.asdict(o)
        return super().default(o)
    

def get_priv_key_from_path(path:str) -> str:
    with open(path, "r") as f:
        return f.read()

def get_pub_key_from_path(path: str) -> str:
    with open(path, "r") as f:
        return f.read()
    
priv_key_path = input("Please enter your private key's absolute path: ")
pub_key_path = input("Please enter your public key's absolute path: ")

#i.e. enter something like
#C:/Users/loren/.udocoin/priv_key
#C:/Users/loren/.udocoin/pub_key.pub

destination_adress = input("Please enter your destination address: ")
amount = float(input("Please enter the amount of Udocoins you wish to send: "))

priv_key_str = get_priv_key_from_path(priv_key_path)
pub_key_str = get_pub_key_from_path(pub_key_path)

transaction_request = create_transaction(priv_key_str,pub_key_str,destination_adress, amount)
print(transaction_request)


import requests
x = requests.post("http://localhost:5000/miner/post_transaction", json= json.loads(transaction_request))
print("POSTED")
print(x)
