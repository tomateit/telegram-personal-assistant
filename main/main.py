"""Telegram personal assistant userbot.

    python main/main.py          run the bot (requires an existing authorized session)
    python main/main.py login    interactive one-time login: asks for phone, code and 2FA password,
                                 saves the session to TELEGRAM_SESSION (default: data/TelegramPA_session)
"""

import logging
import os
import sys
from pathlib import Path

from dotenv import load_dotenv
from telethon import TelegramClient

from features.hallucinate import Hallucinate

# Old features live in features/legacy and are intentionally not registered:
# from features.legacy import UppercaseMessage, InstantMath, JoinMessages

logging.basicConfig(format="[%(levelname) 5s/%(asctime)s] %(name)s: %(message)s", level=logging.WARNING)
load_dotenv()

PROJECT_DIR = Path(__file__).resolve().parent.parent
DATA_DIR = PROJECT_DIR / "data"

API_ID = int(os.environ["API_ID"])
API_HASH = os.environ["API_HASH"]
SESSION_PATH = Path(os.environ.get("TELEGRAM_SESSION", DATA_DIR / "TelegramPA_session"))
CONFIG_PATH = Path(os.environ.get("HALLUCINATE_CONFIG", DATA_DIR / "hallucinate.json"))


def make_client() -> TelegramClient:
    SESSION_PATH.parent.mkdir(parents=True, exist_ok=True)
    return TelegramClient(str(SESSION_PATH), API_ID, API_HASH)


def login():
    client = make_client()
    client.start()  # interactive prompts
    me = client.loop.run_until_complete(client.get_me())
    print(f"Logged in as {me.first_name} (@{me.username}, id {me.id}). Session saved to {SESSION_PATH}.session")
    client.disconnect()


async def run(client: TelegramClient):
    await client.connect()
    if not await client.is_user_authorized():
        sys.exit(
            f"No authorized Telegram session at {SESSION_PATH}.session.\n"
            "Log in once with:  docker compose run --rm telegram-pa login"
        )
    me = await client.get_me()
    print(f"Running as @{me.username} (id {me.id})")
    await client.run_until_disconnected()


def main():
    if sys.argv[1:] == ["login"]:
        login()
        return
    client = make_client()
    Hallucinate(CONFIG_PATH, os.environ["OPENROUTER_API_KEY"]).register(client)
    client.loop.run_until_complete(run(client))


if __name__ == "__main__":
    main()
