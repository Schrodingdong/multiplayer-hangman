#!/bin/bash

# Function to check if ngrok is installed
function check_ngrok_installed {
    if [ ! -f "$PROGRAMFILES/ngrok/ngrok" ]; then
        return 1
    fi
    return 0
}

# Prompt the user to select between two choices
read -p "Select an option (1 or 2):
1. Host
2. Player
?> " choice

# Validate the user input
if [ "$choice" == "1" ]; then
    # Check if ngrok is installed
    if ! check_ngrok_installed; then
        echo "ngrok is not installed. Please install it."
        # You may add installation instructions here depending on the system.
        curl -s https://ngrok-agent.s3.amazonaws.com/ngrok.asc \
            | sudo tee /etc/apt/trusted.gpg.d/ngrok.asc >/dev/null \
            && echo "deb https://ngrok-agent.s3.amazonaws.com buster main" \
            | sudo tee /etc/apt/sources.list.d/ngrok.list \
            && sudo apt update \
            && sudo apt install ngrok
        
        ngrok config add-authtoken $NGROK_TOKEN
    fi
    # Start ngrok in a new terminal window
    gnome-terminal -- ngrok http 8000 & disown
fi

# Install pip dependencies
pip install -r ./requirements.txt

# start application
python ./python_impl/src/main.py
