# Busboard

Multi-tenant arrival board for EMT Madrid bus stops with a menu panel. Each tenant gets a short code URL and can update the menu via Telegram.

## Setup

1. Create a virtual environment and install dependencies:

```bash
python -m venv .venv
. .venv/Scripts/activate
pip install -r requirements.txt
```

2. Copy `.env.example` to `.env` and fill values.

3. Run the server:

```bash
uvicorn app.main:app --reload
```

## Create a tenant (admin)

```bash
curl -X POST http://localhost:8000/api/admin/tenants   -H "Content-Type: application/json"   -H "X-Admin-Secret: change-me"   -d '{"name":"Bar X"}'
```

Response:

```json
{"code":"AB12C9","tenantId":"...","url":"/t/AB12C9"}
```

Open the display:

```
http://localhost:8000/t/AB12C9
```

Optional layout override:

```
http://localhost:8000/t/AB12C9?layout=vertical
```

## EMT configuration

Set the EMT token and base URL in `.env`:

- `EMT_BASE_URL=https://openapi.emtmadrid.es`
- `EMT_ACCESS_TOKEN=...`

## Telegram webhook setup

Set a webhook after setting `TELEGRAM_BOT_TOKEN` and `TELEGRAM_WEBHOOK_SECRET`:

```bash
curl -X POST   https://api.telegram.org/bot<TELEGRAM_BOT_TOKEN>/setWebhook   -d "url=https://your-domain/api/telegram/webhook/<TELEGRAM_WEBHOOK_SECRET>"
```

For local development, use ngrok or cloudflared and set the webhook to the public URL.

## Telegram polling mode (optional)

Set `TELEGRAM_MODE=polling` in `.env`. Polling runs in the app lifespan and does not require a webhook.

## Menu updates via Telegram

1. Link a chat to a tenant:

```
/link <TENANT_CODE>
```

2. Update menu text:

```
/menu Today's menu text here
```

You can also send a plain message as the menu body.

3. Publish menu:

```
/publish
```

4. Upload an image to update the featured image for that tenant.

## Tests

```bash
pytest
```
