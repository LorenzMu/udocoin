from app import app,server_comm
from flask import request,redirect,abort
import os,json
from app.miner import MINER
from app.blockchain_modules.consensus_tests import consensus_test
from app.blockchain_modules.udocoin_dataclasses import SignedTransaction
import dacite

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
<p>Mining with public key: {os.environ["PUBKEY"]}</p>
<p><a href="/miner/stop">stop mining</a> | <a href="/miner/continue">continue mining</a></p>
'''
    return output

@app.route("/miner/blockchain")
def miner_get_blockchain():
    return MINER.blockchain_instance.export_blockchain()

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


@app.route("/miner/post_transaction",methods=["POST"])
def post_transaction():
    post_request = request.get_json()
    signed_trans = dacite.from_dict(data_class=SignedTransaction, data={k: v for k, v in post_request.items() if v is not None})

    return_message = MINER.receive_transaction_request(signed_trans)
    return return_message

@app.route("/miner/get_balance/all")
def get_balance_all():
    return str(MINER.blockchain_instance.balances)

@app.route("/miner/get_balance")
def get_balance():
    public_key = request.args.get("pubkey")
    if public_key == None:
        return redirect("/miner/get_balance/all")
    public_key = public_key.replace("_","\n")
    balance = MINER.blockchain_instance.balances.get(public_key)
    return str(balance) if balance is not None else "0"

@app.route("/miner/mempool")
def get_mempool():
    return MINER.mempool

