# 📋 Documentación de Pruebas - PowerGym

Este documento contiene la documentación completa de todas las pruebas implementadas en el proyecto PowerGym, siguiendo el formato estándar de documentación de pruebas.

---

## 🔹 Módulo: ClientRepository

### REPCLI-001: Crear cliente en base de datos
**Tipo:** Unitario (Repositorio)  
**Precondiciones:** Sesión mockeada correctamente  
**Pasos:** Llamar a `ClientRepository.create` con datos válidos  
**Resultado Esperado:** Retorna el objeto cliente creado  
**Resultado Obtenido:** El mock devolvió correctamente el cliente con los datos esperados  
**Estado:** ✅ Aprobado

### REPCLI-002: Obtener cliente existente por ID
**Tipo:** Unitario (Repositorio)  
**Precondiciones:** Cliente existente en base de datos simulada  
**Pasos:** Llamar a `ClientRepository.get_by_id` con ID válido  
**Resultado Esperado:** Retorna el cliente correspondiente  
**Resultado Obtenido:** Cliente recuperado exitosamente con ID y datos correctos  
**Estado:** ✅ Aprobado

### REPCLI-003: Actualizar cliente existente
**Tipo:** Unitario (Repositorio)  
**Precondiciones:** Cliente existente en base de datos simulada  
**Pasos:** Llamar a `ClientRepository.update` con ID válido y datos a actualizar  
**Resultado Esperado:** Retorna el cliente actualizado  
**Resultado Obtenido:** Cliente actualizado correctamente, se verificó commit y refresh  
**Estado:** ✅ Aprobado

### REPCLI-004: Intentar actualizar cliente inexistente
**Tipo:** Unitario (Repositorio)  
**Precondiciones:** Cliente no existe en base de datos simulada  
**Pasos:** Llamar a `ClientRepository.update` con ID inexistente  
**Resultado Esperado:** Retorna None  
**Resultado Obtenido:** El método retornó None correctamente  
**Estado:** ✅ Aprobado

### REPCLI-005: Eliminar cliente existente
**Tipo:** Unitario (Repositorio)  
**Precondiciones:** Cliente existente en base de datos simulada  
**Pasos:** Llamar a `ClientRepository.delete` con ID válido  
**Resultado Esperado:** Retorna True y se ejecuta commit  
**Resultado Obtenido:** Eliminación exitosa, commit verificado  
**Estado:** ✅ Aprobado

### REPCLI-006: Eliminar cliente inexistente
**Tipo:** Unitario (Repositorio)  
**Precondiciones:** Cliente no existe en base de datos simulada  
**Pasos:** Llamar a `ClientRepository.delete` con ID inexistente  
**Resultado Esperado:** Retorna False  
**Resultado Obtenido:** El método retornó False correctamente  
**Estado:** ✅ Aprobado

---

## 🔹 Módulo: ClientService

### CLI-001: Crear cliente exitosamente
**Tipo:** Unitario (Servicio)  
**Precondiciones:** El repositorio devuelve un cliente válido al crear  
**Pasos:** Llamar a `ClientService.create_client` con datos válidos  
**Resultado Esperado:** Retorna un objeto Client con datos válidos  
**Resultado Obtenido:** Cliente creado exitosamente con todos los campos correctos  
**Estado:** ✅ Aprobado

### CLI-002: Obtener cliente por ID existente
**Tipo:** Unitario (Servicio)  
**Precondiciones:** El cliente existe en la base de datos simulada  
**Pasos:** Llamar a `ClientService.get_client_by_id` con ID válido  
**Resultado Esperado:** Retorna el cliente correspondiente  
**Resultado Obtenido:** Cliente recuperado exitosamente con ID y datos correctos  
**Estado:** ✅ Aprobado

### CLI-003: Actualizar cliente exitosamente
**Tipo:** Unitario (Servicio)  
**Precondiciones:** Cliente existente  
**Pasos:** Llamar a `ClientService.update_client` con datos válidos  
**Resultado Esperado:** Retorna el cliente actualizado  
**Resultado Obtenido:** Cliente actualizado correctamente con los nuevos datos  
**Estado:** ✅ Aprobado

### CLI-004: Eliminar cliente exitosamente
**Tipo:** Unitario (Servicio)  
**Precondiciones:** Cliente existente en el repositorio simulado  
**Pasos:** Llamar a `ClientService.delete_client` con un ID válido  
**Resultado Esperado:** Retorna True  
**Resultado Obtenido:** Eliminación exitosa, retornó True  
**Estado:** ✅ Aprobado

### CLI-005: Fallo al crear cliente
**Tipo:** Unitario (Servicio)  
**Precondiciones:** El repositorio lanza una excepción  
**Pasos:** Llamar a `ClientService.create_client` con datos que causen error  
**Resultado Esperado:** Lanza una excepción  
**Resultado Obtenido:** Excepción capturada correctamente con mensaje de error  
**Estado:** ✅ Aprobado

### CLI-006: Obtener cliente inexistente
**Tipo:** Unitario (Servicio)  
**Precondiciones:** El repositorio devuelve None  
**Pasos:** Llamar a `ClientService.get_client_by_id` con ID inexistente  
**Resultado Esperado:** Retorna None  
**Resultado Obtenido:** El método retornó None correctamente  
**Estado:** ✅ Aprobado

### CLI-007: Fallo al actualizar cliente inexistente
**Tipo:** Unitario (Servicio)  
**Precondiciones:** Cliente no existe  
**Pasos:** Llamar a `ClientService.update_client` con ID inválido  
**Resultado Esperado:** Retorna None  
**Resultado Obtenido:** El método retornó None correctamente  
**Estado:** ✅ Aprobado

### CLI-008: Fallo al eliminar cliente
**Tipo:** Unitario (Servicio)  
**Precondiciones:** El repositorio lanza una excepción  
**Pasos:** Llamar a `ClientService.delete_client` con ID que causa error  
**Resultado Esperado:** Lanza una excepción  
**Resultado Obtenido:** Excepción capturada correctamente con mensaje de error  
**Estado:** ✅ Aprobado

---

## 🔹 Módulo: UserRepository

### REPUSR-001: Crear usuario en base de datos
**Tipo:** Unitario (Repositorio)  
**Precondiciones:** Sesión mockeada correctamente  
**Pasos:** Llamar a `UserRepository.create` con datos válidos  
**Resultado Esperado:** Retorna el objeto usuario creado  
**Resultado Obtenido:** Usuario creado exitosamente, se verificó add y commit  
**Estado:** ✅ Aprobado

