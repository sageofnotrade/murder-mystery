#!/bin/bash
# Backup Murþrą Postgres (Supabase) database tables
# Usage: ./backup_postgres.sh [PG_URI] [BACKUP_DIR]
# Example: ./backup_postgres.sh "postgres://user:pass@host:port/db" ./backups

set -e

PG_URI=${1:-$PG_URI}
BACKUP_DIR=${2:-./backups}
DATE=$(date +"%Y%m%d_%H%M%S")

if [ -z "$PG_URI" ]; then
  echo "Error: PG_URI not set. Pass as first arg or set PG_URI env var."
  exit 1
fi

mkdir -p "$BACKUP_DIR"

for table in profiles mystery_templates mysteries stories boards; do
  pg_dump --data-only --no-owner --no-privileges --table=$table "$PG_URI" > "$BACKUP_DIR/${table}_$DATE.sql"
done

echo "Backup complete: $BACKUP_DIR/*.sql"
