# Plan de Pruebas Sugeridas para PowerGym

Este documento detalla las pruebas que se recomienda implementar para mejorar la cobertura de testing del sistema PowerGym.

## 📊 Estado Actual de Pruebas

### ✅ Módulos con Pruebas Implementadas
- `UserService` - Pruebas básicas de CRUD
- `UserRepository` - Pruebas de acceso a datos
- `ClientService` - Pruebas de CRUD y validaciones
- `ClientRepository` - Pruebas de acceso a datos
- `FaceRecognitionService` - Pruebas básicas de reconocimiento facial

### ❌ Módulos sin Pruebas (Prioridad Alta)

---

## 1. Módulo de Asistencias (Attendance)

### 1.1. `test_attendance_service.py`

```python
# Pruebas para AttendanceService
- test_create_attendance_success()
- test_create_attendance_with_metadata()
- test_get_by_id_success()
- test_get_by_id_not_found()
- test_get_client_attendances_success()
- test_get_client_attendances_empty()
- test_get_all_attendances_with_filters()
- test_get_all_attendances_pagination()
- test_validate_client_access_active_subscription()
- test_validate_client_access_expired_subscription()
- test_validate_client_access_inactive_client()
- test_validate_client_access_no_subscription()
- test_validate_client_access_already_checked_in()
- test_validate_client_access_pending_payment()
- test_get_attendance_statistics_by_client()
- test_get_attendance_statistics_by_date_range()
```

### 1.2. `test_attendance_repository.py`

```python
# Pruebas para AttendanceRepository
- test_create_attendance()
- test_get_by_id_success()
- test_get_by_id_not_found()
- test_get_by_client_id_with_limit_offset()
- test_get_with_client_info()
- test_get_with_client_info_filtered_by_date()
- test_count_by_client_id()
- test_count_by_date_range()
- test_get_by_date_range()
- test_get_latest_attendance_by_client()
```

---

## 2. Módulo de Suscripciones (Subscriptions)

### 2.1. `test_subscription_service.py`

```python
# Pruebas para SubscriptionService
- test_create_subscription_success()
- test_create_subscription_with_custom_dates()
- test_get_by_id_success()
- test_get_by_id_not_found()
- test_get_by_client_id_active()
- test_get_by_client_id_all()
- test_update_subscription_status()
- test_calculate_end_date_daily()
- test_calculate_end_date_weekly()
- test_calculate_end_date_monthly()
- test_calculate_end_date_yearly()
- test_activate_subscription()
- test_expire_subscription()
- test_renew_subscription()
- test_cancel_subscription()
- test_get_expired_subscriptions()
- test_get_subscriptions_expiring_soon()
- test_validate_subscription_active()
- test_validate_subscription_expired()
- test_get_subscription_statistics()
```

### 2.2. `test_subscription_repository.py`

```python
# Pruebas para SubscriptionRepository
- test_create_subscription()
- test_get_by_id()
- test_get_by_client_id()
- test_get_active_by_client_id()
- test_get_by_status()
- test_get_expired_subscriptions()
- test_get_subscriptions_expiring_soon()
- test_update_subscription()
- test_update_status()
- test_count_by_client_id()
- test_count_by_status()
```

---

## 3. Módulo de Pagos (Payments)

### 3.1. `test_payment_service.py`

```python
# Pruebas para PaymentService
- test_create_payment_full()
- test_create_payment_partial()
- test_create_payment_multiple_partial()
- test_get_by_id_success()
- test_get_by_id_not_found()
- test_get_by_subscription_id()
- test_get_by_client_id()
- test_calculate_total_paid()
- test_calculate_remaining_debt()
- test_calculate_debt_percentage()
- test_validate_payment_amount()
- test_validate_payment_amount_exceeds_debt()
- test_validate_payment_method()
- test_get_payment_history()
- test_get_payment_statistics()
- test_apply_payment_to_subscription()
- test_apply_payment_to_multiple_subscriptions()
```

### 3.2. `test_payment_repository.py`

```python
# Pruebas para PaymentRepository
- test_create_payment()
- test_get_by_id()
- test_get_by_subscription_id()
- test_get_by_client_id()
- test_get_by_method()
- test_get_by_date_range()
- test_sum_by_subscription_id()
- test_sum_by_client_id()
- test_count_by_subscription_id()
- test_get_latest_payment_by_subscription()
```

---

## 4. Módulo de Planes (Plans)

### 4.1. `test_plan_service.py`

```python
# Pruebas para PlanService
- test_create_plan_success()
- test_create_plan_with_all_fields()
- test_get_by_id_success()
- test_get_by_id_not_found()
- test_get_all_plans()
- test_get_active_plans()
- test_update_plan_success()
- test_update_plan_not_found()
- test_delete_plan_success()
- test_delete_plan_with_active_subscriptions()
- test_validate_plan_duration()
- test_validate_plan_price()
- test_calculate_plan_price_by_duration()
- test_get_plan_statistics()
```

