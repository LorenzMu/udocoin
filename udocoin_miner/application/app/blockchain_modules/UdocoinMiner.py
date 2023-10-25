from app.blockchain_modules.blockchain import Blockchain
from app.blockchain_modules.udocoin_dataclasses import *
from app.blockchain_modules.transactions import *
import os
import threading

#Separate class, because different people may want to implement it differently
#The blockchain as the central data structure is the consistent class and may not have different implementations
class UdocoinMiner:
    def __init__(self, proof_to_start_with: int):
        self.blockchain_instance = Blockchain()
        self.mempool= BlockData([])
        self.proof_to_start_with = proof_to_start_with
        self.mining = True

    def stop_mining(self):
        print("Stopping mining...")
        self.mining = False

    def continue_mining(self):
        self.mining = True
        self.continuous_mining()

    def start_mining(self):
        print("Starting mining... ")
        while self.mining:
            print("Starting mining block... ")
            new_block = self.mine_block()
            if new_block is None:
                self.mining = False
            print("Found new Block!!!")
            # TODO handle new_block

    def is_mining(self):
        return self.mining

    def continuous_mining(self):
        print("Starting thread")
        mining_thread = threading.Thread(target=self.start_mining)
        mining_thread.start()
        print("Thread running")


    def mine_block(self) -> Block:
        previous_block = self.blockchain_instance.get_previous_block()
        previous_PoW = previous_block.proof_of_work
        new_index = len(self.blockchain_instance.blockchain) 
        new_PoW = self.generate_proof_of_work(previous_PoW=previous_PoW, index=new_index, data= self.blockchain_instance.blockchain[-1].data)
        if new_PoW is None:
            return None
        prev_hash = self.blockchain_instance.hash(previous_block)

        #when a mempool exists in the future, update it
        data = self.update_mempool()
        #for now use static data
        data = static_data()
        new_block = Block(data=data, proof_of_work=new_PoW, prev_hash=prev_hash, index=new_index, 
                        block_author_public_key=get_pub_key_string(),
                        block_value=self.blockchain_instance.get_block_value(new_index))

        self.blockchain_instance.update_blockchain(block = new_block)
        return new_block

    def generate_proof_of_work(self, previous_PoW: int, index: int, data: str) -> int:
        new_proof = self.proof_to_start_with
        check_proof = False

        while not check_proof:
            if not self.mining: # cancel mining if stopped
                return None
            data_to_hash = self.blockchain_instance.generate_pre_hash(new_proof, previous_PoW, index, data)
            hash_operation = hashlib.sha256(data_to_hash).hexdigest()
            #If last four digits of the hash are "0", the proof is accepted
            if hash_operation[:5]== "00000":
                check_proof = True
            else:
                new_proof += 1
        
        # print(new_proof)

        return new_proof

    #Implement this using the network! Verify Transactions!
    def update_mempool(self):
        return None

def static_data():
    pub_key_str = get_pub_key_string()
    my_transaction_data = TransactionData(pub_key_str, "my_destination_adress", timestamp=datetime.now(), amount=50)
    signed_trans = sign_transaction(get_priv_key(), pub_key_str, my_transaction_data)
    verify_transaction(signed_trans)

    return BlockData([signed_trans])

# my_miner = UdocoinMiner(proof_to_start_with=1000)
# for i in range(3):
#     my_miner.mine_block()
# print(my_miner.blockchain_instance.blockchain[-3:])
# print(my_miner.blockchain_instance.balances)
# #my_miner.blockchain_instance.blockchain[3].data.transaction_list[0].signature = 
# #my_miner.blockchain_instance.validate_blockchain()
# with open("blockchain_export.txt", "w") as file:
#     file.write(my_miner.blockchain_instance.export_blockchain())

# with open("blockchain_export.txt", "r") as file:
#     my_miner.blockchain_instance.import_blockchain(file.read())
 
