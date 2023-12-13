from flask import request as flask_request
from flask import abort
from app import socketio,app
from flask_socketio import emit
import os,json,pathlib
import requests
import socketio as client_socketio
import time
from app.blockchain_modules.ReturnValues import ReturnValues
from app.blockchain_modules.udocoin_dataclasses import SignedTransaction, SerializableSignedTransaction, serialize_signed_transaction, deserialize_signed_transaction
from app.blockchain_modules.transactions import verify_transaction
import dacite
from base64 import b64encode, b64decode

from app.miner import MINER

def update_known_seeds():
    received_known_seeds = []
    known_seeds = json.loads(os.environ["known_seeds"])
    known_seeds_ = known_seeds.copy()
    '''Loop through known seeds and request furter seeds'''
    for ip in known_seeds:
        try:
            response = requests.get(f'{ip}/get/seeds')
            if response.status_code == 200:
                '''add seeds to list'''
                if len(response.json()["seeds"]) > 0:
                    received_known_seeds += response.json()["seeds"]
            else:
                '''if seed not active -> remove seed from list'''
                known_seeds_.remove(ip)
        except:
            known_seeds_.remove(ip)
    '''remove duplicates'''
    received_known_seeds = list(set(received_known_seeds))
    '''check all seeds if active'''
    for ip in received_known_seeds:
        if ip not in known_seeds:
            if is_seed_active(ip):
                known_seeds_.append(ip)
    '''update known seeds in environ'''
    os.environ["known_seeds"] = json.dumps(known_seeds_)

def is_seed_active(ip):
    try:
        response = requests.get(f'{ip}/get/is_active')
        return response.status_code == 200
    except:
        return False

socket_clients = []

def setup_socket_connections():
    known_seeds = json.loads(os.environ["known_seeds"])
    for seed_ip in known_seeds:
        socket_client = connect_socket_to_seed(
            seed_ip=seed_ip,
            connection_type="seed-to-seed" if os.environ["IS_SEED_SERVER"] else "peer-to_seed")
        if socket_client is not None:
            set_socket_listeners(socket_client)
            global socket_clients
            socket_clients.append(socket_client)
            # If server is peer server, only one connection is required
            if not os.environ["IS_SEED_SERVER"]:
                print("#########################################################")
                print("Connection set up successfully to " + seed_ip)
                print("#########################################################")
                break
    # raise exception if no connection could be set up
    if len(socket_clients) == 0:
        # raise Exception("Could not create connection from peer to any seed server.")        
        print("#########################################################")
        print("Could not create connection from peer to any seed server.")
        print("#########################################################")

def connect_socket_to_seed(seed_ip:str,connection_type:str):
    try:
        client_sio = client_socketio.Client()
        client_sio.connect(seed_ip)
        client_sio.emit('connect_to_seed',{"connection_type":connection_type})
        return client_sio
    except:
        return None
    
def get_latest_blockchain():
    known_seeds = json.loads(os.environ["known_seeds"])
    blockchains = []
    for known_seed in known_seeds:
        response = requests.get(f"{known_seed}/miner/blockchain")
        blockchain_text = response.text
        blockchain = MINER.blockchain_instance.import_blockchain(blockchain_text)
        blockchains.append(blockchain)
    blockchains.append(MINER.blockchain_instance.blockchain)
    consensus_blockchain = MINER.blockchain_instance.get_consensus_blockchain(blockchains)
    if consensus_blockchain != MINER.blockchain_instance.blockchain:
        MINER.blockchain_instance.blockchain = consensus_blockchain
        MINER.blockchain_instance.index_confirmed = -1
        MINER.blockchain_instance.balances = {}
        MINER.blockchain_instance.update_balances()
        MINER.restart_mining()

@app.route("/register",methods=["POST"])
def register_seed_server():
    data = flask_request.json()
    ip = data["ip"]
    if not is_seed_active(ip):
        return abort(400)
    known_seeds = json.load(os.environ["known_seeds"])
    known_seeds.append(ip)
    os.environ["known_seeds"] = json.dumps(known_seeds)
    return known_seeds

