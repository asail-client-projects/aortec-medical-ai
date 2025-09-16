#!/bin/bash
# AORTEC One-Click Deploy - The Simplest Way

set -e  # Exit on any error

# Get IP address
IP=$(hostname -I | awk '{print $1}')

# Check if running with sudo
if [ "$EUID" -ne 0 ]; then 
    echo "Please run with sudo: sudo ./one-click-deploy.sh"
    exit 1
fi

# Check if Docker is installed, if not install it
if ! command -v docker &> /dev/null; then
    echo "📦 Installing Docker..."
    curl -fsSL https://get.docker.com -o get-docker.sh
    sh get-docker.sh
    rm get-docker.sh
    
    # Add user to docker group
    usermod -aG docker $SUDO_USER
    echo "Docker installed. You may need to log out and back in for group changes."
fi

# Check if docker-compose is installed
if ! command -v docker-compose &> /dev/null; then
    echo "📦 Installing Docker Compose..."
    curl -L "https://github.com/docker/compose/releases/latest/download/docker-compose-$(uname -s)-$(uname -m)" -o /usr/local/bin/docker-compose
    chmod +x /usr/local/bin/docker-compose
fi

# Stop any running containers
echo "🧹 Cleaning up old containers..."
docker-compose -f docker-compose.simple.yml down 2>/dev/null || true

# Build and run
echo "🚀 Building and deploying AORTEC..."
docker-compose -f docker-compose.simple.yml up -d --build

# Wait for startup
echo "⏳ Waiting for services to start..."
sleep 10

# Check if container is actually running
if docker ps | grep -q aortec_app; then
    echo ""
    echo "✅ AORTEC Medical AI is running!"
    echo "================================"
    echo "📍 Access at: http://$IP"
    echo "📊 View logs: docker logs aortec_app -f"
    echo "🛑 Stop: docker-compose -f docker-compose.simple.yml down"
    echo "================================"
else
    echo "❌ Error: Container failed to start!"
    echo "Check logs with: docker-compose -f docker-compose.simple.yml logs"
    exit 1
fi