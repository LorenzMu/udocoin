#!/bin/bash

# Function to prompt user and handle responses
function prompt_for_keys {
    read -p "Do you have a private and a public key? [y/n]" private_key_response

    if [[ "$private_key_response" == "n" ]]; then
        # If venv/Scripts/Activate.ps1 does not exist
        if [ ! -f "application/venv/Scripts/activate" ]; then
            python -m venv application/venv
        fi

        # Activate virtual environment
        source application/venv/Scripts/activate

        # Install cryptography library
        pip install "cryptography==41.0.4"
        
        # Generate keys using key_gen.py
        # private and public key will be saved to .udocoin
        python application/key_gen.py

        # Deactivate virtual environment
        deactivate

    elif [[ "$private_key_response" != "y" ]]; then
        echo "Invalid input. Please enter 'y' or 'n'."
        prompt_for_keys  # Ask again for valid input
    fi
}

function set_privkey_variable {
    try {
        PRIVKEY_PATH="$HOME/.udocoin/priv_key"
        read -p "Please insert the path to your private-key or skip for default [$PRIVKEY_PATH]: " privkey_path_input
        PRIVKEY_PATH="${PRIVKEY_PATH:-$privkey_path_input}"

        if [ ! -f "$PRIVKEY_PATH" ]; then
            echo "File not found: $PRIVKEY_PATH"
            set_privkey_variable
        fi

        PRIVKEY_CONTENT=$(cat "$PRIVKEY_PATH")
        export PRIVKEY="$PRIVKEY_CONTENT"
        return $PRIVKEY_CONTENT
    } catch {
        echo "Error: $_"
    }
}

function set_pubkey_variable {
    try {
        PUBKEY_PATH="$HOME/.udocoin/pub_key.pub"
        read -p "Please insert the path to your public-key or skip for default [$PUBKEY_PATH]: " pubkey_path_input
        PUBKEY_PATH="${PUBKEY_PATH:-$pubkey_path_input}"

        if [ ! -f "$PUBKEY_PATH" ]; then
            echo "File not found: $PUBKEY_PATH"
            set_pubkey_variable
        fi

        PUBKEY_CONTENT=$(cat "$PUBKEY_PATH")
        export PUBKEY="$PUBKEY_CONTENT"
        return $PUBKEY_CONTENT
    } catch {
        echo "Error: $_"
    }
}

function set_seed_server_variable {
    read -p "Is the Server supposed to run as a Seed-Server and has a static and public IP address? [y/n]" seed_server

    if [[ "$seed_server" != "y" && "$seed_server" != "n" ]]; then
        echo "Invalid input. Please enter 'y' or 'n'."
        set_seed_server_variable
    fi

    export SEED_SERVER="$seed_server"
    return $seed_server
}

try {
    prompt_for_keys

    # Get user inputs and set env variables
    PRIVKEY_CONTENT=$(set_privkey_variable)
    PUBKEY_CONTENT=$(set_pubkey_variable)
    SEED_SERVER=$(set_seed_server_variable)

    export PRIVKEY="$PRIVKEY_CONTENT"
    export PUBKEY="$PUBKEY_CONTENT"
    export SEED_SERVER="$SEED_SERVER"

    # python test.py

    # Build docker containers
    docker-compose up --build
}
catch {
    echo "Error: $_"
}
