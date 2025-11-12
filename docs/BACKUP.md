# Database Backup Guide

This guide explains how to configure and use the backup and restore scripts for the PowerGym database.

## Table of Contents

- [Available Scripts](#available-scripts)
- [Initial Setup](#initial-setup)
- [Manual Usage](#manual-usage)
- [Automated Backups (Cron)](#automated-backups-cron)
- [Restoration](#restoration)
- [Best Practices](#best-practices)
- [Troubleshooting](#troubleshooting)

## Available Scripts

### 1. `backup-db.sh`

Creates a compressed backup of the PostgreSQL database.

**Usage:**
```bash
./scripts/backup-db.sh [--env production|development] [--retention-days N]
```

**Examples:**
```bash
# Production backup (default)
./scripts/backup-db.sh

# Development backup
./scripts/backup-db.sh --env development

# Backup with 14-day retention
./scripts/backup-db.sh --retention-days 14
```

### 2. `restore-db.sh`

Restores the database from a backup file.

**⚠️ WARNING:** This script **REPLACES** all existing data in the database.

**Usage:**
```bash
./scripts/restore-db.sh <backup_file> [--env production|development] [--confirm]
```

**Examples:**
```bash
# Restore from backup (with interactive confirmation)
./scripts/restore-db.sh backups/postgres/backup_production_20240115_020000.sql.gz

# Restore without confirmation (useful for scripts)
./scripts/restore-db.sh backup_production_20240115_020000.sql.gz --confirm

# Restore to development environment
./scripts/restore-db.sh backup_production_20240115_020000.sql.gz --env development
```

### 3. `setup-backup-cron.sh`

Configures a cron job for automatic daily backups.

**Usage:**
```bash
./scripts/setup-backup-cron.sh [--env production|development] [--hour HOUR] [--remove]
```

**Examples:**
```bash
# Configure daily backup at 2 AM (default)
./scripts/setup-backup-cron.sh

# Configure daily backup at 3 AM
./scripts/setup-backup-cron.sh --hour 3

# Configure for development environment
./scripts/setup-backup-cron.sh --env development --hour 1

# Remove cron job
./scripts/setup-backup-cron.sh --env production --remove
```

## Initial Setup

### 1. Make Scripts Executable

```bash
chmod +x scripts/backup-db.sh
chmod +x scripts/restore-db.sh
chmod +x scripts/setup-backup-cron.sh
```

### 2. Create Backup Directory

The directory is created automatically, but you can create it manually:

```bash
mkdir -p backups/postgres
```

### 3. Verify Environment Variables

Ensure your `.env` file has the following variables configured:

```env
POSTGRES_USER=your_username
POSTGRES_PASSWORD=your_secure_password
POSTGRES_DB=powergym
```

## Manual Usage

### Create a Manual Backup

```bash
# From the project root directory
./scripts/backup-db.sh

# Backup will be saved to:
# backups/postgres/backup_production_YYYYMMDD_HHMMSS.sql.gz
```

### List Available Backups

```bash
ls -lh backups/postgres/
```

### Verify a Backup

```bash
# View backup size and date
ls -lh backups/postgres/backup_production_*.sql.gz

# Verify backup is not corrupted
gunzip -t backups/postgres/backup_production_20240115_020000.sql.gz
```

## Automated Backups (Cron)

### Configure Automatic Daily Backup

```bash
# Configure daily backup at 2 AM (recommended)
./scripts/setup-backup-cron.sh

# Or at another time (example: 3 AM)
./scripts/setup-backup-cron.sh --hour 3
```

### Verify Cron Job

```bash
# View all cron jobs
crontab -l

# View only PowerGym jobs
crontab -l | grep PowerGym
```

### View Cron Logs

```bash
# View latest logs
tail -f backups/postgres/cron.log

# View last 50 lines
tail -n 50 backups/postgres/cron.log
```

### Remove Cron Job

```bash
./scripts/setup-backup-cron.sh --remove
```

## Restoration

### Restore from Backup

1. **List available backups:**
   ```bash
   ls -lh backups/postgres/
   ```

2. **Restore the backup:**
   ```bash
   ./scripts/restore-db.sh backups/postgres/backup_production_20240115_020000.sql.gz
   ```

3. **The script will ask for confirmation before proceeding.**

### Restore to Different Environment

```bash
# Restore production backup to development (for testing)
./scripts/restore-db.sh backups/postgres/backup_production_20240115_020000.sql.gz --env development
```

## Best Practices

### 1. Backup Frequency

- **Production:** Daily (minimum)
- **Development:** Weekly or before important changes

### 2. Backup Retention

- **Production:** Keep at least 7-30 days of backups
- **Critical backups:** Consider keeping monthly backups for longer periods

### 3. External Storage

Backups are saved locally on the VPS. For additional security:

- **Copy to another server:** Use `scp` or `rsync` to copy backups to another server
- **Cloud storage:** Upload backups to S3, Google Drive, Dropbox, etc.
- **Example with rsync:**
  ```bash
  rsync -avz backups/postgres/ user@other-server:/backups/powergym/
  ```

### 4. Backup Verification

- Periodically verify that backups are being created correctly
- Test restoration in a development environment at least once a month

### 5. Security

- Backups contain sensitive data, ensure:
  - Protect the `backups/` directory with appropriate permissions
  - Do not upload backups to public repositories
  - Encrypt backups if storing externally

### 6. Monitoring

- Regularly review cron logs
- Configure alerts if a backup fails
- Monitor disk space

## Troubleshooting

### Script Cannot Find Container

**Error:** `Container 'powergym_db_prod' is not running`

**Solution:**
```bash
# Verify container is running
docker ps

# If not running, start it
docker compose -f docker-compose.production.yml up -d postgres
```

### Permission Error

**Error:** `Permission denied`

**Solution:**
```bash
chmod +x scripts/backup-db.sh
chmod +x scripts/restore-db.sh
chmod +x scripts/setup-backup-cron.sh
```

### Backup Fails

**Possible causes:**
1. Container is not running
2. Incorrect environment variables
3. Insufficient disk space
4. Incorrect permissions on backup directory

**Solution:**
```bash
# Check container logs
docker logs powergym_db_prod

# Check disk space
df -h

# Check permissions
ls -la backups/postgres/
```

### Cron Job Not Running

**Verifications:**
```bash
# Verify cron job is installed
crontab -l

# Check cron logs
tail -f backups/postgres/cron.log

# Verify cron service is running (Linux)
systemctl status cron

# Check script permissions
ls -la scripts/backup-db.sh
```

### Restoration Fails

**Possible causes:**
1. Backup file is corrupted
2. Container is not running
3. Database has active connections

**Solution:**
```bash
# Verify backup is not corrupted
gunzip -t backups/postgres/backup_production_20240115_020000.sql.gz

# Verify container is running
docker ps | grep powergym_db

# Try restoring again
./scripts/restore-db.sh backups/postgres/backup_production_20240115_020000.sql.gz
```

## File Structure

```
powergym/
├── scripts/
│   ├── backup-db.sh          # Backup script
│   ├── restore-db.sh          # Restore script
│   ├── setup-backup-cron.sh   # Cron setup script
│   └── BACKUP_README_EN.md    # This guide
└── backups/
    └── postgres/
        ├── backup_production_20240115_020000.sql.gz
        ├── backup_production_20240116_020000.sql.gz
        ├── backup.log          # Log of manual backups
        └── cron.log            # Log of automated backups
```

## Additional Security

### VPS Security Recommendations

1. **Firewall:** Block port 5432 from outside if not necessary
   ```bash
   # With UFW (Ubuntu)
   sudo ufw deny 5432
   ```

2. **Strong Passwords:** Use secure passwords in `.env`

3. **Backup Directory Permissions:**
   ```bash
   chmod 700 backups/postgres/
   ```

4. **Remote Backups:** Consider copying backups to another server or cloud service

## Support

If you encounter problems or have questions:

1. Check logs: `backups/postgres/backup.log` and `backups/postgres/cron.log`
2. Verify Docker and containers are running
3. Review environment variables in `.env`

---

**Last Updated:** 2024-01-15

