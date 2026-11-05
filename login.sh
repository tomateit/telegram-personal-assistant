#!/usr/bin/env bash
# One-time interactive Telegram login (phone, code, 2FA) for an account.
# Usage: ./login.sh <name>     e.g. ./login.sh personal
# <name> is just a local label; the session is saved as ./data/sessions/<name>.session.
# Run it once per account. If the bot is running, it is restarted to pick up the new account.
set -euo pipefail
cd "$(dirname "$0")"
name="${1:?usage: ./login.sh <name>   (a local label for the account, e.g. personal, work)}"
docker compose run --rm telegram-pa login "$name"
if [ -n "$(docker compose ps --status running -q telegram-pa)" ]; then
    echo "Restarting the bot to pick up the account..."
    docker compose restart telegram-pa
fi