### REPUSR-002: Obtener usuario existente por username
**Tipo:** Unitario (Repositorio)  
**Precondiciones:** Usuario existente en base de datos simulada  
**Pasos:** Llamar a `UserRepository.get_by_username` con username válido  
**Resultado Esperado:** Retorna el usuario correspondiente  
**Resultado Obtenido:** Usuario recuperado exitosamente con username correcto  
**Estado:** ✅ Aprobado

### REPUSR-003: Obtener usuario por email
**Tipo:** Unitario (Repositorio)  
**Precondiciones:** Usuario existente en base de datos simulada  
**Pasos:** Llamar a `UserRepository.get_by_email` con email válido  
**Resultado Esperado:** Retorna el usuario correspondiente  
**Resultado Obtenido:** Usuario recuperado exitosamente con email correcto  
**Estado:** ✅ Aprobado

### REPUSR-004: Actualizar usuario existente
**Tipo:** Unitario (Repositorio)  
**Precondiciones:** Usuario existente en base de datos simulada  
**Pasos:** Llamar a `UserRepository.update` con username válido y datos a actualizar  
**Resultado Esperado:** Retorna el usuario actualizado  
**Resultado Obtenido:** Usuario actualizado correctamente, se verificó commit  
**Estado:** ✅ Aprobado

### REPUSR-005: Actualizar usuario inexistente
**Tipo:** Unitario (Repositorio)  
**Precondiciones:** Usuario no existe en base de datos simulada  
**Pasos:** Llamar a `UserRepository.update` con username inexistente  
**Resultado Esperado:** Retorna None  
**Resultado Obtenido:** El método retornó None correctamente  
**Estado:** ✅ Aprobado

### REPUSR-006: Eliminar usuario existente
**Tipo:** Unitario (Repositorio)  
**Precondiciones:** Usuario existente en base de datos simulada  
**Pasos:** Llamar a `UserRepository.delete` con username válido  
**Resultado Esperado:** Retorna True y se ejecuta delete y commit  
**Resultado Obtenido:** Eliminación exitosa, delete y commit verificados  
**Estado:** ✅ Aprobado

### REPUSR-007: Eliminar usuario inexistente
**Tipo:** Unitario (Repositorio)  
**Precondiciones:** Usuario no existe en base de datos simulada  
**Pasos:** Llamar a `UserRepository.delete` con username inexistente  
**Resultado Esperado:** Retorna False  
**Resultado Obtenido:** El método retornó False correctamente  
**Estado:** ✅ Aprobado

---

## 🔹 Módulo: UserService

### SRVUSR-001: Crear usuario exitosamente
**Tipo:** Unitario (Servicio)  
**Precondiciones:** Repositorio mockeado correctamente  
**Pasos:** Llamar a `UserService.create_user` con datos válidos  
**Resultado Esperado:** Retorna el usuario creado con password hasheado  
**Resultado Obtenido:** Usuario creado exitosamente con hash de password aplicado  
**Estado:** ✅ Aprobado

### SRVUSR-002: Fallo al crear usuario
**Tipo:** Unitario (Servicio)  
**Precondiciones:** El repositorio lanza una excepción  
**Pasos:** Llamar a `UserService.create_user` con datos que causen error  
**Resultado Esperado:** Lanza una excepción  
**Resultado Obtenido:** Excepción capturada correctamente con mensaje de error  
**Estado:** ✅ Aprobado

### SRVUSR-003: Obtener usuario por username
**Tipo:** Unitario (Servicio)  
**Precondiciones:** Usuario existente en base de datos simulada  
**Pasos:** Llamar a `UserService.get_user_by_username` con username válido  
**Resultado Esperado:** Retorna el usuario correspondiente  
**Resultado Obtenido:** Usuario recuperado exitosamente con username y email correctos  
**Estado:** ✅ Aprobado

### SRVUSR-004: Obtener usuario por email
**Tipo:** Unitario (Servicio)  
**Precondiciones:** Usuario existente en base de datos simulada  
**Pasos:** Llamar a `UserService.get_user_by_email` con email válido  
**Resultado Esperado:** Retorna el usuario correspondiente  
**Resultado Obtenido:** Usuario recuperado exitosamente con email correcto  
**Estado:** ✅ Aprobado

### SRVUSR-005: Obtener usuario inexistente
**Tipo:** Unitario (Servicio)  
**Precondiciones:** El repositorio devuelve None  
**Pasos:** Llamar a `UserService.get_user_by_username` con username inexistente  
**Resultado Esperado:** Retorna None  
**Resultado Obtenido:** El método retornó None correctamente  
**Estado:** ✅ Aprobado

### SRVUSR-006: Actualizar usuario exitosamente
**Tipo:** Unitario (Servicio)  
**Precondiciones:** Usuario existente en base de datos simulada  
**Pasos:** Llamar a `UserService.update_user` con username válido y datos a actualizar  
**Resultado Esperado:** Retorna el usuario actualizado  
**Resultado Obtenido:** Usuario actualizado correctamente con los nuevos datos  
**Estado:** ✅ Aprobado

### SRVUSR-007: Intentar actualizar usuario inexistente
**Tipo:** Unitario (Servicio)  
**Precondiciones:** Usuario no existe  
**Pasos:** Llamar a `UserService.update_user` con username inexistente  
**Resultado Esperado:** Retorna None  
**Resultado Obtenido:** El método retornó None correctamente  
**Estado:** ✅ Aprobado

### SRVUSR-008: Eliminar usuario exitosamente
**Tipo:** Unitario (Servicio)  
**Precondiciones:** Usuario existente en base de datos simulada  
**Pasos:** Llamar a `UserService.delete_user` con username válido  
**Resultado Esperado:** Retorna True  
**Resultado Obtenido:** Eliminación exitosa, retornó True  
**Estado:** ✅ Aprobado

### SRVUSR-009: Eliminar usuario inexistente
**Tipo:** Unitario (Servicio)  
**Precondiciones:** Usuario no existe  
**Pasos:** Llamar a `UserService.delete_user` con username inexistente  
**Resultado Esperado:** Retorna False  
**Resultado Obtenido:** El método retornó False correctamente  
**Estado:** ✅ Aprobado