### 4.2. `test_plan_repository.py`

```python
# Pruebas para PlanRepository
- test_create_plan()
- test_get_by_id()
- test_get_all()
- test_get_active_plans()
- test_update_plan()
- test_delete_plan()
- test_count_plans()
- test_get_plans_by_duration_type()
```

---

## 5. Módulo de Inventario (Inventory)

### 5.1. `test_product_service.py`

```python
# Pruebas para ProductService
- test_create_product_success()
- test_create_product_with_all_fields()
- test_get_by_id_success()
- test_get_by_id_not_found()
- test_get_all_products()
- test_get_active_products()
- test_update_product_success()
- test_update_product_not_found()
- test_delete_product_success()
- test_update_stock_add()
- test_update_stock_subtract()
- test_update_stock_insufficient()
- test_calculate_stock_status_normal()
- test_calculate_stock_status_low()
- test_calculate_stock_status_out()
- test_calculate_stock_status_overstock()
- test_get_low_stock_products()
- test_get_out_of_stock_products()
- test_get_overstock_products()
- test_validate_product_data()
- test_get_product_statistics()
```

### 5.2. `test_movement_service.py`

```python
# Pruebas para MovementService
- test_create_entry_movement()
- test_create_exit_movement()
- test_get_movement_by_id()
- test_get_movements_by_product()
- test_get_movements_by_date_range()
- test_get_movements_by_type()
- test_validate_movement_quantity()
- test_validate_exit_movement_insufficient_stock()
- test_calculate_total_entries()
- test_calculate_total_exits()
- test_get_movement_statistics()
- test_get_sales_by_employee()
```

### 5.3. `test_product_repository.py`

```python
# Pruebas para ProductRepository
- test_create_product()
- test_get_by_id()
- test_get_all()
- test_get_active_products()
- test_update_product()
- test_update_stock()
- test_get_by_stock_status()
- test_get_low_stock_products()
- test_get_out_of_stock_products()
- test_count_products()
- test_count_by_status()
```

### 5.4. `test_movement_repository.py`

```python
# Pruebas para MovementRepository
- test_create_movement()
- test_get_by_id()
- test_get_by_product_id()
- test_get_by_type()
- test_get_by_date_range()
- test_get_by_employee()
- test_sum_entries_by_product()
- test_sum_exits_by_product()
- test_count_by_product()
- test_get_latest_movement_by_product()
```

---

## 6. Módulo de Recompensas (Rewards)

### 6.1. `test_reward_service.py`

```python
# Pruebas para RewardService
- test_create_reward_success()
- test_create_reward_automatic()
- test_get_by_id_success()
- test_get_by_id_not_found()
- test_get_by_client_id()
- test_get_pending_rewards()
- test_get_applied_rewards()
- test_get_expired_rewards()
- test_apply_reward_success()
- test_apply_reward_already_applied()
- test_apply_reward_expired()
- test_validate_reward_eligibility()
- test_calculate_reward_discount()
- test_expire_old_rewards()
- test_get_reward_statistics()
```

### 6.2. `test_reward_repository.py`

```python
# Pruebas para RewardRepository
- test_create_reward()
- test_get_by_id()
- test_get_by_client_id()
- test_get_by_status()
- test_get_pending_rewards()
- test_get_expired_rewards()
- test_update_reward()
- test_update_status()
- test_count_by_client_id()
- test_count_by_status()
```

---

## 7. Módulo de Estadísticas (Statistics)

### 7.1. `test_statistics_service.py`

```python
# Pruebas para StatisticsService
- test_get_dashboard_statistics()
- test_get_revenue_statistics()
- test_get_revenue_by_period()
- test_get_membership_statistics()
- test_get_new_clients_count()
- test_get_attendance_statistics()
- test_get_attendance_by_hour()
- test_get_attendance_by_day()
- test_get_attendance_by_week()
- test_get_inventory_statistics()
- test_get_inventory_value()
- test_get_sales_statistics()
- test_calculate_growth_rate()
- test_get_top_clients_by_attendance()
- test_get_subscription_status_distribution()
```

---

## 8. Módulo de Reconocimiento Facial (Face Recognition) - Ampliación

### 8.1. `test_embedding_service.py` (Ampliación)

