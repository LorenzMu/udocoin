from app.blockchain_modules.UdocoinMiner import UdocoinMiner
#from app.server_comm import * 

def fork_test():
    print("STARTING FORK TEST")
    my_miner = UdocoinMiner(proof_to_start_with=1000)
    my_miner2 = UdocoinMiner(proof_to_start_with= 1)
    my_miner3 = UdocoinMiner(proof_to_start_with=10000)
    for i in range(3):
        my_miner.mine_block()
        my_miner2.mine_block()
        my_miner3.mine_block()

    for i in range(2):
        my_miner2.mine_block()

    bl1 = my_miner.blockchain_instance.blockchain
    bl2 = my_miner2.blockchain_instance.blockchain
    bl3 = my_miner3.blockchain_instance.blockchain

    my_miner.blockchain_instance.blockchain = my_miner.blockchain_instance.get_consensus_blockchain([bl1,bl2,bl3])

    #assert my_miner.blockchain_instance.blockchain == bl2

    print("Blockchains are equal", my_miner.blockchain_instance.blockchain == bl2 )

    print(my_miner.blockchain_instance.blockchain)

    print("FINISHED CONSENSUS TEST")