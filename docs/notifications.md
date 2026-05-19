# Notifications

Aegis can send alerts to Telegram, Discord, Slack, or any webhook endpoint.

## Channel types

### Telegram

1. Create a bot via [@BotFather](https://t.me/BotFather) — save the bot token
2. Start a chat with your bot (send `/start`)
3. In Aegis: **Integrations → Add Channel → Telegram**
4. Enter the bot token, then click **ID** to auto-detect your chat ID

**Owl AI Chat via Telegram**: Enable the "Owl Chat" toggle on a Telegram channel to let Owl respond to messages sent to your bot.

### Webhook (Discord, Slack, generic)

- **Discord**: Server Settings → Integrations → Webhooks → New Webhook → copy URL
- **Slack**: Create an Incoming Webhook app → copy URL
- **Generic**: any URL that accepts a POST with a JSON body

## Events

Toggle which events trigger notifications:

| Event | Description |
|---|---|
| IP Blocked | An IP was auto-blocked by a detection rule |
| DDoS Pattern | High-volume flood detected |
| Error Spike | Unusual 5xx error rate |
| Client Flagged | AI classified an IP as suspicious |
| Cert Expiry | A managed certificate is expiring soon |
| Daily Digest | Daily summary of traffic and security events |
| Owl Patrol | Owl found a threat during an autonomous sweep |

## Suppression

Duplicate alerts for the same IP/pattern within a time window are suppressed and bundled into a follow-up message (e.g. "+12 more suppressed"). This prevents alert fatigue during attacks.

## Daily Digest

Sent on a cron schedule (default: 08:00 daily). Includes traffic summary, top threats, cert status, and — if AI is enabled — a natural-language narrative written by Owl.

Change the schedule under **Integrations → Daily Digest → Cron schedule**. Use [crontab.guru](https://crontab.guru) to build expressions.

## Owl Patrol

Owl analyses recent traffic on a schedule and sends a notification only when it finds something genuinely concerning. Configure the sweep interval and whether Owl is allowed to auto-block IPs during a sweep.

Requires at least one notification channel to be configured.
