from flask import request as flask_request
from flask import abort
from app import socketio,app
from flask_socketio import emit
import os,json,pathlib
import requests
import socketio as client_socketio

def update_known_seeds():
    print("=========== UPDATING SEEDS FROM SEEDS ============")
    received_known_seeds = []
    known_seeds = json.loads(os.environ["known_seeds"])
    known_seeds_ = known_seeds.copy()
    '''Loop through known seeds and request furter seeds'''
    print("Sending requests to " + str(known_seeds_))
    for ip in known_seeds:
        try:
            response = requests.get(f'{ip}/get/seeds')
            if response.status_code == 200:
                '''add seeds to list'''
                print("Valid response at ip " + ip)
                if len(response.json()["seeds"]) > 0:
                    received_known_seeds += response.json()["seeds"]
            else:
                '''if seed not active -> remove seed from list'''
                print("Invalid status code at ip " + ip)
                known_seeds_.remove(ip)
        except:
            print("Exception at seed " + ip)
            known_seeds_.remove(ip)
    '''remove duplicates'''
    received_known_seeds = list(set(received_known_seeds))
    '''check all seeds if active'''
    for ip in received_known_seeds:
        if ip not in known_seeds:
            if is_seed_active(ip):
                known_seeds_.append(ip)
    '''update known seeds in environ'''
    print("Updating seed list to " + str(known_seeds_))
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
    print("Setting up socket-connections to " +str(known_seeds))
    for seed_ip in known_seeds:
        print("Setting up socket-connection to " +seed_ip)
        socket_client = connect_socket_to_seed(
            seed_ip=seed_ip,
            connection_type="seed-to-seed" if os.environ["IS_SEED_SERVER"] else "peer-to_seed")
        if socket_client is not None:
            global socket_clients
            socket_clients.append(socket_client)
            # If server is peer server, only one connection is required
            if not os.environ["IS_SEED_SERVER"]:
                print("#########################################################")
                print("Connection set up successfully to " + seed_ip)
                print("#########################################################")
                break
        else:
            print("Failed connection to " + seed_ip)
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
        print(f"Failed connecting to {seed_ip}")
        return None

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
    sid = flask_request.sid
    connection_type = args["connection_type"]
    room = args["room"]
    print(f'[Peer-Server] Received connection request')
    print(f'[Peer-Server] sid: "{sid}"')
    print(f'[Peer-Server] room: "{room}"')
    print(f'[Peer-Server] Connection type: "{connection_type}"')