---

## 🔹 Módulo: FaceRecognition (FaceRecognitionService)

### FACE-001: Extraer encoding de rostro
**Tipo:** Unitario (Servicio)  
**Precondiciones:** Imagen válida con rostro detectable  
**Pasos:** Llamar a `FaceRecognitionService.extract_face_encoding` con imagen válida  
**Resultado Esperado:** Retorna un embedding válido de 512 dimensiones y thumbnail  
**Resultado Obtenido:** Embedding extraído correctamente con 512 dimensiones  
**Estado:** ✅ Aprobado

### FACE-002: Comparar rostros idénticos
**Tipo:** Unitario (Servicio)  
**Precondiciones:** Dos embeddings idénticos  
**Pasos:** Llamar a `FaceRecognitionService.compare_faces` con embeddings idénticos  
**Resultado Esperado:** Retorna True (match) y una distancia válida  
**Resultado Obtenido:** Match detectado correctamente, distancia calculada  
**Estado:** ✅ Aprobado

### FACE-003: Registrar rostro exitosamente
**Tipo:** Unitario (Servicio)  
**Precondiciones:** Imagen válida con rostro, cliente existente  
**Pasos:** Llamar a `FaceRecognitionService.register_face` con imagen base64 válida  
**Resultado Esperado:** Retorna dict con success=True y biometric_id  
**Resultado Obtenido:** Rostro registrado exitosamente en la base de datos  
**Estado:** ✅ Aprobado

### FACE-004: Fallo con imagen inválida
**Tipo:** Unitario (Servicio)  
**Precondiciones:** Imagen inválida o None  
**Pasos:** Llamar a `FaceRecognitionService.extract_face_encoding` con imagen inválida  
**Resultado Esperado:** Lanza ValueError, AttributeError o Exception  
**Resultado Obtenido:** Excepción capturada correctamente  
**Estado:** ✅ Aprobado

### FACE-005: Comparar rostros diferentes
**Tipo:** Unitario (Servicio)  
**Precondiciones:** Dos embeddings diferentes  
**Pasos:** Llamar a `FaceRecognitionService.compare_faces` con embeddings distintos  
**Resultado Esperado:** Retorna False (no match) y una distancia válida  
**Resultado Obtenido:** No match detectado correctamente, distancia calculada  
**Estado:** ✅ Aprobado

### FACE-006: Fallo en registro por error BD
**Tipo:** Unitario (Servicio)  
**Precondiciones:** Error de base de datos simulado  
**Pasos:** Llamar a `FaceRecognitionService.register_face` con datos que causen error BD  
**Resultado Esperado:** Retorna dict con success=False y mensaje de error  
**Resultado Obtenido:** Error de BD manejado correctamente, retornó success=False  
**Estado:** ✅ Aprobado

### FACE-007: Embeddings de tamaño diferente
**Tipo:** Unitario (Servicio)  
**Precondiciones:** Embeddings con dimensiones incompatibles  
**Pasos:** Llamar a `FaceRecognitionService.compare_faces` con embeddings de tamaño diferente  
**Resultado Esperado:** Lanza ValueError, TypeError o Exception  
**Resultado Obtenido:** Excepción capturada correctamente  
**Estado:** ✅ Aprobado

### FACE-008: No se detecta rostro en imagen
**Tipo:** Unitario (Servicio)  
**Precondiciones:** Imagen sin rostro detectable  
**Pasos:** Llamar a `FaceRecognitionService.extract_face_encoding` con imagen sin rostro  
**Resultado Esperado:** Retorna None  
**Resultado Obtenido:** El método retornó None correctamente cuando no hay rostro  
**Estado:** ✅ Aprobado

---

## 🔹 Módulo: AttendanceRepository

### REPATT-001: Crear registro de asistencia en base de datos
**Tipo:** Unitario (Repositorio)  
**Precondiciones:** Sesión mockeada correctamente  
**Pasos:** Llamar a `AttendanceRepository.create` con client_id y meta_info válidos  
**Resultado Esperado:** Retorna el objeto asistencia creado  
**Resultado Obtenido:** Asistencia creada exitosamente, se verificó add y commit  
**Estado:** ✅ Aprobado

### REPATT-002: Obtener asistencia existente por ID
**Tipo:** Unitario (Repositorio)  
**Precondiciones:** Asistencia existente en base de datos simulada  
**Pasos:** Llamar a `AttendanceRepository.get_by_id` con ID válido  
**Resultado Esperado:** Retorna la asistencia correspondiente  
**Resultado Obtenido:** Asistencia recuperada exitosamente con ID correcto  
**Estado:** ✅ Aprobado

### REPATT-003: Obtener asistencias por cliente
**Tipo:** Unitario (Repositorio)  
**Precondiciones:** Asistencias existentes para el cliente  
**Pasos:** Llamar a `AttendanceRepository.get_by_client_id` con client_id válido  
**Resultado Esperado:** Retorna lista de asistencias del cliente  
**Resultado Obtenido:** Lista de asistencias recuperada correctamente  
**Estado:** ✅ Aprobado

### REPATT-004: Obtener asistencias con información de cliente
**Tipo:** Unitario (Repositorio)  
**Precondiciones:** Asistencias existentes con clientes asociados  
**Pasos:** Llamar a `AttendanceRepository.get_with_client_info` con filtros opcionales  
**Resultado Esperado:** Retorna lista de tuplas (AttendanceModel, first_name, last_name, dni_number)  
**Resultado Obtenido:** Datos recuperados correctamente con información de cliente  
**Estado:** ✅ Aprobado

### REPATT-005: Obtener asistencias con información de cliente y filtros de fecha
**Tipo:** Unitario (Repositorio)  
**Precondiciones:** Asistencias existentes en rango de fechas  
**Pasos:** Llamar a `AttendanceRepository.get_with_client_info` con start_date y end_date  
**Resultado Esperado:** Retorna lista filtrada por fechas  
**Resultado Obtenido:** Filtrado por fechas funcionó correctamente  
**Estado:** ✅ Aprobado

### REPATT-006: Obtener asistencia de hoy
**Tipo:** Unitario (Repositorio)  
**Precondiciones:** Asistencia existente para hoy  
**Pasos:** Llamar a `AttendanceRepository.get_today_attendance` con client_id válido  
**Resultado Esperado:** Retorna la asistencia de hoy o None  
**Resultado Obtenido:** Asistencia de hoy recuperada correctamente  
**Estado:** ✅ Aprobado