```python
# Pruebas adicionales para EmbeddingService
- test_extract_face_encoding_valid_image()
- test_extract_face_encoding_no_face()
- test_extract_face_encoding_multiple_faces()
- test_extract_face_encoding_blurry_image()
- test_compare_embeddings_identical()
- test_compare_embeddings_similar()
- test_compare_embeddings_different()
- test_compare_embeddings_different_dimensions()
- test_validate_embedding_valid()
- test_validate_embedding_wrong_dimensions()
- test_parse_embedding_from_list()
- test_parse_embedding_from_numpy()
- test_parse_embedding_from_string()
- test_parse_embedding_from_json_string()
- test_calculate_cosine_similarity()
- test_calculate_euclidean_distance()
- test_get_face_quality_score_good()
- test_get_face_quality_score_poor()
- test_extract_multiple_faces()
- test_find_best_match()
- test_find_best_match_no_match()
```

### 8.2. `test_image_processor.py` (Nuevo)

```python
# Pruebas para ImageProcessor
- test_decode_base64_image_valid()
- test_decode_base64_image_invalid()
- test_decode_base64_image_empty()
- test_create_thumbnail_valid()
- test_create_thumbnail_dimensions()
- test_create_thumbnail_compression()
- test_validate_image_format()
- test_validate_image_size()
- test_compress_image()
- test_resize_image()
- test_convert_rgb_to_bgr()
```

### 8.3. `test_face_database.py` (Nuevo)

```python
# Pruebas para FaceDatabase
- test_store_face_biometric_success()
- test_store_face_biometric_update_existing()
- test_get_all_active_face_biometrics()
- test_search_similar_faces_found()
- test_search_similar_faces_not_found()
- test_search_similar_faces_with_limit()
- test_search_similar_faces_distance_threshold()
- test_get_client_info_found()
- test_get_client_info_not_found()
- test_get_client_info_inactive()
- test_deactivate_face_biometric_success()
- test_deactivate_face_biometric_not_found()
- test_encryption_of_thumbnail()
```

### 8.4. `test_biometric_repository.py` (Nuevo)

```python
# Pruebas para BiometricRepository
- test_create_biometric()
- test_get_by_id()
- test_get_by_client_id()
- test_get_by_type()
- test_get_active_by_client_id()
- test_search_similar_embeddings()
- test_search_similar_embeddings_with_limit()
- test_search_similar_embeddings_threshold()
- test_update_biometric()
- test_deactivate_biometric()
- test_count_by_client_id()
- test_count_by_type()
```

---

## 9. Módulo de Notificaciones (Notifications)

### 9.1. `test_notification_service.py` (Nuevo)

```python
# Pruebas para NotificationService
- test_send_check_in_notification_success()
- test_send_check_in_notification_telegram_disabled()
- test_send_check_in_notification_telegram_error()
- test_send_notification_with_valid_data()
- test_send_notification_with_invalid_token()
- test_format_check_in_message()
- test_send_notification_async()
```

---

## 10. Pruebas de Integración (API Endpoints)

### 10.1. `test_api_auth.py` (Nuevo)

```python
# Pruebas de integración para endpoints de autenticación
- test_login_success()
- test_login_invalid_credentials()
- test_login_disabled_user()
- test_refresh_token_success()
- test_refresh_token_invalid()
- test_refresh_token_expired()
- test_get_current_user_success()
- test_get_current_user_invalid_token()
- test_get_current_user_expired_token()
```

### 10.2. `test_api_face_recognition.py` (Nuevo)

```python
# Pruebas de integración para endpoints de reconocimiento facial
- test_register_face_success()
- test_register_face_invalid_image()
- test_register_face_no_face_detected()
- test_authenticate_face_success()
- test_authenticate_face_not_found()
- test_compare_faces_success()
- test_compare_faces_different()
- test_delete_face_success()
- test_delete_face_not_found()
```

### 10.3. `test_api_attendances.py` (Nuevo)

```python
# Pruebas de integración para endpoints de asistencias
- test_check_in_success()
- test_check_in_no_face_detected()
- test_check_in_face_not_recognized()
- test_check_in_expired_subscription()
- test_check_in_inactive_client()
- test_check_in_already_checked_in()
- test_get_attendances_success()
- test_get_attendances_with_filters()
- test_get_client_attendances_success()
```

### 10.4. `test_api_clients.py` (Nuevo)

```python
# Pruebas de integración para endpoints de clientes
- test_create_client_success()
- test_create_client_duplicate_dni()
- test_get_client_by_id_success()
- test_get_client_by_id_not_found()
- test_update_client_success()
- test_delete_client_success()
- test_get_all_clients()
- test_search_clients()
```

### 10.5. `test_api_subscriptions.py` (Nuevo)

```python
# Pruebas de integración para endpoints de suscripciones
- test_create_subscription_success()
- test_get_subscription_by_id()
- test_get_subscriptions_by_client()
- test_update_subscription()
- test_cancel_subscription()
- test_get_active_subscriptions()
```

### 10.6. `test_api_payments.py` (Nuevo)

