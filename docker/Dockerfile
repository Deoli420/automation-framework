# ── E2E Automation Framework — Test Runner ────────────────────────────
# Runs pytest against a Selenium Chrome container.
# Does NOT include Chrome itself — use with docker-compose.yml.
# ──────────────────────────────────────────────────────────────────────

FROM python:3.13-slim

WORKDIR /automation

# System deps
RUN apt-get update && \
    apt-get install -y --no-install-recommends curl && \
    rm -rf /var/lib/apt/lists/*

# Python deps (cached layer)
COPY requirements.txt .
RUN pip install --no-cache-dir -r requirements.txt

# Copy framework code
COPY . .

# Non-root user for security
RUN groupadd --gid 1000 tester && \
    useradd --uid 1000 --gid tester --create-home tester && \
    mkdir -p /automation/reports/screenshots && \
    chown -R tester:tester /automation

USER tester

# Default: run all tests
CMD ["pytest", \
     "--html=reports/report.html", \
     "--self-contained-html", \
     "--junitxml=reports/results.xml", \
     "-v"]