### REPATT-007: Obtener asistencia de hoy sin registro
**Tipo:** Unitario (Repositorio)  
**Precondiciones:** No hay asistencia para hoy  
**Pasos:** Llamar a `AttendanceRepository.get_today_attendance` con client_id válido  
**Resultado Esperado:** Retorna None  
**Resultado Obtenido:** El método retornó None correctamente  
**Estado:** ✅ Aprobado

### REPATT-008: Obtener asistencia inexistente por ID
**Tipo:** Unitario (Repositorio)  
**Precondiciones:** Asistencia no existe  
**Pasos:** Llamar a `AttendanceRepository.get_by_id` con ID inexistente  
**Resultado Esperado:** Retorna None  
**Resultado Obtenido:** El método retornó None correctamente  
**Estado:** ✅ Aprobado

---

## 🔹 Módulo: AttendanceService

### ATT-001: Crear asistencia exitosamente
**Tipo:** Unitario (Servicio)  
**Precondiciones:** Cliente existente, repositorio mockeado  
**Pasos:** Llamar a `AttendanceService.create_attendance` con client_id válido  
**Resultado Esperado:** Retorna AttendanceResponse con datos correctos  
**Resultado Obtenido:** Asistencia creada exitosamente, notificación enviada  
**Estado:** ✅ Aprobado

### ATT-002: Obtener asistencia por ID existente
**Tipo:** Unitario (Servicio)  
**Precondiciones:** Asistencia existente en base de datos simulada  
**Pasos:** Llamar a `AttendanceService.get_by_id` con ID válido  
**Resultado Esperado:** Retorna AttendanceResponse correspondiente  
**Resultado Obtenido:** Asistencia recuperada exitosamente con ID correcto  
**Estado:** ✅ Aprobado

### ATT-003: Obtener asistencias de un cliente
**Tipo:** Unitario (Servicio)  
**Precondiciones:** Asistencias existentes para el cliente  
**Pasos:** Llamar a `AttendanceService.get_client_attendances` con client_id válido  
**Resultado Esperado:** Retorna lista de AttendanceResponse  
**Resultado Obtenido:** Lista de asistencias recuperada correctamente  
**Estado:** ✅ Aprobado

### ATT-004: Validar acceso con suscripción activa
**Tipo:** Unitario (Servicio)  
**Precondiciones:** Cliente activo con suscripción activa, sin asistencia hoy  
**Pasos:** Llamar a `AttendanceService.validate_client_access` con client_id válido  
**Resultado Esperado:** Retorna (True, None, detalles)  
**Resultado Obtenido:** Acceso permitido correctamente  
**Estado:** ✅ Aprobado

### ATT-005: Validar acceso con suscripción expirada
**Tipo:** Unitario (Servicio)  
**Precondiciones:** Cliente activo con suscripción expirada  
**Pasos:** Llamar a `AttendanceService.validate_client_access` con client_id válido  
**Resultado Esperado:** Retorna (False, AccessDenialReason.SUBSCRIPTION_EXPIRED, detalles)  
**Resultado Obtenido:** Acceso denegado correctamente por suscripción expirada  
**Estado:** ✅ Aprobado

### ATT-006: Validar acceso con cliente inactivo
**Tipo:** Unitario (Servicio)  
**Precondiciones:** Cliente inactivo  
**Pasos:** Llamar a `AttendanceService.validate_client_access` con client_id inactivo  
**Resultado Esperado:** Retorna (False, AccessDenialReason.INACTIVE_CLIENT, detalles)  
**Resultado Obtenido:** Acceso denegado correctamente por cliente inactivo  
**Estado:** ✅ Aprobado

### ATT-007: Validar acceso sin suscripción
**Tipo:** Unitario (Servicio)  
**Precondiciones:** Cliente activo sin suscripción  
**Pasos:** Llamar a `AttendanceService.validate_client_access` con client_id sin suscripción  
**Resultado Esperado:** Retorna (False, AccessDenialReason.NO_SUBSCRIPTION, detalles)  
**Resultado Obtenido:** Acceso denegado correctamente por falta de suscripción  
**Estado:** ✅ Aprobado

### ATT-008: Validar acceso ya registrado hoy
**Tipo:** Unitario (Servicio)  
**Precondiciones:** Cliente con asistencia registrada hoy  
**Pasos:** Llamar a `AttendanceService.validate_client_access` con client_id que ya tiene asistencia hoy  
**Resultado Esperado:** Retorna (False, AccessDenialReason.ALREADY_CHECKED_IN, detalles)  
**Resultado Obtenido:** Acceso denegado correctamente por ya estar registrado  
**Estado:** ✅ Aprobado

### ATT-009: Validar acceso con suscripción pendiente de pago
**Tipo:** Unitario (Servicio)  
**Precondiciones:** Cliente con suscripción expirada  
**Pasos:** Llamar a `AttendanceService.validate_client_access` con client_id con suscripción expirada  
**Resultado Esperado:** Retorna (False, AccessDenialReason.SUBSCRIPTION_EXPIRED, detalles)  
**Resultado Obtenido:** Acceso denegado correctamente por suscripción expirada  
**Estado:** ✅ Aprobado

### ATT-010: Obtener todas las asistencias
**Tipo:** Unitario (Servicio)  
**Precondiciones:** Múltiples asistencias en base de datos simulada  
**Pasos:** Llamar a `AttendanceService.get_all_attendances` sin filtros  
**Resultado Esperado:** Retorna lista de AttendanceWithClientInfo  
**Resultado Obtenido:** Lista de asistencias recuperada correctamente  
**Estado:** ✅ Aprobado

---

## 🔹 Módulo: SubscriptionRepository

### REPSUB-001: Crear suscripción en base de datos
**Tipo:** Unitario (Repositorio)  
**Precondiciones:** Sesión mockeada correctamente  
**Pasos:** Llamar a `SubscriptionRepository.create` con datos válidos  
**Resultado Esperado:** Retorna el objeto suscripción creado  
**Resultado Obtenido:** Suscripción creada exitosamente, se verificó add y commit  
**Estado:** ✅ Aprobado

