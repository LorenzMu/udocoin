from app import app,socketio
import os

if __name__ == '__main__':
    socketio.run(app=app)
    
    print(f"Server running as {'Seed' if os.environ['IS_SEED_SERVER'] else 'Peer'}-Server")
    print(f"Public key: {os.environ['PUBKEY']}")