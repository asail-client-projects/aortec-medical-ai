#!/bin/bash
# AORTEC Medical AI - Monitoring Script

# Configuration
APP_NAME="AORTEC Medical AI"
HEALTH_URL="http://localhost:8000/health"
LOG_DIR="/opt/aortec/logs"
ALERT_EMAIL="${ALERT_EMAIL:-admin@example.com}"

# Colors
GREEN='\033[0;32m'
RED='\033[0;31m'
YELLOW='\033[1;33m'
BLUE='\033[0;34m'
NC='\033[0m'

# Clear screen
clear

echo -e "${BLUE}=================================================="
echo -e "$APP_NAME - System Monitor"
echo -e "==================================================${NC}"
echo

# Function to check service status
check_service() {
    local service=$1
    local container_name=$2
    
    if docker ps | grep -q $container_name; then
        echo -e "${GREEN}✓${NC} $service: Running"
    else
        echo -e "${RED}✗${NC} $service: Not running"
    fi
}

# Function to check health endpoint
check_health() {
    if curl -sf $HEALTH_URL > /dev/null; then
        echo -e "${GREEN}✓${NC} Health Check: Passed"
    else
        echo -e "${RED}✗${NC} Health Check: Failed"
    fi
}

# System Information
echo -e "${YELLOW}System Information:${NC}"
echo "- Hostname: $(hostname)"
echo "- IP Address: $(curl -s ifconfig.me 2>/dev/null || echo "Unable to determine")"
echo "- Uptime: $(uptime -p)"
echo

# Resource Usage
echo -e "${YELLOW}Resource Usage:${NC}"
echo "- CPU Load: $(uptime | awk -F'load average:' '{print $2}')"
echo "- Memory: $(free -h | awk '/^Mem:/ {print "Used: " $3 " / Total: " $2 " (" int($3/$2 * 100) "%)"}')"
echo "- Disk: $(df -h / | awk 'NR==2 {print "Used: " $3 " / Total: " $2 " (" $5 ")"}')"
echo

# Docker Services Status
echo -e "${YELLOW}Service Status:${NC}"
check_service "Web Application" "aortec_web"
check_service "Nginx Proxy" "aortec_nginx"
check_service "Redis Cache" "aortec_redis"
check_health
echo

# Container Resource Usage
echo -e "${YELLOW}Container Resources:${NC}"
docker stats --no-stream --format "table {{.Container}}\t{{.CPUPerc}}\t{{.MemUsage}}" | grep aortec || echo "No containers running"
echo

# Recent Logs
echo -e "${YELLOW}Recent Application Logs:${NC}"
if [ -f "$LOG_DIR/aortec.log" ]; then
    tail -5 $LOG_DIR/aortec.log 2>/dev/null | sed 's/^/  /'
else
    echo "  No application logs found"
fi
echo

# Recent Errors
echo -e "${YELLOW}Recent Errors (last 24h):${NC}"
if [ -f "$LOG_DIR/aortec.log" ]; then
    grep -i "error\|exception" $LOG_DIR/aortec.log 2>/dev/null | tail -5 | sed 's/^/  /' || echo "  No errors found"
else
    echo "  No log file available"
fi
echo

# Quick Actions
echo -e "${BLUE}Quick Actions:${NC}"
echo "  1. View logs: docker-compose logs -f"
echo "  2. Restart services: docker-compose restart"
echo "  3. Check disk space: df -h"
echo "  4. View processes: htop"
echo "  5. Run backup: ./backup.sh"
echo

# Alert if issues detected
if ! curl -sf $HEALTH_URL > /dev/null; then
    echo -e "${RED}⚠ WARNING: Health check failed! Services may be down.${NC}"
fi

echo -e "${BLUE}==================================================${NC}"
echo "Press Ctrl+C to exit"

# Optional: Send alert email if health check fails
# if ! curl -sf $HEALTH_URL > /dev/null; then
#     echo "AORTEC Health Check Failed on $(hostname)" | mail -s "AORTEC Alert" $ALERT_EMAIL
# fi