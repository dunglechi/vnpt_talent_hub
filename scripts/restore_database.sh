#!/bin/bash

# Database Restore Script for VNPT Talent Hub
# Usage: ./restore_database.sh <backup_file>

set -e

if [ -z "$1" ]; then
    echo "Usage: $0 <backup_file>"
    echo "Example: $0 /var/backups/vnpt-talent-hub/vnpt_talent_hub_20250130_020000.sql.gz"
    exit 1
fi

BACKUP_FILE=$1
DB_CONTAINER="vnpt_talent_hub_db"

if [ ! -f "$BACKUP_FILE" ]; then
    echo "Error: Backup file not found: $BACKUP_FILE"
    exit 1
fi

echo "========================================"
echo "Database Restore"
echo "========================================"
echo "Backup file: $BACKUP_FILE"
echo ""

read -p "⚠️  This will REPLACE the current database. Continue? (yes/no): " CONFIRM

if [ "$CONFIRM" != "yes" ]; then
    echo "Restore cancelled"
    exit 0
fi

echo ""
echo "Stopping API service..."
docker-compose stop api

echo "Restoring database..."
gunzip < $BACKUP_FILE | docker exec -i $DB_CONTAINER psql -U ${DB_USER:-talent_admin}

if [ $? -eq 0 ]; then
    echo "✓ Database restored successfully"
else
    echo "✗ Restore failed"
    exit 1
fi

echo "Starting API service..."
docker-compose start api

echo ""
echo "✓ Restore completed"
echo "Verify the application: docker-compose ps"
