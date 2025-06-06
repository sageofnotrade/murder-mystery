#!/bin/bash
# Restore Murþrą Postgres (Supabase) database tables
# Usage: ./restore_postgres.sh [PG_URI] [BACKUP_DIR]
# Example: ./restore_postgres.sh "postgres://user:pass@host:port/db" ./backups

set -e

PG_URI=${1:-$PG_URI}
BACKUP_DIR=${2:-./backups}

if [ -z "$PG_URI" ]; then
  echo "Error: PG_URI not set. Pass as first arg or set PG_URI env var."
  exit 1
fi

for sqlfile in $BACKUP_DIR/*.sql; do
  echo "Restoring $sqlfile ..."
  psql "$PG_URI" < "$sqlfile"
done

echo "Restore complete."
