#!/bin/bash
# AORTEC One-Click Deploy - The Simplest Way

# Get IP address
IP=$(hostname -I | awk '{print $1}')

# Check if Docker is installed, if not install it
if ! command -v docker &> /dev/null; then
    echo "📦 Installing Docker..."
    curl -fsSL https://get.docker.com -o get-docker.sh
    sudo sh get-docker.sh
    rm get-docker.sh
fi

# Check if docker-compose is installed
if ! command -v docker-compose &> /dev/null; then
    echo "📦 Installing Docker Compose..."
    sudo curl -L "https://github.com/docker/compose/releases/latest/download/docker-compose-$(uname -s)-$(uname -m)" -o /usr/local/bin/docker-compose
    sudo chmod +x /usr/local/bin/docker-compose
fi

# Stop any running containers
docker-compose -f docker-compose.simple.yml down 2>/dev/null

# Build and run
echo "🚀 Deploying AORTEC..."
docker-compose -f docker-compose.simple.yml up -d --build

# Wait for startup
sleep 5

# Show result
clear
echo "✅ AORTEC Medical AI is running!"
echo "================================"
echo "📍 Access at: http://$IP"
echo "📊 View logs: docker logs aortec_app -f"
echo "🛑 Stop: docker-compose -f docker-compose.simple.yml down"
echo "================================"