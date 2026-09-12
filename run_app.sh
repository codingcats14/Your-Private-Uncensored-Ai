#!/usr/bin/env bash
set -e

export AI_NAME="${AI_NAME:-Mikey}"
export WEB_PORT="${WEB_PORT:-5000}"
export LLAMA_URL="${LLAMA_URL:-http://127.0.0.1:8080}"

python app.py
