from copy import deepcopy
from app.blockchain_modules.blockchain import Blockchain
from app.blockchain_modules.udocoin_dataclasses import *
from app.blockchain_modules.transactions import *
import os,time
import threading
from app import server_comm as server_comm
from typing import List
import dataclasses
import datetime

#Separate class, because different people may want to implement it differently
#The blockchain as the central data structure is the consistent class and may not have different implementations
class UdocoinMiner:
    def __init__(self, proof_to_start_with: int):
        self.blockchain_instance: Blockchain = Blockchain()
        self.mempool: list[SignedTransaction] = []
        self.proof_to_start_with: int = proof_to_start_with
        self.mining: bool = True
        self.new_proof: int = proof_to_start_with

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
            
            exported_block = self.blockchain_instance.export_blockchain(single_block=True)
            # broadcast blockchain instance
            server_comm.broadcast_new_block(exported_block)

    def restart_mining(self):
        self.stop_mining()
        self.new_proof = self.proof_to_start_with
        time.sleep(0.1)
        self.continue_mining()

    def is_mining(self) -> bool:
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

        data = self.get_valid_transactions()
        
        #for now use static data
        #data = static_data()
        new_block = Block(data=data, proof_of_work=new_PoW, prev_hash=prev_hash, index=new_index, 
                        block_author_public_key=get_pub_key_string(),
                        block_value=self.blockchain_instance.get_block_value(new_index))

        self.blockchain_instance.append_blockchain(block = new_block)
        self.update_mempool()
        self.new_proof = self.proof_to_start_with
        return new_block

    def generate_proof_of_work(self, previous_PoW: int, index: int, data: str) -> int:
        check_proof = False

        while not check_proof:
            if not self.mining: # cancel mining if stopped
                return None
            data_to_hash = self.blockchain_instance.generate_pre_hash(self.new_proof, previous_PoW, index, data)
            hash_operation = hashlib.sha256(data_to_hash).hexdigest()
            #If last four digits of the hash are "0", the proof is accepted
            if hash_operation[:5]== "00000":
                check_proof = True
            else:
                self.new_proof += 1
        
        # print(new_proof)

        return self.new_proof

    #verifies the transaction's signature and naively check that the user's account balance is high enough to complete it
    def validate_transaction(self, signed_transaction: SignedTransaction, balances: List[AccountBalance]) -> bool:
        transaction_data = verify_transaction(signed_transaction)
        if transaction_data != None:
            if balances[signed_transaction.origin_public_key.decode("utf-8")] >= transaction_data.amount and transaction_data.amount > 0:
                return True
                
        return False

    #Occurs when a new transaction is broadcast to the peer
    def receive_transaction_request(self, signed_transaction: SignedTransaction) -> str:
        if self.validate_transaction(signed_transaction= signed_transaction, balances= self.blockchain_instance.balances): 
            if signed_transaction not in self.mempool:
                
                #binary mode! not serializable to json
                self.mempool.append(signed_transaction)
                #Re-encode to broadcast in JSON format
                serializable_signed_transaction = serialize_signed_transaction(signed_transaction)
            
                
                server_comm.broadcast_transaction_request(transaction=json.dumps(serializable_signed_transaction,cls=EnhancedJSONEncoder), transaction_data= {})
                return "Received transaction and added it to mempool. Your transaction will be processed once 5 more blocks have been published"
            else:
                return "Transaction request already received."
        else:
            return "Your signature is wrong or your account balance is too low!"



    #Deletes Signed Transactions from the mempool if the transaction has been confirmed in a deep block or the transaction is too old.
    #depth_to_purge is the n-th to last Block in the blockchain
    #max_age is the maximum age transaction may have in the mempool in days
    def update_mempool(self, depth_to_purge = 1, max_age_days = 1, max_age_hours = 0 ) -> None:
        cut_off_time = datetime.datetime.now() - datetime.timedelta(days = max_age_days, hours=max_age_hours)

        #Get transaction_list from block from which to filter
        if len(self.blockchain_instance.blockchain)>=depth_to_purge:
            transaction_list =  self.blockchain_instance.blockchain[-depth_to_purge].data.transaction_list
        
            #Delete all already integrated blocks from the mempool
            transactions_without_blocks = [s_t for s_t in self.mempool if s_t not in transaction_list]
            
            #Delete all transactions that are too old
            # self.mempool = [s_t for s_t in transactions_without_blocks if verify_transaction(s_t).timestamp > cut_off_time]
            self.mempool = transactions_without_blocks

    #Collects transactions from the mempool that can be published in the next published block in one list    
    def get_valid_transactions(self) -> BlockData:
        publishable_transactions = []
        temp_balances = deepcopy(self.blockchain_instance.balances)

        transaction_data_list = [verify_transaction(s_t) for s_t in self.mempool]
        print("T_DATA_LIST", transaction_data_list)
        #remove unverifiable messages
        transaction_data_list = [t_d for t_d in transaction_data_list if t_d != None]

        print("T_DATA_LIST", transaction_data_list)

        #Check if account balance is high enough to make transaction
        for transaction_data in transaction_data_list:
            if transaction_data.origin_public_key in temp_balances.keys() and (transaction_data.amount <= temp_balances[transaction_data.origin_public_key]) and transaction_data.amount > 0:
                temp_balances[transaction_data.origin_public_key]-= transaction_data.amount
                if transaction_data.destination_public_key in temp_balances.keys():
                    temp_balances[transaction_data.destination_public_key] += transaction_data.amount
                else:
                    temp_balances[transaction_data.destination_public_key] = transaction_data.amount
                publishable_transactions.append(transaction_data)
        
        print("PUBLISHABLE TRANSACTIONS", publishable_transactions)

        publishable_signed_transactions = BlockData([s_t for s_t in self.mempool if (TransactionData(**loads(s_t.message)) in publishable_transactions)])
        print("PUBLISHABLE SIGNED TRANSACTIONS", publishable_signed_transactions)

        return publishable_signed_transactions
        
class EnhancedJSONEncoder(json.JSONEncoder):
        def default(self, o):
            if dataclasses.is_dataclass(o):
                return dataclasses.asdict(o)
            return super().default(o)
        

def static_data():
    pub_key_str = get_pub_key_string()
    my_transaction_data = TransactionData(pub_key_str, "my_destination_adress", timestamp=datetime.datetime.now(), amount=50)
    signed_trans = sign_transaction(get_priv_key(), bytes(pub_key_str,"utf-8"), my_transaction_data)
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
 