def broadcast_data(data:dict):
    socketio.emit("broadcast_data",data)
    return data

def broadcast_new_blockchain(exported_blockchain:str="",blockchain_data = {}):
    if exported_blockchain!="":
        bf,bd = "broadcast_new_blockchain",{"blockchain":exported_blockchain,"broadcast_id":time.time()}
    else:
        bf,bd = "broadcast_new_blockchain",blockchain_data
    print("Broadcasting new Blockchain :)")
    socketio.emit(bf,bd) # connections set up by clients
    for socket_client in socket_clients:
        socket_client.emit(bf,bd) # connections which the current server has started

def broadcast_new_block(exported_block: str = "", block_data = {}):
    if exported_block!="":
        bf,bd = "broadcast_new_block",{"block": exported_block, "broadcast_id": time.time()}
    else:
        bf,bd = "broadcast_new_block", block_data
    print("Broadcasting new Block :)")
    socketio.emit(bf,bd) # connections set up by clients
    for socket_client in socket_clients:
        socket_client.emit(bf,bd) # connections which the current server has started


def broadcast_transaction_request(transaction: str="", transaction_data = {}):
    if transaction != "":
        bid = time.time()
        bf,bd = "broadcast_transaction_request", {"transaction": transaction, "broadcast_id": bid}
        global received_broadcast_ids
        received_broadcast_ids.append(bid)
    else:
        bf,bd = "broadcast_transaction_request", transaction_data
    print("Broadcasting transaction request")
    socketio.emit(bf,bd) # connections set up by clients
    for socket_client in socket_clients:
        socket_client.emit(bf,bd) # connections which the current server has started


########################
# # socket functions # #
########################

received_broadcast_ids = []

def set_socket_listeners(socket_client):
    # Receive events from connections which the current server has started
    @socket_client.on("broadcast_data")
    def on_broadcast_data_(data):
        return on_broadcast_data(data)
    @socket_client.on("connect_to_seed_response")
    def on_connect_to_seed_response_(args):
        return on_connect_to_seed_response(args)
    @socket_client.on('connect_to_seed')
    def on_connect_to_seed_(args):
        return on_connect_to_seed(args)
    @socket_client.on('broadcast_new_blockchain')
    def on_broadcast_new_blockchain_(data):
        return on_broadcast_new_blockchain(data)
    @socket_client.on('broadcast_new_block')
    def on_broadcast_new_block_(data):
        return on_broadcast_new_block(data)
    @socket_client.on('return_unconfirmed_blocks')
    def on_return_unconfirmed_blocks_(data):
        return on_return_unconfirmed_blocks(data)
    @socket_client.on('broadcast_transaction_request')
    def on_broadcast_transaction_request_(data):
        return on_broadcast_transaction_request(data)
    @socketio.on('request_unconfirmed_blocks')
    def on_request_unconfirmed_blocks_():
        return on_request_unconfirmed_blocks()

# Receive events from connections set up by clients
@socketio.on('broadcast_data')
def on_broadcast_data(data):
    print("Received broadcast message: " + str(data))

@socketio.on('connect_to_seed')
def on_connect_to_seed(args):
    sid = flask_request.sid
    connection_type = args["connection_type"]
    print(f'[Seed-Server] Received connection request')
    print(f'[Seed-Server] Room id: "{sid}"')
    print(f'[Seed-Server] Connection type: "{connection_type}"')
    emit(
        "connect_to_seed_response",
        {"room":sid,"connection_type":connection_type},
        room=sid
    )

@socketio.on('connect_to_seed_response')
def on_connect_to_seed_response(args):
    connection_type = args["connection_type"]
    room = args["room"]
    print(f'[Peer-Server] Received connection request')
    print(f'[Peer-Server] room: "{room}"')
    print(f'[Peer-Server] Connection type: "{connection_type}"')