### REPSUB-002: Obtener suscripción existente por ID
**Tipo:** Unitario (Repositorio)  
**Precondiciones:** Suscripción existente en base de datos simulada  
**Pasos:** Llamar a `SubscriptionRepository.get_by_id` con ID válido  
**Resultado Esperado:** Retorna la suscripción correspondiente  
**Resultado Obtenido:** Suscripción recuperada exitosamente con ID correcto  
**Estado:** ✅ Aprobado

### REPSUB-003: Obtener suscripciones de un cliente
**Tipo:** Unitario (Repositorio)  
**Precondiciones:** Suscripciones existentes para el cliente  
**Pasos:** Llamar a `SubscriptionRepository.get_by_client` con client_id válido  
**Resultado Esperado:** Retorna lista de suscripciones del cliente  
**Resultado Obtenido:** Lista de suscripciones recuperada correctamente  
**Estado:** ✅ Aprobado

### REPSUB-004: Obtener suscripción activa de un cliente
**Tipo:** Unitario (Repositorio)  
**Precondiciones:** Suscripción activa existente para el cliente  
**Pasos:** Llamar a `SubscriptionRepository.get_active_by_client` con client_id válido  
**Resultado Esperado:** Retorna la suscripción activa  
**Resultado Obtenido:** Suscripción activa recuperada correctamente  
**Estado:** ✅ Aprobado

### REPSUB-005: Obtener suscripciones por estado
**Tipo:** Unitario (Repositorio)  
**Precondiciones:** Suscripciones con estado específico  
**Pasos:** Llamar a `SubscriptionRepository.get_by_status` con status válido  
**Resultado Esperado:** Retorna lista de suscripciones con ese estado  
**Resultado Obtenido:** Lista filtrada por estado recuperada correctamente  
**Estado:** ✅ Aprobado

### REPSUB-006: Actualizar suscripción existente
**Tipo:** Unitario (Repositorio)  
**Precondiciones:** Suscripción existente en base de datos simulada  
**Pasos:** Llamar a `SubscriptionRepository.update` con ID válido y datos a actualizar  
**Resultado Esperado:** Retorna la suscripción actualizada  
**Resultado Obtenido:** Suscripción actualizada correctamente, se verificó commit y refresh  
**Estado:** ✅ Aprobado

### REPSUB-007: Obtener suscripciones expiradas
**Tipo:** Unitario (Repositorio)  
**Precondiciones:** Suscripciones expiradas en base de datos simulada  
**Pasos:** Llamar a `SubscriptionRepository.get_expired` con fecha de referencia  
**Resultado Esperado:** Retorna lista de suscripciones expiradas  
**Resultado Obtenido:** Lista de suscripciones expiradas recuperada correctamente  
**Estado:** ✅ Aprobado

### REPSUB-008: Obtener suscripción inexistente por ID
**Tipo:** Unitario (Repositorio)  
**Precondiciones:** Suscripción no existe  
**Pasos:** Llamar a `SubscriptionRepository.get_by_id` con ID inexistente  
**Resultado Esperado:** Retorna None  
**Resultado Obtenido:** El método retornó None correctamente  
**Estado:** ✅ Aprobado

---

## 🔹 Módulo: SubscriptionService

### SUB-001: Crear suscripción exitosamente
**Tipo:** Unitario (Servicio)  
**Precondiciones:** Plan existente, repositorio mockeado  
**Pasos:** Llamar a `SubscriptionService.create_subscription` con datos válidos  
**Resultado Esperado:** Retorna Subscription con datos correctos  
**Resultado Obtenido:** Suscripción creada exitosamente, notificación enviada  
**Estado:** ✅ Aprobado

### SUB-002: Crear suscripción con descuento
**Tipo:** Unitario (Servicio)  
**Precondiciones:** Plan existente, repositorio mockeado  
**Pasos:** Llamar a `SubscriptionService.create_subscription` con discount_percentage  
**Resultado Esperado:** Retorna Subscription con precio final calculado con descuento  
**Resultado Obtenido:** Descuento aplicado correctamente, precio final calculado  
**Estado:** ✅ Aprobado

### SUB-003: Obtener suscripción activa de un cliente
**Tipo:** Unitario (Servicio)  
**Precondiciones:** Suscripción activa existente para el cliente  
**Pasos:** Llamar a `SubscriptionService.get_active_subscription_by_client` con client_id válido  
**Resultado Esperado:** Retorna Subscription activa  
**Resultado Obtenido:** Suscripción activa recuperada correctamente  
**Estado:** ✅ Aprobado

### SUB-004: Obtener suscripción por ID existente
**Tipo:** Unitario (Servicio)  
**Precondiciones:** Suscripción existente en base de datos simulada  
**Pasos:** Llamar a `SubscriptionService.get_subscription_by_id` con ID válido  
**Resultado Esperado:** Retorna Subscription correspondiente  
**Resultado Obtenido:** Suscripción recuperada exitosamente con ID correcto  
**Estado:** ✅ Aprobado

### SUB-005: Renovar suscripción exitosamente
**Tipo:** Unitario (Servicio)  
**Precondiciones:** Suscripción existente próxima a expirar  
**Pasos:** Llamar a `SubscriptionService.renew_subscription` con datos válidos  
**Resultado Esperado:** Retorna nueva Subscription programada  
**Resultado Obtenido:** Suscripción renovada exitosamente, nueva suscripción creada  
**Estado:** ✅ Aprobado

### SUB-006: Cancelar suscripción exitosamente
**Tipo:** Unitario (Servicio)  
**Precondiciones:** Suscripción activa existente  
**Pasos:** Llamar a `SubscriptionService.cancel_subscription` con datos válidos  
**Resultado Esperado:** Retorna Subscription cancelada  
**Resultado Obtenido:** Suscripción cancelada correctamente con fecha y razón  
**Estado:** ✅ Aprobado

### SUB-007: Obtener suscripción inexistente
**Tipo:** Unitario (Servicio)  
**Precondiciones:** Suscripción no existe  
**Pasos:** Llamar a `SubscriptionService.get_subscription_by_id` con ID inexistente  
**Resultado Esperado:** Lanza excepción o retorna None  
**Resultado Obtenido:** Error manejado correctamente  
**Estado:** ✅ Aprobado

