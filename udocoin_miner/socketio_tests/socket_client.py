import socketio
import time
from flask import request

client_sio = socketio.Client()
client_sio.connect('http://localhost:5000')

client_sio.emit('connect_peer_to_seed',{"message":"Hello I am peer"})

@client_sio.on('connection_response_seed_to_client')
def on_connection_response_seed_to_client(args):
    print("[CLIENT] Received connection confirmation from server")
    print("[CLIENT] args: " + str(args))

@client_sio.on('broadcast_data')
def on_broadcast_message(args):
    print("[CLIENT] Received broadcastmessage from seed")
    print('[CLIENT] Message: "' + args["message"] + '"')

# client_sio.wait() # Lässt sich iwi nur jedes 3. mal interrupten? idk
time.sleep(1000)