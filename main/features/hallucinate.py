"""@hallucinate — ask an LLM (via OpenRouter + litellm) from inside a Telegram 1:1 dialog.

Usage (in a private dialog):
    @hallucinate what is the capital of London     -> default model
    @hallucinate:gemini what is ...                 -> model alias from the config
    @hallucinate:openai/gpt-6-astra what is ...     -> any raw OpenRouter model id
    (as a reply) @hallucinate:grok is that true?    -> replied-to message is added as context

Only the triggering message (and the replied-to message, if any) is sent to the LLM,
never the dialog history.

Access control (commands from your own account, in any chat, e.g. Saved Messages):
    @hallucinate(username)    -> allow that user to trigger @hallucinate in your 1:1 dialog with them
    @hallucinate(-username)   -> revoke
    @hallucinate()            -> in a 1:1 dialog: allow the person you're talking to
    @hallucinate(-)           -> in a 1:1 dialog: revoke the person you're talking to
"""

import json
import logging
import os
import re
import tempfile
from pathlib import Path

import litellm
from telethon import events
from telethon.tl.types import User

log = logging.getLogger("hallucinate")
litellm.suppress_debug_info = True

TAG = "@hallucinate"
TRIGGER_RE = re.compile(r"^\s*@hallucinate(?::(?P<model>[\w.\-/~:]+))?(?=\s|$)\s*(?P<prompt>.*)$", re.S | re.I)
GRANT_RE = re.compile(r"^\s*@hallucinate\((?P<revoke>-?)\s*@?(?P<username>\w*)\)\s*$", re.I)

TELEGRAM_LIMIT = 4096

DEFAULT_CONFIG = {
    "default_model": "chatgpt",
    # alias -> OpenRouter model id. "~vendor/...-latest" ids always point to the newest model of that family.
    "models": {
        "chatgpt": "~openai/gpt-sol-latest",
        "gpt": "~openai/gpt-sol-latest",
        "gemini": "~google/gemini-pro-latest",
        "gemini-flash": "~google/gemini-flash-latest",
        "claude": "~anthropic/claude-sonnet-latest",
        "opus": "~anthropic/claude-opus-latest",
        "grok": "~x-ai/grok-latest",
        "deepseek": "~deepseek/deepseek-pro-latest",
        "kimi": "~moonshotai/kimi-latest",
        "glm": "~z-ai/glm-latest",
    },
    "system_prompt": (
        "You are answering a question asked inside a Telegram chat. "
        "Your answer will be posted verbatim as a regular Telegram message in that chat, "
        "where formatting is not rendered. So write plain text only: no Markdown, no headings, "
        "no tables, no bold/italics, no code blocks, no LaTeX. Simple line breaks and plain "
        "'-' list items are fine if really needed. "
        "Keep the answer concise, like a chat reply: a few sentences at most unless the "
        "question truly needs more. Get straight to the point, no preambles or closing remarks. "
        "Reply in the language of the question."
    ),
    "max_tokens": 2000,
    # [{"id": 123, "username": "someone", "name": "Some One"}]
    "allowed_users": [],
}


class Config:
    def __init__(self, path: Path):
        self.path = path
        if path.exists():
            self.data = json.loads(path.read_text(encoding="utf-8"))
            for key, value in DEFAULT_CONFIG.items():
                self.data.setdefault(key, value)
        else:
            self.data = json.loads(json.dumps(DEFAULT_CONFIG))
            self.save()

    def save(self):
        self.path.parent.mkdir(parents=True, exist_ok=True)
        with tempfile.NamedTemporaryFile("w", encoding="utf-8", dir=self.path.parent, delete=False) as f:
            json.dump(self.data, f, ensure_ascii=False, indent=2)
        os.chmod(f.name, 0o644)
        os.replace(f.name, self.path)

    def resolve_model(self, name: str | None) -> tuple[str, str] | None:
        """Returns (label, openrouter_model_id) or None if unknown."""
        name = (name or self.data["default_model"]).lower()
        models = {k.lower(): v for k, v in self.data["models"].items()}
        if name in models:
            return name, models[name]
        if "/" in name:  # raw OpenRouter id
            return name.lstrip("~").split("/", 1)[1], name
        return None

    def is_allowed(self, user_id: int) -> bool:
        return any(u["id"] == user_id for u in self.data["allowed_users"])

    def allow(self, user: User):
        self.revoke(user.id)
        self.data["allowed_users"].append(
            {"id": user.id, "username": user.username, "name": " ".join(filter(None, [user.first_name, user.last_name]))}
        )
        self.save()

    def revoke(self, user_id: int) -> bool:
        before = len(self.data["allowed_users"])
        self.data["allowed_users"] = [u for u in self.data["allowed_users"] if u["id"] != user_id]
        self.save()
        return len(self.data["allowed_users"]) != before


