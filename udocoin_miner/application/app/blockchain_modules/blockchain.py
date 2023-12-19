import datetime
import hashlib
import json
from app.blockchain_modules.udocoin_dataclasses import *
import dataclasses
from base64 import b64encode, b64decode
import dacite
from copy import deepcopy
from app.blockchain_modules.ReturnValues import ReturnValues

#This class' basic structure is taken from https://github.com/sixfwa/blockchain-fastapi/blob/main/blockchain.py
#Its functionality has been heavily extended by us, however.
class Blockchain:
    def __init__(self):
        self.blockchain: list[Block] = []
        self.balances: dict[str, float] = {}
        self.index_confirmed = -1

        #If no blockchain is found in the network, create your own blockchain 
        if self.get_consensus_blockchain(self.blockchain) == None:
            genesis_block = Block(data = BlockData(transaction_list=[]),
                                  proof_of_work= 1, prev_hash= "0", index = 0)
            self.append_blockchain(genesis_block)
            
    #Extends blockchain and updates account balances
    def append_blockchain(self, block: Block) -> ReturnValues:
        self.blockchain.append(block)
        print("appending new block with prev_hash:", block.prev_hash)
        print("This block's hash is: ", self.hash(block))
        #If blockchain no longer valid: Remove newly appended block
        if len(self.blockchain) > 1:
            if not self.validate_blockchain(self.blockchain):
                self.blockchain.pop()
                return ReturnValues.SingleBlockRejected
            
            self.update_balances()
            
            return ReturnValues.SingleBlockAppended
    
    #Do some arbitrary math to "work" the system
    #This formula contains data from the previous block, so work on new blocks cannot be done before the previous block exists
    def generate_pre_hash(self, new_proof: int, previous_proof: int, index: int, data: str) -> str:
        pre_hash = str((((new_proof ** 3) + 1) * ((previous_proof**3)+1)) + index) + str(data)
        return pre_hash.encode()

    def hash(self, block: Block) -> str:
        return hashlib.sha256(str(block).encode()).hexdigest()

    def validate_blockchain(self, blockchain: list[Block]) -> bool:
        print('************ Validating Blockchain ****************')
        previous_block = blockchain[0]
        block_index = 1

        while block_index < len(blockchain):
            # print("index: ",block_index)
            block = blockchain[block_index]
            # Check if the previous hash of the current block is the same as the hash of its previous block
            if block.prev_hash != self.hash(previous_block) and previous_block != blockchain[0]:
                print("Wrong previous hash detected, block rejected!")
                return False
            
            #Check if the given proof_of_work lines up with the required amount of null bytes
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

            if hash_operation[:6] != "000000" and index > 1:
                print(hash_operation)
                print("Invalid proof of work detected, block rejected!")
                return False
            
            #If the mining reward has been altered, reject the block
            if block.block_value  != self.get_block_value(index):
                print("Wrong block value detected, block rejected!")
                return False

            previous_block = block
            block_index += 1

        print("Validated Blockchain of length",len(blockchain))
        return True

    def get_previous_block(self) -> Block | None:
        return self.blockchain[-1] if len(self.blockchain) > 0 else None

    #Exponential block value decay to combat currency inflation
    def get_block_value(self, index):
        return 1024 / (2**(index//1000))


    #Account balance is valid once blocks are 5 blocks deep in the blockchain
    #At this point we must check how many blocks changed when the blockchain updated
    def update_balances(self):
         #If there are 5 or more blocks, the blockchain is long enough to start updating balances 
        if len(self.blockchain) >= 5:
            #Update balances for each newly confirmable block
            while self.index_confirmed < len(self.blockchain)-5:
                self.index_confirmed+=1
                print("CONFIRMING INDEX: ", self.index_confirmed)
                # print(self.balances)
                new_balances = self.balances

                block = self.blockchain[self.index_confirmed]
                
                #Add mining reward to block author's address
                if block.block_author_public_key in new_balances.keys():
                    new_balances[block.block_author_public_key] += block.block_value
                else:
                    new_balances[block.block_author_public_key] = block.block_value

                #Subtract and add balances for each transaction in each block
                for signed_transaction in block.data.transaction_list:
                    message = TransactionData(**json.loads(signed_transaction.message))
                    origin_public_key = signed_transaction.origin_public_key.decode('utf-8')
                    if origin_public_key in new_balances.keys():
                        if new_balances[origin_public_key] >= message.amount:
                            new_balances[origin_public_key] -= message.amount
                            if message.destination_public_key in new_balances.keys():
                                new_balances[message.destination_public_key] += message.amount
                            else:
                                new_balances[message.destination_public_key] = message.amount
                        else:
                            self.blockchain.pop()
                            print("Account Balance of Origin Address too low! Block rejected!")
                            return False
                    else:
                        self.blockchain.pop()
                        print("Origin Address not found. Block rejected!")
                        return False
                print("CONFIRMED BLOCK", self.index_confirmed)
                self.balances = new_balances

    #Converts all binary data into JSON serializable form
    def export_blockchain(self, unconfirmed_blocks = False, single_block = False) -> str:
        exported_blockchain = []

        if self.validate_blockchain(self.blockchain):
            for block in self.blockchain:
                serializable_block_data = []
                for signed_transaction in block.data.transaction_list:
                    if signed_transaction is not None:
                        serializable_block_data.append(serialize_signed_transaction(signed_transaction))
                        
                serializable_block_data = SerializableBlockData(serializable_block_data)
                serializable_block = SerializableBlock(data=serializable_block_data, proof_of_work= block.proof_of_work,
                                                        prev_hash=block.prev_hash,index=block.index,block_author_public_key= block.block_author_public_key,
                                                        block_value=block.block_value)
                exported_blockchain.append(serializable_block)
    
            #If only returning the unconfirmed blocks requested by a connected server
            if unconfirmed_blocks:
                return json.dumps(exported_blockchain[-4:], cls=EnhancedJSONEncoder)
            if single_block:
                return json.dumps(exported_blockchain[-1], cls=EnhancedJSONEncoder)
            return json.dumps(exported_blockchain, cls=EnhancedJSONEncoder)
        else:
            print("Export failed due to invalid blockchain!")
            return False


    #Turns JSON serializable data back into binary data, which can be used by cryptography functions
    def import_blockchain(self, blockchain:str) -> list[Block]:
        loaded_blockchain = json.loads(blockchain) #This is a list[SerializableBlock]
        serializable_blockchain: list[SerializableBlock] = []
        imported_blockchain: list[Block] = []
        

        for serializable_block in loaded_blockchain:
            serializable_blockchain.append(dacite.from_dict(data_class=SerializableBlock, data={k: v for k, v in serializable_block.items() if v is not None}))

        for serializable_block in serializable_blockchain:
            signed_transactions_in_block = []
            for serializable_signed_transaction in serializable_block.data.transaction_list:
                if serializable_signed_transaction is not None:
                    signed_transaction = deserialize_signed_transaction(serializable_signed_transaction)
                    signed_transactions_in_block.append(signed_transaction)
            
            block_data = BlockData(signed_transactions_in_block)
            block = Block(data=block_data, proof_of_work= serializable_block.proof_of_work, prev_hash= serializable_block.prev_hash,
                          index= serializable_block.index, block_author_public_key= serializable_block.block_author_public_key,
                          block_value= serializable_block.block_value)
            imported_blockchain.append(block)

        return imported_blockchain


    #Gets passed a list of blockchains from our P2P network to find a consensus blockchain
    def get_consensus_blockchain(self, list_of_blockchains: list[list[Block]]) -> list[Block] | None:

        #First delete any blockchains that can not be validated
        validated_blockchains = [blch for blch in list_of_blockchains if self.validate_blockchain(blch)]

        if len(validated_blockchains) >= 1:
            #Next get the longest blockchains
            longest_blockchains = [blch for blch in validated_blockchains if (len(blch) == max([len(x) for x in validated_blockchains]))]

            #If there is only one longest blockchain, it is the consensus blockchain
            if len(longest_blockchains) == 1:
                return longest_blockchains[0]

            #If there are multiple blockchains of equal length, choose the one with the highest proof of work
            else:
                highest_pow_blockchains = [blch for blch in longest_blockchains if (blch[-1].proof_of_work == max([x[-1].proof_of_work for x in longest_blockchains]))]

                #If only one blockchain has the highest proof of work, it is the consensus blockchain
                #If there are multiple blockchains of equal length and equal highest proof of work, the network will eventually settle
                #on a canonical blockchain, because, eventually, a block will be mined without a different miner finding it simultaneously.
                #When this happens, the block will propagate throughout the network and the shorter blockchain fork will be eliminated.
                return highest_pow_blockchains[0]

        #If no consensus blockchain is found, create your own in __init__
        else:
            return None

    # #Undoes a transaction; Gets called when one or multiple blocks are replaced in the blockchain, not implemented, because rollbacks are not implemented
    # def undo_transaction(self, signed_transaction: SignedTransaction):
    #     message = TransactionData(**json.loads(signed_transaction.message))
    #     origin_public_key = message.origin_public_key
       
    #     self.balances[origin_public_key] += message.amount
    #     self.balances[message.destination_public_key] -= message.amount


    #Checks if new block's prev hash lines up with previous block's hash
    def detect_blockchain_append(self, new_block: Block):
        #Hash previous Block and see if hashes allign
        return_value = ReturnValues.SingleBlockRejected
        if self.hash(self.blockchain[-1]) == new_block.prev_hash:
            return_value = self.append_blockchain(new_block)
        if return_value == ReturnValues.SingleBlockRejected:
            print("Block Rejected")
        return return_value
    
    #Checks if there was a recent fork in the blockchain. If there was, it replaces blocks up to 5 blocks deep
    def detect_multiple_changes(self, multiple_blocks: list[Block]):
        #first check where the fork occured
        fork_index = "NaN"
        for block in multiple_blocks:
            if block.prev_hash != self.hash(self.blockchain[block.index-1]):
                fork_index = block.index
                break
        #If a fork was detected in yet unconfirmed blocks, simply replace all blocks following the fork with the blocks received via the network
        if fork_index != "NaN":
            for block in multiple_blocks:
                if block.index >= fork_index-1:
                    try:
                        self.blockchain[fork_index] = block
                    except IndexError:
                        self.blockchain.append(block)
                    self.update_balances()
            return ReturnValues.BlocksReplaced, fork_index
        return ReturnValues.BlocksRejected, "NaN"

#This is required for dataclass object json serialization
#Taken from https://stackoverflow.com/questions/51286748/make-the-python-json-encoder-support-pythons-new-dataclasses
class EnhancedJSONEncoder(json.JSONEncoder):
        def default(self, o):
            if dataclasses.is_dataclass(o):
                return dataclasses.asdict(o)
            return super().default(o)
