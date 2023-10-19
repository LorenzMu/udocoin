# Run application with Docker

Navigate to directory /udocoin/udocoin_miner

run start-files

Windows
```sh
.\start.ps1
```

Linux
```sh
.\start.sh
```

## OR

run docker-compose with variables

Windows
```sh
$env:SEED_SERVER = "<[y/n]>"; $env:PUBKEY = "<public_key>"; docker-compose up --build --scale app=1
```

Linux
```sh
SEED_SERVER=<[y/n]> PUBKEY=<public_key> docker-compose up --build --scale app=1
```

stop Docker-compose to stop application

```sh
docker-compose down
```