### SUB-008: Fallo al crear suscripción sin plan
**Tipo:** Unitario (Servicio)  
**Precondiciones:** Plan no existe  
**Pasos:** Llamar a `SubscriptionService.create_subscription` con plan_id inexistente  
**Resultado Esperado:** Lanza excepción  
**Resultado Obtenido:** Excepción capturada correctamente  
**Estado:** ✅ Aprobado

---

## 🔹 Módulo: PaymentService

### PAY-001: Crear pago completo que activa suscripción
**Tipo:** Unitario (Servicio)  
**Precondiciones:** Suscripción pendiente de pago, repositorio mockeado  
**Pasos:** Llamar a `PaymentService.create_payment` con monto completo  
**Resultado Esperado:** Retorna Payment y activa la suscripción  
**Resultado Obtenido:** Pago creado exitosamente, suscripción activada  
**Estado:** ✅ Aprobado

### PAY-002: Crear pago parcial
**Tipo:** Unitario (Servicio)  
**Precondiciones:** Suscripción pendiente de pago  
**Pasos:** Llamar a `PaymentService.create_payment` con monto parcial  
**Resultado Esperado:** Retorna Payment, suscripción sigue pendiente  
**Resultado Obtenido:** Pago parcial creado correctamente, suscripción no activada  
**Estado:** ✅ Aprobado

### PAY-003: Obtener pagos de una suscripción
**Tipo:** Unitario (Servicio)  
**Precondiciones:** Pagos existentes para la suscripción  
**Pasos:** Llamar a `PaymentService.get_payments_by_subscription` con subscription_id válido  
**Resultado Esperado:** Retorna lista de Payment  
**Resultado Obtenido:** Lista de pagos recuperada correctamente  
**Estado:** ✅ Aprobado

### PAY-004: Obtener total pagado por suscripción
**Tipo:** Unitario (Servicio)  
**Precondiciones:** Pagos existentes para la suscripción  
**Pasos:** Llamar a `PaymentService.get_total_paid_by_subscription` con subscription_id válido  
**Resultado Esperado:** Retorna Decimal con el total pagado  
**Resultado Obtenido:** Total calculado correctamente  
**Estado:** ✅ Aprobado

### PAY-005: Obtener deuda restante de suscripción
**Tipo:** Unitario (Servicio)  
**Precondiciones:** Suscripción con pagos parciales  
**Pasos:** Llamar a `PaymentService.get_remaining_debt` con subscription_id válido  
**Resultado Esperado:** Retorna Decimal con la deuda restante  
**Resultado Obtenido:** Deuda calculada correctamente  
**Estado:** ✅ Aprobado

### PAY-006: Obtener estadísticas de pagos
**Tipo:** Unitario (Servicio)  
**Precondiciones:** Pagos existentes  
**Pasos:** Llamar a `PaymentService.get_payment_statistics` con filtros opcionales  
**Resultado Esperado:** Retorna PaymentStats con estadísticas  
**Resultado Obtenido:** Estadísticas calculadas correctamente  
**Estado:** ✅ Aprobado

### PAY-007: Fallo al crear pago sin suscripción
**Tipo:** Unitario (Servicio)  
**Precondiciones:** Suscripción no existe  
**Pasos:** Llamar a `PaymentService.create_payment` con subscription_id inexistente  
**Resultado Esperado:** Lanza excepción  
**Resultado Obtenido:** Excepción capturada correctamente  
**Estado:** ✅ Aprobado

### PAY-008: Fallo al crear pago con monto inválido
**Tipo:** Unitario (Servicio)  
**Precondiciones:** Suscripción existente  
**Pasos:** Llamar a `PaymentService.create_payment` con monto negativo o cero  
**Resultado Esperado:** Lanza ValueError  
**Resultado Obtenido:** Validación de monto funcionó correctamente  
**Estado:** ✅ Aprobado

---

## 🔹 Módulo: PlanService

### PLN-001: Crear plan exitosamente
**Tipo:** Unitario (Servicio)  
**Precondiciones:** Repositorio mockeado  
**Pasos:** Llamar a `PlanService.create_plan` con datos válidos  
**Resultado Esperado:** Retorna Plan con datos correctos  
**Resultado Obtenido:** Plan creado exitosamente con todos los campos  
**Estado:** ✅ Aprobado

### PLN-002: Obtener plan por ID existente
**Tipo:** Unitario (Servicio)  
**Precondiciones:** Plan existente en base de datos simulada  
**Pasos:** Llamar a `PlanService.get_plan_by_id` con ID válido  
**Resultado Esperado:** Retorna Plan correspondiente  
**Resultado Obtenido:** Plan recuperado exitosamente con ID correcto  
**Estado:** ✅ Aprobado

### PLN-003: Obtener plan por slug existente
**Tipo:** Unitario (Servicio)  
**Precondiciones:** Plan existente con slug  
**Pasos:** Llamar a `PlanService.get_plan_by_slug` con slug válido  
**Resultado Esperado:** Retorna Plan correspondiente  
**Resultado Obtenido:** Plan recuperado exitosamente con slug correcto  
**Estado:** ✅ Aprobado

### PLN-004: Listar todos los planes
**Tipo:** Unitario (Servicio)  
**Precondiciones:** Múltiples planes en base de datos simulada  
**Pasos:** Llamar a `PlanService.list_plans` con paginación  
**Resultado Esperado:** Retorna lista de Plan con total  
**Resultado Obtenido:** Lista de planes recuperada correctamente con paginación  
**Estado:** ✅ Aprobado

### PLN-005: Buscar planes por nombre
**Tipo:** Unitario (Servicio)  
**Precondiciones:** Planes con nombres específicos  
**Pasos:** Llamar a `PlanService.search_plans` con query de búsqueda  
**Resultado Esperado:** Retorna lista de Plan que coinciden  
**Resultado Obtenido:** Búsqueda funcionó correctamente  
**Estado:** ✅ Aprobado

### PLN-006: Actualizar plan exitosamente
**Tipo:** Unitario (Servicio)  
**Precondiciones:** Plan existente  
**Pasos:** Llamar a `PlanService.update_plan` con ID válido y datos a actualizar  
**Resultado Esperado:** Retorna Plan actualizado  
**Resultado Obtenido:** Plan actualizado correctamente con los nuevos datos  
**Estado:** ✅ Aprobado

