"""Telegram personal assistant userbot, serving one or more Telegram accounts in one process.

    python main/main.py               run the bot for every logged-in account in SESSIONS_DIR
    python main/main.py login NAME    interactive one-time login (phone, code, 2FA) for an account,
                                      saved as SESSIONS_DIR/NAME.session (NAME is just a local label)
    python main/main.py list          show the accounts and whether each session is still valid
"""

import asyncio
import logging
import os
import re
import sys
from pathlib import Path

from dotenv import load_dotenv
from telethon import TelegramClient

from features.hallucinate import Hallucinate

# Old features live in features/legacy and are intentionally not registered:
# from features.legacy import UppercaseMessage, InstantMath, JoinMessages

logging.basicConfig(format="[%(levelname) 5s/%(asctime)s] %(name)s: %(message)s", level=logging.WARNING)
log = logging.getLogger("main")
load_dotenv()

PROJECT_DIR = Path(__file__).resolve().parent.parent
DATA_DIR = PROJECT_DIR / "data"

API_ID = int(os.environ["API_ID"])
API_HASH = os.environ["API_HASH"]
SESSIONS_DIR = Path(os.environ.get("SESSIONS_DIR", DATA_DIR / "sessions"))
CONFIG_PATH = Path(os.environ.get("HALLUCINATE_CONFIG", DATA_DIR / "hallucinate.json"))

NAME_RE = re.compile(r"^[\w-]+$")
LOGIN_HINT = "./login.sh <name>   (= docker compose run --rm telegram-pa login <name>)"


def make_client(name: str) -> TelegramClient:
    SESSIONS_DIR.mkdir(parents=True, exist_ok=True)
    return TelegramClient(str(SESSIONS_DIR / name), API_ID, API_HASH)


def session_names() -> list[str]:
    return sorted(p.stem for p in SESSIONS_DIR.glob("*.session"))


def describe(me) -> str:
    return f"{me.first_name} (@{me.username}, id {me.id})"


async def login(name: str):
    if not NAME_RE.match(name):
        sys.exit(f"Invalid account name {name!r}: use letters, digits, '_' or '-'")
    client = make_client(name)
    await client.start()  # interactive prompts
    me = await client.get_me()
    print(f"Logged in as {describe(me)}. Session saved as {SESSIONS_DIR / name}.session")
    others = []
    for other in session_names():
        if other != name:
            async with make_client(other) as c:
                if await c.is_user_authorized() and (await c.get_me()).id == me.id:
                    others.append(other)
    if others:
        print(f"WARNING: this account is also logged in as {', '.join(others)}; remove the duplicate session file.")
    await client.disconnect()


async def list_accounts():
    names = session_names()
    if not names:
        print(f"No sessions in {SESSIONS_DIR}. Add one with: {LOGIN_HINT}")
    for name in names:
        client = make_client(name)
        await client.connect()
        status = describe(await client.get_me()) if await client.is_user_authorized() else "NOT AUTHORIZED, log in again"
        print(f"{name}: {status}")
        await client.disconnect()


async def serve(name: str, client: TelegramClient):
    try:
        await client.run_until_disconnected()
        log.warning("account %s disconnected", name)
    except Exception:
        log.exception("account %s stopped with an error", name)


async def run():
    hallucinate = Hallucinate(CONFIG_PATH, os.environ["OPENROUTER_API_KEY"])
    running, seen_ids = [], set()
    for name in session_names():
        client = make_client(name)
        await client.connect()
        if not await client.is_user_authorized():
            log.warning("account %s: session is not authorized, skipping. Log in again with: %s", name, LOGIN_HINT)
            await client.disconnect()
            continue
        me = await client.get_me()
        if me.id in seen_ids:
            log.warning("account %s: %s is already running from another session, skipping", name, describe(me))
            await client.disconnect()
            continue
        seen_ids.add(me.id)
        client.account_id = me.id
        hallucinate.register(client)
        print(f"account {name}: running as {describe(me)}")
        running.append(serve(name, client))

    if not running:
        sys.exit(f"No authorized Telegram sessions in {SESSIONS_DIR}.\nLog in with: {LOGIN_HINT}")
    await asyncio.gather(*running)


def main():
    args = sys.argv[1:]
    if args[:1] == ["login"]:
        if len(args) != 2:
            sys.exit(f"Usage: {LOGIN_HINT}")
        asyncio.run(login(args[1]))
    elif args == ["list"]:
        asyncio.run(list_accounts())
    elif not args:
        asyncio.run(run())
    else:
        sys.exit(__doc__)


if __name__ == "__main__":
    main()
