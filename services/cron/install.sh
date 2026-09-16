#!/usr/bin/env bash

set -euo pipefail

PROJECT_DIR="$(cd "$(dirname "${BASH_SOURCE[0]}")/../.." && pwd)"
PIPELINE_SCRIPT="$PROJECT_DIR/run_pipeline.sh"
CRON_SCHEDULE="${PIPELINE_CRON_SCHEDULE:-*/5 * * * *}"
CRON_LINE="$CRON_SCHEDULE \"$PIPELINE_SCRIPT\""
CURRENT_CRONTAB="$(crontab -l 2>/dev/null || true)"
UPDATED_CRONTAB="$(printf '%s\n' "$CURRENT_CRONTAB" | grep -Fv "$PIPELINE_SCRIPT" || true)"

{
    printf '%s\n' "$UPDATED_CRONTAB"
    printf '%s\n' "$CRON_LINE"
} | sed '/^[[:space:]]*$/d' | crontab -

printf 'Installed cron job:\n%s\n' "$CRON_LINE"
