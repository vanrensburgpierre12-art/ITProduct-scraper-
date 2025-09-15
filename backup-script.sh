#!/bin/bash

# Database backup script for production

set -e

BACKUP_DIR="/backups"
DATE=$(date +%Y%m%d_%H%M%S)
BACKUP_FILE="electronics_db_backup_${DATE}.sql"

echo "🗄️ Starting database backup: ${BACKUP_FILE}"

# Create backup
pg_dump -h postgres -U electronics_user -d electronics_db > "${BACKUP_DIR}/${BACKUP_FILE}"

# Compress backup
gzip "${BACKUP_DIR}/${BACKUP_FILE}"

# Remove backups older than 7 days
find ${BACKUP_DIR} -name "electronics_db_backup_*.sql.gz" -mtime +7 -delete

echo "✅ Backup completed: ${BACKUP_FILE}.gz"

# Optional: Upload to cloud storage
# aws s3 cp "${BACKUP_DIR}/${BACKUP_FILE}.gz" s3://your-backup-bucket/