#!/bin/bash
# Deployment script for PowerGym Backend
# Usage: ./scripts/deploy.sh [--no-cache] [--branch BRANCH]
#
# This script should be run from the project root directory.
# It will automatically change to the project root if run from scripts/

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
NC='\033[0m' # No Color

# Default values
NO_CACHE=""
BRANCH=""

# Parse arguments
while [[ $# -gt 0 ]]; do
    case $1 in
        --no-cache)
            NO_CACHE="--no-cache"
            shift
            ;;
        --branch)
            BRANCH="$2"
            shift 2
            ;;
        *)
            echo -e "${RED}Unknown option: $1${NC}"
            echo "Usage: ./scripts/deploy.sh [--no-cache] [--branch BRANCH]"
            exit 1
            ;;
    esac
done

echo -e "${GREEN}========================================${NC}"
echo -e "${GREEN}PowerGym Backend Deployment${NC}"
echo -e "${GREEN}========================================${NC}"
echo ""

# Check prerequisites
echo -e "${YELLOW}Checking prerequisites...${NC}"
command -v git >/dev/null 2>&1 || { echo -e "${RED}Error: git is not installed${NC}" >&2; exit 1; }
command -v docker >/dev/null 2>&1 || { echo -e "${RED}Error: docker is not installed${NC}" >&2; exit 1; }
command -v docker-compose >/dev/null 2>&1 || { echo -e "${RED}Error: docker-compose is not installed${NC}" >&2; exit 1; }
echo -e "${GREEN}✓ Prerequisites OK${NC}"
echo ""

# Get latest changes
echo -e "${YELLOW}Pulling latest changes from repository...${NC}"
if [ -n "$BRANCH" ]; then
    git checkout "$BRANCH"
    git pull origin "$BRANCH"
else
    git pull
fi
echo -e "${GREEN}✓ Repository updated${NC}"
echo ""

# Stop containers gracefully
echo -e "${YELLOW}Stopping containers...${NC}"
docker-compose down
echo -e "${GREEN}✓ Containers stopped${NC}"
echo ""

# Rebuild backend image
echo -e "${YELLOW}Rebuilding backend image...${NC}"
if [ -n "$NO_CACHE" ]; then
    echo "Building without cache (this will take longer)..."
    docker-compose build --no-cache backend
else
    echo "Building with cache (faster)..."
    docker-compose build backend
fi
echo -e "${GREEN}✓ Image rebuilt${NC}"
echo ""

# Start containers
echo -e "${YELLOW}Starting containers...${NC}"
docker-compose up -d
echo -e "${GREEN}✓ Containers started${NC}"
echo ""

# Show backend logs
echo -e "${YELLOW}Backend logs (last 50 lines):${NC}"
docker-compose logs --tail=50 backend

echo ""
echo -e "${GREEN}========================================${NC}"
echo -e "${GREEN}Deployment completed successfully!${NC}"
echo -e "${GREEN}========================================${NC}"

