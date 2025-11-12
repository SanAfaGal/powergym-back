# Rewards System

This guide explains the rewards system in PowerGym, including business rules, eligibility calculation, and usage.

## Table of Contents

- [Overview](#overview)
- [Business Rules](#business-rules)
- [Reward Eligibility](#reward-eligibility)
- [Reward Application](#reward-application)
- [API Endpoints](#api-endpoints)
- [Configuration](#configuration)
- [Examples](#examples)

## Overview

The PowerGym rewards system incentivizes member attendance by offering discounts on subscriptions. Members earn rewards based on their attendance frequency during subscription cycles.

### Key Features

- **Attendance-Based**: Rewards earned through gym attendance
- **Automatic Calculation**: Eligibility calculated automatically
- **Time-Limited**: Rewards expire after 7 days
- **Subscription Discount**: Applied as percentage discount on new subscriptions
- **Monthly Plans Only**: Only available for monthly subscription plans

## Business Rules

### Eligibility Requirements

1. **Subscription Type**
   - Only **monthly plans** (`duration_unit == 'month'`) are eligible
   - Weekly, daily, or yearly plans do not qualify

2. **Attendance Threshold**
   - Minimum **20 attendances** required in subscription cycle
   - Attendances counted from subscription `start_date` to `end_date` (or today if active)

3. **One Reward Per Subscription**
   - Only one reward can be earned per subscription cycle
   - If reward already exists for subscription, returns existing reward

4. **Reward Expiration**
   - Rewards expire **7 days** after becoming eligible
   - Expired rewards cannot be applied

### Reward Details

- **Discount Percentage**: 20% (default, configurable)
- **Expiration Period**: 7 days from eligible date
- **Status**: `pending` → `applied` → `expired`

### Attendance Counting

**For Active Subscriptions**:
- Count from `start_date` to `today`
- Formula: `WHERE check_in >= start_date AND check_in <= today`

**For Terminated Subscriptions**:
- Count from `start_date` to `end_date`
- Formula: `WHERE check_in >= start_date AND check_in <= end_date`

## Reward Eligibility

### Calculation Process

1. **Verify Subscription Exists**
   - Subscription must exist (can be active or terminated)

2. **Check Plan Type**
   - Plan must be monthly (`duration_unit == 'month'`)
   - Returns `eligible=False` if not monthly

3. **Check Existing Reward**
   - If reward already exists for subscription, returns existing reward info

4. **Count Attendances**
   - Counts attendances in subscription cycle
   - Uses date range based on subscription status

5. **Check Threshold**
   - If attendance count < 20: Returns `eligible=False`
   - If attendance count >= 20: Creates reward

6. **Create Reward**
   - Sets `eligible_date` (today if active, `end_date` if terminated)
   - Sets `expires_at` to `eligible_date + 7 days`
   - Sets discount to 20%
   - Status: `pending`

### Eligibility Response

```python
{
    "eligible": True,
    "attendance_count": 25,
    "reward_id": "123e4567-e89b-12d3-a456-426614174000",
    "expires_at": "2025-01-22T00:00:00Z"
}
```

## Reward Application

### Applying a Reward

Rewards can be applied when creating a new subscription:

1. **Validate Reward**
   - Reward must exist
   - Status must be `pending`
   - Reward must not be expired (`expires_at > NOW()`)

2. **Validate Subscription**
   - Target subscription must exist

3. **Apply Discount**
   - Discount percentage applied to subscription price
   - Final price calculated: `price * (1 - discount_percentage / 100)`

4. **Update Reward**
   - Status changed to `applied`
   - `applied_at` set to current time
   - `applied_subscription_id` set to target subscription

5. **Send Notification**
   - Telegram notification sent (if configured)

### Application Constraints

- **One-Time Use**: Each reward can only be applied once
- **Cannot Revert**: Applied rewards cannot be unapplied
- **Expired Rewards**: Cannot apply expired rewards
- **Status Check**: Only `pending` rewards can be applied

## API Endpoints

### Calculate Eligibility

Calculate if a subscription qualifies for a reward:

```http
POST /api/v1/subscriptions/{subscription_id}/rewards/calculate
Authorization: Bearer <token>
```

**Response**:
```json
{
  "eligible": true,
  "attendance_count": 25,
  "reward_id": "123e4567-e89b-12d3-a456-426614174000",
  "expires_at": "2025-01-22T00:00:00Z"
}
```

### Get Available Rewards

Get all available (pending, not expired) rewards for a client:

```http
GET /api/v1/clients/{client_id}/rewards/available
Authorization: Bearer <token>
```

**Response**:
```json
[
  {
    "id": "123e4567-e89b-12d3-a456-426614174000",
    "subscription_id": "...",
    "client_id": "...",
    "attendance_count": 25,
    "discount_percentage": 20.00,
    "eligible_date": "2025-01-15",
    "expires_at": "2025-01-22T00:00:00Z",
    "status": "pending"
  }
]
```

### Apply Reward

Apply a reward to a subscription:

```http
POST /api/v1/rewards/{reward_id}/apply
Authorization: Bearer <token>
Content-Type: application/json

{
  "subscription_id": "987fcdeb-51a2-43f1-9876-543210fedcba",
  "discount_percentage": 20.00
}
```

**Response**:
```json
{
  "id": "123e4567-e89b-12d3-a456-426614174000",
  "status": "applied",
  "applied_at": "2025-01-15T10:30:00Z",
  "applied_subscription_id": "987fcdeb-51a2-43f1-9876-543210fedcba"
}
```

### Get Rewards by Subscription

Get all rewards for a subscription:

```http
GET /api/v1/subscriptions/{subscription_id}/rewards
Authorization: Bearer <token>
```

## Configuration

### Reward Constants

Currently hardcoded in the service, but can be configured:

```python
# In app/services/reward_service.py
ATTENDANCE_THRESHOLD = 20  # Minimum attendances required
DISCOUNT_PERCENTAGE = 20.00  # Default discount percentage
EXPIRATION_DAYS = 7  # Days until reward expires
```

### Database Schema

```sql
CREATE TABLE rewards (
    id UUID PRIMARY KEY,
    subscription_id UUID REFERENCES subscriptions(id),
    client_id UUID REFERENCES clients(id),
    attendance_count INTEGER NOT NULL,
    discount_percentage DECIMAL(5,2) NOT NULL DEFAULT 20.00,
    eligible_date DATE NOT NULL,
    expires_at TIMESTAMP WITH TIME ZONE NOT NULL,
    status reward_status_enum NOT NULL DEFAULT 'pending',
    applied_at TIMESTAMP WITH TIME ZONE,
    applied_subscription_id UUID REFERENCES subscriptions(id),
    created_at TIMESTAMP WITH TIME ZONE DEFAULT NOW(),
    updated_at TIMESTAMP WITH TIME ZONE DEFAULT NOW()
);
```

### Reward Status Enum

- `pending`: Reward earned but not yet applied
- `applied`: Reward has been applied to a subscription
- `expired`: Reward expired without being applied

## Examples

### Example 1: Client Earns Reward

**Scenario**:
- Client has monthly subscription (Jan 1 - Jan 31)
- Client attends gym 25 times in January
- Reward eligibility calculated on Jan 31

**Process**:
1. System counts attendances: 25
2. 25 >= 20 threshold → Reward created
3. `eligible_date`: Jan 31
4. `expires_at`: Feb 7 (Jan 31 + 7 days)
5. Status: `pending`

**Result**:
```json
{
  "eligible": true,
  "attendance_count": 25,
  "reward_id": "...",
  "expires_at": "2025-02-07T00:00:00Z"
}
```

### Example 2: Client Applies Reward

**Scenario**:
- Client has pending reward (20% discount, expires Feb 7)
- Client creates new subscription on Feb 1
- Subscription price: $50.00

**Process**:
1. Reward validated (pending, not expired)
2. Discount applied: 20% of $50.00 = $10.00
3. Final price: $50.00 - $10.00 = $40.00
4. Reward status updated to `applied`

**Result**:
- Subscription created with `final_price`: $40.00
- Reward status: `applied`
- Notification sent to client

### Example 3: Reward Expires

**Scenario**:
- Reward created on Jan 15
- Expires on Jan 22
- Client doesn't apply before expiration

**Process**:
1. System checks expired rewards (via cron or manual)
2. Finds rewards where `expires_at < NOW()` and `status = 'pending'`
3. Updates status to `expired`

**Result**:
- Reward status: `expired`
- Cannot be applied to new subscriptions

## Reward Expiration

### Automatic Expiration

Rewards can be expired automatically:

```python
from app.services.reward_service import RewardService

# Expire all pending rewards that have passed expiration date
expired_count = RewardService.expire_rewards(db)
```

### Manual Expiration

Rewards expire automatically based on their `expires_at` timestamp. There is no dedicated expiration endpoint - rewards are checked for expiration when accessed or can be expired via database queries if needed.

## Best Practices

### 1. Calculate Eligibility Regularly

- Calculate eligibility when subscription ends
- Calculate eligibility when checking subscription status
- Consider cron job for batch calculations

### 2. Notify Clients

- Send notification when reward is earned
- Remind clients before reward expires
- Notify when reward is applied

### 3. Display Rewards

- Show available rewards in client dashboard
- Display expiration countdown
- Show reward history

### 4. Handle Edge Cases

- Multiple subscriptions: Each subscription cycle is independent
- Subscription renewal: New cycle, new eligibility calculation
- Partial months: Count attendances in actual cycle period

## Troubleshooting

### Reward Not Created

**Possible Causes**:
1. Attendance count < 20
2. Plan is not monthly
3. Reward already exists for subscription

**Solution**: Check eligibility response for details

### Cannot Apply Reward

**Possible Causes**:
1. Reward expired (`expires_at < NOW()`)
2. Reward already applied (`status != 'pending'`)
3. Reward doesn't exist

**Solution**: Check reward status and expiration date

### Attendance Count Incorrect

**Possible Causes**:
1. Date range calculation error
2. Timezone issues
3. Missing attendance records

**Solution**: Verify attendance records and date calculations

---

**Next**: [API Documentation](API.md) | [Notifications Guide](NOTIFICATIONS.md)

