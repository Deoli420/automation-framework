#!/usr/bin/env bash
# ── E2E Automation — Nightly Regression Runner ────────────────────────
# Runs the full test suite in Docker, copies reports to nginx-served dir,
# cleans old runs, and prunes Docker resources.
#
# Cron entry (2:30 AM IST = 9:00 PM UTC):
#   0 21 * * * /home/deploy/automation-framework/scripts/run-nightly.sh >> /home/deploy/automation-framework/nightly.log 2>&1
# ──────────────────────────────────────────────────────────────────────
set -euo pipefail

PROJECT_DIR="/home/deploy/automation-framework"
REPORT_DIR="/home/deploy/automation-reports"
DATE=$(date +%Y%m%d_%H%M%S)
RUN_DIR="$REPORT_DIR/$DATE"
LOG="$PROJECT_DIR/nightly.log"

echo ""
echo "$(date '+%Y-%m-%d %H:%M:%S') ═══ Starting nightly automation run ═══"

# Pull latest code
cd "$PROJECT_DIR"
git pull origin main --quiet 2>/dev/null || echo "Git pull skipped (not a git repo or no remote)"

# Create report directory for this run
mkdir -p "$RUN_DIR"

# Run tests in Docker
echo "$(date '+%Y-%m-%d %H:%M:%S') Running tests in Docker..."
docker compose -f docker/docker-compose.yml up --build --abort-on-container-exit 2>&1 || true

# Copy reports
cp -r "$PROJECT_DIR/reports/"* "$RUN_DIR/" 2>/dev/null || true

# Create "latest" symlink for easy access
ln -sfn "$RUN_DIR" "$REPORT_DIR/latest"

echo "$(date '+%Y-%m-%d %H:%M:%S') Reports: $RUN_DIR"

# ── Cleanup ───────────────────────────────────────────────────────────

# Clean runs older than 14 days
find "$REPORT_DIR" -maxdepth 1 -type d -mtime +14 -exec rm -rf {} + 2>/dev/null || true

# Clean Docker resources
docker compose -f docker/docker-compose.yml down --volumes 2>/dev/null || true
docker image prune -f 2>/dev/null || true

# Log rotation: keep last 500 lines
if [ -f "$LOG" ] && [ "$(wc -l < "$LOG")" -gt 1000 ]; then
    tail -500 "$LOG" > "${LOG}.tmp" && mv "${LOG}.tmp" "$LOG"
fi

echo "$(date '+%Y-%m-%d %H:%M:%S') ═══ Nightly run complete ═══"