### PLN-007: Eliminar plan exitosamente
**Tipo:** Unitario (Servicio)  
**Precondiciones:** Plan existente  
**Pasos:** Llamar a `PlanService.delete_plan` con ID válido  
**Resultado Esperado:** Retorna True  
**Resultado Obtenido:** Plan eliminado exitosamente  
**Estado:** ✅ Aprobado

### PLN-008: Fallo al obtener plan inexistente
**Tipo:** Unitario (Servicio)  
**Precondiciones:** Plan no existe  
**Pasos:** Llamar a `PlanService.get_plan_by_id` con ID inexistente  
**Resultado Esperado:** Lanza excepción o retorna None  
**Resultado Obtenido:** Error manejado correctamente  
**Estado:** ✅ Aprobado

---

## 🔹 Módulo: ProductService

### PROD-001: Crear producto exitosamente
**Tipo:** Unitario (Servicio)  
**Precondiciones:** Repositorio mockeado  
**Pasos:** Llamar a `ProductService.create_product` con datos válidos  
**Resultado Esperado:** Retorna ProductResponse con datos correctos  
**Resultado Obtenido:** Producto creado exitosamente con todos los campos  
**Estado:** ✅ Aprobado

### PROD-002: Obtener producto por ID existente
**Tipo:** Unitario (Servicio)  
**Precondiciones:** Producto existente en base de datos simulada  
**Pasos:** Llamar a `ProductService.get_product` con ID válido  
**Resultado Esperado:** Retorna ProductResponse correspondiente  
**Resultado Obtenido:** Producto recuperado exitosamente con ID correcto  
**Estado:** ✅ Aprobado

### PROD-003: Agregar stock a producto
**Tipo:** Unitario (Servicio)  
**Precondiciones:** Producto existente con stock actual  
**Pasos:** Llamar a `ProductService.add_stock` con ID y cantidad válidos  
**Resultado Esperado:** Retorna ProductResponse con stock actualizado  
**Resultado Obtenido:** Stock agregado correctamente, producto actualizado  
**Estado:** ✅ Aprobado

### PROD-004: Restar stock de producto
**Tipo:** Unitario (Servicio)  
**Precondiciones:** Producto existente con stock suficiente  
**Pasos:** Llamar a `ProductService.remove_stock` con ID y cantidad válidos  
**Resultado Esperado:** Retorna ProductResponse con stock actualizado  
**Resultado Obtenido:** Stock restado correctamente, producto actualizado  
**Estado:** ✅ Aprobado

### PROD-005: Obtener todos los productos
**Tipo:** Unitario (Servicio)  
**Precondiciones:** Múltiples productos en base de datos simulada  
**Pasos:** Llamar a `ProductService.get_all_products` con paginación  
**Resultado Esperado:** Retorna lista de ProductResponse con total  
**Resultado Obtenido:** Lista de productos recuperada correctamente con paginación  
**Estado:** ✅ Aprobado

### PROD-006: Obtener productos con stock bajo
**Tipo:** Unitario (Servicio)  
**Precondiciones:** Productos con stock por debajo del mínimo  
**Pasos:** Llamar a `ProductService.get_low_stock_alerts`  
**Resultado Esperado:** Retorna lista de ProductResponse con stock bajo  
**Resultado Obtenido:** Productos con stock bajo recuperados correctamente  
**Estado:** ✅ Aprobado

### PROD-007: Actualizar producto exitosamente
**Tipo:** Unitario (Servicio)  
**Precondiciones:** Producto existente  
**Pasos:** Llamar a `ProductService.update_product` con ID válido y datos a actualizar  
**Resultado Esperado:** Retorna ProductResponse actualizado  
**Resultado Obtenido:** Producto actualizado correctamente con los nuevos datos  
**Estado:** ✅ Aprobado

### PROD-008: Fallo al restar stock insuficiente
**Tipo:** Unitario (Servicio)  
**Precondiciones:** Producto con stock insuficiente  
**Pasos:** Llamar a `ProductService.remove_stock` con cantidad mayor al stock disponible  
**Resultado Esperado:** Lanza ValueError  
**Resultado Obtenido:** Validación de stock funcionó correctamente  
**Estado:** ✅ Aprobado

---

## 🔹 Módulo: EmbeddingService

### EMB-001: Extraer embedding de imagen válida con rostro
**Tipo:** Unitario (Servicio)  
**Precondiciones:** Imagen válida con rostro detectable  
**Pasos:** Llamar a `EmbeddingService.extract_face_encoding` con imagen válida  
**Resultado Esperado:** Retorna array numpy de 512 dimensiones  
**Resultado Obtenido:** Embedding extraído correctamente con 512 dimensiones  
**Estado:** ✅ Aprobado

### EMB-002: Comparar embeddings idénticos
**Tipo:** Unitario (Servicio)  
**Precondiciones:** Dos embeddings idénticos  
**Pasos:** Llamar a `EmbeddingService.compare_embeddings` con embeddings idénticos  
**Resultado Esperado:** Retorna True (match) y similitud alta  
**Resultado Obtenido:** Match detectado correctamente, similitud calculada  
**Estado:** ✅ Aprobado

### EMB-003: Comparar embeddings diferentes
**Tipo:** Unitario (Servicio)  
**Precondiciones:** Dos embeddings diferentes  
**Pasos:** Llamar a `EmbeddingService.compare_embeddings` con embeddings distintos  
**Resultado Esperado:** Retorna False (no match) y similitud baja  
**Resultado Obtenido:** No match detectado correctamente, similitud calculada  
**Estado:** ✅ Aprobado

### EMB-004: Validar embedding con dimensiones correctas
**Tipo:** Unitario (Servicio)  
**Precondiciones:** Embedding con 512 dimensiones  
**Pasos:** Llamar a `EmbeddingService.validate_embedding` con embedding válido  
**Resultado Esperado:** Retorna True  
**Resultado Obtenido:** Validación pasó correctamente  
**Estado:** ✅ Aprobado

### EMB-005: Validar embedding con dimensiones incorrectas
**Tipo:** Unitario (Servicio)  
**Precondiciones:** Embedding con dimensiones incorrectas  
**Pasos:** Llamar a `EmbeddingService.validate_embedding` con embedding inválido  
**Resultado Esperado:** Lanza ValueError  
**Resultado Obtenido:** Validación falló correctamente  
**Estado:** ✅ Aprobado

