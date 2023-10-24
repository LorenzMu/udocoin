# Function to prompt user and handle responses
function PromptForKeys {
    $privateKeyResponse = Read-Host "Do you have a private and a public key? [y/n]"

    if ($privateKeyResponse -eq "n") {
        # If venv\Scripts\Activate.ps1 does not exist
        if (-Not (Test-Path application\venv\Scripts\Activate.ps1)) {
            python -m venv application\venv
        }

        # Activate virtual environment
        application\venv\Scripts\Activate.ps1

        # Install cryptography library
        pip install "cryptography==41.0.4"
        
        # Generate keys using key_gen.py
        # private and public key will be saved to \.udocoin
        python application\key_gen.py

        # Deactivate virtual environment
        Deactivate

    }
    elseif (-Not ($privateKeyResponse -eq "y")) {
        Write-Host "Invalid input. Please enter 'y' or 'n'."
        PromptForKeys # Ask again for valid input
    }
}

function SetPrivkeyVariable {
    try {
        $PRIVKEY_PATH = Read-Host "Please insert the path to your private-key"
        if (-Not (Test-Path $PRIVKEY_PATH)) {
            Write-Host "File not found: $PRIVKEY_PATH"
            return SetPrivkeyVariable
        }
        $PRIVKEY_CONTENT = Get-Content -Path $PRIVKEY_PATH -Encoding UTF8
        [Environment]::SetEnvironmentVariable("PRIVKEY", $PRIVKEY_CONTENT, [System.EnvironmentVariableTarget]::User)
        
        # Write-Host $PRIVKEY_CONTENT
        return $PRIVKEY_CONTENT
    } catch {
        Write-Host "Error: $_"
    }
}

function SetPubkeyVariable {
    try {
        $PUBKEY_PATH = Read-Host "Please insert the path to your public-key"
        if (-Not (Test-Path $PUBKEY_PATH)) {
            Write-Host "File not found: $PUBKEY_PATH"
            return SetPubkeyVariable
        }
        $PUBKEY_CONTENT = Get-Content -Path $PUBKEY_PATH -Encoding UTF8
        [Environment]::SetEnvironmentVariable("PUBKEY", $PUBKEY_CONTENT, [System.EnvironmentVariableTarget]::User)
        
        # Write-Host $PUBKEY_CONTENT
        return $PUBKEY_CONTENT
    } catch {
        Write-Host "Error: $_"
    }
}

function SetSeedServerVariable {
    $SEED_SERVER = Read-Host "Is the Server supposed to run as a Seed-Server and has a static and public ip address? [y/n]"
    if( -Not (($SEED_SERVER -eq "y") -or ($SEED_SERVER -eq "n"))){
        Write-Host "Invalid input. Please enter 'y' or 'n'."
        return SetSeedServerVariable
    }
    [Environment]::SetEnvironmentVariable("SEED_SERVER", $SEED_SERVER, [System.EnvironmentVariableTarget]::User)
    
    return $SEED_SERVER
}


try {
    PromptForKeys

    # Get user inputs and set env variables
    $PRIVKEY_CONTENT = SetPrivkeyVariable
    $PUBKEY_CONTENT = SetPubkeyVariable
    $SEED_SERVER = SetSeedServerVariable

    $env:PRIVKEY = $PRIVKEY_CONTENT
    $env:PUBKEY = $PUBKEY_CONTENT
    $env:SEED_SERVER = $SEED_SERVER

    # python test.py

    # Build docker containers
    docker-compose up --build 
}
catch {
    Write-Host "Error: $_"
}
