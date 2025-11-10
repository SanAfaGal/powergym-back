# GitHub Actions Workflows

This directory contains automated GitHub Actions workflows for PowerGym.

## Workflow: Automatic Subscription Expiration

The `expire-subscriptions.yml` workflow runs daily at 00:00 Bogotá time to automatically expire subscriptions that have ended.

### Required Configuration

Before the workflow can function, you need to configure the following secrets in GitHub:

#### 1. Configure Secrets in GitHub

1. Go to your repository on GitHub
2. Navigate to **Settings** → **Secrets and variables** → **Actions**
3. Click **New repository secret**
4. Add the following secrets:

##### `API_BASE_URL`
- **Description**: Base URL of your API
- **Example**: `https://api.powergym.com` or `http://localhost:8000` (for development)
- **Important**: Do not include the trailing slash (`/`)

##### `API_TOKEN`
- **Description**: JWT authentication token to access the endpoint
- **How to obtain it**: See "Obtain Authentication Token" section below

### Obtain Authentication Token

You have several options to obtain a valid JWT token:

#### Option 1: Use the administrator user (Recommended for development)

1. Log in to the API using the login endpoint:
   ```bash
   curl -X POST "https://api.powergym.com/api/v1/auth/token" \
     -H "Content-Type: application/x-www-form-urlencoded" \
     -d "username=admin&password=your_password"
   ```

2. The response will include an `access_token`:
   ```json
   {
     "access_token": "eyJhbGciOiJIUzI1NiIsInR5cCI6IkpXVCJ9...",
     "refresh_token": "eyJhbGciOiJIUzI1NiIsInR5cCI6IkpXVCJ9...",
     "token_type": "bearer"
   }
   ```

3. Copy the `access_token` value and use it as `API_TOKEN` in GitHub secrets

**Note**: Access tokens have a limited duration (default 5 hours according to configuration). If you need a long-lived token, consider creating a service user.

#### Option 2: Create a service user (Recommended for production)

1. Create a specific user for this purpose using the registration endpoint (requires administrator permissions):
   ```bash
   curl -X POST "https://api.powergym.com/api/v1/auth/register" \
     -H "Authorization: Bearer YOUR_ADMIN_TOKEN" \
     -H "Content-Type: application/json" \
     -d '{
       "username": "service_expire_subscriptions",
       "email": "service@powergym.com",
       "password": "secure_password",
       "full_name": "Service Account - Expire Subscriptions",
       "role": "admin"
     }'
   ```

2. Get the token for this user using the login endpoint (see Option 1)

3. Use this token as `API_TOKEN` in GitHub secrets

**Advantages**:
- You can easily rotate credentials
- You have control over user permissions
- It's more secure than using the main administrator's token

#### Option 3: Use the refresh token (if the access token expires)

If the `access_token` expires, you can use the `refresh_token` to get a new one:

```bash
curl -X POST "https://api.powergym.com/api/v1/auth/refresh" \
  -H "Content-Type: application/json" \
  -d '{
    "refresh_token": "your_refresh_token"
  }'
```

### Verify Configuration

Once the secrets are configured, you can:

1. **Run the workflow manually**:
   - Go to the **Actions** tab in GitHub
   - Select the "Expire Subscriptions" workflow
   - Click **Run workflow** → **Run workflow**

2. **View execution logs**:
   - In the **Actions** tab, click on the most recent run
   - Review the logs of the "expire-subscriptions" job
   - You should see information about how many subscriptions were expired

3. **Verify in the database**:
   - Query subscriptions with `EXPIRED` status
   - Verify that expiration dates match the execution date

### Workflow Schedule

The workflow is configured to run:
- **Daily at 00:00 Bogotá time (America/Bogota)**
- **Equivalent to 05:00 UTC** (GitHub Actions uses UTC)

To change the schedule, edit the `expire-subscriptions.yml` file and modify the line:
```yaml
- cron: '0 5 * * *'  # Format: minute hour day month day-of-week
```

**Cron examples**:
- `0 5 * * *` - Daily at 05:00 UTC (00:00 Bogotá)
- `0 6 * * *` - Daily at 06:00 UTC (01:00 Bogotá)
- `0 0 * * *` - Daily at 00:00 UTC (19:00 Bogotá of previous day)

### Troubleshooting

#### Error: "API_BASE_URL is not configured"
- Verify that you have added the `API_BASE_URL` secret in GitHub
- Make sure the secret name is exactly `API_BASE_URL` (case-sensitive)

#### Error: "API_TOKEN is not configured"
- Verify that you have added the `API_TOKEN` secret in GitHub
- Make sure the secret name is exactly `API_TOKEN` (case-sensitive)

#### Error: "401 Unauthorized"
- The JWT token has expired or is invalid
- Get a new token using the login endpoint
- Update the `API_TOKEN` secret in GitHub

#### Error: "404 Not Found"
- Verify that the base URL (`API_BASE_URL`) is correct
- Make sure it does not include the trailing slash (`/`)
- Verify that the `/api/v1/subscriptions/expire` endpoint is available

#### The workflow does not run automatically
- Verify that the workflow is in the `main` or `master` branch
- Workflows only run automatically if they are in the default branch
- You can run it manually using `workflow_dispatch`

### Important Notes

- Secrets are sensitive and should not be shared publicly
- JWT tokens have a limited duration, consider creating a service user with credentials you can rotate
- The workflow uses `curl` and `jq` (if available) to make HTTP requests
- Workflow logs are available in the **Actions** tab of GitHub
