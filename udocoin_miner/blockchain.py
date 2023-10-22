import datetime
import hashlib
import json
from udocoin_dataclasses import Block, BlockData, TransactionData, AccountBalance, SignedTransaction
import dataclasses
from base64 import b64encode, b64decode
import dacite
from copy import deepcopy

class Blockchain:
    def __init__(self):
        #If no blockchain is found in the network, create your own blockchain 
        self.blockchain: list[Block] = []
        self.balances: dict[str, float] = {}

        if self.find_consensus_blockchain() == None:
            genesis_block = Block(data = BlockData(transaction_list=[]),
                                  proof_of_work= 1, prev_hash= "0", index = 0)
            self.update_blockchain(genesis_block)

    def update_blockchain(self, block: Block):
        self.blockchain.append(block)
        print("appending new block with prev_hash:", block.prev_hash)
        print("This block's hash is: ", self.hash(block))
        #If blockchain no longer valid: Remove newly appended block
        if len(self.blockchain) > 1:
            if not self.validate_blockchain(self.blockchain):
                self.blockchain.pop()
                raise Exception("Blockchain not valid, block rejected!")
            #if len(self.blockchain)%100 == 0:
            self.update_balances(index_start = (len(self.blockchain)-1))
    
    #Do some arbitrary math to "work" the system
    def generate_pre_hash(self, new_proof: int, previous_proof: int, index: int, data: str) -> str:
        pre_hash = str((((new_proof ** 3) + 1) * ((previous_proof**3)+1)) + index) + str(data)
        return pre_hash.encode()

    def hash(self, block: Block) -> str:
        return hashlib.sha256(str(block).encode()).hexdigest()

    def validate_blockchain(self, blockchain: list[Block]) -> bool:
        previous_block = blockchain[0]
        block_index = 1

        while block_index < len(blockchain):
            block = blockchain[block_index]
            # Check if the previous hash of the current block is the same as the hash of its previous block
            if block.prev_hash != self.hash(previous_block) and previous_block != blockchain[0]:
                raise Exception("Wrong previous hash detected, block rejected!")
                return False

            previous_proof = previous_block.proof_of_work
            index, previous_data, proof_of_work = block.index, previous_block.data, block.proof_of_work
            hash_operation = hashlib.sha256(
                self.generate_pre_hash(
                    new_proof=proof_of_work,
                    previous_proof=previous_proof,
                    index=index,
                    data=previous_data
                )
            ).hexdigest()

            if hash_operation[:8] != "00000000" and index > 1:
                print(hash_operation)
                raise Exception("Invalid proof of work detected, block rejected!")
                return False

            if block.block_value  != self.get_block_value(index):
                raise Exception("Wrong block value detected, block rejected!")
                return False

            previous_block = block
            block_index += 1

        return True

    def get_previous_block(self) -> Block | None:
        return self.blockchain[-1] if len(self.blockchain) > 0 else None

    #Exponential block value decay
    def get_block_value(self, index):
        return 1024 / (2**(index//100))
    
    #Here is where we will access our decentralized P2P network to find our consensus blockchain
    #Maybe refactor into different class
    def find_consensus_blockchain(self) -> bool | None:

        found_blockchains = ["juhu","jippie"]
        consensus_blockchain = "juhu"

        if False:
            self.blockchain = consensus_blockchain
            return True
        
        #If no consensus blockchain is found, create your own in __init__
        else:
            return None
    
    def update_balances(self, index_start):
        new_balances = self.balances
        for block in self.blockchain[index_start:]:
            #Get Block values summed per public key
            balance_from_mining = AccountBalance(block.block_author_public_key, block.block_value)
            if block.block_author_public_key in new_balances.keys():
                new_balances[block.block_author_public_key] += block.block_value
            else:
                new_balances[block.block_author_public_key] = block.block_value

            #Subtract and add balances for each transaction in each block
            for signed_transaction in block.data.transaction_list:
                message = TransactionData(**json.loads(signed_transaction.message))
                if signed_transaction.origin_public_key in new_balances.keys():
                    if new_balances[signed_transaction.origin_public_key] >= message.amount:
                        new_balances[signed_transaction.origin_public_key] -= message.amount
                        if message.destination_public_key in new_balances.keys():
                            new_balances[message.destination_public_key] += message.amount
                        else:
                            new_balances[message.destination_public_key] = message.amount
                    else:
                        self.blockchain.pop()
                        raise Exception("Account Balance of Origin Adress too low! Block rejected!")
                else:
                    self.blockchain.pop()
                    raise Exception("Origin Address not found. Block rejected!")

        self.balances = new_balances

    def export_blockchain(self):
        if self.validate_blockchain(self.blockchain):
            exported_blockchain = deepcopy(self.blockchain)
            for block in exported_blockchain:
                for signed_transaction in block.data.transaction_list:
                    if signed_transaction is not None:
                        signed_transaction.origin_public_key = signed_transaction.origin_public_key.decode("utf-8")
                        #signed_transaction.signature = signed_transaction.signature.decode("utf-8")
                        signed_transaction.signature = b64encode(signed_transaction.signature).decode('utf-8')
                        signed_transaction.message = signed_transaction.message.decode("utf-8")
                if block.block_author_public_key is not None:
                    block.block_author_public_key = block.block_author_public_key.decode("utf-8")
    
            return json.dumps(exported_blockchain, cls=EnhancedJSONEncoder)
        else:
            raise Exception("Export failed due to invalid blockchain!")


    
    def import_blockchain(self, blockchain):
        loaded_blockchain = json.loads(blockchain)
        imported_blockchain = []

        for block in loaded_blockchain:
            imported_blockchain.append(dacite.from_dict(data_class=Block, data={k: v for k, v in block.items() if v is not None}))

        for block in imported_blockchain:
                for signed_transaction in block.data.transaction_list:
                    if signed_transaction is not None:
                        signed_transaction.origin_public_key = signed_transaction.origin_public_key.encode('utf-8')
                        #signed_transaction.signature = signed_transaction.signature.decode("utf-8")
                        signed_transaction.signature = b64decode(signed_transaction.signature)#.encode('utf-8')
                        signed_transaction.message = signed_transaction.message.encode('utf-8')
                if block.block_author_public_key is not None:
                    block.block_author_public_key = block.block_author_public_key.encode('utf-8')
        

        if self.validate_blockchain(imported_blockchain):
            print("import succesful!")
            return loaded_blockchain
        
        
class EnhancedJSONEncoder(json.JSONEncoder):
        def default(self, o):
            if dataclasses.is_dataclass(o):
                return dataclasses.asdict(o)
            return super().default(o)

# my_blockchain = Blockchain(proof_to_start_with=1)
# my_blockchain.mine_block(BlockData(transaction_list=[TransactionData("udos_wallet","seans_wallet",str(datetime.datetime.now()),50.2)]))
# for i in my_blockchain.blockchain:  
#     print("\n",i,"\n")

# print(my_blockchain.validate_blockchain())

# my_blockchain.blockchain[0].data.transaction_list[0].destination_address = "matthis_wallet"

# print(my_blockchain.validate_blockchain())