from app import app,server_comm
from flask import request

@app.route("/",methods=["GET"])
def index():
    return "Running healthy"

@app.route("/broadcast",methods=["GET"]) # Will prob. be changed to POST
def notify_peers():
    message = request.args.get("message") if request.args.get("message") else "No message provided."
    data = {"message":message}
    return server_comm.broadcast_data(data)
