#!/bin/bash
# Script to apply production changes to Docker server
# Usage: ./deploy.sh [--no-cache] [--branch BRANCH]
#   --no-cache: Force rebuild without using cache (slower but ensures clean build)
#   --branch:   Specify branch to pull from (default: current branch)

set -e

# Colors for output
GREEN='\033[0;32m'
YELLOW='\033[1;33m'
RED='\033[0;31m'
BLUE='\033[0;34m'
NC='\033[0m' # No Color

# Parse arguments
NO_CACHE=false
BRANCH=""

while [[ $# -gt 0 ]]; do
    case $1 in
        --no-cache)
            NO_CACHE=true
            shift
            ;;
        --branch)
            BRANCH="$2"
            shift 2
            ;;
        *)
            echo "Unknown option: $1"
            echo "Usage: ./deploy.sh [--no-cache] [--branch BRANCH]"
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

# Verify prerequisites
verify_command() {
    if ! command -v "$1" &> /dev/null; then
        error "$1 is not installed or not in PATH"
        exit 1
    fi
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
echo "  PowerGym - Deploy from Production"
echo "=========================================="
echo ""

# Verify prerequisites
info "Verifying prerequisites..."
verify_command "git"
verify_command "docker"
COMPOSE_CMD=$(get_compose_cmd)
info "Using: $COMPOSE_CMD"

# Verify we're in the correct directory
if [ ! -f "docker-compose.yml" ]; then
    error "docker-compose.yml not found. Make sure you're in the project directory."
    exit 1
fi

# Verify we're in a git repository
if [ ! -d ".git" ]; then
    error "Not a git repository. Make sure you're in the project root."
    exit 1
fi

echo ""

# Step 1: Pull changes
step "Step 1: Fetching changes from repository..."
CURRENT_BRANCH=$(git branch --show-current)
if [ -n "$BRANCH" ]; then
    info "Switching to branch: $BRANCH"
    git checkout "$BRANCH" || {
        error "Failed to checkout branch: $BRANCH"
        exit 1
    }
fi

if git pull; then
    info "✓ Changes fetched successfully from branch: $(git branch --show-current)"
else
    error "✗ Error fetching changes from repository"
    exit 1
fi

echo ""

# Step 2: Stop containers gracefully
step "Step 2: Stopping containers..."
if $COMPOSE_CMD down; then
    info "✓ Containers stopped"
else
    warn "Some containers may not have stopped correctly"
fi

echo ""

# Step 3: Rebuild backend image
step "Step 3: Rebuilding backend image..."
BUILD_ARGS=""
if [ "$NO_CACHE" = true ]; then
    BUILD_ARGS="--no-cache"
    warn "Using --no-cache (this will be slower)"
else
    info "Using Docker cache for faster build"
fi

if $COMPOSE_CMD build $BUILD_ARGS backend; then
    info "✓ Image rebuilt successfully"
else
    error "✗ Error rebuilding image"
    exit 1
fi

echo ""

# Step 4: Start containers
step "Step 4: Starting containers..."
if $COMPOSE_CMD up -d; then
    info "✓ Containers started"
else
    error "✗ Error starting containers"
    exit 1
fi

echo ""

# Step 5: Wait a moment for services to initialize
step "Step 5: Waiting for services to initialize..."
sleep 2

# Step 6: Show backend logs
step "Step 6: Showing backend logs (last 50 lines)..."
echo ""
$COMPOSE_CMD logs --tail=50 backend

echo ""
info "=========================================="
info "  Deploy completed successfully!"
info "=========================================="
info ""
info "Current branch: $(git branch --show-current)"
info ""
info "Useful commands:"
info "  View logs in real-time:    $COMPOSE_CMD logs -f backend"
info "  Check container status:    $COMPOSE_CMD ps"
info "  View all logs:             $COMPOSE_CMD logs --tail=100"
info ""
if [ "$NO_CACHE" = false ]; then
    info "Tip: Use --no-cache flag for a clean rebuild if you encounter issues"
fi
info ""
