# Get user input
$SEED_SERVER = Read-Host "Is the Server a Seed-Server? [y/n]"
$PUBKEY = Read-Host "Please insert your public-key"

# Set environment variables
$env:SEED_SERVER = $SEED_SERVER
$env:PUBKEY = $PUBKEY

# Build docker containers
docker-compose up --build