#!/bin/bash
# Setup Cron Job for Database Backups
# Usage: ./scripts/setup-backup-cron.sh [--env production|development] [--hour HOUR] [--remove]
#
# This script sets up a cron job to automatically backup the database daily.
# The backup will run at the specified hour (default: 2 AM).

set -e

# Get the directory where this script is located
SCRIPT_DIR="$( cd "$( dirname "${BASH_SOURCE[0]}" )" && pwd )"
# Get the project root (parent of scripts/)
PROJECT_ROOT="$( cd "$SCRIPT_DIR/.." && pwd )"

# Colors for output
RED='\033[0;31m'
GREEN='\033[0;32m'
YELLOW='\033[1;33m'
BLUE='\033[0;34m'
NC='\033[0m' # No Color

# Default values
ENV="production"
HOUR=2
REMOVE=false

# Parse arguments
while [[ $# -gt 0 ]]; do
    case $1 in
        --env)
            ENV="$2"
            if [ "$ENV" != "production" ] && [ "$ENV" != "development" ]; then
                echo -e "${RED}Error: --env must be 'production' or 'development'${NC}"
                exit 1
            fi
            shift 2
            ;;
        --hour)
            HOUR="$2"
            if ! [[ "$HOUR" =~ ^[0-9]+$ ]] || [ "$HOUR" -lt 0 ] || [ "$HOUR" -gt 23 ]; then
                echo -e "${RED}Error: --hour must be a number between 0 and 23${NC}"
                exit 1
            fi
            shift 2
            ;;
        --remove)
            REMOVE=true
            shift
            ;;
        *)
            echo -e "${RED}Unknown option: $1${NC}"
            echo "Usage: ./scripts/setup-backup-cron.sh [--env production|development] [--hour HOUR] [--remove]"
            exit 1
            ;;
    esac
done

BACKUP_SCRIPT="$PROJECT_ROOT/scripts/backup-db.sh"
CRON_COMMENT="# PowerGym DB Backup ($ENV)"
CRON_JOB="0 $HOUR * * * $BACKUP_SCRIPT --env $ENV >> $PROJECT_ROOT/backups/postgres/cron.log 2>&1"

echo -e "${BLUE}========================================${NC}"
echo -e "${BLUE}PowerGym Backup Cron Job Setup${NC}"
echo -e "${BLUE}========================================${NC}"
echo ""

# Check if backup script exists
if [ ! -f "$BACKUP_SCRIPT" ]; then
    echo -e "${RED}Error: Backup script not found: $BACKUP_SCRIPT${NC}"
    exit 1
fi

# Make sure backup script is executable
chmod +x "$BACKUP_SCRIPT"

if [ "$REMOVE" = true ]; then
    echo -e "${YELLOW}Removing cron job for $ENV environment...${NC}"
    # Remove the cron job
    (crontab -l 2>/dev/null | grep -v "$CRON_COMMENT" | grep -v "$BACKUP_SCRIPT.*--env $ENV" || true) | crontab -
    echo -e "${GREEN}✓ Cron job removed${NC}"
    echo ""
    echo -e "${BLUE}Current cron jobs:${NC}"
    crontab -l 2>/dev/null | grep -E "(PowerGym|backup-db)" || echo "  No PowerGym backup jobs found"
else
    echo -e "${YELLOW}Setting up cron job for $ENV environment...${NC}"
    echo "  Schedule: Daily at ${HOUR}:00"
    echo "  Script: $BACKUP_SCRIPT"
    echo "  Environment: $ENV"
    echo ""
    
    # Check if cron job already exists
    if crontab -l 2>/dev/null | grep -q "$BACKUP_SCRIPT.*--env $ENV"; then
        echo -e "${YELLOW}Cron job already exists. Updating...${NC}"
        # Remove existing job and add new one
        (crontab -l 2>/dev/null | grep -v "$CRON_COMMENT" | grep -v "$BACKUP_SCRIPT.*--env $ENV" || true; echo "$CRON_COMMENT"; echo "$CRON_JOB") | crontab -
    else
        # Add new cron job
        (crontab -l 2>/dev/null || true; echo "$CRON_COMMENT"; echo "$CRON_JOB") | crontab -
    fi
    
    echo -e "${GREEN}✓ Cron job installed successfully${NC}"
    echo ""
    echo -e "${BLUE}Current cron jobs:${NC}"
    crontab -l 2>/dev/null | grep -E "(PowerGym|backup-db)" || echo "  No PowerGym backup jobs found"
    echo ""
    echo -e "${GREEN}========================================${NC}"
    echo -e "${GREEN}Cron job setup completed!${NC}"
    echo -e "${GREEN}========================================${NC}"
    echo ""
    echo -e "${BLUE}To verify the cron job:${NC}"
    echo "  crontab -l"
    echo ""
    echo -e "${BLUE}To remove the cron job:${NC}"
    echo "  ./scripts/setup-backup-cron.sh --env $ENV --remove"
    echo ""
    echo -e "${BLUE}To view backup logs:${NC}"
    echo "  tail -f $PROJECT_ROOT/backups/postgres/cron.log"
fi

