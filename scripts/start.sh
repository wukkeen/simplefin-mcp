#!/usr/bin/env bash
set -euo pipefail

ROOT_DIR="$(cd "$(dirname "${BASH_SOURCE[0]}")/.." && pwd)"
LOG_DIR="${ROOT_DIR}/logs"
LOG_FILE="${LOG_DIR}/server.log"
PID_FILE="${ROOT_DIR}/simplefin-mcp.pid"

mkdir -p "${LOG_DIR}"

if [[ -f "${ROOT_DIR}/.venv/bin/activate" ]]; then
  # shellcheck disable=SC1091
  source "${ROOT_DIR}/.venv/bin/activate"
fi

cd "${ROOT_DIR}"

if [[ -f "${PID_FILE}" ]]; then
  if kill -0 "$(cat "${PID_FILE}")" >/dev/null 2>&1; then
    echo "Server already running (pid $(cat "${PID_FILE}"))."
    exit 0
  fi
  rm -f "${PID_FILE}"
fi

echo "Starting SimpleFIN MCP server in background..."
echo "Logging to ${LOG_FILE}"

nohup python3 src/server.py >> "${LOG_FILE}" 2>&1 &
echo $! > "${PID_FILE}"
echo "Started (pid $(cat "${PID_FILE}"))."