```python
# Pruebas de integración para endpoints de pagos
- test_create_payment_success()
- test_create_payment_partial()
- test_get_payments_by_subscription()
- test_get_payments_by_client()
- test_get_payment_statistics()
```

### 10.7. `test_api_inventory.py` (Nuevo)

```python
# Pruebas de integración para endpoints de inventario
- test_create_product_success()
- test_update_product_stock()
- test_create_movement_entry()
- test_create_movement_exit()
- test_get_low_stock_products()
- test_get_inventory_reports()
```

---

## 11. Pruebas de Utilidades (Utils)

### 11.1. `test_encryption_service.py` (Nuevo)

```python
# Pruebas para EncryptionService
- test_encrypt_image_data()
- test_decrypt_image_data()
- test_encrypt_decrypt_roundtrip()
- test_encrypt_different_data()
- test_encryption_key_validation()
```

### 11.2. `test_compression_service.py` (Nuevo)

```python
# Pruebas para CompressionService
- test_compress_image()
- test_compress_image_quality()
- test_decompress_image()
- test_compress_decompress_roundtrip()
- test_compression_ratio()
```

### 11.3. `test_attendance_utils.py` (Nuevo)

```python
# Pruebas para utilidades de asistencia
- test_validate_client_access_all_valid()
- test_format_access_denial_message()
- test_check_duplicate_check_in()
```

### 11.4. `test_subscription_utils.py` (Nuevo)

```python
# Pruebas para utilidades de suscripción
- test_calculate_end_date()
- test_validate_subscription_dates()
- test_check_subscription_status()
```

### 11.5. `test_payment_utils.py` (Nuevo)

```python
# Pruebas para utilidades de pago
- test_validate_payment_amount()
- test_calculate_debt()
- test_format_payment_data()
```

### 11.6. `test_client_utils.py` (Nuevo)

```python
# Pruebas para utilidades de cliente
- test_validate_client_data()
- test_format_client_name()
- test_validate_dni()
```

---

## 12. Pruebas de Middleware

### 12.1. `test_middleware.py` (Nuevo)

```python
# Pruebas para middleware
- test_cors_middleware()
- test_compression_middleware()
- test_logging_middleware()
- test_rate_limiting_middleware()
- test_error_handler_middleware()
```

---

## 📋 Priorización de Implementación

### Fase 1 - Crítico (Implementar Primero)
1. ✅ `test_attendance_service.py` - Flujo crítico de check-in
2. ✅ `test_subscription_service.py` - Validación de acceso
3. ✅ `test_payment_service.py` - Cálculos financieros
4. ✅ `test_api_attendances.py` - Integración crítica
5. ✅ `test_face_database.py` - Búsqueda vectorial

### Fase 2 - Importante
6. `test_plan_service.py` - Gestión de planes
7. `test_product_service.py` - Inventario
8. `test_reward_service.py` - Sistema de recompensas
9. `test_api_face_recognition.py` - Integración facial
10. `test_embedding_service.py` - Ampliación

### Fase 3 - Complementario
11. `test_statistics_service.py` - Reportes
12. `test_notification_service.py` - Notificaciones
13. `test_api_subscriptions.py` - Integración suscripciones
14. `test_api_payments.py` - Integración pagos
15. Pruebas de utilidades

### Fase 4 - Mejoras
16. Pruebas de middleware
17. Pruebas de rendimiento
18. Pruebas de carga
19. Pruebas de seguridad

---

## 🎯 Criterios de Éxito

Para cada módulo, las pruebas deben cubrir:

1. **Casos Exitosos**: Operaciones válidas que retornan resultados esperados
2. **Casos de Error**: Manejo de errores y validaciones
3. **Casos Límite**: Valores extremos, null, empty, etc.
4. **Validaciones de Negocio**: Reglas de negocio específicas
5. **Integridad de Datos**: Transacciones y consistencia
6. **Performance**: Tiempos de respuesta aceptables

---

## 📝 Notas de Implementación

1. **Usar fixtures de conftest.py** para setup común
2. **Mockear dependencias externas** (InsightFace, Telegram, etc.)
3. **Usar base de datos de prueba** (SQLite in-memory)
4. **Aislar pruebas** - cada test debe ser independiente
5. **Usar parámetros** para tests repetitivos (`@pytest.mark.parametrize`)
6. **Documentar casos de prueba** con docstrings
7. **Mantener código DRY** - crear helpers y fixtures reutilizables

---

## 🔧 Herramientas Recomendadas

- **pytest**: Framework de testing
- **pytest-cov**: Cobertura de código
- **pytest-mock**: Mocks avanzados
- **pytest-asyncio**: Pruebas asíncronas
- **faker**: Generación de datos de prueba
- **factory-boy**: Factories para modelos de prueba

---

**Última actualización**: Generado basado en análisis del código fuente de PowerGym v2


