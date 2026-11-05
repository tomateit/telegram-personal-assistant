#!/usr/bin/env bash
# One-time interactive Telegram login (phone, code, 2FA). Session is saved to ./data.
set -euo pipefail
cd "$(dirname "$0")"
docker compose run --rm telegram-pa login
