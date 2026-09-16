#!/usr/bin/env bash

set -euo pipefail

PROJECT_DIR="$(cd "$(dirname "${BASH_SOURCE[0]}")" && pwd)"
PIPELINE_LOG_DIR="$PROJECT_DIR/logs"
PIPELINE_LOG_FILE="$PIPELINE_LOG_DIR/pipeline.log"
PIPELINE_LOCK_FILE="$PROJECT_DIR/.pipeline.lock"
VENV_ACTIVATE="$PROJECT_DIR/.venv/bin/activate"
COMPOSE_FILE="$PROJECT_DIR/code/deployment/docker-compose.yml"

mkdir -p "$PIPELINE_LOG_DIR"
touch "$PIPELINE_LOG_FILE"
exec > >(tee -a "$PIPELINE_LOG_FILE") 2>&1

exec 9>"$PIPELINE_LOCK_FILE"

if ! flock -n 9; then
    printf '[%s] Pipeline skipped: another run is active\n' "$(date --iso-8601=seconds)"
    exit 0
fi

finish() {
    status=$?
    trap - EXIT

    if [[ "$status" -eq 0 ]]; then
        printf '[%s] Pipeline finished successfully\n' "$(date --iso-8601=seconds)"
    else
        printf '[%s] Pipeline failed with status %s\n' "$(date --iso-8601=seconds)" "$status"
    fi

    exit "$status"
}

trap finish EXIT

printf '[%s] Pipeline started\n' "$(date --iso-8601=seconds)"

if [[ ! -f "$VENV_ACTIVATE" ]]; then
    printf 'Virtual environment not found: %s\n' "$VENV_ACTIVATE"
    exit 1
fi

if [[ -f "$PROJECT_DIR/.env" ]]; then
    set -a
    source "$PROJECT_DIR/.env"
    set +a
fi

export API_PORT="${API_PORT:-8000}"
export APP_PORT="${APP_PORT:-8501}"
export COMPOSE_PROJECT_NAME="${COMPOSE_PROJECT_NAME:-pmldl-assignment1}"
export DVC_SITE_CACHE_DIR="${DVC_SITE_CACHE_DIR:-$PROJECT_DIR/.dvc/site-cache}"

source "$VENV_ACTIVATE"
cd "$PROJECT_DIR"

dvc repro
docker compose -f "$COMPOSE_FILE" up --build -d
docker compose -f "$COMPOSE_FILE" ps
