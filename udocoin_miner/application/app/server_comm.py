from flask import request as flask_request
from flask import abort
from app import socketio,app
from flask_socketio import emit
import os,json,pathlib
import requests

def update_known_seeds():
    received_known_seeds = []
    known_seeds = json.load(os.environ["known_seeds"])
    known_seeds_ = known_seeds.copy()
    '''Loop through known seeds and request furter seeds'''
    for ip in known_seeds:
        response = requests.get(f"{ip}/get/seeds")
        if response.status_code == 200:
            '''add seeds to list'''
            received_known_seeds += response["seeds"]
        else:
            '''if seed not active -> remove seed from list'''
            known_seeds_.remove(ip)
    '''remove duplicates'''
    received_known_seeds = list(set(received_known_seeds))
    '''check all seeds if active'''
    for ip in received_known_seeds:
        if ip not in known_seeds:
            if is_seed_active(ip):
                known_seeds_.append(ip)
    '''update known seeds in environ'''
    os.environ["known_seeds"] = known_seeds_

def is_seed_active(ip):
    response = requests.get(f"{ip}/get/is_active")
    return response.status_code == 200

@app.route('/get/seeds')
def get_seeds():
    return {"seeds":json.load(os.environ["known_seeds"])}

@app.route('/get/is_active')
def get_active():
    return {"active":True}

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

def broadcast_data(to_seeds:bool,data:dict):
    socketio.emit("broadcast_data",data)
    return data

@socketio.on('client_broadcast')
def on_client_broadcast(data):
    return broadcast_data(data)

@socketio.on('connect_peer_to_seed')
def on_connection(args):
    sid = flask_request.sid
    args_ = str(args)
    print(f'[Server] Received connection request')
    print(f'[Server] Room id: "{sid}"')
    print(f'[Server] Args: "{args_}"')
    # respond with successfull connection
    emit(
        "connection_response_seed_to_client",
        {"data":flask_request.sid,"request_args":args},
        room=sid
    )
