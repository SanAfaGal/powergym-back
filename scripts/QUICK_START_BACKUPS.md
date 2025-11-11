# 🚀 Inicio Rápido: Configuración de Backups

## Configuración en 3 Pasos

### 1️⃣ Hacer los scripts ejecutables

```bash
cd /ruta/a/tu/proyecto/powergym
chmod +x scripts/*.sh
```

### 2️⃣ Crear tu primer backup manual

```bash
./scripts/backup-db.sh
```

Esto creará un backup en `backups/postgres/backup_production_YYYYMMDD_HHMMSS.sql.gz`

### 3️⃣ Configurar backup automático diario

```bash
# Backup diario a las 2 AM (recomendado)
./scripts/setup-backup-cron.sh
```

¡Listo! Tu base de datos se respaldará automáticamente todos los días a las 2 AM.

## Verificar que funciona

```bash
# Ver los backups creados
ls -lh backups/postgres/

# Ver el cron job configurado
crontab -l | grep PowerGym

# Ver los logs del último backup automático
tail -f backups/postgres/cron.log
```

## Restaurar un backup (si es necesario)

```bash
# Listar backups disponibles
ls -lh backups/postgres/

# Restaurar (te pedirá confirmación)
./scripts/restore-db.sh backups/postgres/backup_production_20240115_020000.sql.gz
```

## 📚 Documentación Completa

Para más detalles, consulta: `scripts/BACKUP_README.md`

---

**Nota:** Los backups se guardan localmente en tu VPS. Para mayor seguridad, considera copiar los backups a otro servidor o servicio en la nube.

