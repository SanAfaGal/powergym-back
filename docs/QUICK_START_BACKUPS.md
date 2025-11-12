# Quick Start: Backup Configuration

## Setup in 3 Steps

### 1️⃣ Make Scripts Executable

```bash
cd /path/to/your/project/powergym
chmod +x scripts/*.sh
```

### 2️⃣ Create Your First Manual Backup

```bash
./scripts/backup-db.sh
```

This will create a backup in `backups/postgres/backup_production_YYYYMMDD_HHMMSS.sql.gz`

### 3️⃣ Configure Automatic Daily Backup

```bash
# Daily backup at 2 AM (recommended)
./scripts/setup-backup-cron.sh
```

Done! Your database will be backed up automatically every day at 2 AM.

## Verify It Works

```bash
# View created backups
ls -lh backups/postgres/

# View configured cron job
crontab -l | grep PowerGym

# View logs from last automatic backup
tail -f backups/postgres/cron.log
```

## Restore a Backup (if needed)

```bash
# List available backups
ls -lh backups/postgres/

# Restore (will ask for confirmation)
./scripts/restore-db.sh backups/postgres/backup_production_20240115_020000.sql.gz
```

## Complete Documentation

For more details, see: `scripts/BACKUP_README_EN.md`

---

**Note:** Backups are saved locally on your VPS. For additional security, consider copying backups to another server or cloud service.

