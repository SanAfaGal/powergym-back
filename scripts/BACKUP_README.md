# 🔒 Guía de Backups de Base de Datos

Esta guía explica cómo configurar y usar los scripts de backup y restauración para la base de datos de PowerGym.

## 📋 Contenido

- [Scripts Disponibles](#scripts-disponibles)
- [Configuración Inicial](#configuración-inicial)
- [Uso Manual](#uso-manual)
- [Backups Automáticos (Cron)](#backups-automáticos-cron)
- [Restauración](#restauración)
- [Mejores Prácticas](#mejores-prácticas)
- [Solución de Problemas](#solución-de-problemas)

## 📦 Scripts Disponibles

### 1. `backup-db.sh`
Crea un backup comprimido de la base de datos PostgreSQL.

**Uso:**
```bash
./scripts/backup-db.sh [--env production|development] [--retention-days N]
```

**Ejemplos:**
```bash
# Backup de producción (por defecto)
./scripts/backup-db.sh

# Backup de desarrollo
./scripts/backup-db.sh --env development

# Backup con retención de 14 días
./scripts/backup-db.sh --retention-days 14
```

### 2. `restore-db.sh`
Restaura la base de datos desde un archivo de backup.

**⚠️ ADVERTENCIA:** Este script **REEMPLAZA** todos los datos existentes en la base de datos.

**Uso:**
```bash
./scripts/restore-db.sh <backup_file> [--env production|development] [--confirm]
```

**Ejemplos:**
```bash
# Restaurar desde un backup (con confirmación interactiva)
./scripts/restore-db.sh backups/postgres/backup_production_20240115_020000.sql.gz

# Restaurar sin confirmación (útil para scripts)
./scripts/restore-db.sh backup_production_20240115_020000.sql.gz --confirm

# Restaurar en desarrollo
./scripts/restore-db.sh backup_production_20240115_020000.sql.gz --env development
```

### 3. `setup-backup-cron.sh`
Configura un trabajo cron para realizar backups automáticos diarios.

**Uso:**
```bash
./scripts/setup-backup-cron.sh [--env production|development] [--hour HOUR] [--remove]
```

**Ejemplos:**
```bash
# Configurar backup diario a las 2 AM (por defecto)
./scripts/setup-backup-cron.sh

# Configurar backup diario a las 3 AM
./scripts/setup-backup-cron.sh --hour 3

# Configurar para desarrollo
./scripts/setup-backup-cron.sh --env development --hour 1

# Remover el cron job
./scripts/setup-backup-cron.sh --env production --remove
```

## 🚀 Configuración Inicial

### 1. Hacer los scripts ejecutables

```bash
chmod +x scripts/backup-db.sh
chmod +x scripts/restore-db.sh
chmod +x scripts/setup-backup-cron.sh
```

### 2. Crear directorio de backups

El directorio se crea automáticamente, pero puedes crearlo manualmente:

```bash
mkdir -p backups/postgres
```

### 3. Verificar variables de entorno

Asegúrate de que tu archivo `.env` tenga las siguientes variables configuradas:

```env
POSTGRES_USER=tu_usuario
POSTGRES_PASSWORD=tu_contraseña_segura
POSTGRES_DB=powergym
```

## 📝 Uso Manual

### Crear un Backup Manual

```bash
# Desde el directorio raíz del proyecto
./scripts/backup-db.sh

# El backup se guardará en:
# backups/postgres/backup_production_YYYYMMDD_HHMMSS.sql.gz
```

### Listar Backups Disponibles

```bash
ls -lh backups/postgres/
```

### Verificar un Backup

```bash
# Ver el tamaño y fecha del backup
ls -lh backups/postgres/backup_production_*.sql.gz

# Verificar que el archivo no esté corrupto
gunzip -t backups/postgres/backup_production_20240115_020000.sql.gz
```

## ⏰ Backups Automáticos (Cron)

### Configurar Backup Automático Diario

```bash
# Configurar backup diario a las 2 AM (recomendado)
./scripts/setup-backup-cron.sh

# O a otra hora (ejemplo: 3 AM)
./scripts/setup-backup-cron.sh --hour 3
```

### Verificar el Cron Job

```bash
# Ver todos los cron jobs
crontab -l

# Ver solo los jobs de PowerGym
crontab -l | grep PowerGym
```

### Ver Logs del Cron

```bash
# Ver los últimos logs
tail -f backups/postgres/cron.log

# Ver las últimas 50 líneas
tail -n 50 backups/postgres/cron.log
```

### Remover el Cron Job

```bash
./scripts/setup-backup-cron.sh --remove
```

## 🔄 Restauración

### Restaurar desde un Backup

1. **Listar backups disponibles:**
   ```bash
   ls -lh backups/postgres/
   ```

2. **Restaurar el backup:**
   ```bash
   ./scripts/restore-db.sh backups/postgres/backup_production_20240115_020000.sql.gz
   ```

3. **El script te pedirá confirmación antes de proceder.**

### Restaurar en un Entorno Diferente

```bash
# Restaurar un backup de producción en desarrollo (para testing)
./scripts/restore-db.sh backups/postgres/backup_production_20240115_020000.sql.gz --env development
```

## ✅ Mejores Prácticas

### 1. **Frecuencia de Backups**
- **Producción:** Diario (mínimo)
- **Desarrollo:** Semanal o antes de cambios importantes

### 2. **Retención de Backups**
- **Producción:** Mantener al menos 7-30 días de backups
- **Backups críticos:** Considerar mantener backups mensuales por más tiempo

### 3. **Almacenamiento Externo**
Los backups se guardan localmente en el VPS. Para mayor seguridad:

- **Copia a otro servidor:** Usar `scp` o `rsync` para copiar backups a otro servidor
- **Almacenamiento en la nube:** Subir backups a S3, Google Drive, Dropbox, etc.
- **Ejemplo con rsync:**
  ```bash
  rsync -avz backups/postgres/ usuario@otro-servidor:/backups/powergym/
  ```

### 4. **Verificación de Backups**
- Verifica periódicamente que los backups se estén creando correctamente
- Prueba la restauración en un entorno de desarrollo al menos una vez al mes

### 5. **Seguridad**
- Los backups contienen datos sensibles, asegúrate de:
  - Proteger el directorio `backups/` con permisos adecuados
  - No subir backups a repositorios públicos
  - Encriptar backups si los almacenas externamente

### 6. **Monitoreo**
- Revisa los logs del cron regularmente
- Configura alertas si un backup falla
- Monitorea el espacio en disco

## 🔧 Solución de Problemas

### El script no encuentra el contenedor

**Error:** `Container 'powergym_db_prod' is not running`

**Solución:**
```bash
# Verificar que el contenedor esté corriendo
docker ps

# Si no está corriendo, iniciarlo
docker compose -f docker-compose.production.yml up -d postgres
```

### Error de permisos

**Error:** `Permission denied`

**Solución:**
```bash
chmod +x scripts/backup-db.sh
chmod +x scripts/restore-db.sh
chmod +x scripts/setup-backup-cron.sh
```

### El backup falla

**Posibles causas:**
1. El contenedor no está corriendo
2. Variables de entorno incorrectas
3. Espacio en disco insuficiente
4. Permisos incorrectos en el directorio de backups

**Solución:**
```bash
# Verificar logs del contenedor
docker logs powergym_db_prod

# Verificar espacio en disco
df -h

# Verificar permisos
ls -la backups/postgres/
```

### El cron job no se ejecuta

**Verificaciones:**
```bash
# Verificar que el cron job esté instalado
crontab -l

# Verificar logs del cron
tail -f backups/postgres/cron.log

# Verificar que el servicio cron esté corriendo (Linux)
systemctl status cron

# Verificar permisos del script
ls -la scripts/backup-db.sh
```

### Restauración falla

**Posibles causas:**
1. El archivo de backup está corrupto
2. El contenedor no está corriendo
3. La base de datos tiene conexiones activas

**Solución:**
```bash
# Verificar que el backup no esté corrupto
gunzip -t backups/postgres/backup_production_20240115_020000.sql.gz

# Verificar que el contenedor esté corriendo
docker ps | grep powergym_db

# Intentar restaurar de nuevo
./scripts/restore-db.sh backups/postgres/backup_production_20240115_020000.sql.gz
```

## 📊 Estructura de Archivos

```
powergym/
├── scripts/
│   ├── backup-db.sh          # Script de backup
│   ├── restore-db.sh          # Script de restauración
│   ├── setup-backup-cron.sh   # Script de configuración de cron
│   └── BACKUP_README.md        # Esta guía
└── backups/
    └── postgres/
        ├── backup_production_20240115_020000.sql.gz
        ├── backup_production_20240116_020000.sql.gz
        ├── backup.log          # Log de backups manuales
        └── cron.log            # Log de backups automáticos
```

## 🔐 Seguridad Adicional

### Recomendaciones de Seguridad del VPS

1. **Firewall:** Bloquear el puerto 5432 desde el exterior si no es necesario
   ```bash
   # Con UFW (Ubuntu)
   sudo ufw deny 5432
   ```

2. **Contraseñas Fuertes:** Usar contraseñas seguras en `.env`

3. **Permisos del Directorio de Backups:**
   ```bash
   chmod 700 backups/postgres/
   ```

4. **Backups Remotos:** Considerar copiar backups a otro servidor o servicio en la nube

## 📞 Soporte

Si encuentras problemas o tienes preguntas:
1. Revisa los logs: `backups/postgres/backup.log` y `backups/postgres/cron.log`
2. Verifica que Docker y los contenedores estén corriendo
3. Revisa las variables de entorno en `.env`

---

**Última actualización:** 2024-01-15

