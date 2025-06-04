#!/bin/bash

# Start SSH Agent and Add Key
eval "$(ssh-agent -s)"
ssh-add ~/.ssh/github

# Pull Latest Code from GitHub
echo "Pulling latest changes from GitHub..."
git pull origin main

# Restart the Service
echo "Restarting mmovie service..."
sudo systemctl stop mmovie
sudo systemctl start mmovie

# Check Service Status
echo "Checking mmovie service status..."
sudo systemctl status mmovie --no-pager
