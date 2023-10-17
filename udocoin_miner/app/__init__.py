from flask import Flask
from flask_cors import CORS
from flask_socketio import SocketIO

app = Flask(__name__)
app.config.from_object("config.DevelopmentConfig")

CORS(app)

socketio = SocketIO(app)

from app import endpoints
from app import server_comm as server_comm