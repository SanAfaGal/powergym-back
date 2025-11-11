# Correcciones Necesarias para las Pruebas

## Problemas Identificados

### 1. ProductService
- ❌ `update_stock()` no existe → Usar `add_stock()` y `remove_stock()`
- ❌ `get_low_stock_products()` no existe → Usar `get_low_stock_alerts()`

### 2. SubscriptionRepository
- ❌ `get_active_by_client_id()` → Usar `get_active_by_client()`
- ❌ `get_by_client_id()` → Usar `get_by_client()`
- ❌ `get_expired_subscriptions()` → Verificar si existe

### 3. PaymentRepository
- ❌ `get_by_subscription_id()` → Usar `get_by_subscription()`
- ❌ `get_statistics()` → No existe, usar métodos individuales

### 4. PaymentService
- ❌ `get_total_paid_by_subscription()` → No existe como método directo
- ❌ `get_remaining_debt()` → No existe como método directo
- ❌ `get_payment_statistics()` → Usar `get_subscription_payment_stats()`

### 5. SubscriptionService
- ❌ `get_subscription_by_id()` → No existe directamente
- Los mocks necesitan valores reales para Pydantic

### 6. Mocks de Pydantic
- Los mocks necesitan valores reales, no MagicMock para campos que Pydantic valida


