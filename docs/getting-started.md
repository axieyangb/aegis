# Getting Started

## Requirements

- Docker and Docker Compose
- Port 8765 accessible on your local network (dashboard)
- Ports 80 and 443 open if you want Envoy to handle public internet traffic

## 1. Download the starter files

```bash
mkdir aegis && cd aegis

# Download docker-compose config
curl -O https://raw.githubusercontent.com/axieyangb/aegis/main/docker-compose.yml

# Download Envoy bootstrap configuration
mkdir envoy
curl -o envoy/envoy.yaml https://raw.githubusercontent.com/axieyangb/aegis/main/envoy/envoy.yaml
```

## 2. Set your admin password

Edit `docker-compose.yml` and change `ADMIN_PASSWORD=changeme` to something secure.

## 3. Start the gateway

```bash
docker compose up -d
```

- Aegis dashboard: `http://localhost:8765`
- Default login: `admin` / `changeme` (or the password you set in `ADMIN_PASSWORD`)

On first boot, Aegis automatically seeds the database with a working baseline — an HTTP listener (port 10080) and an HTTPS listener (port 10443). No file import required.

You should see **"xDS synced"** in green on the Gateway page, confirming Envoy has connected and loaded the configuration.

---

## What's next

Your gateway is running. Pick the path that matches your goal:

- **Test locally with a sample service** — follow the [Local HTTPS with whoami tutorial](tutorial-whoami-local-https.md) to add a service, issue a cert, and verify HTTPS end-to-end on your machine
- **Expose a real service over the internet** — see [Envoy configuration](envoy-config.md) for how to add clusters, configure filter chains, and issue ACME certificates (Let's Encrypt)
- **Set up notifications** — connect Telegram, Slack, or a webhook in Settings → Integrations
- **Enable AI threat analysis** — configure an AI provider in Settings → AI to automatically classify and block malicious IPs
