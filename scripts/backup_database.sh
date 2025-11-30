#!/bin/bash

# Database Backup Script for VNPT Talent Hub
# Run this script regularly (e.g., via cron) to backup your database

set -e

# Configuration
BACKUP_DIR="/var/backups/vnpt-talent-hub"
TIMESTAMP=$(date +"%Y%m%d_%H%M%S")
RETENTION_DAYS=30

# Docker container name
DB_CONTAINER="vnpt_talent_hub_db"

# Create backup directory if it doesn't exist
mkdir -p $BACKUP_DIR

# Backup filename
BACKUP_FILE="$BACKUP_DIR/vnpt_talent_hub_$TIMESTAMP.sql.gz"

echo "Starting database backup..."
echo "Backup file: $BACKUP_FILE"

# Perform backup using docker exec
docker exec -t $DB_CONTAINER pg_dumpall -c -U ${DB_USER:-talent_admin} | gzip > $BACKUP_FILE

# Check if backup was successful
if [ $? -eq 0 ]; then
    echo "✓ Backup completed successfully"
    echo "  File size: $(du -h $BACKUP_FILE | cut -f1)"
else
    echo "✗ Backup failed"
    exit 1
fi

# Remove old backups
echo "Cleaning up old backups (older than $RETENTION_DAYS days)..."
find $BACKUP_DIR -name "vnpt_talent_hub_*.sql.gz" -type f -mtime +$RETENTION_DAYS -delete

# Count remaining backups
BACKUP_COUNT=$(find $BACKUP_DIR -name "vnpt_talent_hub_*.sql.gz" -type f | wc -l)
echo "✓ Current backups: $BACKUP_COUNT"

# Optional: Upload to cloud storage (S3, Google Cloud Storage, etc.)
# Uncomment and configure as needed
# aws s3 cp $BACKUP_FILE s3://your-bucket/backups/
# gsutil cp $BACKUP_FILE gs://your-bucket/backups/

echo "Backup process completed"
