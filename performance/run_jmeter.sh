#!/usr/bin/env bash
# ── JMeter CLI Wrapper ────────────────────────────────────────────────
# Usage: bash performance/run_jmeter.sh [test_plan]
# Default: runs nykaa_search_load.jmx
# ──────────────────────────────────────────────────────────────────────
set -euo pipefail

SCRIPT_DIR="$(cd "$(dirname "${BASH_SOURCE[0]}")" && pwd)"
PROJECT_DIR="$(dirname "$SCRIPT_DIR")"
REPORT_DIR="$PROJECT_DIR/reports/jmeter"
TEST_PLAN="${1:-$SCRIPT_DIR/test_plans/nykaa_search_load.jmx}"
TIMESTAMP=$(date +%Y%m%d_%H%M%S)

mkdir -p "$REPORT_DIR"

echo "Running JMeter test plan: $TEST_PLAN"
echo "Results: $REPORT_DIR"

jmeter -n \
    -t "$TEST_PLAN" \
    -l "$REPORT_DIR/results_${TIMESTAMP}.jtl" \
    -e -o "$REPORT_DIR/dashboard_${TIMESTAMP}/"

echo "JMeter run complete."
echo "Results: $REPORT_DIR/results_${TIMESTAMP}.jtl"
echo "Dashboard: $REPORT_DIR/dashboard_${TIMESTAMP}/index.html"
