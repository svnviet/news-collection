#!/bin/bash

# === Config ===
PROJECT_DIR="/home/administrator/news-collection"
ENV_PATH="$PROJECT_DIR/env/bin/activate"
SCRIPT_PATH="$PROJECT_DIR/rss_schedule.py"
LOG_PATH="$PROJECT_DIR/logs/rss_job.log"

# === Ensure logs directory exists ===
mkdir -p "$(dirname "$LOG_PATH")"

# === Activate virtual environment ===

# === Kill any existing job (optional, if you want to prevent duplicates) ===
pkill -f "$SCRIPT_PATH"

# === Start the job in background using nohup ===
nohup python "$SCRIPT_PATH" >> "$LOG_PATH" 2>&1 &

echo "RSS job deployed. Logging to $LOG_PATH"
