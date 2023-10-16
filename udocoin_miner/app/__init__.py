from flask import Flask
from flask_cors import CORS
from flask_socketio import SocketIO

app = Flask(__name__)

CORS(app)

socketio = SocketIO(app)

from app import endpoints