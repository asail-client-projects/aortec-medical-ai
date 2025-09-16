# AORTEC Medical AI - Production Deployment Guide

## Overview
This guide provides step-by-step instructions for deploying the AORTEC Medical AI application to AWS Lightsail without a domain name.

## Prerequisites
- AWS Lightsail account
- SSH key pair for instance access
- Basic knowledge of Linux commands
- Git repository access (optional)

## Deployment Steps

### 1. Create AWS Lightsail Instance

1. Log into AWS Lightsail Console
2. Create new instance:
   - Platform: Linux/Unix
   - Blueprint: Ubuntu 22.04 LTS
   - Instance plan: Minimum 2GB RAM (recommended: 4GB)
   - Name: aortec-production
3. Download SSH key
4. Create static IP and attach to instance
5. Configure firewall:
   - SSH (22) - Default
   - HTTP (80) - Add
   - HTTPS (443) - Add (for future)
   - Custom TCP (8000) - Add (for testing)

### 2. Initial Server Setup

SSH into your instance:
```bash
ssh -i your-key.pem ubuntu@YOUR_INSTANCE_IP
```

Run the setup script:
```bash
# Download and run setup script
wget https://raw.githubusercontent.com/your-repo/aortec-medical-ai/main/setup-lightsail.sh
chmod +x setup-lightsail.sh
sudo ./setup-lightsail.sh
```

This script will:
- Update system packages
- Install Docker and Docker Compose
- Set up firewall rules
- Create application directories
- Configure swap space
- Set up auto-start service

### 3. Deploy Application

#### Option A: Clone from Git Repository
```bash
cd /opt/aortec
git clone https://github.com/your-repo/aortec-medical-ai.git .
```

#### Option B: Upload Files Manually
Use SCP or SFTP to upload project files:
```bash
scp -i your-key.pem -r ./aortec-medical-ai/* ubuntu@YOUR_INSTANCE_IP:/opt/aortec/
```

### 4. Configure Environment

1. Copy and edit environment file:
```bash
cd /opt/aortec
cp .env.example .env
nano .env
```

2. Update these critical values:
```env
FLASK_ENV=production
SECRET_KEY=your-generated-secret-key-here
CORS_ORIGINS=http://YOUR_INSTANCE_IP
```

3. Generate a secret key:
```bash
python3 -c 'import secrets; print(secrets.token_hex(32))'
```

### 5. Deploy with Docker

Run the deployment script:
```bash
cd /opt/aortec
chmod +x deploy.sh
sudo ./deploy.sh
```

This will:
- Build Docker images
- Start all services
- Verify health status
- Set up log rotation

### 6. Access Application

Your application will be available at:
- Main application: `http://YOUR_INSTANCE_IP`
- Direct Flask app (testing): `http://YOUR_INSTANCE_IP:8000`

## Post-Deployment Tasks

### 1. Set Up Monitoring

Run the monitoring script:
```bash
chmod +x monitor.sh
./monitor.sh
```

### 2. Configure Backups

Set up automated backups:
```bash
chmod +x backup.sh

# Add to crontab for daily backups at 2 AM
crontab -e
# Add: 0 2 * * * /opt/aortec/backup.sh
```

### 3. Security Hardening

1. Change default SSH port (optional):
```bash
sudo nano /etc/ssh/sshd_config
# Change Port 22 to Port 2222
sudo systemctl restart sshd
```

2. Set up fail2ban:
```bash
sudo apt install fail2ban
sudo systemctl enable fail2ban
```

3. Configure UFW firewall:
```bash
sudo ufw status
```

## Maintenance Commands

### View Logs
```bash
# All services
docker-compose logs -f

# Specific service
docker-compose logs -f web
docker-compose logs -f nginx

# Application logs
tail -f logs/aortec.log
```

### Restart Services
```bash
# Restart all
docker-compose restart

# Restart specific service
docker-compose restart web
```

### Update Application
```bash
cd /opt/aortec
git pull origin main  # If using Git
sudo ./deploy.sh
```

### Check Status
```bash
# Service status
docker-compose ps

# System resources
docker stats

# Health check
curl http://localhost:8000/health
```

## Troubleshooting

### Container Won't Start
```bash
# Check logs
docker-compose logs web

# Rebuild
docker-compose build --no-cache
docker-compose up -d
```

### Out of Memory
```bash
# Check memory
free -h

# Increase swap
sudo fallocate -l 8G /swapfile2
sudo chmod 600 /swapfile2
sudo mkswap /swapfile2
sudo swapon /swapfile2
```

### Permission Issues
```bash
# Fix ownership
sudo chown -R ubuntu:ubuntu /opt/aortec
sudo chown -R 1000:1000 uploads processed models data
```

### Port Already in Use
```bash
# Find process using port
sudo lsof -i :8000

# Kill process
sudo kill -9 PID
```

## Performance Optimization

1. **Enable Redis Caching**: Already configured in docker-compose.yml

2. **Optimize Images**: Use image compression for uploaded files

3. **Monitor Resources**:
```bash
htop  # CPU and memory
iotop  # Disk I/O
docker stats  # Container resources
```

4. **Scale Workers**: Edit gunicorn_config.py to adjust worker count

## Backup and Recovery

### Manual Backup
```bash
./backup.sh
```

### Restore from Backup
```bash
cd /opt/aortec
tar -xzf /opt/backups/aortec/backup_TIMESTAMP.tar.gz
docker-compose down
docker-compose up -d
```

## Security Checklist

- [ ] Changed SECRET_KEY in .env
- [ ] Configured firewall rules
- [ ] Set up automated backups
- [ ] Enabled automatic security updates
- [ ] Configured fail2ban
- [ ] Set up monitoring
- [ ] Reviewed file permissions
- [ ] Disabled debug mode

## Support

For issues:
1. Check logs: `docker-compose logs`
2. Review health status: `./monitor.sh`
3. Check system resources: `htop`
4. Review this guide's troubleshooting section

## Cost Optimization

- Use Lightsail snapshots for backups ($0.05/GB/month)
- Monitor bandwidth usage (first 3TB free)
- Consider reserved instances for long-term savings
- Use CloudWatch for detailed monitoring (optional)