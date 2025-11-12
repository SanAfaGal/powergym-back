# Database Guide

This guide covers database setup, migrations, maintenance, and best practices for the PowerGym Backend.

## Table of Contents

- [Database Overview](#database-overview)
- [PostgreSQL Setup](#postgresql-setup)
- [pgvector Extension](#pgvector-extension)
- [Database Schema](#database-schema)
- [Migrations](#migrations)
- [Backup and Restore](#backup-and-restore)
- [Performance Optimization](#performance-optimization)
- [Maintenance](#maintenance)
- [Troubleshooting](#troubleshooting)

## Database Overview

PowerGym uses **PostgreSQL 18** with the **pgvector** extension for:

- Relational data storage (users, clients, subscriptions, etc.)
- Vector storage for face embeddings (pgvector)
- Full-text search capabilities
- ACID compliance and data integrity

### Key Features

- **PostgreSQL 18**: Latest stable version
- **pgvector 0.8.1**: Vector similarity search for face recognition
- **Alembic**: Database migration management
- **SQLAlchemy 2.0**: Modern ORM with type safety

## PostgreSQL Setup

### Using Docker (Recommended)

PostgreSQL is included in the Docker Compose setup:

```yaml
postgres:
  image: pgvector/pgvector:0.8.1-pg18-trixie
  environment:
    POSTGRES_USER: powergym_user
    POSTGRES_PASSWORD: password
    POSTGRES_DB: powergym
  ports:
    - "5432:5432"
```

### Manual Installation

1. **Install PostgreSQL 18**
   ```bash
   # Ubuntu/Debian
   sudo apt install postgresql-18 postgresql-contrib
   
   # macOS (Homebrew)
   brew install postgresql@18
   ```

2. **Create Database**
   ```bash
   sudo -u postgres psql
   ```
   
   ```sql
   CREATE DATABASE powergym;
   CREATE USER powergym_user WITH PASSWORD 'your_password';
   GRANT ALL PRIVILEGES ON DATABASE powergym TO powergym_user;
   \q
   ```

3. **Enable pgvector Extension**
   ```bash
   psql -U powergym_user -d powergym
   ```
   
   ```sql
   CREATE EXTENSION IF NOT EXISTS vector;
   ```

## pgvector Extension

### What is pgvector?

pgvector is a PostgreSQL extension for storing and querying vector embeddings. It's used for:

- Storing face embeddings (512-dimensional vectors)
- Fast similarity search using cosine distance
- Efficient indexing for large-scale vector operations

### Installation

pgvector is included in the `pgvector/pgvector` Docker image. For manual installation:

```bash
# Clone and build
git clone --branch v0.8.1 https://github.com/pgvector/pgvector.git
cd pgvector
make
sudo make install

# Enable in database
psql -U powergym_user -d powergym -c "CREATE EXTENSION vector;"
```

### Vector Indexing

For optimal performance, create an index on vector columns:

```sql
-- Create index on biometrics.embedding
CREATE INDEX ON biometrics 
USING ivfflat (embedding vector_cosine_ops)
WITH (lists = 100);
```

**Note**: Index creation is handled automatically in migrations.

### Vector Operations

Common vector operations:

```sql
-- Cosine similarity search
SELECT client_id, 1 - (embedding <=> query_vector) AS similarity
FROM biometrics
WHERE embedding <=> query_vector < 0.4
ORDER BY embedding <=> query_vector
LIMIT 1;

-- L2 distance
SELECT * FROM biometrics
ORDER BY embedding <-> query_vector
LIMIT 10;
```

## Database Schema

### Core Tables

#### Users
```sql
CREATE TABLE users (
    username VARCHAR PRIMARY KEY,
    email VARCHAR UNIQUE,
    full_name VARCHAR,
    hashed_password VARCHAR NOT NULL,
    role user_role_enum NOT NULL DEFAULT 'employee',
    disabled BOOLEAN DEFAULT FALSE,
    created_at TIMESTAMP WITH TIME ZONE DEFAULT NOW(),
    updated_at TIMESTAMP WITH TIME ZONE DEFAULT NOW()
);
```

#### Clients
```sql
CREATE TABLE clients (
    id UUID PRIMARY KEY DEFAULT gen_random_uuid(),
    dni_type document_type_enum NOT NULL,
    dni_number VARCHAR UNIQUE NOT NULL,
    first_name VARCHAR NOT NULL,
    last_name VARCHAR NOT NULL,
    -- ... other fields
    is_active BOOLEAN DEFAULT TRUE,
    created_at TIMESTAMP WITH TIME ZONE DEFAULT NOW(),
    updated_at TIMESTAMP WITH TIME ZONE DEFAULT NOW()
);
```

#### Biometrics (Face Recognition)
```sql
CREATE TABLE biometrics (
    id UUID PRIMARY KEY DEFAULT gen_random_uuid(),
    client_id UUID REFERENCES clients(id),
    type biometric_type_enum NOT NULL,
    embedding vector(512),  -- pgvector type
    thumbnail_encrypted BYTEA,
    is_active BOOLEAN DEFAULT TRUE,
    created_at TIMESTAMP WITH TIME ZONE DEFAULT NOW()
);
```

#### Subscriptions
```sql
CREATE TABLE subscriptions (
    id UUID PRIMARY KEY DEFAULT gen_random_uuid(),
    client_id UUID REFERENCES clients(id),
    plan_id UUID REFERENCES plans(id),
    start_date DATE NOT NULL,
    end_date DATE NOT NULL,
    status subscription_status_enum NOT NULL,
    -- ... other fields
    created_at TIMESTAMP WITH TIME ZONE DEFAULT NOW()
);
```

### Relationships

- **Clients** → **Biometrics** (one-to-many)
- **Clients** → **Subscriptions** (one-to-many)
- **Subscriptions** → **Plans** (many-to-one)
- **Subscriptions** → **Payments** (one-to-many)
- **Clients** → **Attendances** (one-to-many)

### Enums

The database uses several ENUM types:

- `user_role_enum`: `admin`, `employee`
- `document_type_enum`: `CC`, `TI`, `CE`, `PP`
- `gender_type_enum`: `male`, `female`, `other`
- `biometric_type_enum`: `FACE`, `FINGERPRINT`
- `subscription_status_enum`: `active`, `expired`, `pending_payment`, `scheduled`, `canceled`
- `payment_method_enum`: `cash`, `qr`
- `stock_status_enum`: `NORMAL`, `LOW_STOCK`, `STOCK_OUT`, `OVERSTOCK`

## Migrations

### Alembic Overview

Alembic is used for database schema versioning and migrations:

- **Version Control**: Track schema changes
- **Auto-generation**: Generate migrations from model changes
- **Rollback**: Downgrade to previous versions
- **History**: View migration history

### Creating Migrations

#### Auto-generate from Models

```bash
# Generate migration from model changes
alembic revision --autogenerate -m "add new column to users"

# Review the generated migration in alembic/versions/
```

#### Manual Migration

```bash
# Create empty migration
alembic revision -m "custom data migration"

# Edit the migration file in alembic/versions/
```

### Migration File Structure

```python
"""add new column to users

Revision ID: abc123
Revises: def456
Create Date: 2025-01-15 10:00:00.000000

"""
from alembic import op
import sqlalchemy as sa

# revision identifiers
revision = 'abc123'
down_revision = 'def456'
branch_labels = None
depends_on = None

def upgrade():
    op.add_column('users', sa.Column('new_column', sa.String(), nullable=True))

def downgrade():
    op.drop_column('users', 'new_column')
```

### Applying Migrations

```bash
# Apply all pending migrations
alembic upgrade head

# Apply specific migration
alembic upgrade <revision_id>

# Check current version
alembic current

# View migration history
alembic history
```

### Rolling Back Migrations

```bash
# Rollback one migration
alembic downgrade -1

# Rollback to specific revision
alembic downgrade <revision_id>

# Rollback all migrations (WARNING: Deletes all data)
alembic downgrade base
```

### Migration Best Practices

1. **Always Review Auto-generated Migrations**
   - Check for unintended changes
   - Verify data types and constraints
   - Test on development database first

2. **Use Transactions**
   ```python
   def upgrade():
       with op.batch_alter_table('users') as batch_op:
           batch_op.add_column(sa.Column('new_column', sa.String()))
   ```

3. **Data Migrations**
   ```python
   def upgrade():
       # Schema change
       op.add_column('users', sa.Column('status', sa.String()))
       
       # Data migration
       connection = op.get_bind()
       connection.execute(
           sa.text("UPDATE users SET status = 'active' WHERE status IS NULL")
       )
   ```

4. **Never Edit Applied Migrations**
   - Create new migrations instead
   - Migrations are immutable once applied

5. **Test Migrations**
   - Test on development database
   - Test rollback procedures
   - Verify data integrity after migration

### Common Migration Commands

```bash
# Show current revision
alembic current

# Show migration history
alembic history

# Show pending migrations
alembic heads

# Show branches
alembic branches

# Stamp database (mark as current version without running)
alembic stamp head
```

## Backup and Restore

### Automated Backups

See [scripts/BACKUP_README.md](../scripts/BACKUP_README.md) for detailed backup documentation.

#### Quick Backup

```bash
# Manual backup
./scripts/backup-db.sh

# Automated daily backups
./scripts/setup-backup-cron.sh
```

#### Backup Location

Backups are stored in: `backups/postgres/`

Format: `backup_production_YYYYMMDD_HHMMSS.sql.gz`

### Manual Backup

#### Using pg_dump

```bash
# Full database backup
pg_dump -U powergym_user -d powergym -F c -f backup.dump

# SQL format
pg_dump -U powergym_user -d powergym -f backup.sql

# Compressed
pg_dump -U powergym_user -d powergym | gzip > backup.sql.gz
```

#### Using Docker

```bash
# Backup from Docker container
docker compose exec postgres pg_dump -U powergym_user powergym > backup.sql

# Compressed
docker compose exec postgres pg_dump -U powergym_user powergym | gzip > backup.sql.gz
```

### Restore

#### Using pg_restore

```bash
# Restore from dump file
pg_restore -U powergym_user -d powergym backup.dump

# Restore from SQL file
psql -U powergym_user -d powergym < backup.sql
```

#### Using Docker

```bash
# Restore from SQL file
docker compose exec -T postgres psql -U powergym_user powergym < backup.sql

# Restore compressed
gunzip < backup.sql.gz | docker compose exec -T postgres psql -U powergym_user powergym
```

#### Using Restore Script

```bash
./scripts/restore-db.sh backups/postgres/backup_production_20250115_020000.sql.gz
```

**WARNING**: Restore will **replace all existing data**. Always backup before restoring.

## Performance Optimization

### Indexing

#### Standard Indexes

Ensure indexes on frequently queried columns:

```sql
-- Users
CREATE INDEX idx_users_email ON users(email);
CREATE INDEX idx_users_username ON users(username);

-- Clients
CREATE INDEX idx_clients_dni ON clients(dni_number);
CREATE INDEX idx_clients_active ON clients(is_active);

-- Subscriptions
CREATE INDEX idx_subscriptions_client ON subscriptions(client_id);
CREATE INDEX idx_subscriptions_status ON subscriptions(status);
CREATE INDEX idx_subscriptions_dates ON subscriptions(start_date, end_date);

-- Attendances
CREATE INDEX idx_attendances_client ON attendances(client_id);
CREATE INDEX idx_attendances_date ON attendances(entry_time);
```

#### Vector Indexes

For face recognition:

```sql
-- IVFFlat index for fast similarity search
CREATE INDEX idx_biometrics_embedding ON biometrics 
USING ivfflat (embedding vector_cosine_ops)
WITH (lists = 100);
```

**Note**: Indexes are created automatically in migrations.

### Query Optimization

1. **Use EXPLAIN ANALYZE**
   ```sql
   EXPLAIN ANALYZE
   SELECT * FROM clients WHERE dni_number = '1234567890';
   ```

2. **Avoid N+1 Queries**
   - Use SQLAlchemy's `joinedload` or `selectinload`
   - Eager load relationships when needed

3. **Limit Results**
   ```python
   # Use pagination
   query = query.limit(20).offset(0)
   ```

4. **Use Indexes**
   - Ensure WHERE clauses use indexed columns
   - Avoid functions on indexed columns

### Connection Pooling

Configure in `app/db/session.py`:

```python
engine = create_engine(
    settings.DATABASE_URL,
    pool_size=20,          # Number of connections to maintain
    max_overflow=10,       # Additional connections allowed
    pool_pre_ping=True,     # Verify connections before use
    pool_recycle=3600      # Recycle connections after 1 hour
)
```

### Vacuum and Analyze

Regular maintenance:

```sql
-- Vacuum (reclaim space)
VACUUM ANALYZE;

-- Analyze (update statistics)
ANALYZE;

-- Full vacuum (requires exclusive lock)
VACUUM FULL;
```

Schedule regular vacuum:

```bash
# Add to cron
0 2 * * * psql -U powergym_user -d powergym -c "VACUUM ANALYZE;"
```

## Maintenance

### Regular Tasks

1. **Daily**
   - Monitor database size
   - Check backup completion
   - Review error logs

2. **Weekly**
   - Run VACUUM ANALYZE
   - Review slow queries
   - Check disk space

3. **Monthly**
   - Review and optimize indexes
   - Analyze query performance
   - Review backup retention

### Database Size

Check database size:

```sql
-- Database size
SELECT pg_size_pretty(pg_database_size('powergym'));

-- Table sizes
SELECT 
    schemaname,
    tablename,
    pg_size_pretty(pg_total_relation_size(schemaname||'.'||tablename)) AS size
FROM pg_tables
WHERE schemaname = 'public'
ORDER BY pg_total_relation_size(schemaname||'.'||tablename) DESC;
```

### Monitoring

Key metrics to monitor:

- **Database Size**: Growth rate
- **Connection Count**: Active connections
- **Query Performance**: Slow queries
- **Index Usage**: Unused indexes
- **Lock Contention**: Blocking queries

### Logging

Enable query logging in PostgreSQL:

```sql
-- In postgresql.conf
log_statement = 'all'  # or 'mod', 'ddl', 'none'
log_duration = on
log_line_prefix = '%t [%p]: [%l-1] user=%u,db=%d,app=%a,client=%h '
```

## Troubleshooting

### Connection Issues

**Error**: "Connection refused" or "Connection timeout"

**Solutions**:
1. Verify PostgreSQL is running: `docker compose ps` or `systemctl status postgresql`
2. Check `DATABASE_URL` in `.env`
3. Verify network connectivity
4. Check firewall rules

### Migration Errors

**Error**: "Target database is not up to date"

**Solutions**:
1. Check current version: `alembic current`
2. View history: `alembic history`
3. Apply pending migrations: `alembic upgrade head`

### Performance Issues

**Symptoms**: Slow queries, high CPU usage

**Solutions**:
1. Check indexes: `\d+ table_name`
2. Analyze queries: `EXPLAIN ANALYZE`
3. Review connection pool settings
4. Check for missing indexes

### pgvector Issues

**Error**: "Extension vector does not exist"

**Solutions**:
1. Enable extension: `CREATE EXTENSION vector;`
2. Verify installation: `\dx vector`
3. Check PostgreSQL version (requires 11+)

### Disk Space

**Error**: "No space left on device"

**Solutions**:
1. Check disk usage: `df -h`
2. Vacuum database: `VACUUM FULL;`
3. Remove old backups
4. Archive old data

---

**Next**: [API Documentation](API.md) | [Troubleshooting Guide](TROUBLESHOOTING.md)

