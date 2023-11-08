from app import app,server_comm,MINER
from flask import request,redirect
import os,json

from app.blockchain_modules.consensus_tests import consensus_test

@app.route("/",methods=["GET"])
def index():
    return f"Running healthy as {'Seed' if os.environ['IS_SEED_SERVER'] else 'Peer'}-Server"

@app.route("/broadcast",methods=["GET"]) # Will prob. be changed to POST
def notify_peers():
    message = request.args.get("message") if request.args.get("message") else "No message provided."
    data = {"message":message}
    return server_comm.broadcast_data(data)


@app.route('/get/seeds')
def get_seeds():
    return {"seeds":json.loads(os.environ["known_seeds"])}

@app.route('/get/is_active')
def get_active():
    return {"active":True}

''' miner '''

@app.route("/miner/kill")
def application_kill():
    MINER.stop_mining()
    exit()
    return redirect("/miner")

@app.route("/miner")
def miner_index():
    output = f'''
<p>Is currently mining: {MINER.is_mining()}</p>
<p>Mining with prublic key: {os.environ["PUBKEY"]}</p>
<p><a href="/miner/stop">stop mining</a> | <a href="/miner/continue">continue mining</a></p>
'''
    return output

@app.route("/miner/blockchain")
def miner_get_blockchain():
    chain = MINER.blockchain_instance.export_blockchain()
    length = len(chain)
    return f"<p>Number of Blocks: {str(length)}</p><p>{str(chain)}</p>"

@app.route("/miner/stop")
def miner_stop():
    MINER.stop_mining()
    return redirect("/miner")

@app.route("/miner/continue")
def miner_continue():
    MINER.continue_mining()
    return redirect("/miner")

@app.route("/consensus_test",methods=["GET"])
def cons_test():
    consensus_test()
    return "Ran consesnsus test, check console for more information"