from app import app,socketio
import os

print(__name__ + " called")

if __name__ == '__main__':
    print(f"Server running as {'Seed' if os.environ['IS_SEED_SERVER'] else 'Peer'}-Server")
    print(f"Public key: {os.environ['PUBKEY']}")

    socketio.run(app=app)