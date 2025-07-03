#!/bin/bash

# Variables
SERVER_IP="204.12.205.107"  # Replace with your actual server IP
FLASK_APP_PATH="/home/administrator/news-collection"
NGINX_CONFIG="/etc/nginx/sites-available/news-collection"

# Update and install dependencies
echo "Updating system and installing required packages..."
sudo apt update -y
sudo apt install -y nginx python3 python3-pip python3-venv ufw

# Install Gunicorn if not installed
if ! command -v gunicorn &> /dev/null; then
    echo "Installing Gunicorn..."
    pip3 install gunicorn
fi

# Create Flask app directory if it doesn't exist
if [ ! -d "$FLASK_APP_PATH" ]; then
    echo "Creating Flask app directory at $FLASK_APP_PATH..."
    sudo mkdir -p "$FLASK_APP_PATH"
    sudo chown -R $USER:$USER "$FLASK_APP_PATH"
fi

# Create a basic Flask app if not exists
if [ ! -f "$FLASK_APP_PATH/app.py" ]; then
    echo "Creating a basic Flask app..."
    cat <<EOF | sudo tee "$FLASK_APP_PATH/app.py"
from flask import Flask

app = Flask(__name__)

@app.route('/')
def home():
    return "Hello, Flask is running behind Nginx!"

if __name__ == '__main__':
    app.run(host='0.0.0.0', port=5000)
EOF
fi

# Setup Gunicorn Systemd service
echo "Setting up Gunicorn as a systemd service..."
sudo tee /etc/systemd/system/news-collection.service > /dev/null <<EOF
[Unit]
Description=Gunicorn instance to serve news-collection
After=network.target

[Service]
User=$USER
Group=www-data
WorkingDirectory=$FLASK_APP_PATH
ExecStart=$(which gunicorn) --workers 3 --bind 127.0.0.1:5000 app:app

[Install]
WantedBy=multi-user.target
EOF

# Start and enable Gunicorn service
sudo systemctl daemon-reload
sudo systemctl start news-collection
sudo systemctl enable news-collection

# Create Nginx configuration file
echo "Configuring Nginx..."
sudo tee "$NGINX_CONFIG" > /dev/null <<EOF
server {
    listen 80;
    server_name $SERVER_IP;

    location / {
        proxy_pass http://127.0.0.1:5000;
        proxy_set_header Host \$host;
        proxy_set_header X-Real-IP \$remote_addr;
        proxy_set_header X-Forwarded-For \$proxy_add_x_forwarded_for;
        proxy_set_header X-Forwarded-Proto \$scheme;
    }
}
EOF

# Enable Nginx site and restart Nginx
sudo ln -s "$NGINX_CONFIG" /etc/nginx/sites-enabled/
sudo nginx -t && sudo systemctl restart nginx

# Open necessary ports in firewall
echo "Configuring firewall..."
sudo ufw allow 80/tcp
sudo ufw allow 5000/tcp
sudo ufw reload

echo "Setup complete! Visit http://$SERVER_IP to check your Flask app."