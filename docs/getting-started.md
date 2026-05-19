# Getting Started

## Requirements

- Docker and Docker Compose
- A domain pointing to your server (for TLS / ACME)
- Port 8765 accessible on your local network (dashboard)
- Ports 80 and 443 open if you want Envoy to handle public traffic

## 1. Download the starter files

```bash
mkdir aegis && cd aegis
curl -O https://raw.githubusercontent.com/axieyangb/aegis/main/docker-compose.yml
mkdir configs
curl -o configs/starter.json https://raw.githubusercontent.com/axieyangb/aegis/main/configs/starter.json
```

## 2. Set your admin password

Edit `docker-compose.yml` and change `ADMIN_PASSWORD=changeme` to something secure.

## 3. Start

```bash
docker compose up -d
```

Aegis dashboard: `http://localhost:8765`
Default login: `admin` / (your password)

## 4. Connect Envoy to Aegis

The starter config in `configs/starter.json` already points Envoy's xDS endpoint at `aegis:18000`. Envoy will connect automatically once both containers are running.

Open **Gateway** in the dashboard — you should see "xDS synced" in green.

## 5. Add your first listener

Go to **Gateway → Listeners → Add filter chain**. Configure your domain, backend cluster, and TLS secret. Changes push to Envoy immediately.

## 6. Issue a TLS certificate

Go to **Certificates → Add Provider** and configure an ACME provider (Let's Encrypt + HTTP-01 is the easiest). Then **Issue Certificate** for your domain.

> **Note:** HTTP-01 requires the `acme-renewer` cluster and a port-80 filter chain. Open the Owl chat and say "Help me set up HTTP-01" — it will walk you through the gateway configuration.

## 7. Enable AI (optional)

Go to **Settings → AI**, enable Intelligence Review, and enter an API key for your chosen provider (Gemini, Claude, OpenAI, DeepSeek, or Ollama for local inference). Aegis will start classifying IPs in the background.

Enable **Owl Chat** to talk to your gateway in natural language.

## Next steps

- [Envoy configuration reference](envoy-config.md)
- [AI setup](ai-setup.md)
- [Notifications](notifications.md)
