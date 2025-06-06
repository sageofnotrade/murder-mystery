# Murþrą Database Schema

This directory contains the database schema, migration, and backup scripts for the Murþrą application.

## Schema Overview

(unchanged...)

## Backup & Restore

### Postgres (Supabase)

#### Backup
To back up all user data tables:
```bash
cd backend/db
./backup_postgres.sh "<PG_URI>" ./backups
```
- Replace `<PG_URI>` with your Postgres connection string.
- Backups are saved as one file per table, timestamped.

#### Restore
To restore from backup files:
```bash
cd backend/db
./restore_postgres.sh "<PG_URI>" ./backups
```
- Restores all tables from the specified backup directory.

### Redis (Cache)

#### Backup
To back up all relevant Redis keys (story, board, LLM cache):
```bash
cd backend/db
python backup_redis.py <REDIS_URL> redis_backup.json
```
- Default `REDIS_URL` is `redis://localhost:6379/0` if not provided.
- Output is a JSON file with all relevant keys/values.

#### Restore
To restore Redis from a backup file:
```bash
cd backend/db
python restore_redis.py <REDIS_URL> redis_backup.json
```

### Automation
- For regular backups, schedule these scripts via cron or CI (see below for a sample cron job):

#### Example cron (Linux):
```
0 2 * * * cd /path/to/backend/db && ./backup_postgres.sh "$PG_URI" /path/to/backups
0 3 * * * cd /path/to/backend/db && python backup_redis.py $REDIS_URL /path/to/redis_backups/redis_backup_$(date +\%Y\%m\%d).json
```

### Recovery Steps
- For disaster recovery, restore Postgres first, then Redis cache if needed.
- Always test restores on staging before production.

## Usage

(unchanged...)

## Notes

(unchanged...)
