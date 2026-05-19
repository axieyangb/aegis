# Getting Started

## Requirements

- Docker and Docker Compose
- A domain pointing to your server (for TLS / ACME)
- Port 8765 accessible on your local network (dashboard)
- Ports 80 and 443 open if you want Envoy to handle public traffic

## 1. Download the starter files

Create a new directory for Aegis and download the required configuration files:

```bash
mkdir aegis && cd aegis

# Download docker-compose config
curl -O https://raw.githubusercontent.com/axieyangb/aegis/main/docker-compose.yml

# Download Envoy bootstrap configuration
mkdir envoy
curl -o envoy/envoy.yaml https://raw.githubusercontent.com/axieyangb/aegis/main/envoy/envoy.yaml

# Download baseline database configuration
mkdir configs
curl -o configs/starter.json https://raw.githubusercontent.com/axieyangb/aegis/main/configs/starter.json
```

## 2. Set your admin password

Edit `docker-compose.yml` and change `ADMIN_PASSWORD=changeme` to something secure.

## 3. Start the gateway

```bash
docker compose up -d
```

*   Aegis dashboard: `http://localhost:8765`
*   Default login: `admin` / (your password)

## 4. Connect Envoy to Aegis (Importing baseline)

1.  Open the Aegis dashboard in your browser.
2.  Go to **Gateway** page.
3.  Click the **Import** button at the top right.
4.  Upload the `configs/starter.json` file you downloaded in Step 1.

This will seed Aegis's database with a standard baseline configuration (a port 80 listener that redirects to HTTPS and handles ACME challenges). Aegis will immediately generate the correct Envoy configuration and push it to Envoy via xDS.

You should see **"xDS synced"** in green on the Gateway page, confirming Envoy has successfully connected and loaded the configuration!

## 5. Add your first service

Go to **Gateway → Clusters** to configure your backend services, and **Gateway → Listeners** to edit the `https_listener` filter chains to route your domain to your new cluster.
