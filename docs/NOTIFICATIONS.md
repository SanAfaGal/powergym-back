# Notifications System

This guide explains the Telegram notification system in PowerGym, including setup, configuration, and usage.

## Table of Contents

- [Overview](#overview)
- [Configuration](#configuration)
- [Notification Types](#notification-types)
- [Notification Handlers](#notification-handlers)
- [Usage](#usage)
- [Troubleshooting](#troubleshooting)

## Overview

PowerGym includes a comprehensive notification system that sends Telegram messages for important events:

- **Client Registration**: New client sign-ups
- **Subscription Events**: Creation, activation, expiration, renewal
- **Payment Events**: Payment received, payment overdue
- **Attendance Events**: Check-in notifications
- **Reward Events**: Reward earned, reward applied
- **Inventory Events**: Low stock alerts, stock movements

### Features

- **Asynchronous**: Non-blocking notification sending
- **Error Handling**: Graceful failure without affecting main operations
- **Configurable**: Enable/disable per notification type
- **Telegram Integration**: Uses python-telegram-bot library

## Configuration

### Telegram Bot Setup

1. **Create Telegram Bot**
   - Open Telegram
   - Search for [@BotFather](https://t.me/botfather)
   - Send `/newbot` command
   - Follow instructions to create bot
   - Save the **bot token**

2. **Get Chat ID**
   - Start a conversation with your bot
   - Send any message to the bot
   - Visit: `https://api.telegram.org/bot<YOUR_TOKEN>/getUpdates`
   - Find `chat.id` in the response

3. **Configure Environment Variables**

   Add to `.env`:

   ```env
   TELEGRAM_BOT_TOKEN=123456789:ABCdefGHIjklMNOpqrsTUVwxyz
   TELEGRAM_CHAT_ID=123456789
   TELEGRAM_ENABLED=true
   ```

### Environment Variables

| Variable | Description | Required | Default |
|----------|-------------|----------|---------|
| `TELEGRAM_BOT_TOKEN` | Bot token from BotFather | Yes (if enabled) | - |
| `TELEGRAM_CHAT_ID` | Chat ID for notifications | Yes (if enabled) | - |
| `TELEGRAM_ENABLED` | Enable/disable notifications | No | `true` |

## Notification Types

### Client Notifications

#### Client Registration

Sent when a new client is registered.

**Trigger**: `ClientService.create_client()`

**Message Format**:
```
👤 New Client Registered

Name: John Doe
DNI: 1234567890
Phone: +1234567890
```

**Handler**: `ClientNotificationHandler.send_registration_notification()`

### Subscription Notifications

#### Subscription Created

Sent when a new subscription is created.

**Trigger**: `SubscriptionService.create_subscription()`

**Message Format**:
```
📅 New Subscription Created

Client: John Doe
Plan: Monthly Premium
Start Date: 2025-01-15
End Date: 2025-02-15
Price: $50.00
```

#### Subscription Activated

Sent when a subscription becomes active.

**Trigger**: `SubscriptionService.activate_subscription()`

**Message Format**:
```
✅ Subscription Activated

Client: John Doe
Plan: Monthly Premium
Active until: 2025-02-15
```

#### Subscription Expired

Sent when a subscription expires.

**Trigger**: `SubscriptionService.expire_subscription()`

**Message Format**:
```
⏰ Subscription Expired

Client: John Doe
Plan: Monthly Premium
Expired on: 2025-01-15
```

#### Subscription Renewed

Sent when a subscription is renewed.

**Trigger**: `SubscriptionService.renew_subscription()`

**Message Format**:
```
🔄 Subscription Renewed

Client: John Doe
New End Date: 2025-03-15
```

### Payment Notifications

#### Payment Received

Sent when a payment is received.

**Trigger**: `PaymentService.create_payment()`

**Message Format**:
```
💰 Payment Received

Client: John Doe
Amount: $50.00
Method: Cash
Subscription: Monthly Premium
Remaining Debt: $0.00
```

#### Payment Overdue

Sent when a subscription payment is overdue.

**Trigger**: Payment validation logic

**Message Format**:
```
⚠️ Payment Overdue

Client: John Doe
Amount Due: $50.00
Days Overdue: 5
```

### Attendance Notifications

#### Check-in Notification

Sent when a client checks in.

**Trigger**: `AttendanceService.create_attendance()`

**Message Format**:
```
✅ Check-in Recorded

Client: John Doe
Time: 2025-01-15 10:30 AM
Subscription: Active
```

### Reward Notifications

#### Reward Earned

Sent when a client earns a reward.

**Trigger**: `RewardService.calculate_eligibility()`

**Message Format**:
```
🎁 Reward Earned!

Client: John Doe
Discount: 20%
Attendances: 20
Expires: 2025-01-22
```

#### Reward Applied

Sent when a reward is applied to a subscription.

**Trigger**: `RewardService.apply_reward()`

**Message Format**:
```
✨ Reward Applied

Client: John Doe
Discount: 20%
Applied to: Monthly Premium
```

### Inventory Notifications

#### Low Stock Alert

Sent when product stock is below threshold.

**Trigger**: Inventory validation

**Message Format**:
```
📦 Low Stock Alert

Product: Protein Powder
Current Stock: 5
Minimum: 10
```

#### Stock Movement

Sent when significant stock movements occur.

**Trigger**: Stock add/remove operations

**Message Format**:
```
📊 Stock Movement

Product: Protein Powder
Type: Entry
Quantity: +50
New Stock: 55
```

## Notification Handlers

The notification system uses a handler pattern for organization:

### Handler Structure

```
app/services/notifications/
├── handlers/
│   ├── base_handler.py          # Base handler class
│   ├── attendance_handler.py     # Attendance notifications
│   ├── client_handler.py         # Client notifications
│   ├── inventory_handler.py      # Inventory notifications
│   ├── payment_handler.py        # Payment notifications
│   ├── reward_handler.py         # Reward notifications
│   └── subscription_handler.py   # Subscription notifications
└── messages.py                   # Message templates
```

### Base Handler

All handlers extend `BaseNotificationHandler`:

```python
from app.services.notifications.handlers.base_handler import BaseNotificationHandler

class CustomHandler(BaseNotificationHandler):
    async def send_custom_notification(self, data: dict):
        message = self.format_message("Custom notification", data)
        await self.send(message)
```

### Creating Custom Handlers

1. **Create handler file**: `app/services/notifications/handlers/custom_handler.py`

2. **Extend base handler**:
   ```python
   from app.services.notifications.handlers.base_handler import BaseNotificationHandler
   
   class CustomNotificationHandler(BaseNotificationHandler):
       async def send_custom_notification(self, data: dict):
           message = f"Custom: {data['info']}"
           await self.send(message)
   ```

3. **Register in NotificationService**:
   ```python
   from app.services.notifications.handlers.custom_handler import CustomNotificationHandler
   
   @staticmethod
   async def send_custom_notification(data: dict):
       await CustomNotificationHandler().send_custom_notification(data)
   ```

## Usage

### Sending Notifications

Notifications are sent automatically by services. You can also send them manually:

```python
from app.services.notification_service import NotificationService

# Send client registration notification
await NotificationService.send_client_registration_notification(
    first_name="John",
    last_name="Doe",
    dni_number="1234567890",
    phone="+1234567890"
)

# Send subscription notification
await NotificationService.send_subscription_created_notification(
    client_name="John Doe",
    plan_name="Monthly Premium",
    start_date="2025-01-15",
    end_date="2025-02-15",
    price=50.00
)
```

### Error Handling

Notifications are sent asynchronously and won't block main operations:

```python
# Notification failure won't affect subscription creation
try:
    subscription = SubscriptionService.create_subscription(...)
    # Notification sent in background
    await NotificationService.send_subscription_created_notification(...)
except Exception as e:
    # Subscription creation error is handled
    # Notification error is logged but doesn't raise
    logger.error(f"Notification failed: {e}")
```

### Disabling Notifications

**Globally**:
```env
TELEGRAM_ENABLED=false
```

**Per notification type**:
Modify handler to check condition before sending.

## Troubleshooting

### Notifications Not Sending

**Check Configuration**:
1. Verify `TELEGRAM_ENABLED=true`
2. Check `TELEGRAM_BOT_TOKEN` is valid
3. Verify `TELEGRAM_CHAT_ID` is correct
4. Ensure bot is started (send `/start` to bot)

**Check Logs**:
```bash
# Docker
docker compose logs backend | grep -i telegram

# Local
tail -f logs/app.log | grep -i telegram
```

### Invalid Bot Token

**Error**: "Unauthorized" or "Invalid token"

**Solution**:
1. Verify token from BotFather
2. Check for extra spaces in `.env`
3. Regenerate token if needed

### Chat ID Not Found

**Error**: "Chat not found"

**Solution**:
1. Start conversation with bot
2. Send message to bot
3. Get chat ID from: `https://api.telegram.org/bot<TOKEN>/getUpdates`
4. Update `TELEGRAM_CHAT_ID` in `.env`

### Notifications Delayed

**Problem**: Notifications arrive late

**Solutions**:
1. Check network connectivity
2. Verify Telegram API is accessible
3. Check application logs for errors
4. Consider using webhook instead of polling

### Testing Notifications

**Manual Test**:
```python
from app.services.notification_service import NotificationService

# Test notification
await NotificationService.send_client_registration_notification(
    first_name="Test",
    last_name="User",
    dni_number="1234567890",
    phone="+1234567890"
)
```

**Via API** (if endpoint exists):
```bash
curl -X POST http://localhost:8000/api/v1/test/notification \
  -H "Authorization: Bearer <token>"
```

## Best Practices

### 1. Message Formatting

- **Keep messages concise** but informative
- **Use emojis** for visual clarity
- **Include relevant data** (dates, amounts, names)
- **Format consistently** across notification types

### 2. Error Handling

- **Never raise exceptions** from notification code
- **Log errors** for debugging
- **Continue main operation** even if notification fails

### 3. Performance

- **Send asynchronously** to avoid blocking
- **Batch notifications** when possible
- **Rate limit** if sending many notifications

### 4. Security

- **Never log tokens** in plain text
- **Use environment variables** for secrets
- **Restrict bot access** to authorized chats only

## Advanced Configuration

### Multiple Chat IDs

To send to multiple chats, modify the handler:

```python
CHAT_IDS = [
    "123456789",  # Admin chat
    "987654321",  # Operations chat
]

for chat_id in CHAT_IDS:
    await self.send(message, chat_id=chat_id)
```

### Custom Message Templates

Edit `app/services/notifications/messages.py`:

```python
def format_subscription_message(data: dict) -> str:
    return f"""
📅 New Subscription

Client: {data['client_name']}
Plan: {data['plan_name']}
Dates: {data['start_date']} to {data['end_date']}
"""
```

### Notification Filtering

Add filtering logic to handlers:

```python
async def send_notification(self, data: dict):
    # Only send for premium plans
    if data.get('plan_type') != 'premium':
        return
    
    await self.send(format_message(data))
```

---

**Next**: [Configuration Guide](CONFIGURATION.md) | [API Documentation](API.md)