@socketio.on('broadcast_new_blockchain')
def on_broadcast_new_blockchain(data):
    if not message_previously_received(data):
        # validate new blockchain
        new_blockchain = data["blockchain"]
        unverified_blockchain = MINER.blockchain_instance.import_blockchain(new_blockchain)
        verified_blockchain = MINER.blockchain_instance.validate_blockchain(unverified_blockchain)

        if verified_blockchain is None:
            return
        consensus_blockchain = MINER.blockchain_instance.get_consensus_blockchain([MINER.blockchain_instance.blockchain,verified_blockchain])
        if consensus_blockchain == MINER.blockchain_instance.blockchain:
            return
        # restart mining with new chain
        MINER.blockchain_instance.blockchain = consensus_blockchain
        MINER.restart_mining()
        broadcast_new_blockchain(data={"blockchain":new_blockchain,"broadcast_id":data["broadcast_id"]})

@socketio.on('broadcast_new_block')
def on_broadcast_new_block(data):
    if not message_previously_received(data):
        
        new_block = data["block"]
        block = MINER.blockchain_instance.import_blockchain("[" + new_block + "]")
        if block is None:
            return
        if block[0].index > MINER.blockchain_instance.blockchain[-1].index:
            return_value = MINER.blockchain_instance.detect_blockchain_append(block[0])
            if return_value == ReturnValues.SingleBlockAppended:
                MINER.restart_mining()
                MINER.update_mempool(depth_to_purge=1)

            #Ask the peer that broadcasted the block for their previous five blocks
            if return_value == ReturnValues.SingleBlockRejected:
                ##################################################
                #TODO: How do I get this SPECIFIC peer's blockchain?
                socketio.emit('request_unconfirmed_blocks',{})
                for socket_client in socket_clients:
                    socket_client.emit('request_unconfirmed_blocks',{})
                return
                ##################################################
        
#If a new block's hash does not line up with the previous block's hash, get the peer's last five blocks and check for changes within
@socketio.on('return_unconfirmed_blocks')
def on_return_unconfirmed_blocks(data):
    if not message_previously_received(data):
        new_blocks = data["blocks"]
        blocks = MINER.blockchain_instance.import_blockchain(new_blocks)
        return_value, fork_index = MINER.blockchain_instance.detect_multiple_changes(blocks)
        if return_value == ReturnValues.BlocksReplaced:
            print("At least one block was replaced")
            for i in range((len(MINER.blockchain_instance.blockchain)-fork_index), 0):
                MINER.update_mempool(depth_to_purge=i)
        #If there are even more changes, ask for the entire blockchain and run the consensus algorithm
        if return_value == ReturnValues.BlocksRejected:
            get_latest_blockchain()

@socketio.on('broadcast_transaction_request')
def on_broadcast_transaction_request(data):
    print("******** Transaction received")
    if not message_previously_received(data):
        print("Transaction received ******** ")
        transaction_dict = json.loads(data["transaction"])

        serializable_signed_transaction = dacite.from_dict(data_class=SerializableSignedTransaction, data={k: v for k, v in transaction_dict.items() if v is not None})
        signed_transaction = deserialize_signed_transaction(serializable_signed_transaction)

        transaction_data = verify_transaction(signed_transaction)
        #Only allow spending values greater than 0
        if transaction_data.amount > 0:
            MINER.mempool.append(signed_transaction)
            broadcast_transaction_request(transaction="", transaction_data=data)

@socketio.on('request_unconfirmed_blocks')
def on_request_unconfirmed_blocks():
    exported_blocks = MINER.blockchain_instance.export_blockchain(unconfirmed_blocks=True)
    bf,bd = "return_unconfirmed_blocks",{"block": exported_blocks, "broadcast_id": time.time()}
    print("Broadcasting multiple Blocks :)")
    socketio.emit(bf,bd) # connections set up by clients
    for socket_client in socket_clients:
        socket_client.emit(bf,bd) # connections which the current server has started


def message_previously_received(data):
    # Only broadcast once, stop propagation otherwise
    global received_broadcast_ids
    broadcast_id = data["broadcast_id"]
    if broadcast_id in received_broadcast_ids:
        return True
    received_broadcast_ids.append(broadcast_id)
    if len(received_broadcast_ids) > 100:
        received_broadcast_ids.pop(0)
    return False