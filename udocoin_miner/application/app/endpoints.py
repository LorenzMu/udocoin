from app import app,server_comm
from flask import request,redirect,abort
import os,json
from app import formate_key
from app.miner import MINER
from app.blockchain_modules.consensus_tests import consensus_test
from app.blockchain_modules.udocoin_dataclasses import SignedTransaction, SerializableSignedTransaction, serialize_signed_transaction, deserialize_signed_transaction
import dacite
from base64 import b64encode, b64decode

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

@app.route('/get/connections')
def get_connections():
    return {"connections":server_comm.count_clients()}

''' miner '''

@app.route("/miner/kill")
def application_kill():
    MINER.stop_mining()
    exit()
    return redirect("/miner")

@app.route("/miner")
def miner_index():
    key = os.environ["PUBKEY"]
    print("key:",key)
    formated_key = formate_key(key).replace("\n","_")
    print("formated key: ",formated_key)
    # sorry for that, the keys formatting breaks with only html
    output = f'''
<p>Is currently mining: {MINER.is_mining()}</p>
<p><img id="qr_code_img" alt="{key}"></p>
<p><a href="/miner/stop">stop mining</a> 
| <a href="/miner/continue">continue mining</a>
| <a href="/miner/blockchain" target="_blank">See blockchain</a>
| <a href="/miner/get_balance/all" target="_blank">See balances</a>
| <a href="/miner/mempool" target="_blank">See Mempool</a></p>
<script>
    const key = "{formated_key}";
    const src = "https://api.qrserver.com/v1/create-qr-code/?size=300x300&data=" + key.replaceAll("_","\\n")
    console.log(src)
    document.getElementById("qr_code_img").src = encodeURI(src);
</script>
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
    #print(post_request)
    try:
        serializable_signed_transaction = SerializableSignedTransaction(post_request["origin_public_key"],post_request["signature"], post_request["message"])
        signed_transaction = deserialize_signed_transaction(serializable_signed_transaction)
        return_message = MINER.receive_transaction_request(signed_transaction)
        return return_message
    
    except KeyError as ke:
        return f"Invalid Post Request: {str(ke)}"

@app.route("/miner/get_balance/all")
def get_balance_all():
    return str(MINER.blockchain_instance.balances) + "\n\n INDEX CONFIRMED: " + str(MINER.blockchain_instance.index_confirmed)

@app.route("/miner/get_balance")
def get_balance():
    public_key = request.args.get("pubkey")
    if public_key == None:
        return redirect("/miner/get_balance/all")
    public_key = public_key.replace("_","\n")
    balance = MINER.blockchain_instance.balances.get(public_key)
    return (str(balance) if balance is not None else "0") + "\n\n INDEX CONFIRMED: " + str(MINER.blockchain_instance.index_confirmed)

@app.route("/miner/mempool")
def get_mempool():
    if len(MINER.mempool) == 0:
        return []
    if type(MINER.mempool[0].origin_public_key) != bytes:
        return MINER.mempool
    serializable_transaction_list = []
    for signed_transaction in MINER.mempool:
        serializable_signed_transaction = serialize_signed_transaction(signed_transaction)
        serializable_transaction_list.append(serializable_signed_transaction)

    return serializable_transaction_list

