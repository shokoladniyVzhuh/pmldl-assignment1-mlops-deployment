#!/usr/bin/env bash

set -euo pipefail

PROJECT_DIR="$(cd "$(dirname "${BASH_SOURCE[0]}")/../.." && pwd)"
PIPELINE_SCRIPT="$PROJECT_DIR/run_pipeline.sh"
CURRENT_CRONTAB="$(crontab -l 2>/dev/null || true)"
UPDATED_CRONTAB="$(printf '%s\n' "$CURRENT_CRONTAB" | grep -Fv "$PIPELINE_SCRIPT" || true)"

printf '%s\n' "$UPDATED_CRONTAB" | sed '/^[[:space:]]*$/d' | crontab -

printf 'Removed cron jobs for:\n%s\n' "$PIPELINE_SCRIPT"
