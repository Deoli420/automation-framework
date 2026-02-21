#!/usr/bin/env bash
# ── JMeter HTML Report Generator ──────────────────────────────────────
# Converts a .jtl results file into an HTML dashboard.
# Usage: bash performance/generate_report.sh results.jtl
# ──────────────────────────────────────────────────────────────────────
set -euo pipefail

JTL_FILE="${1:?Usage: generate_report.sh <results.jtl>}"
REPORT_DIR="${2:-reports/jmeter/dashboard}"

if [ ! -f "$JTL_FILE" ]; then
    echo "ERROR: File not found: $JTL_FILE"
    exit 1
fi

# Remove existing dashboard if present (JMeter requires empty dir)
rm -rf "$REPORT_DIR"
mkdir -p "$REPORT_DIR"

echo "Generating HTML report from: $JTL_FILE"

jmeter -g "$JTL_FILE" -o "$REPORT_DIR"

echo "Report generated: $REPORT_DIR/index.html"
