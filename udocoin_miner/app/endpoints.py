from app import app,socketio
from flask_socketio import emit
from flask import request

@app.route("/",methods=["GET"])
def index():
    return "Running healthy"

@app.route("/notify",methods=["GET"])
def notify_peers():
    message = request.args.get("message") if request.args.get("message") else "No message provided."
    socketio.emit("broadcast_message",{"message":message})
    return f'Broadcasted message: "{message}"'

@socketio.on('connect_peer_to_seed')
def on_connection(args):
    sid = request.sid
    args_ = str(args)
    print("[Server] Received connection request")
    print(f'[Server] Client id: "{sid}"')
    print(f'[Server] args: "{args_}"')
    # respond with successfull connection
    emit("connection_response_seed_to_client",{"data":request.sid,"request_args":args},room=sid)