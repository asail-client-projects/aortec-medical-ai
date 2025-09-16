#!/bin/bash
# AORTEC Update Deployment Script
# This script pulls latest changes from GitHub and redeploys

set -e  # Exit on error

echo "🔄 Starting AORTEC Update Process..."
echo "================================"

# Store current directory
CURRENT_DIR=$(pwd)

# Navigate to project directory
cd /home/ubuntu/aortec

echo "📥 Pulling latest changes from GitHub..."
git pull origin main

# Check if there are changes to docker files
if git diff HEAD@{1} --name-only | grep -E "(Dockerfile|docker-compose|requirements)" > /dev/null; then
    echo "🔨 Docker configuration changed. Rebuilding containers..."
    
    # Stop current containers
    echo "🛑 Stopping current containers..."
    docker-compose -f docker-compose.simple.yml down
    
    # Remove old images to force rebuild
    echo "🧹 Cleaning old images..."
    docker-compose -f docker-compose.simple.yml rm -f
    docker image prune -f
    
    # Rebuild and start containers
    echo "🚀 Building and starting updated containers..."
    docker-compose -f docker-compose.simple.yml up -d --build --force-recreate
else
    echo "♻️  No Docker changes. Restarting containers with new code..."
    
    # Just restart containers to pick up code changes
    docker-compose -f docker-compose.simple.yml restart
fi

# Wait for services to be ready
echo "⏳ Waiting for services to start..."
sleep 5

# Check if services are running
if docker ps | grep aortec_app > /dev/null; then
    echo "✅ Update completed successfully!"
    echo "================================"
    
    # Get IP address
    IP=$(hostname -I | awk '{print $1}')
    
    echo "📍 AORTEC is running at: http://$IP"
    echo "📊 View logs: docker logs aortec_app -f"
    echo "🔍 Check status: docker ps"
    
    # Show last 5 commits
    echo ""
    echo "📝 Latest updates:"
    git log --oneline -5
else
    echo "❌ Error: Container failed to start!"
    echo "Check logs with: docker logs aortec_app"
    exit 1
fi

# Return to original directory
cd $CURRENT_DIR