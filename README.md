# Telegram PA

A self-hosted userbot ([Telethon](https://pypi.org/project/Telethon/)) that runs on your personal Telegram account.

## Feature: `@hallucinate`

In a 1:1 dialog (or Saved Messages):

- `@hallucinate what is the capital of London`: asks the default model (ChatGPT).
- `@hallucinate:gemini ...`: picks a model by alias (`chatgpt`, `gemini`, `gemini-flash`, `claude`, `opus`, `grok`, `deepseek`, `kimi`, `glm`) or by any raw OpenRouter id (`@hallucinate:openai/gpt-6-astra ...`).
- Sent as a reply to a message, that message is added as context. The rest of the dialog is never sent.
- Images (photos or image files) on the replied-to message and/or on your own message are sent too, if the model accepts images. Models that don't (e.g. `deepseek`, `glm`) get the text only, and the answer notes that the image was ignored.
- The answer is posted from your account as `<model> said: ...`.

Other people can't trigger it unless you allow them:

- `@hallucinate(username)` / `@hallucinate(-username)`: allow / revoke a user.
- `@hallucinate()` / `@hallucinate(-)`: inside a 1:1 dialog, allow / revoke the person you're talking to.

Settings (model aliases, default model, system prompt, max tokens, allowed users) are in `data/hallucinate.json`, which is created on first run. Restart after editing it.

LLM calls go through [litellm](https://github.com/BerriAI/litellm) to [OpenRouter](https://openrouter.ai).

The old features (instant math, uppercase, message joining) are kept in `main/features/legacy` but not loaded.

## Deploy

```bash
git clone <repo> app_telegram_pa && cd app_telegram_pa
cp .env.example .env   # fill API_ID, API_HASH (https://my.telegram.org), OPENROUTER_API_KEY
docker compose build
./login.sh personal   # one time per account: phone, code, 2FA password
docker compose up -d
```

### Multiple accounts

Run `./login.sh <name>` once for each Telegram account; `<name>` is just a local label.
The bot serves every logged-in account in one process, and `login.sh` restarts it to pick up a new one.

- Sessions: `./data/sessions/<name>.session`. To remove an account, delete its file and `docker compose restart`.
- `docker compose run --rm telegram-pa list` shows each account and whether its session is still valid.
- An account whose session has expired is skipped (with a warning in `docker compose logs`); re-run `./login.sh <name>` for it.
- `@hallucinate(...)` allowlists are per account; model settings in `data/hallucinate.json` are shared.

Sessions and config live in `./data` (mounted into the container, not in git or the image).

Never run the same session in two places at once, because Telegram may revoke it.

## Local development

```bash
uv sync
uv run main/main.py login personal
uv run main/main.py
```
