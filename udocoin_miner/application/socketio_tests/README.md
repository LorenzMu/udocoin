# Test socketio

activate venv

```sh
udocoin\udocoin_miner\application\venv\Scripts\activate.ps1
```

Navigate to /udocoin/udocoin_miner/application/socketio_tests

run script

```sh
python socket_client.py
```

Post broadcast message

```sh
http://localhost/broadcast?message=<message>
```