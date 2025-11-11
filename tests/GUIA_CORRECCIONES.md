# Guía de Correcciones para Pruebas

## Resumen de Problemas y Soluciones

### 1. **test_product_service.py**

**Problemas:**
- `update_stock()` no existe → Usar `add_stock()` o `remove_stock()`
- `get_low_stock_products()` no existe → Usar `get_low_stock_alerts()`
- Los mocks necesitan valores reales para Pydantic

**Solución:**
```python
# ❌ INCORRECTO
service.update_stock(product_id, 20)

# ✅ CORRECTO
service.add_stock(product_id, Decimal('20'))
```

### 2. **test_subscription_service.py**

**Problemas:**
- `get_active_by_client_id()` → Usar `get_active_by_client()` (retorna lista)
- `get_subscription_by_id()` no existe → Usar directamente `SubscriptionRepository.get_by_id()`
- `SubscriptionRenew` requiere `client_id` y `subscription_id`
- `SubscriptionCancel` requiere `subscription_id`
- Los mocks necesitan valores reales para `Subscription.from_orm()`

**Solución:**
```python
# Mock completo para Subscription.from_orm
mock_subscription = MagicMock()
mock_subscription.id = uuid4()
mock_subscription.client_id = client_id
mock_subscription.plan_id = plan_id
mock_subscription.start_date = date.today()
mock_subscription.end_date = date.today() + timedelta(days=30)
mock_subscription.status = SubscriptionStatusEnum.PENDING_PAYMENT
mock_subscription.cancellation_date = None  # Importante!
mock_subscription.cancellation_reason = None  # Importante!
mock_subscription.final_price = None
mock_subscription.created_at = datetime.now()
mock_subscription.updated_at = datetime.now()
mock_subscription.meta_info = {}
```

### 3. **test_subscription_repository.py**

**Problemas:**
- `get_by_client_id()` → Usar `get_by_client()`
- `get_active_by_client_id()` → Usar `get_active_by_client()`
- `get_expired_subscriptions()` → Verificar si existe en el repositorio
- Los mocks de SQLAlchemy 2.0 necesitan estructura diferente

**Solución:**
```python
# Para métodos que usan db.query()
mock_db.query.return_value.filter.return_value.first.return_value = expected
```

### 4. **test_attendance_repository.py**

**Problemas:**
- `get_latest_by_client_id_today()` → Verificar nombre real
- `count_by_client_id()` → Verificar nombre real
- Los mocks de SQLAlchemy necesitan ajuste

### 5. **test_attendance_service_example.py**

**Problemas:**
- Imports incorrectos: `app.services.attendance_service.ClientRepository` → `app.repositories.client_repository.ClientRepository`

### 6. **test_api_face_recognition.py**

**Problemas:**
- Los endpoints necesitan rutas correctas
- Los mocks de autenticación necesitan ajuste

### 7. **test_face_service.py**

**Problemas:**
- Los embeddings deben ser de 512 dimensiones, no 128

**Solución:**
```python
# ❌ INCORRECTO
e1 = np.array([0.1] * 128)

# ✅ CORRECTO
e1 = np.array([0.1] * 512)
```

## Recomendaciones

1. **Revisar la implementación real** antes de escribir pruebas
2. **Usar valores reales en mocks** cuando Pydantic valida
3. **Verificar nombres de métodos** en repositorios y servicios
4. **Ajustar mocks de SQLAlchemy** según versión (1.x vs 2.x)

## Prioridad de Corrección

1. **Alta**: test_subscription_service.py, test_product_service.py
2. **Media**: test_payment_service.py, test_subscription_repository.py
3. **Baja**: test_api_face_recognition.py, test_attendance_repository.py


