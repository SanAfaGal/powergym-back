# Deployment Scripts

This guide documents the utility scripts available in the PowerGym Backend project.

## Table of Contents

- [Available Scripts](#available-scripts)
- [deploy.sh](#deploysh)
- [rebuild.sh](#rebuildsh)
- [Backup Scripts](#backup-scripts)
- [Usage Examples](#usage-examples)
- [Troubleshooting](#troubleshooting)

## Available Scripts

The `scripts/` directory contains utility scripts for deployment and maintenance:

```
scripts/
├── deploy.sh              # Full deployment script
├── rebuild.sh             # Rebuild without git pull
├── backup-db.sh           # Database backup
├── restore-db.sh          # Database restore
└── setup-backup-cron.sh   # Setup automated backups
```

## deploy.sh

Full deployment script that pulls latest code and rebuilds the application.

### Usage

```bash
./scripts/deploy.sh [--no-cache] [--branch BRANCH]
```

### Options

- `--no-cache`: Build Docker image without cache (slower but ensures fresh build)
- `--branch BRANCH`: Checkout and pull specific branch (default: current branch)

### What It Does

1. **Checks Prerequisites**
   - Verifies Git is installed
   - Verifies Docker is installed
   - Verifies Docker Compose is installed

2. **Pulls Latest Code**
   - Checks out specified branch (or current branch)
   - Pulls latest changes from repository

3. **Stops Containers**
   - Gracefully stops all running containers
   - Uses `docker compose down`

4. **Rebuilds Backend**
   - Builds backend Docker image
   - Uses cache by default (faster)
   - Can use `--no-cache` for fresh build

5. **Starts Services**
   - Starts all services with `docker compose up -d`
   - Waits for services to be ready

6. **Shows Logs**
   - Displays last 50 lines of backend logs
   - Helps verify deployment success

### Examples

**Standard Deployment**:
```bash
./scripts/deploy.sh
```

**Deploy Without Cache**:
```bash
./scripts/deploy.sh --no-cache
```

**Deploy Specific Branch**:
```bash
./scripts/deploy.sh --branch production
```

**Deploy Production Branch Without Cache**:
```bash
./scripts/deploy.sh --branch production --no-cache
```

### Output Example

```
========================================
PowerGym Backend Deployment
========================================

Checking prerequisites...
✓ Prerequisites OK

Pulling latest changes from repository...
✓ Repository updated

Stopping containers...
✓ Containers stopped

Rebuilding backend image...
Building with cache (faster)...
✓ Image rebuilt

Starting containers...
✓ Containers started

Backend logs (last 50 lines):
...

========================================
Deployment completed successfully!
========================================
```

## rebuild.sh

Rebuild script that rebuilds the application without pulling code from Git.

### Usage

```bash
./scripts/rebuild.sh [--no-cache]
```

### Options

- `--no-cache`: Build Docker image without cache

### What It Does

1. **Checks Prerequisites**
   - Verifies Docker is installed
   - Verifies Docker Compose is installed

2. **Stops Containers**
   - Gracefully stops all running containers

3. **Rebuilds Backend**
   - Builds backend Docker image
   - Uses cache by default

4. **Starts Services**
   - Starts all services

5. **Shows Logs**
   - Displays last 50 lines of backend logs

### When to Use

- **After code changes** (without pulling from Git)
- **After dependency updates** in `pyproject.toml`
- **After Dockerfile changes**
- **Quick rebuild** without Git operations

### Examples

**Standard Rebuild**:
```bash
./scripts/rebuild.sh
```

**Rebuild Without Cache**:
```bash
./scripts/rebuild.sh --no-cache
```

## Backup Scripts

### backup-db.sh

Creates a compressed backup of the PostgreSQL database.

**Usage**:
```bash
./scripts/backup-db.sh [--env production|development] [--retention-days N]
```

**See**: [Backup Guide](BACKUP_README_EN.md) for detailed documentation

### restore-db.sh

Restores the database from a backup file.

**Usage**:
```bash
./scripts/restore-db.sh <backup_file> [--env production|development] [--confirm]
```

**See**: [Backup Guide](BACKUP_README_EN.md) for detailed documentation

### setup-backup-cron.sh

Configures automated daily backups via cron.

**Usage**:
```bash
./scripts/setup-backup-cron.sh [--env production|development] [--hour HOUR] [--remove]
```

**See**: [Backup Guide](BACKUP_README_EN.md) for detailed documentation

## Usage Examples

### Complete Deployment Workflow

```bash
# 1. Pull latest code and deploy
./scripts/deploy.sh

# 2. Verify deployment
docker compose ps
curl http://localhost:8000/

# 3. Check logs if needed
docker compose logs -f backend
```

### Quick Rebuild After Local Changes

```bash
# Make code changes locally
# ...

# Rebuild without pulling from Git
./scripts/rebuild.sh

# Test changes
curl http://localhost:8000/api/v1/docs
```

### Deployment with Fresh Build

```bash
# Deploy with no cache (ensures all dependencies are fresh)
./scripts/deploy.sh --no-cache
```

### Production Deployment

```bash
# Deploy production branch
./scripts/deploy.sh --branch production

# Or with no cache
./scripts/deploy.sh --branch production --no-cache
```

### Backup Before Deployment

```bash
# 1. Backup database
./scripts/backup-db.sh

# 2. Deploy
./scripts/deploy.sh

# 3. Verify
docker compose ps
```

## Script Requirements

### Prerequisites

All scripts require:
- **Bash**: Scripts are bash scripts
- **Docker**: For container operations
- **Docker Compose**: For multi-container management
- **Git**: For `deploy.sh` only

### Permissions

Make scripts executable:

```bash
chmod +x scripts/*.sh
```

### Working Directory

Scripts automatically detect project root:

- Can be run from project root: `./scripts/deploy.sh`
- Can be run from scripts directory: `cd scripts && ./deploy.sh`
- Scripts will change to project root automatically

## Troubleshooting

### Script Not Executable

**Error**: `Permission denied`

**Solution**:
```bash
chmod +x scripts/deploy.sh
chmod +x scripts/rebuild.sh
```

### Docker Not Found

**Error**: `docker: command not found`

**Solution**:
- Install Docker
- Verify Docker is in PATH
- Check Docker is running: `docker ps`

### Docker Compose Not Found

**Error**: `docker compose: command not found`

**Solution**:
- Install Docker Compose
- Use `docker compose` (two words) for Docker Compose V2
- Update script to use correct command

### Git Pull Fails

**Error**: `git pull` fails in `deploy.sh`

**Solutions**:
1. Check Git repository is clean
2. Resolve merge conflicts
3. Use `rebuild.sh` if you don't need to pull code

### Build Fails

**Error**: Docker build fails

**Solutions**:
1. Check Dockerfile syntax
2. Verify dependencies in `pyproject.toml`
3. Check Docker logs: `docker compose logs backend`
4. Try `--no-cache` to rebuild from scratch

### Containers Won't Start

**Error**: Containers exit immediately

**Solutions**:
1. Check logs: `docker compose logs backend`
2. Verify `.env` file exists and is configured
3. Check database connection
4. Verify ports are not in use

## Best Practices

### 1. Always Backup Before Deployment

```bash
./scripts/backup-db.sh
./scripts/deploy.sh
```

### 2. Test in Development First

```bash
# Test in development
./scripts/deploy.sh --branch develop

# Then deploy to production
./scripts/deploy.sh --branch production
```

### 3. Monitor After Deployment

```bash
# Deploy
./scripts/deploy.sh

# Monitor logs
docker compose logs -f backend

# Check health
curl http://localhost:8000/
```

### 4. Use No-Cache Sparingly

- `--no-cache` is slower but ensures fresh build
- Use when:
  - Dependencies updated
  - Dockerfile changed
  - Suspecting cache issues

### 5. Version Control

- Commit changes before deploying
- Tag releases
- Keep deployment logs

## Customization

### Adding New Scripts

1. **Create script file**: `scripts/your-script.sh`
2. **Add shebang**: `#!/bin/bash`
3. **Make executable**: `chmod +x scripts/your-script.sh`
4. **Follow patterns**: Use same structure as existing scripts

### Modifying Scripts

Scripts are designed to be:
- **Idempotent**: Can run multiple times safely
- **Error Handling**: Use `set -e` for error handling
- **User-Friendly**: Clear output and error messages

### Environment Detection

Scripts can detect environment:

```bash
# Detect environment from .env or docker compose configuration
ENV=${ENVIRONMENT:-development}
```

---

**Next**: [Deployment Guide](DEPLOYMENT.md) | [Backup Guide](BACKUP_README_EN.md)

