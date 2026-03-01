#!/bin/bash
set -e

MC_DIR=~/afk-andy/minecraft
mkdir -p "$MC_DIR"
cd "$MC_DIR"

# Download latest Paper 1.21.4
echo "Downloading Paper..."
PAPER_VERSION="1.21.4"
BUILD=$(curl -s "https://api.papermc.io/v2/projects/paper/versions/$PAPER_VERSION/builds" | jq '.builds[-1].build')
DOWNLOAD=$(curl -s "https://api.papermc.io/v2/projects/paper/versions/$PAPER_VERSION/builds/$BUILD" | jq -r '.downloads.application.name')
curl -o paper.jar "https://api.papermc.io/v2/projects/paper/versions/$PAPER_VERSION/builds/$BUILD/downloads/$DOWNLOAD"
echo "Downloaded Paper $PAPER_VERSION build $BUILD"

# Accept EULA
echo "eula=true" > eula.txt

# Generate a random RCON password
RCON_PASS=$(openssl rand -hex 12)

# Create server.properties
cat > server.properties <<PROPS
server-port=25565
enable-rcon=true
rcon.port=25575
rcon.password=$RCON_PASS
white-list=true
motd=AFK Andy's Minecraft Server
max-players=10
view-distance=10
simulation-distance=8
online-mode=true
PROPS

echo ""
echo "=== Paper server ready in $MC_DIR ==="
echo ""
echo "RCON password (auto-generated): $RCON_PASS"
echo ""
echo "IMPORTANT: Add this to your .env file:"
echo "  RCON_PASSWORD=$RCON_PASS"
echo ""
