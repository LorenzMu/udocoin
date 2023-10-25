from app import app,socketio
import os

if __name__ == '__main__':
    print(f"Server running as {'Seed' if os.environ['IS_SEED_SERVER'] else 'Peer'}-Server")
    socketio.run(app=app)