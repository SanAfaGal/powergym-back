#!/bin/bash
# Database Restore Script for PowerGym Backend
# Usage: ./scripts/restore-db.sh <backup_file> [--env production|development] [--confirm]
#
# This script restores a PostgreSQL database from a backup file.
# WARNING: This will REPLACE all existing data in the database!
#
# Prerequisites:
# - Docker must be installed and running
# - The database container must be running
# - A valid backup file (.sql.gz or .sql)

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
CONFIRM=false
COMPOSE_FILE="docker-compose.production.yml"

# Parse arguments
BACKUP_FILE=""
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
        --confirm)
            CONFIRM=true
            shift
            ;;
        *)
            if [ -z "$BACKUP_FILE" ]; then
                BACKUP_FILE="$1"
            else
                echo -e "${RED}Unknown option: $1${NC}"
                echo "Usage: ./scripts/restore-db.sh <backup_file> [--env production|development] [--confirm]"
                exit 1
            fi
            shift
            ;;
    esac
done

# Check if backup file was provided
if [ -z "$BACKUP_FILE" ]; then
    echo -e "${RED}Error: Backup file is required${NC}"
    echo "Usage: ./scripts/restore-db.sh <backup_file> [--env production|development] [--confirm]"
    echo ""
    echo "Available backups:"
    if [ -d "$PROJECT_ROOT/backups/postgres" ]; then
        ls -lh "$PROJECT_ROOT/backups/postgres/"*.sql.gz 2>/dev/null | awk '{print "  " $9 " (" $5 ")"}'
    else
        echo "  No backups directory found"
    fi
    exit 1
fi

# Resolve backup file path (handle relative and absolute paths)
if [[ "$BACKUP_FILE" != /* ]]; then
    # Relative path - try from project root first, then from backups directory
    if [ -f "$PROJECT_ROOT/$BACKUP_FILE" ]; then
        BACKUP_FILE="$PROJECT_ROOT/$BACKUP_FILE"
    elif [ -f "$PROJECT_ROOT/backups/postgres/$BACKUP_FILE" ]; then
        BACKUP_FILE="$PROJECT_ROOT/backups/postgres/$BACKUP_FILE"
    fi
fi

# Check if backup file exists
if [ ! -f "$BACKUP_FILE" ]; then
    echo -e "${RED}Error: Backup file not found: $BACKUP_FILE${NC}"
    exit 1
fi

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

# Set container name based on environment
CONTAINER_NAME="${ENV}_db_${ENV}"
if [ "$ENV" = "production" ]; then
    CONTAINER_NAME="powergym_db_prod"
elif [ "$ENV" = "development" ]; then
    CONTAINER_NAME="powergym_db_dev"
fi

DB_NAME="${POSTGRES_DB:-powergym}"
DB_USER="${POSTGRES_USER:-user}"

echo -e "${RED}========================================${NC}"
echo -e "${RED}WARNING: DATABASE RESTORE${NC}"
echo -e "${RED}========================================${NC}"
echo ""
echo -e "${YELLOW}This operation will REPLACE all existing data in the database!${NC}"
echo ""
echo "Environment: ${GREEN}$ENV${NC}"
echo "Container: ${GREEN}$CONTAINER_NAME${NC}"
echo "Database: ${GREEN}$DB_NAME${NC}"
echo "Backup file: ${GREEN}$BACKUP_FILE${NC}"
echo "Backup size: ${GREEN}$(du -h "$BACKUP_FILE" | cut -f1)${NC}"
echo ""

# Confirmation prompt
if [ "$CONFIRM" = false ]; then
    echo -e "${RED}Are you sure you want to continue? (yes/no):${NC} "
    read -r response
    if [ "$response" != "yes" ]; then
        echo -e "${YELLOW}Restore cancelled.${NC}"
        exit 0
    fi
fi

# Check if Docker is running
if ! docker info >/dev/null 2>&1; then
    echo -e "${RED}Error: Docker is not running${NC}"
    exit 1
fi

# Check if container exists and is running
if ! docker ps --format '{{.Names}}' | grep -q "^${CONTAINER_NAME}$"; then
    echo -e "${RED}Error: Container '$CONTAINER_NAME' is not running${NC}"
    echo -e "${YELLOW}Available containers:${NC}"
    docker ps --format '{{.Names}}' | sed 's/^/  - /'
    exit 1
fi

echo ""
echo -e "${YELLOW}Starting restore process...${NC}"
echo ""

# Determine if backup is compressed
if [[ "$BACKUP_FILE" == *.gz ]]; then
    echo -e "${BLUE}Detected compressed backup (.gz)${NC}"
    RESTORE_CMD="gunzip -c"
else
    echo -e "${BLUE}Detected uncompressed backup${NC}"
    RESTORE_CMD="cat"
fi

# Drop existing connections and restore
echo -e "${YELLOW}Step 1: Terminating existing connections...${NC}"
docker exec "$CONTAINER_NAME" psql -U "$DB_USER" -d postgres -c "SELECT pg_terminate_backend(pid) FROM pg_stat_activity WHERE datname = '$DB_NAME' AND pid <> pg_backend_pid();" 2>/dev/null || true

echo -e "${YELLOW}Step 2: Dropping existing database...${NC}"
docker exec "$CONTAINER_NAME" psql -U "$DB_USER" -d postgres -c "DROP DATABASE IF EXISTS $DB_NAME;" 2>/dev/null || true

echo -e "${YELLOW}Step 3: Creating new database...${NC}"
docker exec "$CONTAINER_NAME" psql -U "$DB_USER" -d postgres -c "CREATE DATABASE $DB_NAME;" || {
    echo -e "${RED}Error: Failed to create database${NC}"
    exit 1
}

echo -e "${YELLOW}Step 4: Restoring data from backup...${NC}"
if $RESTORE_CMD "$BACKUP_FILE" | docker exec -i "$CONTAINER_NAME" psql -U "$DB_USER" -d "$DB_NAME" >/dev/null 2>&1; then
    echo -e "${GREEN}✓ Restore completed successfully${NC}"
else
    echo -e "${RED}✗ Restore failed${NC}"
    exit 1
fi

echo ""
echo -e "${GREEN}========================================${NC}"
echo -e "${GREEN}Database restored successfully!${NC}"
echo -e "${GREEN}========================================${NC}"
echo ""
echo -e "${BLUE}Next steps:${NC}"
echo "  1. Verify the data in the database"
echo "  2. Restart your backend application if needed"
echo "  3. Test the application functionality"

