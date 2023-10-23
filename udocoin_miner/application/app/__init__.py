from flask import Flask
from flask_cors import CORS
from flask_socketio import SocketIO
import os,pathlib
import threading,time

SEED_SERVER = ""
# default path
PUBKEY_PATH = os.path.join(pathlib.Path(__file__).parent,"blockchain_modules","blockchain_secrets","pub_key.pub")
PRIVKEY_PATH = os.path.join(pathlib.Path(__file__).parent,"blockchain_modules","blockchain_secrets","priv_key")

if "SKIP_ENV_INPUT" in os.environ.keys() and os.environ["SKIP_ENV_INPUT"]:
    # If started from Docker -> get environment variables
    SEED_SERVER = os.environ["SEED_SERVER"]
    PUBKEY_PATH = os.environ["PUBKEY_PATH"]
    PRIVKEY_PATH = os.environ["PRIVKEY_PATH"]
else:
    # If started locally -> get user input and set variables
    SEED_SERVER = input("Is the server a Seed-Server? [y/n] ")
    pubkey_path_input = input("Please insert the path to your public-key or skip for default: ")
    PUBKEY_PATH = pubkey_path_input if pubkey_path_input != "" else PUBKEY_PATH
    privkey_path_input = input("Please insert the path to your private-keyor skip for default: ")
    PRIVKEY_PATH = privkey_path_input if privkey_path_input != "" else PRIVKEY_PATH
    
os.environ["IS_SEED_SERVER"] = "True" if SEED_SERVER == "y" or SEED_SERVER == "yes" else ""
os.environ["PUBKEY_PATH"] = PUBKEY_PATH
os.environ["PRIVKEY_PATH"] = PRIVKEY_PATH
# TODO verify pubkey else create new key and notify user

# with open(PUBKEY_PATH,"r") as pub_key_file:
#     os.environ["PUBKEY"] = pub_key_file.read()

# with open(PRIVKEY_PATH,"r") as priv_key_file:
#     os.environ["PRIVKEY"] = priv_key_file.read()

from app.blockchain_modules.UdocoinMiner import UdocoinMiner

MINER = UdocoinMiner(1)
MINER_THREAD = MINER.continuous_mining()

# for i in range(3):
#     my_miner.mine_block()
# print(my_miner.blockchain_instance.blockchain[-3:])
# print(my_miner.blockchain_instance.balances)
# #my_miner.blockchain_instance.blockchain[3].data.transaction_list[0].signature = 
# #my_miner.blockchain_instance.validate_blockchain()
# with open("blockchain_export.txt", "w") as file:
#     file.write(my_miner.blockchain_instance.export_blockchain())
# # with open("blockchain_export.txt", "r") as file:
#     # my_miner.blockchain_instance.import_blockchain(file.read())

app = Flask(__name__)
app.config.from_object("config.DevelopmentConfig")

print("App initialized...")
CORS(app)

socketio = SocketIO(app)

from app import endpoints
from app import server_comm as server_comm