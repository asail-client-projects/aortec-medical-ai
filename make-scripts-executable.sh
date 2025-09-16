#!/bin/bash
# Make all deployment scripts executable

echo "Making deployment scripts executable..."

chmod +x setup-lightsail.sh
chmod +x deploy.sh
chmod +x backup.sh
chmod +x monitor.sh

echo "Done! All scripts are now executable."
echo
echo "Script purposes:"
echo "- setup-lightsail.sh: Initial server setup (run once)"
echo "- deploy.sh: Deploy/update the application"
echo "- backup.sh: Backup data and configurations"
echo "- monitor.sh: Monitor system and service status"