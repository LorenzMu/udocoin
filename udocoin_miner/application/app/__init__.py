from flask import Flask
from flask_cors import CORS
from flask_socketio import SocketIO
import os,pathlib,json

SEED_SERVER = ""
PUBKEY = ""
PRIVKEY = ""

from app.blockchain_modules.transactions import get_priv_key_from_path,get_pub_key_from_path

def getPubkey():
    # ONLY USED IN DEV ENV
    PUBKEY_PATH = os.path.join(os.path.expanduser("~"),".udocoin","pub_key.pub")
    pubkey_path_input = input("Please insert the path to your public-key or skip for default: ")
    PUBKEY_PATH = pubkey_path_input if pubkey_path_input != "" else PUBKEY_PATH
    if not os.path.exists(PUBKEY_PATH):
        print(f'File not found: {PUBKEY_PATH}')
        return getPubkey()
    return get_pub_key_from_path(PUBKEY_PATH)

def getPrivkey():
    # ONLY USED IN DEV ENV
    PRIVKEY_PATH = os.path.join(os.path.expanduser("~"),".udocoin","priv_key")
    privkey_path_input = input("Please insert the path to your private-key or skip for default: ")
    PRIVKEY_PATH = privkey_path_input if privkey_path_input != "" else PRIVKEY_PATH
    if not os.path.exists(PRIVKEY_PATH):
        print(f'File not found: {PRIVKEY_PATH}')
        return getPrivkey()
    return get_priv_key_from_path(PRIVKEY_PATH)


# If started from Docker -> get environment variables
if "SKIP_ENV_INPUT" in os.environ.keys() and os.environ["SKIP_ENV_INPUT"]:
    SEED_SERVER = os.environ["SEED_SERVER"]
    PUBKEY = os.environ["PUBKEY"]
    PRIVKEY = os.environ["PRIVKEY"]
else: # If started locally -> get user input and set variables
    SEED_SERVER = input("Is the server a Seed-Server? [y/n] ")
    PRIVKEY = getPrivkey()
    PUBKEY = getPubkey()
    
os.environ["IS_SEED_SERVER"] = "True" if SEED_SERVER == "y" or SEED_SERVER == "yes" else ""
os.environ["PUBKEY"] = PUBKEY
os.environ["PRIVKEY"] = PRIVKEY
# TODO verify pubkey else create new key and notify user

app = Flask(__name__)
app.config.from_object("config.DevelopmentConfig")

CORS(app)

socketio = SocketIO(app)

'''
update known seed server ips
'''
from app import server_comm as server_comm

if "known_seeds" not in os.environ.keys() or len(json.loads(os.environ["known_seeds"])) == 0:
    print("Found no seeds in env-variables")
    o = json.load(open(os.path.join(pathlib.Path(__file__).parent.parent,"seeds.json")))
    str = json.dumps(o)
    os.environ["known_seeds"] = str
    print("Found seeds in local file: " + str)
else:
    print("Found seeds in env-variables: " + os.environ["known_seeds"])

server_comm.update_known_seeds()

server_comm.setup_socket_connections()



from app import endpoints
