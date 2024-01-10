#!/bin/bash

# Update package index
sudo apt update

# Install required dependencies
sudo apt install -y apt-transport-https ca-certificates curl software-properties-common

# Add Docker GPG key
curl -fsSL https://download.docker.com/linux/ubuntu/gpg | sudo gpg --dearmor -o /usr/share/keyrings/docker-archive-keyring.gpg

# Add Docker repository
echo "deb [signed-by=/usr/share/keyrings/docker-archive-keyring.gpg] https://download.docker.com/linux/ubuntu $(lsb_release -cs) stable" | sudo tee /etc/apt/sources.list.d/docker.list > /dev/null

# Update package index again
sudo apt update

# Install Docker version 20.10.24
sudo apt install -y docker-ce=5:20.10.24~3-0~ubuntu-$(lsb_release -cs) docker-ce-cli=5:20.10.24~3-0~ubuntu-$(lsb_release -cs) containerd.io

# Add your user to the docker group to run Docker without sudo
sudo usermod -aG docker $USER

# Install Docker Compose version 2.23.3
sudo curl -L "https://github.com/docker/compose/releases/download/v2.23.3/docker-compose-$(uname -s)-$(uname -m)" -o /usr/local/bin/docker-compose

# Apply executable permissions to the Docker Compose binary
sudo chmod +x /usr/local/bin/docker-compose

# Create a symbolic link to allow using the 'docker-compose' command without specifying the full path
sudo ln -s /usr/local/bin/docker-compose /usr/bin/docker-compose

# Display Docker and Docker Compose versions
docker --version
docker-compose --version