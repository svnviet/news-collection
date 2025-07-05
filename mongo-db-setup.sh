#!/bin/bash

# Configuration
MONGO_ADMIN_USER="admin"
MONGO_ADMIN_PASS="admin"
ALLOW_REMOTE_IP="0.0.0.0/0"
MONGO_PORT=27017

echo "[1/6] Updating system..."
sudo apt update -y

echo "[2/6] Installing MongoDB..."
wget -qO - https://www.mongodb.org/static/pgp/server-6.0.asc | sudo gpg --dearmor -o /usr/share/keyrings/mongodb-server-6.gpg
echo "deb [ signed-by=/usr/share/keyrings/mongodb-server-6.gpg ] https://repo.mongodb.org/apt/ubuntu focal/mongodb-org/6.0 multiverse" | sudo tee /etc/apt/sources.list.d/mongodb-org-6.0.list
sudo apt update -y
sudo apt install -y mongodb-org

echo "[3/6] Enabling and starting MongoDB..."
sudo systemctl enable mongod
sudo systemctl start mongod

echo "[4/6] Configuring mongod.conf for remote access and auth..."

# Use yq to safely edit YAML if available, otherwise fallback
if command -v yq &> /dev/null; then
  sudo yq -i '.net.bindIp = "0.0.0.0"' /etc/mongod.conf
  sudo yq -i '.security.authorization = "enabled"' /etc/mongod.conf
else
  sudo sed -i 's/^\([[:space:]]*bindIp:\).*/\1 0.0.0.0/' /etc/mongod.conf

  # Append security block only if it doesn't exist
  if ! grep -q "^security:" /etc/mongod.conf; then
    echo -e "\nsecurity:\n  authorization: enabled" | sudo tee -a /etc/mongod.conf > /dev/null
  else
    sudo sed -i "/^security:/,/^ *[^:]*:/{s/^ *authorization:.*/  authorization: enabled/}" /etc/mongod.conf
  fi
fi

echo "[5/6] Restarting MongoDB..."
sudo systemctl restart mongod
sleep 5

echo "Creating admin user..."
mongosh admin --eval "db.createUser({user: '$MONGO_ADMIN_USER', pwd: '$MONGO_ADMIN_PASS', roles: [{ role: 'root', db: 'admin' }]})"

echo "[6/6] Configuring firewall..."
sudo ufw allow "$MONGO_PORT"
sudo ufw allow from "$ALLOW_REMOTE_IP" to any port "$MONGO_PORT"
sudo ufw reload || echo "Firewall not enabled — skipping."

echo "✅ MongoDB setup complete!"
echo "  IP Allow: $ALLOW_REMOTE_IP"
echo "  Username: $MONGO_ADMIN_USER"
echo "  Password: $MONGO_ADMIN_PASS"
