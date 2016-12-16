#!/bin/bash
set -euo pipefail

if [ ! -f /var/rtrack/rtrack.db ]; then
  mkdir -p /var/rtrack
  cat /opt/rtrack/schema.sql | sqlite3 /var/rtrack/rtrack.db
fi

PYTHONPATH=/opt/rtrack gunicorn --bind 0.0.0.0:8000 --workers=4 rtrack:app
