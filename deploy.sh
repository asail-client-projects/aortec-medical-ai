#!/bin/bash
# AORTEC Medical AI - Production Deployment Script for AWS Lightsail

set -e  # Exit on error

echo "======================================"
echo "AORTEC Medical AI - Deployment Script"
echo "======================================"

# Configuration
PROJECT_NAME="aortec-medical-ai"
DEPLOY_DIR="/opt/aortec"
BACKUP_DIR="/opt/backups/aortec"

# Colors for output
RED='\033[0;31m'
GREEN='\033[0;32m'
YELLOW='\033[1;33m'
NC='\033[0m' # No Color

# Function to print colored output
print_status() {
    echo -e "${GREEN}[$(date +'%Y-%m-%d %H:%M:%S')]${NC} $1"
}

print_error() {
    echo -e "${RED}[ERROR]${NC} $1"
}

print_warning() {
    echo -e "${YELLOW}[WARNING]${NC} $1"
}

# Check if running as root or with sudo
if [ "$EUID" -ne 0 ]; then 
    print_error "This script must be run as root or with sudo"
    exit 1
fi

# Create necessary directories
print_status "Creating deployment directories..."
mkdir -p $DEPLOY_DIR
mkdir -p $BACKUP_DIR
mkdir -p $DEPLOY_DIR/logs

# Navigate to deployment directory
cd $DEPLOY_DIR

# Check if .env file exists
if [ ! -f ".env" ]; then
    print_warning ".env file not found. Creating from .env.example..."
    if [ -f ".env.example" ]; then
        cp .env.example .env
        print_warning "Please edit .env file with production values before proceeding!"
        print_warning "Run: nano $DEPLOY_DIR/.env"
        exit 1
    else
        print_error ".env.example file not found!"
        exit 1
    fi
fi

# Backup current deployment if exists
if [ -d "$DEPLOY_DIR/docker-compose.yml" ]; then
    print_status "Backing up current deployment..."
    BACKUP_TIMESTAMP=$(date +%Y%m%d_%H%M%S)
    tar -czf "$BACKUP_DIR/backup_$BACKUP_TIMESTAMP.tar.gz" \
        --exclude='uploads/*' \
        --exclude='processed/*' \
        --exclude='logs/*' \
        .
fi

# Pull latest code (if using Git)
if [ -d ".git" ]; then
    print_status "Pulling latest code from repository..."
    git pull origin main
else
    print_warning "Git repository not found. Skipping code update."
fi

# Build and deploy with Docker Compose
print_status "Building Docker images..."
docker-compose build --no-cache

print_status "Stopping existing containers..."
docker-compose down

print_status "Starting new containers..."
docker-compose up -d

# Wait for services to be healthy
print_status "Waiting for services to be healthy..."
sleep 10

# Check service health
print_status "Checking service health..."
if curl -f http://localhost:8000/health > /dev/null 2>&1; then
    print_status "Health check passed!"
else
    print_error "Health check failed! Check logs with: docker-compose logs"
    exit 1
fi

# Clean up old Docker images
print_status "Cleaning up old Docker images..."
docker image prune -af

# Set up log rotation
print_status "Setting up log rotation..."
cat > /etc/logrotate.d/aortec << EOF
$DEPLOY_DIR/logs/*.log {
    daily
    rotate 7
    compress
    delaycompress
    missingok
    notifempty
    create 0644 aortec aortec
}
EOF

# Display deployment status
print_status "Deployment completed successfully!"
echo
echo "======================================"
echo "Deployment Summary:"
echo "======================================"
docker-compose ps
echo
echo "Application URL: http://$(curl -s ifconfig.me)"
echo "Logs: docker-compose logs -f"
echo "Stop: docker-compose down"
echo "Restart: docker-compose restart"
echo "======================================"