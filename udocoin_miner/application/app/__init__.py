from flask import Flask
from flask_cors import CORS
from flask_socketio import SocketIO
import os,pathlib
import threading,time

SEED_SERVER = ""
PUBKEY = ""
PRIVKEY = ""

from app.blockchain_modules.transactions import get_priv_key_from_path,get_pub_key_from_path

def getPubkey():
    # default path
    PUBKEY_PATH = os.path.join(os.path.expanduser("~"),".udocoin","pub_key.pub")
    pubkey_path_input = input("Please insert the path to your public-key or skip for default: ")
    PUBKEY_PATH = pubkey_path_input if pubkey_path_input != "" else PUBKEY_PATH
    if not os.path.exists(PUBKEY_PATH):
        print(f'File not found: {PUBKEY_PATH}')
        return getPubkey()
    return get_pub_key_from_path(PUBKEY_PATH)

def getPrivkey():
    # default path
    PRIVKEY_PATH = os.path.join(os.path.expanduser("~"),".udocoin","priv_key")
    privkey_path_input = input("Please insert the path to your private-keyor skip for default: ")
    PRIVKEY_PATH = privkey_path_input if privkey_path_input != "" else PRIVKEY_PATH
    if not os.path.exists(PRIVKEY_PATH):
        print(f'File not found: {PRIVKEY_PATH}')
        return getPrivkey()
    return get_priv_key_from_path(PRIVKEY_PATH)


if "SKIP_ENV_INPUT" in os.environ.keys() and os.environ["SKIP_ENV_INPUT"]:
    # If started from Docker -> get environment variables
    SEED_SERVER = os.environ["SEED_SERVER"]
    PUBKEY = os.environ["PUBKEY"]
    PRIVKEY = os.environ["PRIVKEY"]
else:
    # If started locally -> get user input and set variables
    SEED_SERVER = input("Is the server a Seed-Server? [y/n] ")
    PRIVKEY = getPrivkey()
    PUBKEY = getPubkey()
    
os.environ["IS_SEED_SERVER"] = "True" if SEED_SERVER == "y" or SEED_SERVER == "yes" else ""
os.environ["PUBKEY"] = PUBKEY
os.environ["PRIVKEY"] = PRIVKEY
# TODO verify pubkey else create new key and notify user

from app.blockchain_modules.UdocoinMiner import UdocoinMiner

MINER = UdocoinMiner(1)
MINER_THREAD = MINER.continuous_mining()
MINER.stop_mining()

app = Flask(__name__)
app.config.from_object("config.DevelopmentConfig")

print("App initialized...")
CORS(app)

socketio = SocketIO(app)

from app import endpoints
from app import server_comm as server_comm