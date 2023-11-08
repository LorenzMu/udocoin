from flask import request as flask_request
from flask import abort
from app import socketio,app
from flask_socketio import emit
import os,json,pathlib
import requests
import socketio as client_socketio
import time

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
        blockchain_text = response.j
        blockchain = MINER.blockchain_instance.import_blockchain(blockchain_text)
        blockchains.append(blockchain)
    blockchain.append(MINER.blockchain_instance.blockchain)
    consensus_blockchain = MINER.blockchain_instance.get_consensus_blockchain(blockchains)
    MINER.blockchain_instance = consensus_blockchain

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

def broadcast_new_blockchain(exported_blockchain:str):
    bf,bd = "broadcast_new_blockchain",{"blockchain":exported_blockchain,"broadcast_id":time.time()}
    print("Broadcasting new Blockchain :)")
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
    @socketio.on('connect_to_seed')
    def on_connect_to_seed_(args):
        return on_connect_to_seed(args)
    @socketio.on('broadcast_new_blockchain')
    def on_broadcast_new_blockchain_(data):
        return on_broadcast_new_blockchain(data)

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
    # Only broadcast once
    global received_broadcast_ids
    broadcast_id = data["broadcast_id"]
    if broadcast_id in received_broadcast_ids:
        return
    received_broadcast_ids.append(broadcast_id)
    if len(received_broadcast_ids) > 100:
        received_broadcast_ids.pop(0)
    # validate new blockchain
    new_blockchain = data["blockchain"]
    verified_blockchain = MINER.blockchain_instance.import_blockchain(new_blockchain)
    if verified_blockchain is None:
        return
    consensus_blockchain = MINER.blockchain_instance.get_consensus_blockchain([MINER.blockchain_instance.blockchain,verified_blockchain])
    if consensus_blockchain == MINER.blockchain_instance.blockchain:
        return
    # restart mining with new chain
    MINER.blockchain_instance.blockchain = consensus_blockchain
    MINER.restart_mining()
    broadcast_new_blockchain('broadcast_new_blockchain',{"blockchain":new_blockchain,"broadcast_id":broadcast_id})