def _split(text: str, limit: int = TELEGRAM_LIMIT) -> list[str]:
    chunks = []
    while len(text) > limit:
        cut = text.rfind("\n", 0, limit)
        if cut < limit // 2:
            cut = limit
        chunks.append(text[:cut])
        text = text[cut:].lstrip("\n")
    chunks.append(text)
    return chunks


class Hallucinate:
    def __init__(self, config_path: Path, api_key: str):
        self.config = Config(config_path)
        self.api_key = api_key
        log.warning("hallucinate config: %s", config_path)

    def register(self, client):
        client.add_event_handler(self.on_message, events.NewMessage(pattern=re.compile(r"^\s*@hallucinate", re.I)))

    async def on_message(self, event: events.NewMessage.Event):
        msg = event.message
        text = msg.raw_text or ""

        if msg.out and (m := GRANT_RE.match(text)):
            await self._grant(event, m)
            return

        if not event.is_private:
            return
        if not msg.out and not self.config.is_allowed(event.sender_id):
            return  # someone else used the tag without permission: noop

        m = TRIGGER_RE.match(text)
        if not m:
            return
        await self._answer(event, m["model"], m["prompt"].strip())

    async def _grant(self, event, m):
        revoke, username = bool(m["revoke"]), m["username"]
        try:
            if username:
                user = await event.client.get_entity(username)
            elif event.is_private and event.chat_id != (await event.client.get_me()).id:
                user = await event.get_chat()
            else:
                await event.message.edit("⚠️ @hallucinate(): specify a username, or use it inside a 1:1 dialog")
                return
            if not isinstance(user, User):
                await event.message.edit(f"⚠️ @hallucinate: {username!r} is not a user")
                return
        except ValueError:
            await event.message.edit(f"⚠️ @hallucinate: user {username!r} not found")
            return

        who = f"@{user.username}" if user.username else (user.first_name or str(user.id))
        if revoke:
            removed = self.config.revoke(user.id)
            note = f"🔒 {who} can no longer use {TAG}" if removed else f"{who} wasn't allowed anyway"
        else:
            self.config.allow(user)
            note = f"🔓 {who} can now use {TAG} in your 1:1 dialog"
        await event.message.edit(note)

    async def _answer(self, event, model_name, prompt):
        resolved = self.config.resolve_model(model_name)
        if resolved is None:
            aliases = ", ".join(self.config.data["models"])
            await event.reply(f"⚠️ unknown model {model_name!r}. Known: {aliases}")
            return
        label, model_id = resolved

        context = None
        if event.message.is_reply:
            replied = await event.message.get_reply_message()
            if replied and replied.raw_text:
                context = replied.raw_text
        if not prompt and not context:
            return

        if context and prompt:
            user_content = f"Message being discussed:\n\"\"\"\n{context}\n\"\"\"\n\n{prompt}"
        else:
            user_content = prompt or context

        messages = [
            {"role": "system", "content": self.config.data["system_prompt"]},
            {"role": "user", "content": user_content},
        ]
        log.warning("hallucinate -> %s (%d chars, context=%s)", model_id, len(user_content), bool(context))
        try:
            async with event.client.action(event.chat_id, "typing"):
                response = await litellm.acompletion(
                    model=f"openrouter/{model_id}",
                    messages=messages,
                    api_key=self.api_key,
                    max_tokens=self.config.data["max_tokens"],
                )
            answer = (response.choices[0].message.content or "").strip() or "(empty response)"
        except Exception as e:
            log.exception("LLM call failed")
            await event.reply(f"⚠️ {label} failed: {type(e).__name__}")
            return

        reply_to = event.message
        for chunk in _split(f"{label} said: {answer}"):
            reply_to = await event.client.send_message(
                event.chat_id, chunk, reply_to=reply_to, parse_mode=None, link_preview=False
            )
