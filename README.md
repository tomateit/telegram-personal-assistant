# Telegram PA

A self-hosted userbot ([Telethon](https://pypi.org/project/Telethon/)) that runs on your personal Telegram account.

## Feature: `@hallucinate`

In a 1:1 dialog (or Saved Messages):

- `@hallucinate what is the capital of London`: asks the default model (ChatGPT).
- `@hallucinate:gemini ...`: picks a model by alias (`chatgpt`, `gemini`, `gemini-flash`, `claude`, `opus`, `grok`, `deepseek`, `kimi`, `glm`) or by any raw OpenRouter id (`@hallucinate:openai/gpt-6-astra ...`).
- Sent as a reply to a message, that message is added as context. The rest of the dialog is never sent.
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
./login.sh   # one time: phone, code, 2FA password (= docker compose run --rm telegram-pa login)
docker compose up -d
```

The session and the config are stored in `./data` (mounted into the container, not in git or the image).
If the session ever expires, the container exits with a message; run the `login` command again.

Never run the same session in two places at once, because Telegram may revoke it.

## Local development

```bash
uv sync
uv run main/main.py login
uv run main/main.py
```
