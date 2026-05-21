# Tutorial: Local HTTPS with a whoami service

> **Prerequisite:** Before starting this tutorial, make sure your Aegis gateway and Envoy are up and running. Follow the [Getting Started](getting-started.md) guide first — this tutorial picks up from a working gateway.

This tutorial walks through deploying a simple whoami web service and exposing it over HTTPS through Envoy, using Aegis's built-in Local CA — no public domain or open ports required.

**You will:**
1. Run a `whoami` container alongside Aegis + Envoy
2. Add a cluster and filter chain in Aegis
3. Issue a TLS certificate from the Local CA
4. Add a `/etc/hosts` entry
5. Access `https://whoami.local` from your browser

---

## Prerequisites

- Docker and Docker Compose installed
- Aegis + Envoy already running and accessible at `http://localhost:8765`
- Admin access to add an `/etc/hosts` entry on your machine

---

## Step 1 — Run the whoami container

Start `whoami` as a standalone container with a published port:

```bash
docker run -d --name whoami -p 8081:80 --restart unless-stopped traefik/whoami
```

It runs independently — no changes to your existing `docker-compose.yml` needed.

---

## Step 2 — Add a cluster in Aegis

Open the Aegis dashboard → **Gateway → Clusters → Add Cluster**.

| Field | Value |
|---|---|
| Name | `whoami` |
| Type | `STRICT_DNS` |
| Host | `host.docker.internal` |
| Port | `8081` |
| Connect timeout | `5s` |
| DNS Lookup Family | `V4_ONLY` |

Save — Aegis pushes the cluster to Envoy immediately.

---

## Step 3 — Issue a Local CA certificate

### 3a — Create a Local CA provider (first time only)

Go to **Certificates → Signing Providers → Add Provider**, choose **Local CA**, give it a name (e.g. `Local CA`), and save.

### 3b — Issue the certificate

Go to **Certificates → Managed Certs → Issue Certificate**:

| Field | Value |
|---|---|
| Domain | `whoami.local` |
| Provider | `Local CA` |
| Auto-renew | on |

Click **Issue**. The cert is generated and pushed to Envoy SDS within a second. Note the **secret name** shown (e.g. `tls-whoami-local`).

---

## Step 4 — Add a filter chain to the HTTPS listener

Go to **Gateway → Listeners → `https_listener` → Edit**.

Click **Add Filter Chain** and fill in:

| Field | Value |
|---|---|
| Domain(s) | `whoami.local` |
| Backend Cluster | `whoami` |
| TLS Secret | `tls-whoami-local` _(or the name shown on the cert page)_ |

Leave Route Prefix as `/` and click **Add**. Envoy picks up the new filter chain within ~1 second.

---

## Step 5 — Trust the Root CA

Download the Root CA certificate and install it in your OS trust store.

**macOS:**
```bash
curl -s http://localhost:8765/api/certs/ca -o aegis-local-ca.crt
sudo security add-trusted-cert -d -r trustRoot -k /Library/Keychains/System.keychain aegis-local-ca.crt
```

**Linux:**
```bash
curl -s http://localhost:8765/api/certs/ca -o aegis-local-ca.crt
sudo cp aegis-local-ca.crt /usr/local/share/ca-certificates/aegis-local-ca.crt
sudo update-ca-certificates
```

**Windows (PowerShell as Administrator):**
```powershell
Invoke-WebRequest http://localhost:8765/api/certs/ca -OutFile aegis-local-ca.crt
Import-Certificate -FilePath aegis-local-ca.crt -CertStoreLocation Cert:\LocalMachine\Root
```

Restart your browser after installing the CA.

---

## Step 6 — Add an `/etc/hosts` entry

Map `whoami.local` to the IP address of the machine running Envoy:

- **Running on your local machine** — use `127.0.0.1`
- **Running on a NAS or remote server** — use that machine's LAN IP (e.g. `192.168.1.100`)

```bash
# Local machine
echo "127.0.0.1  whoami.local" | sudo tee -a /etc/hosts

# Or remote host (replace with actual IP)
echo "192.168.1.100  whoami.local" | sudo tee -a /etc/hosts
```

On Windows, edit `C:\Windows\System32\drivers\etc\hosts` as Administrator.

---

## Step 7 — Open in browser

Navigate to **`https://whoami.local`**.

You should see the whoami response — hostname, IP, headers — served over HTTPS with a valid (locally trusted) certificate and no browser warning.

---

## What just happened

```
Browser → https://whoami.local:443
            │  SNI = whoami.local
            ▼
         Envoy (port 10443)
            │  filter chain match: whoami.local
            │  TLS: cert from Aegis SDS (signed by Local CA)
            ▼
         whoami container (port 80)
```

Aegis issued the cert from its internal Root CA, pushed it to Envoy via xDS SDS, and Envoy presented it during the TLS handshake. Your browser trusted it because you installed the Root CA.

---

## Cleanup

To remove the setup:

1. Delete the managed cert in Aegis → Certificates
2. Remove the filter chain from `https_listener`
3. Delete the `whoami` cluster
4. Remove the `/etc/hosts` line
5. Stop the whoami container: `docker rm -f whoami`
