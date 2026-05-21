# Getting Started

## Requirements

- Docker and Docker Compose
- Port 8765 accessible on your local network (dashboard)
- Ports 80 and 443 open if you want Envoy to handle public internet traffic

## 1. Download the starter files

Create a new directory for Aegis and download the required configuration files:

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

On first boot, Aegis automatically seeds the database with a working baseline configuration — an HTTP listener (port 10080) that redirects to HTTPS and handles ACME challenges, and an HTTPS listener (port 10443) ready for SNI-based TLS routing. No file import required.

## 4. Add your first service

**Configure a backend cluster:**

Go to **Gateway → Clusters** and add a cluster pointing to your upstream service (hostname/IP + port).

**Configure TLS:**

- For an **internet-facing domain**: go to **Certificates → Signing Providers**, add an ACME provider (Let's Encrypt), then issue a cert for your domain. See [TLS with ACME](#tls-with-acme-lets-encrypt) below.
- For an **internal or lab service**: use the built-in Local CA — no domain, no open ports required. See [Local CA](#local-ca-for-internal-use) below.

**Wire your domain to the listener:**

Go to **Gateway → Listeners → https_listener** and add a filter chain for your domain: set the SNI match, point it to your cluster, and attach the TLS certificate secret.

You should see **"xDS synced"** in green on the Gateway page, confirming Envoy has loaded the configuration.

---

## TLS with ACME (Let's Encrypt)

For domains that are publicly reachable:

1. Go to **Certificates → Signing Providers → Add Provider**
2. Choose **ACME**, select **Let's Encrypt**, set your email, and pick a challenge type:
   - **HTTP-01** — easiest; requires port 80 open and domain pointing here
   - **DNS-01** — works behind NAT; requires Cloudflare / Route 53 / GoDaddy API access
3. Go to **Certificates → Managed Certs → Issue Certificate**, choose your provider and domain
4. Aegis solves the challenge and pushes the cert to Envoy SDS automatically
5. Auto-renewal runs 30 days before expiry — no action needed

---

## Local CA for internal use

For internal services, home lab, or dev environments where you don't have a public domain:

1. Go to **Certificates → Signing Providers → Add Provider**, choose **Local CA**
2. Go to **Certificates → Managed Certs → Issue Certificate**, select the Local CA provider and enter any hostname (e.g. `homelab.local`)
3. The cert is issued instantly and pushed to Envoy — no domain validation, no open ports
4. Download the **Root CA certificate** from the Certificates page and install it in your browser or OS trust store so the cert is trusted

By default Aegis auto-generates a 10-year ECDSA Root CA on first use. If you already have your own CA (corporate PKI, internal CA), you can import it instead: go to **Certificates → Local CA → Import CA** and upload your CA certificate and private key in PEM format. Aegis will use your CA to sign all subsequent leaf certificates.

All certs issued by the Local CA auto-renew via Aegis before expiry.

---

## What's next

- **Try the Local CA tutorial** — [Tutorial: Local HTTPS with whoami](tutorial-whoami-local-https.md) walks through adding a service, issuing a cert, and accessing it over HTTPS from your browser — a good end-to-end test of your setup
- **IP Intelligence** — enable AI classification in Settings → AI to automatically profile and classify every IP that hits your gateway
- **Notifications** — connect Telegram, Slack, or a webhook in Settings → Integrations to get alerted on threats and anomalies
- **Owl AI** — click the owl icon to chat with your gateway in plain language
