from flask import Flask
from flask_cors import CORS
from flask_socketio import SocketIO
import os

SEED_SERVER = ""
PUBKEY = ""

if "SKIP_ENV_INPUT" in os.environ.keys() and os.environ["SKIP_ENV_INPUT"]:
    SEED_SERVER = os.environ["SEED_SERVER"]
    PUBKEY = os.environ["PUBKEY"]
else:
    SEED_SERVER = input("Is the server a Seed-Server? [y/n] ")
    PUBKEY = input("Please insert your public-key: ")
    
os.environ["IS_SEED_SERVER"] = "yes" if SEED_SERVER == "y" or SEED_SERVER == "yes" else ""
# TODO verify pubkey else create new key and notify user
os.environ["PUBKEY"] = PUBKEY

app = Flask(__name__)
app.config.from_object("config.DevelopmentConfig")

print("App initialized...")
CORS(app)

socketio = SocketIO(app)

from app import endpoints
from app import server_comm as server_comm