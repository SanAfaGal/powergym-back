# CI/CD and GitHub Actions

This guide explains the continuous integration and deployment workflows configured for PowerGym Backend.

## Table of Contents

- [Overview](#overview)
- [GitHub Actions Workflows](#github-actions-workflows)
  - [Expire Subscriptions](#expire-subscriptions)
  - [Activate Subscriptions](#activate-subscriptions)
- [Configuration](#configuration)
- [Manual Execution](#manual-execution)
- [Troubleshooting](#troubleshooting)

## Overview

PowerGym uses **GitHub Actions** to automate scheduled tasks that maintain the system:

- **Subscription Expiration**: Automatically expires subscriptions that have ended
- **Subscription Activation**: Activates scheduled subscriptions that are due to start

These workflows run daily at scheduled times and can also be triggered manually.

## GitHub Actions Workflows

### Expire Subscriptions

**File**: `.github/workflows/expire-subscriptions.yml`

This workflow automatically expires subscriptions that have passed their end date.

#### Schedule

- **Runs**: Daily at 00:00 Bogotá time (05:00 UTC)
- **Cron**: `0 5 * * *` (UTC)
- **Timezone**: America/Bogota (UTC-5)

#### What It Does

1. Calls the API endpoint: `POST /api/v1/subscriptions/expire`
2. Expires all subscriptions where `end_date < today`
3. Updates subscription status to `expired`
4. Sends notifications (if configured)

#### Configuration

Required GitHub Secrets:

- `API_BASE_URL`: Base URL of your API (e.g., `https://api.your-domain.com`)
- `API_TOKEN`: JWT authentication token

#### Example Output

```
🚀 Starting subscription expiration...
📅 Date/Time (UTC): 2025-01-15 05:00:00 UTC
📅 Date/Time (Bogotá): 2025-01-15 00:00:00 COT
🔗 API Base URL: https://api.your-domain.com
🔗 Endpoint URL: https://api.your-domain.com/api/v1/subscriptions/expire
✅ Subscriptions expired successfully
```

### Activate Subscriptions

**File**: `.github/workflows/activate-subscriptions.yml`

This workflow automatically activates subscriptions that are scheduled to start.

#### Schedule

- **Runs**: Daily at 00:05 Bogotá time (05:05 UTC)
- **Cron**: `5 5 * * *` (UTC)
- **Timezone**: America/Bogota (UTC-5)
- **Note**: Runs 5 minutes after expire-subscriptions to ensure proper ordering

#### What It Does

1. Calls the API endpoint: `POST /api/v1/subscriptions/activate`
2. Activates all subscriptions where:
   - Status is `scheduled`
   - `start_date <= today`
3. Updates subscription status to `active`
4. Sends notifications (if configured)

#### Configuration

Same secrets as expire-subscriptions:

- `API_BASE_URL`: Base URL of your API
- `API_TOKEN`: JWT authentication token

## Configuration

### Setting Up GitHub Secrets

1. **Navigate to Repository Settings**
   - Go to your GitHub repository
   - Click **Settings** → **Secrets and variables** → **Actions**

2. **Add API_BASE_URL Secret**
   - Click **New repository secret**
   - Name: `API_BASE_URL`
   - Value: Your API base URL (e.g., `https://api.your-domain.com`)
   - **Important**: Do not include trailing slash (`/`)

3. **Add API_TOKEN Secret**
   - Click **New repository secret**
   - Name: `API_TOKEN`
   - Value: JWT access token (see below)

### Obtaining API Token

You have two options for obtaining a valid JWT token:

#### Option 1: Use Administrator Account (Development)

1. **Login via API**:
   ```bash
   curl -X POST "https://api.your-domain.com/api/v1/auth/token" \
     -H "Content-Type: application/x-www-form-urlencoded" \
     -d "username=admin&password=your_password"
   ```

2. **Extract Access Token**:
   ```json
   {
     "access_token": "eyJhbGciOiJIUzI1NiIsInR5cCI6IkpXVCJ9...",
     "refresh_token": "...",
     "token_type": "bearer"
   }
   ```

3. **Use `access_token` as `API_TOKEN`**

   **Note**: Access tokens expire (default: 5 hours). You'll need to update the secret periodically.

#### Option 2: Create Service User (Production - Recommended)

1. **Create a dedicated service user**:
   ```bash
   curl -X POST "https://api.your-domain.com/api/v1/auth/register" \
     -H "Authorization: Bearer <admin_token>" \
     -H "Content-Type: application/json" \
     -d '{
       "username": "github_actions",
       "email": "github-actions@powergym.com",
       "password": "strong_password",
       "full_name": "GitHub Actions Service"
     }'
   ```

2. **Login with service user**:
   ```bash
   curl -X POST "https://api.your-domain.com/api/v1/auth/token" \
     -H "Content-Type: application/x-www-form-urlencoded" \
     -d "username=github_actions&password=strong_password"
   ```

3. **Use the access token** (update when it expires)

**Best Practice**: For production, create a service user with appropriate permissions and rotate the token regularly.

### Updating Token Expiration

To reduce token rotation frequency, you can increase token expiration (development only):

```env
ACCESS_TOKEN_EXPIRE_MINUTES=1440  # 24 hours
REFRESH_TOKEN_EXPIRE_HOURS=168    # 7 days
```

**Warning**: Longer token expiration reduces security. Use with caution.

## Manual Execution

Both workflows support manual execution via GitHub's web interface:

1. **Navigate to Actions Tab**
   - Go to your repository on GitHub
   - Click **Actions** tab

2. **Select Workflow**
   - Click on "Expire Subscriptions" or "Activate Subscriptions"

3. **Run Workflow**
   - Click **Run workflow** button
   - Select branch (usually `main` or `master`)
   - Click **Run workflow**

4. **Monitor Execution**
   - View real-time logs
   - Check for errors
   - Verify API responses

## Workflow Details

### Expire Subscriptions Workflow

**Endpoint Called**: `POST /api/v1/subscriptions/expire`

**Request**:
```http
POST /api/v1/subscriptions/expire
Authorization: Bearer <API_TOKEN>
Content-Type: application/json
```

**Expected Response**:
```json
{
  "expired_count": 5,
  "message": "Subscriptions expired successfully"
}
```

**HTTP Status Codes**:
- `200`: Success
- `401`: Authentication failed (invalid token)
- `500`: Server error

### Activate Subscriptions Workflow

**Endpoint Called**: `POST /api/v1/subscriptions/activate`

**Request**:
```http
POST /api/v1/subscriptions/activate
Authorization: Bearer <API_TOKEN>
Content-Type: application/json
```

**Expected Response**:
```json
{
  "activated_count": 3,
  "message": "Subscriptions activated successfully"
}
```

**HTTP Status Codes**:
- `200`: Success
- `401`: Authentication failed
- `500`: Server error

## Troubleshooting

### Workflow Fails with 401 Unauthorized

**Problem**: API token is invalid or expired

**Solution**:
1. Check token expiration
2. Generate new token (see [Obtaining API Token](#obtaining-api-token))
3. Update `API_TOKEN` secret in GitHub

### Workflow Fails with Connection Error

**Problem**: Cannot reach API

**Solutions**:
1. Verify `API_BASE_URL` is correct (no trailing slash)
2. Check API is running and accessible
3. Verify network/firewall allows GitHub Actions IPs
4. Check API logs for connection attempts

### Workflow Runs but No Subscriptions Processed

**Problem**: No subscriptions match criteria

**Solutions**:
1. Check subscription dates in database
2. Verify timezone settings (workflow uses Bogotá time)
3. Check API endpoint logs
4. Verify endpoint logic is correct

### Token Expires Frequently

**Problem**: Access token expires before next workflow run

**Solutions**:
1. Increase `ACCESS_TOKEN_EXPIRE_MINUTES` (development)
2. Use refresh token mechanism (if implemented)
3. Create automated token rotation
4. Use service account with longer-lived tokens

### Viewing Workflow Logs

1. **GitHub Actions Tab**:
   - Go to repository → **Actions**
   - Click on workflow run
   - View step-by-step logs

2. **API Logs**:
   ```bash
   # Docker
   docker compose logs backend | grep "subscriptions/expire"
   
   # Local
   tail -f logs/app.log | grep "subscriptions/expire"
   ```

## Best Practices

### 1. Token Security

- **Never commit tokens** to repository
- **Use GitHub Secrets** for all sensitive data
- **Rotate tokens regularly** (monthly recommended)
- **Use service accounts** with minimal permissions

### 2. Monitoring

- **Set up notifications** for workflow failures
- **Monitor API logs** for errors
- **Track subscription counts** processed
- **Alert on unexpected behavior**

### 3. Testing

- **Test workflows manually** before relying on schedule
- **Verify API endpoints** work correctly
- **Test with sample data** before production
- **Monitor first few automated runs**

### 4. Error Handling

- **Workflows fail on non-200 responses**
- **Check logs** for detailed error messages
- **Implement retry logic** if needed
- **Notify team** on failures

## Customization

### Changing Schedule

Edit the cron expression in workflow files:

```yaml
schedule:
  - cron: '0 5 * * *'  # Change to desired time (UTC)
```

**Cron Format**: `minute hour day month weekday`

Examples:
- `0 5 * * *` - Daily at 05:00 UTC
- `0 */6 * * *` - Every 6 hours
- `0 0 * * 1` - Every Monday at 00:00 UTC

### Adding New Workflows

1. **Create workflow file**: `.github/workflows/your-workflow.yml`
2. **Define schedule or triggers**
3. **Configure secrets** if needed
4. **Test manually** first
5. **Monitor execution**

Example workflow structure:

```yaml
name: Your Workflow

on:
  schedule:
    - cron: '0 0 * * *'  # Daily at midnight UTC
  workflow_dispatch:  # Allow manual execution

jobs:
  your-job:
    runs-on: ubuntu-latest
    steps:
      - name: Your Step
        env:
          API_BASE_URL: ${{ secrets.API_BASE_URL }}
          API_TOKEN: ${{ secrets.API_TOKEN }}
        run: |
          # Your commands here
```

---

**Next**: [Deployment Guide](DEPLOYMENT.md) | [API Documentation](API.md)

