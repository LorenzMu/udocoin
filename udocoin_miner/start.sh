#!/bin/bash

# Get user input
read -p "Is the Server a Seed-Server? [y/n] " SEED_SERVER
read -p "Please insert your public-key: " PUBKEY

# Set environment variables
export SEED_SERVER=$SEED_SERVER
export PUBKEY=$PUBKEY

# Build docker containers
docker-compose up --build
