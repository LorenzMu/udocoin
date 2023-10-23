from app import app,server_comm,MINER,MINER_THREAD
from flask import request,redirect
import os

@app.route("/",methods=["GET"])
def index():
    return f"Running healthy as {'Seed' if os.environ['IS_SEED_SERVER'] else 'Peer'}-Server"

@app.route("/broadcast",methods=["GET"]) # Will prob. be changed to POST
def notify_peers():
    message = request.args.get("message") if request.args.get("message") else "No message provided."
    data = {"message":message}
    return server_comm.broadcast_data(data)

@app.route("/kill")
def application_kill():
    MINER.stop_mining()
    exit()

@app.route("/miner")
def miner_index():
    output = f'''
<p>Is currently mining: {MINER.is_mining()}</p>
<p><a href="/miner/stop">stop mining</a></p>
<p><a href="/miner/continue">continue mining</a></p>
'''
    return output

@app.route("/miner/stop")
def miner_stop():
    MINER.stop_mining()
    return redirect("/miner")

@app.route("/miner/continue")
def miner_continue():
    MINER.continue_mining()
    return redirect("/miner")