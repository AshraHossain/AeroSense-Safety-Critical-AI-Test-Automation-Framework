#!/bin/bash
# Backup PostgreSQL database to file and optionally to S3

set -e

DB_URL="${DATABASE_URL:-postgresql://postgres:postgres@localhost:5432/aerosense}"
BACKUP_DIR="${BACKUP_DIR:-.}"
BACKUP_FILE="$BACKUP_DIR/backup_$(date +%Y%m%d_%H%M%S).sql.gz"
S3_BUCKET="${S3_BUCKET:-s3://aerosense-backups/postgres}"

echo "📦 Backing up PostgreSQL..."

# Extract connection details from URL
# postgresql://user:password@host:port/dbname
DB_NAME=$(echo "$DB_URL" | sed 's/.*\///')
DB_HOST=$(echo "$DB_URL" | sed 's/.*@\(.*\):.*/\1/')

# Perform backup
pg_dump "$DB_URL" | gzip > "$BACKUP_FILE"
echo "✓ Backed up to $BACKUP_FILE ($(du -h "$BACKUP_FILE" | cut -f1))"

# Upload to S3 if configured
if command -v aws &> /dev/null && [ -n "$S3_BUCKET" ]; then
  echo "☁️  Uploading to $S3_BUCKET..."
  aws s3 cp "$BACKUP_FILE" "$S3_BUCKET/"
  echo "✓ Uploaded to S3"
else
  echo "⚠️  S3 upload skipped (aws CLI not available)"
fi

# Verify backup integrity
echo "🔍 Verifying backup..."
gunzip -t "$BACKUP_FILE" && echo "✓ Backup integrity verified"

echo ""
echo "Backup complete: $BACKUP_FILE"
echo "Restore with: gunzip < $BACKUP_FILE | psql \$DATABASE_URL"
