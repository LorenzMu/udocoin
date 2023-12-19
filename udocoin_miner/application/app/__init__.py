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

import re
def formate_key(key:str)->str:
    if "-----BEGIN RSA PRIVATE KEY-----" in key:
        pattern = r"-----BEGIN RSA PRIVATE KEY-----(.*?)-----END RSA PRIVATE KEY-----"
        key_data = re.search(pattern, key, re.DOTALL)
        
        if key_data:
            formatted_key = key_data.group(1).strip().replace(" ", "\n")
            final_key = f"-----BEGIN RSA PRIVATE KEY-----\n{formatted_key}\n-----END RSA PRIVATE KEY-----"
            return final_key
        else:
            raise Exception("Invalid RSA key")
    elif "-----BEGIN PUBLIC KEY-----" in key:
        pattern = r"-----BEGIN PUBLIC KEY-----(.*?)-----END PUBLIC KEY-----"
        key_data = re.search(pattern, key, re.DOTALL)
        
        if key_data:
            formatted_key = key_data.group(1).strip().replace(" ", "\n")
            final_key = f"-----BEGIN PUBLIC KEY-----\n{formatted_key}\n-----END PUBLIC KEY-----"
            return final_key + "\n"
        else:
            raise Exception("Invalid PUBLIC key")
    else:
        raise Exception("Invalid key")
    
os.environ["IS_SEED_SERVER"] = "True" if SEED_SERVER == "y" or SEED_SERVER == "yes" else ""
os.environ["PUBKEY"] = formate_key(PUBKEY)
os.environ["PRIVKEY"] = formate_key(PRIVKEY)
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
    known_seeds = server_comm.get_known_seeds()
    os.environ["known_seeds"] = json.dumps(known_seeds)
    ###### DEPRECATED ######
    # o = json.load(open(os.path.join(pathlib.Path(__file__).parent.parent,"seeds.json")))
    # str = json.dumps(o)
    # os.environ["known_seeds"] = str
    print("Found seeds in local in repo:",known_seeds)
else:
    print("Found seeds in env-variables: " + os.environ["known_seeds"])

server_comm.update_known_seeds()

server_comm.setup_socket_connections()

server_comm.get_latest_blockchain()

from app import endpoints
