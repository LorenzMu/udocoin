from flask import request
from app import socketio
from flask_socketio import emit


def broadcast_data(data):
    socketio.emit("broadcast_data",data)
    return data

@socketio.on('client_broadcast')
def on_client_broadcast(data):
    return broadcast_data(data)

@socketio.on('connect_peer_to_seed')
def on_connection(args):
    sid = request.sid
    args_ = str(args)
    print(f'[Server] Received connection request')
    print(f'[Server] Room id: "{sid}"')
    print(f'[Server] Args: "{args_}"')
    # respond with successfull connection
    emit(
        "connection_response_seed_to_client",
        {"data":request.sid,"request_args":args},
        room=sid
    )
