#!/bin/bash
# AORTEC Medical AI - Backup Script

set -e  # Exit on error

# Configuration
TIMESTAMP=$(date +%Y%m%d_%H%M%S)
BACKUP_DIR="/opt/backups/aortec"
APP_DIR="/opt/aortec"
BACKUP_RETENTION_DAYS=30

# Colors for output
GREEN='\033[0;32m'
RED='\033[0;31m'
YELLOW='\033[1;33m'
NC='\033[0m'

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

# Create backup directory
mkdir -p $BACKUP_DIR

print_status "Starting AORTEC backup process..."

# Backup uploaded files
if [ -d "$APP_DIR/uploads" ]; then
    print_status "Backing up uploaded files..."
    tar -czf "$BACKUP_DIR/uploads_$TIMESTAMP.tar.gz" -C "$APP_DIR" uploads/
else
    print_warning "No uploads directory found"
fi

# Backup processed files
if [ -d "$APP_DIR/processed" ]; then
    print_status "Backing up processed files..."
    tar -czf "$BACKUP_DIR/processed_$TIMESTAMP.tar.gz" -C "$APP_DIR" processed/
else
    print_warning "No processed directory found"
fi

# Backup models
if [ -d "$APP_DIR/models" ]; then
    print_status "Backing up AI models..."
    tar -czf "$BACKUP_DIR/models_$TIMESTAMP.tar.gz" -C "$APP_DIR" models/
else
    print_warning "No models directory found"
fi

# Backup Docker volumes
print_status "Backing up Docker volumes..."
docker run --rm \
    -v aortec-medical-ai_redis_data:/data \
    -v $BACKUP_DIR:/backup \
    alpine tar czf /backup/redis_$TIMESTAMP.tar.gz -C / data

# Backup environment configuration (without secrets)
if [ -f "$APP_DIR/.env" ]; then
    print_status "Backing up environment configuration..."
    grep -v "SECRET\|KEY\|PASSWORD" "$APP_DIR/.env" > "$BACKUP_DIR/env_$TIMESTAMP.txt"
fi

# Create backup manifest
print_status "Creating backup manifest..."
cat > "$BACKUP_DIR/manifest_$TIMESTAMP.txt" << EOF
AORTEC Medical AI Backup Manifest
=================================
Timestamp: $TIMESTAMP
Date: $(date)
Host: $(hostname)

Files backed up:
$(ls -la $BACKUP_DIR/*_$TIMESTAMP.* 2>/dev/null | awk '{print "- " $9 " (" $5 " bytes)"}')

Disk usage:
$(df -h $APP_DIR | tail -1)

Docker containers:
$(docker ps --format "table {{.Names}}\t{{.Status}}" | tail -n +2)
EOF

# Calculate total backup size
TOTAL_SIZE=$(du -sh $BACKUP_DIR/*_$TIMESTAMP.* 2>/dev/null | awk '{sum+=$1} END {print sum}')

# Clean old backups
print_status "Cleaning old backups (older than $BACKUP_RETENTION_DAYS days)..."
find $BACKUP_DIR -type f -name "*.tar.gz" -mtime +$BACKUP_RETENTION_DAYS -delete
find $BACKUP_DIR -type f -name "*.txt" -mtime +$BACKUP_RETENTION_DAYS -delete

# Optional: Upload to S3 (requires AWS CLI configured)
if command -v aws &> /dev/null && [ ! -z "$S3_BUCKET" ]; then
    print_status "Uploading backups to S3..."
    aws s3 sync $BACKUP_DIR s3://$S3_BUCKET/aortec-backups/$TIMESTAMP/ --exclude "*" --include "*_$TIMESTAMP.*"
fi

print_status "Backup completed successfully!"
echo
echo "======================================"
echo "Backup Summary:"
echo "======================================"
echo "Location: $BACKUP_DIR"
echo "Timestamp: $TIMESTAMP"
echo "Files created:"
ls -lh $BACKUP_DIR/*_$TIMESTAMP.* 2>/dev/null | awk '{print "  - " $9 " (" $5 ")"}'
echo "======================================="