### EMB-006: Fallo con imagen inválida
**Tipo:** Unitario (Servicio)  
**Precondiciones:** Imagen inválida o None  
**Pasos:** Llamar a `EmbeddingService.extract_face_encoding` con imagen inválida  
**Resultado Esperado:** Lanza ValueError, AttributeError o Exception  
**Resultado Obtenido:** Excepción capturada correctamente  
**Estado:** ✅ Aprobado

### EMB-007: No se detecta rostro en imagen
**Tipo:** Unitario (Servicio)  
**Precondiciones:** Imagen sin rostro detectable  
**Pasos:** Llamar a `EmbeddingService.extract_face_encoding` con imagen sin rostro  
**Resultado Esperado:** Lanza ValueError o retorna None  
**Resultado Obtenido:** Error manejado correctamente cuando no hay rostro  
**Estado:** ✅ Aprobado

### EMB-008: Múltiples rostros en imagen
**Tipo:** Unitario (Servicio)  
**Precondiciones:** Imagen con múltiples rostros  
**Pasos:** Llamar a `EmbeddingService.extract_face_encoding` con imagen con múltiples rostros  
**Resultado Esperado:** Lanza ValueError o retorna el primer rostro  
**Resultado Obtenido:** Manejo de múltiples rostros funcionó correctamente  
**Estado:** ✅ Aprobado

---

## 🔹 Módulo: API Face Recognition

### API-FACE-001: Registrar rostro exitosamente
**Tipo:** Integración (API)  
**Precondiciones:** Usuario autenticado, imagen válida con rostro  
**Pasos:** POST `/api/v1/face/register` con imagen base64 válida  
**Resultado Esperado:** Retorna 201 con biometric_id  
**Resultado Obtenido:** Rostro registrado exitosamente, respuesta 201 recibida  
**Estado:** ✅ Aprobado

### API-FACE-002: Autenticar rostro exitosamente
**Tipo:** Integración (API)  
**Precondiciones:** Rostro registrado previamente, imagen válida  
**Pasos:** POST `/api/v1/face/authenticate` con imagen base64 válida  
**Resultado Esperado:** Retorna 200 con client_id y match=True  
**Resultado Obtenido:** Autenticación exitosa, match detectado  
**Estado:** ✅ Aprobado

### API-FACE-003: Comparar dos rostros exitosamente
**Tipo:** Integración (API)  
**Precondiciones:** Dos imágenes válidas con rostros  
**Pasos:** POST `/api/v1/face/compare` con dos imágenes base64  
**Resultado Esperado:** Retorna 200 con match y similarity  
**Resultado Obtenido:** Comparación exitosa, match y similitud calculados  
**Estado:** ✅ Aprobado

### API-FACE-004: Eliminar rostro exitosamente
**Tipo:** Integración (API)  
**Precondiciones:** Rostro registrado previamente, usuario autenticado  
**Pasos:** DELETE `/api/v1/face/{client_id}` con client_id válido  
**Resultado Esperado:** Retorna 200 con mensaje de éxito  
**Resultado Obtenido:** Rostro eliminado exitosamente  
**Estado:** ✅ Aprobado

### API-FACE-005: Fallo al registrar rostro sin autenticación
**Tipo:** Integración (API)  
**Precondiciones:** Usuario no autenticado  
**Pasos:** POST `/api/v1/face/register` sin token  
**Resultado Esperado:** Retorna 401 Unauthorized  
**Resultado Obtenido:** Error de autenticación manejado correctamente  
**Estado:** ✅ Aprobado

### API-FACE-006: Fallo con imagen inválida
**Tipo:** Integración (API)  
**Precondiciones:** Usuario autenticado, imagen inválida  
**Pasos:** POST `/api/v1/face/register` con imagen base64 inválida  
**Resultado Esperado:** Retorna 400 Bad Request  
**Resultado Obtenido:** Error de validación manejado correctamente  
**Estado:** ✅ Aprobado

### API-FACE-007: Fallo al autenticar rostro no registrado
**Tipo:** Integración (API)  
**Precondiciones:** Rostro no registrado, imagen válida  
**Pasos:** POST `/api/v1/face/authenticate` con imagen de rostro no registrado  
**Resultado Esperado:** Retorna 404 Not Found o 200 con match=False  
**Resultado Obtenido:** Error manejado correctamente cuando no hay match  
**Estado:** ✅ Aprobado

### API-FACE-008: Fallo al eliminar rostro inexistente
**Tipo:** Integración (API)  
**Precondiciones:** Rostro no existe, usuario autenticado  
**Pasos:** DELETE `/api/v1/face/{client_id}` con client_id inexistente  
**Resultado Esperado:** Retorna 404 Not Found  
**Resultado Obtenido:** Error manejado correctamente cuando no existe  
**Estado:** ✅ Aprobado

---

## 📊 Resumen de Pruebas

| Módulo | Total Pruebas | Aprobadas | Fallidas | Pendientes |
|--------|---------------|-----------|----------|-----------|
| ClientRepository | 6 | 6 | 0 | 0 |
| ClientService | 8 | 8 | 0 | 0 |
| UserRepository | 7 | 7 | 0 | 0 |
| UserService | 9 | 9 | 0 | 0 |
| FaceRecognition | 8 | 8 | 0 | 0 |
| AttendanceRepository | 8 | 8 | 0 | 0 |
| AttendanceService | 10 | 10 | 0 | 0 |
| SubscriptionRepository | 8 | 8 | 0 | 0 |
| SubscriptionService | 8 | 8 | 0 | 0 |
| PaymentService | 8 | 8 | 0 | 0 |
| PlanService | 8 | 8 | 0 | 0 |
| ProductService | 8 | 8 | 0 | 0 |
| EmbeddingService | 8 | 8 | 0 | 0 |
| API Face Recognition | 8 | 8 | 0 | 0 |
| **TOTAL** | **119** | **119** | **0** | **0** |

---

## 📝 Notas Generales

- Todas las pruebas están implementadas usando `pytest` y `unittest.mock`
- Las pruebas de repositorio validan la interacción con la base de datos simulada
- Las pruebas de servicio validan la lógica de negocio y transformación de datos
- Las pruebas de API validan los endpoints de forma integrada
- Se utilizan mocks para aislar las dependencias y hacer las pruebas más rápidas
- El estado de todas las pruebas es **Aprobado** ✅

---

**Última actualización:** 2025-11-05  
**Versión del documento:** 1.0

