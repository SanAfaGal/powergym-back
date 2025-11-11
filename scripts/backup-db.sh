#!/bin/bash
# Database Backup Script for PowerGym Backend
# Usage: ./scripts/backup-db.sh [--env production|development] [--retention-days N]
#
# This script creates a compressed backup of the PostgreSQL database
# running in a Docker container. Backups are stored in ./backups/postgres/
#
# Prerequisites:
# - Docker must be installed and running
# - The database container must be running
# - Environment variables must be set in .env file

set -e

# Get the directory where this script is located
SCRIPT_DIR="$( cd "$( dirname "${BASH_SOURCE[0]}" )" && pwd )"
# Get the project root (parent of scripts/)
PROJECT_ROOT="$( cd "$SCRIPT_DIR/.." && pwd )"

# Change to project root
cd "$PROJECT_ROOT"

# Colors for output
RED='\033[0;31m'
GREEN='\033[0;32m'
YELLOW='\033[1;33m'
BLUE='\033[0;34m'
NC='\033[0m' # No Color

# Default values
ENV="production"
RETENTION_DAYS=7
COMPOSE_FILE="docker-compose.production.yml"

# Parse arguments
while [[ $# -gt 0 ]]; do
    case $1 in
        --env)
            ENV="$2"
            if [ "$ENV" = "production" ]; then
                COMPOSE_FILE="docker-compose.production.yml"
            elif [ "$ENV" = "development" ]; then
                COMPOSE_FILE="docker-compose.development.yml"
            else
                echo -e "${RED}Error: --env must be 'production' or 'development'${NC}"
                exit 1
            fi
            shift 2
            ;;
        --retention-days)
            RETENTION_DAYS="$2"
            shift 2
            ;;
        *)
            echo -e "${RED}Unknown option: $1${NC}"
            echo "Usage: ./scripts/backup-db.sh [--env production|development] [--retention-days N]"
            exit 1
            ;;
    esac
done

# Check if compose file exists
if [ ! -f "$COMPOSE_FILE" ]; then
    echo -e "${RED}Error: $COMPOSE_FILE not found${NC}"
    exit 1
fi

# Load environment variables from .env file
if [ -f .env ]; then
    export $(grep -v '^#' .env | xargs)
else
    echo -e "${YELLOW}Warning: .env file not found. Using defaults or environment variables.${NC}"
fi

# Set defaults from environment or use defaults
CONTAINER_NAME="${ENV}_db_${ENV}"
if [ "$ENV" = "production" ]; then
    CONTAINER_NAME="powergym_db_prod"
elif [ "$ENV" = "development" ]; then
    CONTAINER_NAME="powergym_db_dev"
fi

DB_NAME="${POSTGRES_DB:-powergym}"
DB_USER="${POSTGRES_USER:-user}"
BACKUP_DIR="$PROJECT_ROOT/backups/postgres"
DATE=$(date +%Y%m%d_%H%M%S)
BACKUP_FILE="$BACKUP_DIR/backup_${ENV}_${DATE}.sql.gz"
LOG_FILE="$BACKUP_DIR/backup.log"

# Create backup directory if it doesn't exist
mkdir -p "$BACKUP_DIR"

# Function to log messages
log() {
    echo -e "$1" | tee -a "$LOG_FILE"
}

log "${BLUE}========================================${NC}"
log "${BLUE}PowerGym Database Backup${NC}"
log "${BLUE}========================================${NC}"
log "Environment: ${GREEN}$ENV${NC}"
log "Date: $(date '+%Y-%m-%d %H:%M:%S')"
log ""

# Check if Docker is running
if ! docker info >/dev/null 2>&1; then
    log "${RED}Error: Docker is not running${NC}"
    exit 1
fi

# Check if container exists and is running
if ! docker ps --format '{{.Names}}' | grep -q "^${CONTAINER_NAME}$"; then
    log "${RED}Error: Container '$CONTAINER_NAME' is not running${NC}"
    log "${YELLOW}Available containers:${NC}"
    docker ps --format '{{.Names}}' | sed 's/^/  - /'
    exit 1
fi

log "${YELLOW}Creating backup...${NC}"
log "Container: ${GREEN}$CONTAINER_NAME${NC}"
log "Database: ${GREEN}$DB_NAME${NC}"
log "User: ${GREEN}$DB_USER${NC}"
log "Backup file: ${GREEN}$BACKUP_FILE${NC}"
log ""

# Create backup using pg_dump inside the container
if docker exec "$CONTAINER_NAME" pg_dump -U "$DB_USER" -d "$DB_NAME" --no-owner --no-acl 2>/dev/null | gzip > "$BACKUP_FILE"; then
    BACKUP_SIZE=$(du -h "$BACKUP_FILE" | cut -f1)
    log "${GREEN}✓ Backup created successfully${NC}"
    log "  Size: ${GREEN}$BACKUP_SIZE${NC}"
    log "  File: ${GREEN}$BACKUP_FILE${NC}"
else
    log "${RED}✗ Backup failed${NC}"
    # Clean up failed backup file if it exists
    [ -f "$BACKUP_FILE" ] && rm -f "$BACKUP_FILE"
    exit 1
fi

log ""

# Clean up old backups (keep only last N days)
log "${YELLOW}Cleaning up old backups (keeping last $RETENTION_DAYS days)...${NC}"
DELETED_COUNT=$(find "$BACKUP_DIR" -name "backup_${ENV}_*.sql.gz" -type f -mtime +$RETENTION_DAYS -delete -print | wc -l)
if [ "$DELETED_COUNT" -gt 0 ]; then
    log "${GREEN}✓ Deleted $DELETED_COUNT old backup(s)${NC}"
else
    log "${GREEN}✓ No old backups to delete${NC}"
fi

log ""

# Show backup summary
log "${BLUE}Backup Summary:${NC}"
TOTAL_BACKUPS=$(find "$BACKUP_DIR" -name "backup_${ENV}_*.sql.gz" -type f | wc -l)
TOTAL_SIZE=$(du -sh "$BACKUP_DIR" | cut -f1)
log "  Total backups ($ENV): ${GREEN}$TOTAL_BACKUPS${NC}"
log "  Total size: ${GREEN}$TOTAL_SIZE${NC}"
log ""

log "${GREEN}========================================${NC}"
log "${GREEN}Backup completed successfully!${NC}"
log "${GREEN}========================================${NC}"

