# API Documentation

This guide provides an overview of the PowerGym Backend API, including authentication, endpoints, request/response formats, and usage examples.

## Table of Contents

- [API Overview](#api-overview)
- [Base URL](#base-url)
- [Authentication](#authentication)
- [API Versioning](#api-versioning)
- [Request/Response Formats](#requestresponse-formats)
- [Error Handling](#error-handling)
- [Rate Limiting](#rate-limiting)
- [Endpoint Categories](#endpoint-categories)
- [Interactive Documentation](#interactive-documentation)
- [Examples](#examples)

## API Overview

The PowerGym Backend API is a RESTful API built with FastAPI, providing:

- **RESTful Design**: Standard HTTP methods and status codes
- **JSON Format**: All requests and responses use JSON
- **OpenAPI Documentation**: Auto-generated Swagger/ReDoc documentation
- **Type Safety**: Request/response validation using Pydantic
- **Authentication**: JWT-based authentication
- **Rate Limiting**: Built-in request rate limiting

## Base URL

### Development
```
http://localhost:8000
```

### Production
```
https://your-api-domain.com
```

### API Prefix
All endpoints are prefixed with `/api/v1`:

```
http://localhost:8000/api/v1
```

## Authentication

### JWT Tokens

The API uses JWT (JSON Web Tokens) for authentication:

1. **Login** to receive access and refresh tokens
2. **Include token** in Authorization header for protected endpoints
3. **Refresh token** when access token expires

### Login

```http
POST /api/v1/auth/token
Content-Type: application/x-www-form-urlencoded

username=admin&password=your_password
```

**Response:**
```json
{
  "access_token": "eyJhbGciOiJIUzI1NiIsInR5cCI6IkpXVCJ9...",
  "token_type": "bearer",
  "refresh_token": "eyJhbGciOiJIUzI1NiIsInR5cCI6IkpXVCJ9..."
}
```

### Using Access Token

Include the token in the Authorization header:

```http
GET /api/v1/users/me
Authorization: Bearer eyJhbGciOiJIUzI1NiIsInR5cCI6IkpXVCJ9...
```

### Refresh Token

Refresh an expired access token:

```http
POST /api/v1/auth/refresh
Content-Type: application/json

{
  "refresh_token": "eyJhbGciOiJIUzI1NiIsInR5cCI6IkpXVCJ9..."
}
```

### Token Expiration

- **Access Token**: 5 hours (configurable via `ACCESS_TOKEN_EXPIRE_MINUTES`)
- **Refresh Token**: 12 hours (configurable via `REFRESH_TOKEN_EXPIRE_HOURS`)

## API Versioning

The API uses URL-based versioning:

- Current version: `v1`
- Base path: `/api/v1`

Future versions will use `/api/v2`, `/api/v3`, etc.

## Request/Response Formats

### Request Format

All requests use JSON (except login which uses form data):

```http
POST /api/v1/clients
Content-Type: application/json
Authorization: Bearer <token>

{
  "dni_type": "CC",
  "dni_number": "1234567890",
  "first_name": "John",
  "last_name": "Doe",
  ...
}
```

### Response Format

Successful responses:

```json
{
  "id": "123e4567-e89b-12d3-a456-426614174000",
  "dni_number": "1234567890",
  "first_name": "John",
  "last_name": "Doe",
  ...
}
```

Error responses:

```json
{
  "detail": "Error message here"
}
```

### Pagination

List endpoints support pagination using `limit` and `offset`:

```http
GET /api/v1/clients?limit=20&offset=0
```

**Response:**
```json
[
  {
    "id": "...",
    "first_name": "John",
    ...
  }
]
```

Note: Most list endpoints return arrays directly, not paginated objects. Use `limit` and `offset` query parameters for pagination.

## Error Handling

### HTTP Status Codes

- **200 OK**: Successful request
- **201 Created**: Resource created successfully
- **400 Bad Request**: Invalid request data
- **401 Unauthorized**: Authentication required or invalid token
- **403 Forbidden**: Insufficient permissions
- **404 Not Found**: Resource not found
- **409 Conflict**: Resource already exists
- **422 Unprocessable Entity**: Validation error
- **429 Too Many Requests**: Rate limit exceeded
- **500 Internal Server Error**: Server error

### Error Response Format

```json
{
  "detail": "Error message describing what went wrong"
}
```

### Validation Errors

```json
{
  "detail": [
    {
      "loc": ["body", "dni_number"],
      "msg": "field required",
      "type": "value_error.missing"
    }
  ]
}
```

## Rate Limiting

The API implements rate limiting to prevent abuse:

- **Default**: 60 requests per minute per IP
- **Configurable**: Via `RATE_LIMIT_PER_MINUTE` environment variable

### Rate Limit Headers

```http
X-RateLimit-Limit: 60
X-RateLimit-Remaining: 59
X-RateLimit-Reset: 1640995200
```

### Rate Limit Exceeded

When rate limit is exceeded:

```http
HTTP/1.1 429 Too Many Requests
Content-Type: application/json

{
  "detail": "Rate limit exceeded: 60 requests per minute"
}
```

## Endpoint Categories

### Authentication (`/api/v1/auth`)

- `POST /auth/token` - User login (get access and refresh tokens)
- `POST /auth/refresh` - Refresh access token
- `POST /auth/register` - Register new user (admin only)
- `POST /auth/logout` - Logout current user
- `GET /auth/me` - Get current authenticated user

### Users (`/api/v1/users`)

- `GET /users/me` - Get current user
- `PUT /users/me` - Update current user
- `PATCH /users/me/password` - Change current user password
- `DELETE /users/me` - Disable own account
- `GET /users` - List all users (admin only)
- `GET /users/{username}` - Get user by username (admin only)
- `PUT /users/{username}` - Update user (admin only)
- `PATCH /users/{username}/password` - Reset user password (admin only)
- `PATCH /users/{username}/role` - Change user role (admin only)
- `PATCH /users/{username}/disable` - Disable user (admin only)
- `PATCH /users/{username}/enable` - Enable user (admin only)
- `DELETE /users/{username}` - Delete user (admin only)

### Clients (`/api/v1/clients`)

- `GET /clients` - List clients (with search and filters)
- `GET /clients/dni/{dni_number}` - Get client by DNI number
- `GET /clients/{client_id}` - Get client by ID
- `POST /clients` - Create client
- `PUT /clients/{client_id}` - Update client
- `PATCH /clients/{client_id}` - Partial update client
- `GET /clients/{client_id}/dashboard` - Get client dashboard with statistics

### Face Recognition (`/api/v1/face`)

- `POST /face/register` - Register face biometric for a client
- `POST /face/authenticate` - Authenticate face (used internally by check-in)
- `POST /face/compare` - Compare two face images
- `PUT /face/update` - Update face registration for a client
- `DELETE /face/{client_id}` - Delete face registration for a client

### Attendances (`/api/v1/attendances`)

- `POST /check-in` - Check-in with facial recognition
- `GET /attendances` - List all attendances (admin only, with date filters)
- `GET /clients/{client_id}/attendances` - Get client attendance history
- `GET /{attendance_id}` - Get attendance by ID

### Plans (`/api/v1/plans`)

- `GET /plans` - List all membership plans
- `GET /plans/search` - Search plans by name or description
- `GET /plans/slug/{slug}` - Get plan by slug
- `GET /plans/{plan_id}` - Get plan by ID
- `POST /plans` - Create plan (admin only)
- `PUT /plans/{plan_id}` - Update plan (admin only)
- `DELETE /plans/{plan_id}` - Delete plan (admin only)

### Subscriptions

#### Client Subscriptions (`/api/v1/clients/{client_id}/subscriptions`)

- `POST /` - Create subscription for a client
- `GET /active` - Get active subscription for a client
- `GET /` - Get all subscriptions for a client
- `POST /{subscription_id}/renew` - Renew a subscription
- `PATCH /{subscription_id}/cancel` - Cancel a subscription

#### Global Subscriptions (`/api/v1/subscriptions`)

- `GET /` - List all subscriptions (with optional filters)
- `GET /{subscription_id}` - Get subscription by ID
- `POST /expire` - Expire subscriptions (automated task)
- `POST /activate` - Activate scheduled subscriptions (automated task)

### Payments (`/api/v1/payments`)

#### Subscription Payments

- `POST /subscriptions/{subscription_id}/payments` - Create payment for a subscription
- `GET /subscriptions/{subscription_id}/payments` - List payments for a subscription
- `GET /subscriptions/{subscription_id}/payments/stats` - Get payment statistics for a subscription

#### Client Payments

- `GET /clients/{client_id}/payments` - List all payments made by a client
- `GET /clients/{client_id}/payments/stats` - Get payment statistics for a client

### Inventory (`/api/v1/inventory`)

#### Products (`/inventory/products`)

- `GET /inventory/products` - List products with pagination
- `GET /inventory/products/search` - Search products
- `GET /inventory/products/{product_id}` - Get product by ID
- `POST /inventory/products` - Create product (admin only)
- `PATCH /inventory/products/{product_id}` - Update product (admin only)
- `DELETE /inventory/products/{product_id}` - Delete product (admin only)

#### Stock (`/inventory/stock`)

- `POST /inventory/stock/add` - Add stock to a product
- `POST /inventory/stock/remove` - Remove stock from a product

#### Movements (`/inventory/movements`)

- `GET /inventory/movements` - List all movements with pagination
- `GET /inventory/movements/{movement_id}` - Get movement by ID

#### Reports (`/inventory/reports`)

- `GET /inventory/reports/stats` - Get inventory statistics
- `GET /inventory/reports/low-stock` - Get low stock products
- `GET /inventory/reports/out-of-stock` - Get out of stock products
- `GET /inventory/reports/overstock` - Get overstock products
- `GET /inventory/reports/products/{product_id}/history` - Get product movement history
- `GET /inventory/reports/daily-sales` - Get daily sales report
- `GET /inventory/reports/daily-sales-by-employee` - Get daily sales by employee
- `GET /inventory/reports/reconciliation` - Get reconciliation report

### Statistics (`/api/v1/statistics`)

- `GET /statistics` - Get comprehensive dashboard statistics (requires date range filters)
- `GET /statistics/recent-activities` - Get recent activities from last 24 hours

### Rewards (`/api/v1/rewards`)

- `POST /subscriptions/{subscription_id}/rewards/calculate` - Calculate reward eligibility for a subscription
- `GET /clients/{client_id}/rewards/available` - Get available rewards for a client
- `GET /subscriptions/{subscription_id}/rewards` - Get all rewards for a subscription
- `POST /rewards/{reward_id}/apply` - Apply a reward to a subscription

### Roles (`/api/v1/roles`)

- `GET /roles` - List available roles and descriptions

## Interactive Documentation

### Swagger UI

Access interactive API documentation at:

```
http://localhost:8000/api/v1/docs
```

Features:
- Browse all endpoints
- Test endpoints directly
- View request/response schemas
- See authentication requirements

### ReDoc

Alternative documentation format:

```
http://localhost:8000/api/v1/redoc
```

### OpenAPI JSON

Raw OpenAPI specification:

```
http://localhost:8000/api/v1/openapi.json
```

## Examples

### Python Example

```python
import requests

# Base URL
BASE_URL = "http://localhost:8000/api/v1"

# Login
response = requests.post(
    f"{BASE_URL}/auth/token",
    data={"username": "admin", "password": "password"}
)
tokens = response.json()
access_token = tokens["access_token"]

# Get current user
headers = {"Authorization": f"Bearer {access_token}"}
response = requests.get(f"{BASE_URL}/users/me", headers=headers)
user = response.json()

# Create client
client_data = {
    "dni_type": "CC",
    "dni_number": "1234567890",
    "first_name": "John",
    "last_name": "Doe",
    "email": "john@powergym.com",
    "phone": "+1234567890"
}
response = requests.post(
    f"{BASE_URL}/clients",
    json=client_data,
    headers=headers
)
client = response.json()
```

### cURL Examples

#### Login

```bash
curl -X POST http://localhost:8000/api/v1/auth/token \
  -H "Content-Type: application/x-www-form-urlencoded" \
  -d "username=admin&password=password"
```

#### Get Current User

```bash
curl -X GET http://localhost:8000/api/v1/users/me \
  -H "Authorization: Bearer YOUR_ACCESS_TOKEN"
```

#### Create Client

```bash
curl -X POST http://localhost:8000/api/v1/clients \
  -H "Authorization: Bearer YOUR_ACCESS_TOKEN" \
  -H "Content-Type: application/json" \
  -d '{
    "dni_type": "CC",
    "dni_number": "1234567890",
    "first_name": "John",
    "last_name": "Doe",
    "email": "john@powergym.com"
  }'
```

#### Register Face

```bash
curl -X POST http://localhost:8000/api/v1/face/register \
  -H "Authorization: Bearer YOUR_ACCESS_TOKEN" \
  -H "Content-Type: application/json" \
  -d '{
    "client_id": "123e4567-e89b-12d3-a456-426614174000",
    "image_base64": "data:image/jpeg;base64,..."
  }'
```

#### Check-in with Face Recognition

```bash
curl -X POST http://localhost:8000/api/v1/check-in \
  -H "Authorization: Bearer YOUR_ACCESS_TOKEN" \
  -H "Content-Type: application/json" \
  -d '{
    "image_base64": "data:image/jpeg;base64,..."
  }'
```

### JavaScript/TypeScript Example

```typescript
const BASE_URL = 'http://localhost:8000/api/v1';

// Login
const loginResponse = await fetch(`${BASE_URL}/auth/token`, {
  method: 'POST',
  headers: { 'Content-Type': 'application/x-www-form-urlencoded' },
  body: new URLSearchParams({ username: 'admin', password: 'password' })
});
const { access_token } = await loginResponse.json();

// Get clients
const clientsResponse = await fetch(`${BASE_URL}/clients`, {
  headers: { 'Authorization': `Bearer ${access_token}` }
});
const clients = await clientsResponse.json();
```

## Best Practices

### 1. Error Handling

Always check response status:

```python
response = requests.get(url, headers=headers)
if response.status_code == 200:
    data = response.json()
else:
    error = response.json()
    print(f"Error: {error['detail']}")
```

### 2. Token Management

- Store tokens securely
- Refresh tokens before expiration
- Handle 401 errors by re-authenticating

### 3. Pagination

Always use pagination for list endpoints:

```python
offset = 0
limit = 20
while True:
    response = requests.get(
        f"{BASE_URL}/clients?limit={limit}&offset={offset}",
        headers=headers
    )
    items = response.json()
    if not items:
        break
    # Process items
    offset += limit
```

### 4. Rate Limiting

Respect rate limits:

- Monitor `X-RateLimit-Remaining` header
- Implement exponential backoff
- Cache responses when possible

### 5. Request Timeouts

Set appropriate timeouts:

```python
response = requests.get(url, timeout=30)  # 30 seconds
```

---

**Next**: [Face Recognition Guide](FACE_RECOGNITION.md) | [Troubleshooting Guide](TROUBLESHOOTING.md)

