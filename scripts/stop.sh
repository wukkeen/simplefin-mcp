#!/usr/bin/env bash
set -euo pipefail

ROOT_DIR="$(cd "$(dirname "${BASH_SOURCE[0]}")/.." && pwd)"
PID_FILE="${ROOT_DIR}/simplefin-mcp.pid"

if [[ ! -f "${PID_FILE}" ]]; then
  echo "No PID file found. Is the server running?"
  exit 0
fi

PID="$(cat "${PID_FILE}")"
if kill -0 "${PID}" >/dev/null 2>&1; then
  echo "Stopping server (pid ${PID})..."
  kill "${PID}"
else
  echo "Process ${PID} not running. Cleaning up PID file."
fi

rm -f "${PID_FILE}"
