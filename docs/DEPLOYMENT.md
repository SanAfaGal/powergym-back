# Deployment Guide

This guide covers deploying the PowerGym Backend API to production environments.

## Table of Contents

- [Pre-Deployment Checklist](#pre-deployment-checklist)
- [Deployment Methods](#deployment-methods)
  - [Docker Compose (Recommended)](#docker-compose-recommended)
  - [Manual Deployment](#manual-deployment)
  - [Cloud Platforms](#cloud-platforms)
- [Production Configuration](#production-configuration)
- [Security Considerations](#security-considerations)
- [Performance Optimization](#performance-optimization)
- [Monitoring and Logging](#monitoring-and-logging)
- [Backup Strategy](#backup-strategy)
- [Scaling Considerations](#scaling-considerations)
- [Maintenance](#maintenance)

## Pre-Deployment Checklist

Before deploying to production, ensure:

- [ ] All environment variables are configured
- [ ] Strong secrets are generated (`SECRET_KEY`, `BIOMETRIC_ENCRYPTION_KEY`)
- [ ] Database credentials are secure
- [ ] CORS origins are restricted to production frontend URLs
- [ ] `DEBUG=false` in production
- [ ] Database migrations are tested
- [ ] Backup strategy is in place
- [ ] SSL/TLS certificates are configured (if using HTTPS)
- [ ] Firewall rules are configured
- [ ] Monitoring is set up
- [ ] Log rotation is configured

## Deployment Methods

### Docker Compose (Recommended)

Docker Compose is the recommended deployment method for most scenarios.

#### Step 1: Prepare Production Configuration

```bash
# Copy production docker-compose file
cp docker-compose.production.yml docker-compose.yml

# Create production .env file
cp .env.example .env.production
# Edit .env.production with production values
```

#### Step 2: Configure Production Environment

Edit `.env` with production values:

```env
# Application
ENVIRONMENT=production
DEBUG=false
API_PORT=8000

# Security - GENERATE STRONG RANDOM VALUES
SECRET_KEY=<generate-strong-random-key>
BIOMETRIC_ENCRYPTION_KEY=<generate-strong-random-key>

# Database - Use strong passwords
DATABASE_URL=postgresql://powergym_user:STRONG_PASSWORD@postgres:5432/powergym
POSTGRES_USER=powergym_user
POSTGRES_PASSWORD=STRONG_PASSWORD_HERE
POSTGRES_DB=powergym

# CORS - Only production frontend URLs
ALLOWED_ORIGINS_STR=https://app.your-domain.com,https://www.your-domain.com

# Super Admin - Change defaults
SUPER_ADMIN_USERNAME=admin
SUPER_ADMIN_PASSWORD=STRONG_PASSWORD_HERE
SUPER_ADMIN_EMAIL=admin@powergym.com
SUPER_ADMIN_FULL_NAME=Administrator

# Face Recognition
EMBEDDING_DIMENSIONS=512
INSIGHTFACE_MODEL=buffalo_s
FACE_RECOGNITION_TOLERANCE=0.6

# Rate Limiting - Lower for production
RATE_LIMIT_ENABLED=true
RATE_LIMIT_PER_MINUTE=60

# Telegram (Optional)
TELEGRAM_BOT_TOKEN=your_token
TELEGRAM_CHAT_ID=your_chat_id
TELEGRAM_ENABLED=true
```

#### Step 3: Deploy

```bash
# Build and start services
docker compose up -d --build

# Verify services are running
docker compose ps

# Check logs
docker compose logs -f backend
```

#### Step 4: Verify Deployment

```bash
# Health check
curl http://localhost:8000/

# Check API documentation
curl http://localhost:8000/api/v1/docs
```

### Manual Deployment

For deployments without Docker:

#### Step 1: Server Setup

1. **Install Python 3.10+**
   ```bash
   sudo apt update
   sudo apt install python3.10 python3.10-venv python3-pip
   ```

2. **Install PostgreSQL 18+ with pgvector**
   ```bash
   # Ubuntu/Debian
   sudo apt install postgresql-18 postgresql-contrib
   # Install pgvector extension
   ```

3. **Create system user**
   ```bash
   sudo useradd -m -s /bin/bash powergym
   ```

#### Step 2: Application Setup

1. **Clone repository**
   ```bash
   cd /opt
   sudo git clone <repository-url> powergym
   sudo chown -R powergym:powergym powergym
   ```

2. **Set up virtual environment**
   ```bash
   cd /opt/powergym
   python3 -m venv .venv
   source .venv/bin/activate
   pip install -e .
   ```

3. **Configure environment**
   ```bash
   cp .env.example .env
   # Edit .env with production values
   ```

4. **Run migrations**
   ```bash
   alembic upgrade head
   ```

#### Step 3: Set Up Process Manager

Use systemd or supervisor to manage the application:

**systemd service** (`/etc/systemd/system/powergym.service`):

```ini
[Unit]
Description=PowerGym Backend API
After=network.target postgresql.service

[Service]
Type=simple
User=powergym
WorkingDirectory=/opt/powergym
Environment="PATH=/opt/powergym/.venv/bin"
ExecStart=/opt/powergym/.venv/bin/uvicorn main:app --host 0.0.0.0 --port 8000
Restart=always
RestartSec=10

[Install]
WantedBy=multi-user.target
```

Enable and start:

```bash
sudo systemctl enable powergym
sudo systemctl start powergym
sudo systemctl status powergym
```

### Cloud Platforms

#### AWS (EC2 + RDS)

1. **Launch EC2 instance** (Ubuntu 22.04 LTS recommended)
2. **Set up RDS PostgreSQL** with pgvector extension
3. **Deploy application** using Docker Compose or manual method
4. **Configure security groups**:
   - Allow port 8000 from load balancer only
   - Allow port 5432 from EC2 to RDS only

#### Google Cloud Platform

1. **Create Compute Engine instance**
2. **Set up Cloud SQL** PostgreSQL with pgvector
3. **Deploy using Docker** or manual method
4. **Configure firewall rules**

#### DigitalOcean

1. **Create Droplet** (Ubuntu 22.04)
2. **Set up Managed Database** (PostgreSQL)
3. **Deploy using Docker Compose**
4. **Configure firewall**

## Production Configuration

### Environment Variables

See [CONFIGURATION.md](CONFIGURATION.md) for all configuration options.

**Critical production settings:**

```env
ENVIRONMENT=production
DEBUG=false
ACCESS_TOKEN_EXPIRE_MINUTES=60
RATE_LIMIT_PER_MINUTE=60
ALLOWED_ORIGINS_STR=https://your-frontend-domain.com
```

### Docker Compose Production Settings

The `docker-compose.production.yml` includes:

- Resource limits (CPU and memory)
- Health checks
- Restart policies (`always`)
- Log rotation
- Network isolation

Review and adjust resource limits based on your server:

```yaml
deploy:
  resources:
    limits:
      cpus: '1.2'
      memory: 2.5G
    reservations:
      cpus: '0.7'
      memory: 1.5G
```

## Security Considerations

### 1. Secrets Management

**Never commit secrets to version control.**

- Use environment variables or secret management services
- Rotate secrets regularly
- Use different secrets for each environment

### 2. Database Security

- Use strong passwords (16+ characters, mixed case, numbers, symbols)
- Restrict database access to application server only
- Use SSL/TLS for database connections
- Regularly update PostgreSQL

### 3. Network Security

- **Firewall**: Only expose necessary ports
  ```bash
  # UFW example
  sudo ufw allow 22/tcp    # SSH
  sudo ufw allow 80/tcp     # HTTP (if using reverse proxy)
  sudo ufw allow 443/tcp    # HTTPS
  sudo ufw enable
  ```

- **Reverse Proxy**: Use Nginx or Traefik
  - Terminate SSL/TLS
  - Hide backend port
  - Add security headers

### 4. Application Security

- **CORS**: Restrict to production frontend URLs only
- **Rate Limiting**: Enable and configure appropriately
- **Input Validation**: All inputs validated via Pydantic
- **SQL Injection**: Use SQLAlchemy ORM (parameterized queries)
- **XSS**: Sanitize user inputs

### 5. SSL/TLS

Use a reverse proxy (Nginx/Traefik) with Let's Encrypt:

**Nginx configuration example:**

```nginx
server {
    listen 443 ssl http2;
    server_name api.your-domain.com;

    ssl_certificate /etc/letsencrypt/live/api.your-domain.com/fullchain.pem;
    ssl_certificate_key /etc/letsencrypt/live/api.your-domain.com/privkey.pem;

    location / {
        proxy_pass http://localhost:8000;
        proxy_set_header Host $host;
        proxy_set_header X-Real-IP $remote_addr;
        proxy_set_header X-Forwarded-For $proxy_add_x_forwarded_for;
        proxy_set_header X-Forwarded-Proto $scheme;
    }
}
```

## Performance Optimization

### 1. Database Optimization

- **Connection Pooling**: Configured in SQLAlchemy
- **Indexes**: Ensure proper indexes on frequently queried columns
- **Query Optimization**: Use `explain analyze` to optimize slow queries
- **pgvector Index**: Ensure vector indexes are created for face embeddings

### 2. Application Optimization

- **Caching**: Consider Redis for frequently accessed data
- **Compression**: Enable response compression (already configured)
- **Async Operations**: Use async for I/O-bound operations
- **Face Recognition**: Use GPU if available (`INSIGHTFACE_CTX_ID=0`)

### 3. Resource Limits

Adjust Docker resource limits based on server capacity:

```yaml
# For 2 vCPU / 4GB RAM server
deploy:
  resources:
    limits:
      cpus: '1.2'
      memory: 2.5G
```

### 4. Database Connection Pool

Configure in `app/db/session.py`:

```python
engine = create_engine(
    settings.DATABASE_URL,
    pool_size=20,
    max_overflow=10,
    pool_pre_ping=True
)
```

## Monitoring and Logging

### 1. Application Logs

Logs are written to `logs/` directory:

```bash
# View logs
tail -f logs/app.log

# Docker
docker compose logs -f backend
```

### 2. Log Rotation

Configure log rotation in Docker Compose:

```yaml
logging:
  driver: "json-file"
  options:
    max-size: "100m"
    max-file: "10"
```

### 3. Health Checks

Health check endpoint:

```bash
curl http://localhost:8000/
```

### 4. Monitoring Tools

Consider integrating:

- **Prometheus**:** Metrics collection
- **Grafana**:** Visualization
- **Sentry**:** Error tracking
- **Datadog**:** APM and monitoring

### 5. Telegram Notifications

Configure Telegram bot for alerts:

```env
TELEGRAM_BOT_TOKEN=your_token
TELEGRAM_CHAT_ID=your_chat_id
TELEGRAM_ENABLED=true
```

## Backup Strategy

### 1. Database Backups

See [scripts/BACKUP_README.md](../scripts/BACKUP_README.md) for backup scripts.

**Automated daily backups:**

```bash
# Set up cron job
./scripts/setup-backup-cron.sh
```

**Manual backup:**

```bash
./scripts/backup-db.sh
```

### 2. Backup Storage

- **Local**: Keep on server (short-term)
- **Remote**: Copy to S3, Google Cloud Storage, or another server
- **Retention**: Keep 7-30 days of daily backups

### 3. Restore Procedure

```bash
./scripts/restore-db.sh backups/postgres/backup_production_YYYYMMDD_HHMMSS.sql.gz
```

### 4. Application Files

Backup important directories:

- `uploads/` - User uploaded files
- `logs/` - Application logs (optional)

## Scaling Considerations

### Horizontal Scaling

1. **Load Balancer**: Use Nginx or cloud load balancer
2. **Multiple Instances**: Run multiple backend containers
3. **Shared Database**: Use managed database service
4. **Session Management**: Use JWT (stateless)

### Vertical Scaling

1. **Increase Resources**: Upgrade server/container resources
2. **Database**: Use managed database with higher tier
3. **GPU**: Add GPU for face recognition if needed

### Database Scaling

1. **Read Replicas**: For read-heavy workloads
2. **Connection Pooling**: Optimize connection pool size
3. **Query Optimization**: Index and optimize slow queries

## Maintenance

### 1. Regular Updates

- **Dependencies**: Regularly update Python packages
- **PostgreSQL**: Keep database updated
- **Docker Images**: Update base images
- **Security Patches**: Apply promptly

### 2. Database Maintenance

```bash
# Check database size
docker compose exec postgres psql -U powergym_user -d powergym -c "SELECT pg_size_pretty(pg_database_size('powergym'));"

# Vacuum database
docker compose exec postgres psql -U powergym_user -d powergym -c "VACUUM ANALYZE;"
```

### 3. Log Rotation

Ensure logs don't fill disk:

```bash
# Check log sizes
du -sh logs/

# Rotate if needed
docker compose restart backend
```

### 4. Monitoring Disk Space

```bash
df -h
docker system df
```

### 5. Restart Services

```bash
# Restart all services
docker compose restart

# Restart specific service
docker compose restart backend

# Rebuild and restart
docker compose up -d --build
```

## Troubleshooting Production Issues

### Service Won't Start

1. Check logs: `docker compose logs backend`
2. Verify environment variables
3. Check database connectivity
4. Verify port availability

### High Memory Usage

1. Check resource limits
2. Review application logs for memory leaks
3. Consider increasing container memory
4. Optimize database queries

### Slow Performance

1. Check database query performance
2. Review application logs
3. Monitor resource usage
4. Consider scaling up

For more troubleshooting, see [TROUBLESHOOTING.md](TROUBLESHOOTING.md).

## Post-Deployment Checklist

After deployment:

- [ ] Verify health endpoint responds
- [ ] Test authentication
- [ ] Test face recognition (if applicable)
- [ ] Verify database connectivity
- [ ] Check logs for errors
- [ ] Monitor resource usage
- [ ] Test backup/restore procedure
- [ ] Verify SSL/TLS (if using)
- [ ] Test rate limiting
- [ ] Verify CORS configuration

---

**Next**: [Troubleshooting Guide](TROUBLESHOOTING.md) | [Database Guide](DATABASE.md)

