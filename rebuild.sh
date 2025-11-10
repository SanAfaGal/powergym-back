#!/bin/bash
# Script to rebuild and restart containers without pulling changes
# Useful when you already have local changes and only need to rebuild
# Usage: ./rebuild.sh [--no-cache]
#   --no-cache: Force rebuild without using cache (slower but ensures clean build)

set -e

# Colors for output
GREEN='\033[0;32m'
YELLOW='\033[1;33m'
RED='\033[0;31m'
BLUE='\033[0;34m'
NC='\033[0m' # No Color

# Parse arguments
NO_CACHE=false

while [[ $# -gt 0 ]]; do
    case $1 in
        --no-cache)
            NO_CACHE=true
            shift
            ;;
        *)
            echo "Unknown option: $1"
            echo "Usage: ./rebuild.sh [--no-cache]"
            exit 1
            ;;
    esac
done

# Functions
info() {
    echo -e "${GREEN}[INFO]${NC} $1"
}

warn() {
    echo -e "${YELLOW}[WARN]${NC} $1"
}

error() {
    echo -e "${RED}[ERROR]${NC} $1"
}

step() {
    echo -e "${BLUE}[STEP]${NC} $1"
}

# Check for docker-compose or docker compose
get_compose_cmd() {
    if command -v docker-compose &> /dev/null; then
        echo "docker-compose"
    elif docker compose version &> /dev/null; then
        echo "docker compose"
    else
        error "Neither 'docker-compose' nor 'docker compose' is available"
        exit 1
    fi
}

echo "=========================================="
echo "  PowerGym - Rebuild Containers"
echo "=========================================="
echo ""

# Verify we're in the correct directory
if [ ! -f "docker-compose.yml" ]; then
    error "docker-compose.yml not found. Make sure you're in the project directory."
    exit 1
fi

COMPOSE_CMD=$(get_compose_cmd)
info "Using: $COMPOSE_CMD"

echo ""

# Stop containers
step "Stopping containers..."
$COMPOSE_CMD down
info "✓ Containers stopped"

echo ""

# Rebuild backend image
step "Rebuilding backend image..."
BUILD_ARGS=""
if [ "$NO_CACHE" = true ]; then
    BUILD_ARGS="--no-cache"
    warn "Using --no-cache (this will be slower)"
else
    info "Using Docker cache for faster build"
fi

$COMPOSE_CMD build $BUILD_ARGS backend
info "✓ Image rebuilt successfully"

echo ""

# Start containers
step "Starting containers..."
$COMPOSE_CMD up -d
info "✓ Containers started"

echo ""

# Wait a moment for services to initialize
step "Waiting for services to initialize..."
sleep 2

# Show logs
step "Showing backend logs (last 50 lines)..."
echo ""
$COMPOSE_CMD logs --tail=50 backend

echo ""
info "=========================================="
info "  Rebuild completed!"
info "=========================================="
info ""
info "Useful commands:"
info "  View logs in real-time:    $COMPOSE_CMD logs -f backend"
info "  Check container status:    $COMPOSE_CMD ps"
info ""
if [ "$NO_CACHE" = false ]; then
    info "Tip: Use --no-cache flag for a clean rebuild if you encounter issues"
fi
info ""

