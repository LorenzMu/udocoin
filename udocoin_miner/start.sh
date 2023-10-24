#!/bin/bash

# Function to prompt user and handle responses
function prompt_for_keys {
    read -p "Do you have a private and a public key? [y/n] " privateKeyResponse

    if [ "$privateKeyResponse" == "n" ]; then
        if [ ! -f "application/venv/Scripts/Activate.ps1" ]; then
            python -m venv application/venv
        fi

        source application/venv/Scripts/activate

        pip install "cryptography==41.0.4"

        python application/key_gen.py

        deactivate

    elif [ "$privateKeyResponse" != "y" ]; then
        echo "Invalid input. Please enter 'y' or 'n'."
        prompt_for_keys
    fi
}

function set_privkey_variable {
    while true; do
        read -p "Please insert the path to your private-key: " PRIVKEY_PATH

        if [ ! -f "$PRIVKEY_PATH" ]; then
            echo "File not found: $PRIVKEY_PATH"
        else
            PRIVKEY_CONTENT=$(<$PRIVKEY_PATH)
            export PRIVKEY_CONTENT
            break
        fi
    done
}

function set_pubkey_variable {
    while true; do
        read -p "Please insert the path to your public-key: " PUBKEY_PATH

        if [ ! -f "$PUBKEY_PATH" ]; then
            echo "File not found: $PUBKEY_PATH"
        else
            PUBKEY_CONTENT=$(<$PUBKEY_PATH)
            export PUBKEY_CONTENT
            break
        fi
    done
}

function set_seed_server_variable {
    while true; do
        read -p "Is the Server supposed to run as a Seed-Server and has a static and public ip address? [y/n] " SEED_SERVER

        if [ "$SEED_SERVER" != "y" ] && [ "$SEED_SERVER" != "n" ]; then
            echo "Invalid input. Please enter 'y' or 'n'."
        else
            export SEED_SERVER
            break
        fi
    done
}

# Main Script

prompt_for_keys

set_privkey_variable
set_pubkey_variable
set_seed_server_variable

export PRIVKEY="$PRIVKEY_CONTENT"
export PUBKEY="$PUBKEY_CONTENT"

# python test.py

# Build docker containers
# docker-compose up --build
