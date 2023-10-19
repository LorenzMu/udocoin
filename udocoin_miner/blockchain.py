import datetime
import hashlib
import json
from udocoin_dataclasses import Block, BlockData, TransactionData

class Blockchain:
    def __init__(self):
        #If no blockchain is found in the network, create your own blockchain 
        self.blockchain = []

        if self.find_consensus_blockchain() == None:
            genesis_block = Block(data = BlockData(transaction_list=[TransactionData("root","udos_wallet",str(datetime.datetime.now()),50.2)]),
                                  proof_of_work= 1, prev_hash= "0", index = 1)
            self.blockchain.append(genesis_block)
    
    #Do some arbitrary math to "work" the system
    def generate_pre_hash(self, new_proof: int, previous_proof: int, index: int) -> str:
        pre_hash = str((((new_proof ** 3) + 1) * ((previous_proof**3)+1)) + index)
        return pre_hash.encode()

    def hash(self, block: Block) -> str:
        return hashlib.sha256(str(block).encode()).hexdigest()

    def validate_blockchain(self) -> bool:
        previous_block = self.blockchain[0]
        block_index = 1

        while block_index < len(self.blockchain):
            block = self.blockchain[block_index]
            # Check if the previous hash of the current block is the same as the hash of it's previous block
            if block.prev_hash != self.hash(previous_block):
                return False

            previous_proof = previous_block.proof_of_work
            index, data, proof_of_work = block.index, block.data, block.proof_of_work
            hash_operation = hashlib.sha256(
                self.generate_pre_hash(
                    new_proof=proof_of_work,
                    previous_proof=previous_proof,
                    index=index,
                    data=data,
                )
            ).hexdigest()

            if hash_operation[:4] != "0000":
                return False

            previous_block = block
            block_index += 1

        return True

    def get_previous_block(self) -> Block | None:
        return self.blockchain[-1] if len(self.blockchain) > 0 else None

    #Exponential block value decay
    def get_block_value(self, index):
        return 1024 / (2**((index//100)))

    
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
        
        

# my_blockchain = Blockchain(proof_to_start_with=1)
# my_blockchain.mine_block(BlockData(transaction_list=[TransactionData("udos_wallet","seans_wallet",str(datetime.datetime.now()),50.2)]))
# for i in my_blockchain.blockchain:  
#     print("\n",i,"\n")

# print(my_blockchain.validate_blockchain())

# my_blockchain.blockchain[0].data.transaction_list[0].destination_address = "matthis_wallet"

# print(my_blockchain.validate_blockchain())