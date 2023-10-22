from flask import Flask
from flask_cors import CORS
from flask_socketio import SocketIO
import os

SEED_SERVER = ""
PUBKEY = ""
PUBKEY_PATH = ""

if "SKIP_ENV_INPUT" in os.environ.keys() and os.environ["SKIP_ENV_INPUT"]:
    SEED_SERVER = os.environ["SEED_SERVER"]
    # PUBKEY = os.environ["PUBKEY"]
    PUBKEY_PATH = os.environ["PUBKEY_PATH"]
else:
    SEED_SERVER = input("Is the server a Seed-Server? [y/n] ")
    PUBKEY_PATH = input("Please insert your public-key path: ")
    
os.environ["IS_SEED_SERVER"] = "yes" if SEED_SERVER == "y" or SEED_SERVER == "yes" else ""
# TODO verify pubkey else create new key and notify user
with open(PUBKEY_PATH,"rb") as pub_key_file:
    os.environ["PUBKEY"] = pub_key_file.read()
    PUBKEY = pub_key_file.read()

from app.blockchain_modules.UdocoinMiner import UdocoinMiner

my_miner = UdocoinMiner(1,PUBKEY)

for i in range(3):
    my_miner.mine_block()
print(my_miner.blockchain_instance.blockchain[-3:])
print(my_miner.blockchain_instance.balances)
#my_miner.blockchain_instance.blockchain[3].data.transaction_list[0].signature = 
#my_miner.blockchain_instance.validate_blockchain()
with open("blockchain_export.txt", "w") as file:
    file.write(my_miner.blockchain_instance.export_blockchain())
# with open("blockchain_export.txt", "r") as file:
    # my_miner.blockchain_instance.import_blockchain(file.read())

app = Flask(__name__)
app.config.from_object("config.DevelopmentConfig")

print("App initialized...")
CORS(app)

socketio = SocketIO(app)

from app import endpoints
from app import server_comm as server_comm