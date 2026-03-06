#!/bin/bash
#
# Daily Intake Automation Wrapper Script
# Runs the daily intake automation with proper environment setup and logging
#
# Usage:
#   ./run_daily_intake.sh [--test-mode] [--limit N]
#
# Location: /data/workspace/deliverables/run_daily_intake.sh
#

set -euo pipefail

# Get script directory
SCRIPT_DIR="$(cd "$(dirname "${BASH_SOURCE[0]}")" && pwd)"
PROJECT_ROOT="$(cd "$SCRIPT_DIR/../.." && pwd)"
DELIVERABLES_DIR="$SCRIPT_DIR"
LOGS_DIR="$DELIVERABLES_DIR/logs"

# Create logs directory if needed
mkdir -p "$LOGS_DIR"

# Generate log filename with timestamp
LOG_FILE="$LOGS_DIR/intake_$(date +%Y%m%d_%H%M%S).log"

# Load environment from .env file if it exists
if [[ -f "$PROJECT_ROOT/.env" ]]; then
    echo "[$(date -Iseconds)] Loading environment from .env file..." | tee -a "$LOG_FILE"
    set -a
    source "$PROJECT_ROOT/.env"
    set +a
elif [[ -f "$DELIVERABLES_DIR/.env" ]]; then
    echo "[$(date -Iseconds)] Loading environment from deliverables/.env file..." | tee -a "$LOG_FILE"
    set -a
    source "$DELIVERABLES_DIR/.env"
    set +a
else
    echo "[$(date -Iseconds)] Warning: No .env file found. Using existing environment variables." | tee -a "$LOG_FILE"
fi

# Log startup info
echo "[$(date -Iseconds)] =========================================" | tee -a "$LOG_FILE"
echo "[$(date -Iseconds)] Daily Intake Automation Started" | tee -a "$LOG_FILE"
echo "[$(date -Iseconds)] Log file: $LOG_FILE" | tee -a "$LOG_FILE"
echo "[$(date -Iseconds)] Arguments: $@" | tee -a "$LOG_FILE"
echo "[$(date -Iseconds)] =========================================" | tee -a "$LOG_FILE"

# Check Python availability
if ! command -v python3 &> /dev/null; then
    echo "[$(date -Iseconds)] ERROR: python3 not found" | tee -a "$LOG_FILE"
    exit 1
fi

# Check if psycopg is installed (required for database connectivity)
if ! python3 -c "import psycopg" 2>/dev/null; then
    echo "[$(date -Iseconds)] Installing required dependency: psycopg..." | tee -a "$LOG_FILE"
    pip3 install psycopg --quiet 2>&1 | tee -a "$LOG_FILE"
fi

# Run the automation script with all arguments passed through
if python3 "$DELIVERABLES_DIR/daily_intake_automation.py" "$@" 2>&1 | tee -a "$LOG_FILE"; then
    EXIT_CODE=$?
    echo "[$(date -Iseconds)] =========================================" | tee -a "$LOG_FILE"
    echo "[$(date -Iseconds)] Automation completed successfully" | tee -a "$LOG_FILE"
    echo "[$(date -Iseconds)] Exit code: $EXIT_CODE" | tee -a "$LOG_FILE"
    echo "[$(date -Iseconds)] =========================================" | tee -a "$LOG_FILE"
else
    EXIT_CODE=$?
    echo "[$(date -Iseconds)] =========================================" | tee -a "$LOG_FILE"
    echo "[$(date -Iseconds)] ERROR: Automation failed with exit code $EXIT_CODE" | tee -a "$LOG_FILE"
    echo "[$(date -Iseconds)] =========================================" | tee -a "$LOG_FILE"
    exit $EXIT_CODE
fi

# Also create a symlink to the latest log for convenience
ln -sf "$LOG_FILE" "$LOGS_DIR/latest.log"

exit $EXIT_CODE
