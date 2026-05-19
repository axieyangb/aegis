# Envoy Configuration

Aegis controls Envoy via xDS (ADS protocol). You configure everything through the Aegis UI — no manual YAML editing required.

## How it works

1. Envoy connects to Aegis at `aegis:18000` (gRPC ADS)
2. Aegis pushes listeners, clusters, and secrets dynamically
3. Changes in the Aegis UI take effect in Envoy within ~1 second

## Static bootstrap (envoy.yaml / starter.json)

Envoy needs a static bootstrap file to know where to find the xDS server. The provided `configs/starter.json` configures:

- xDS server: `aegis:18000`
- Access log: streamed to Aegis via gRPC ALS (provides real-time traffic data)
- Node ID: `home` (must match `NODE_ID` env var in Aegis)

**Do not add listeners or clusters to the bootstrap file** — manage them entirely through the Aegis Gateway UI.

## Gateway concepts

### Listeners
A listener binds to a port and accepts connections. Typically:
- One listener on port 80 (HTTP)
- One listener on port 443 (HTTPS)

### Filter chains
Each listener can have multiple filter chains. A filter chain matches incoming connections (by SNI/domain) and routes them to a backend cluster. Each filter chain can have:
- A TLS secret (for HTTPS)
- A backend cluster
- HTTP extensions (OIDC, rate limiting, Lua, etc.)

### Clusters
An upstream cluster defines where traffic goes. Types:
- `STATIC` — fixed IP/hostname (resolved once at startup)
- `LOGICAL_DNS` — resolve hostname once and cache
- `STRICT_DNS` — resolve on every connection

### Secrets (SDS)
TLS certificates stored in Envoy's Secret Discovery Service. Aegis manages these automatically when you issue certificates via the Certs page.

## Common setups

### Reverse proxy for a single service

1. Create a cluster pointing to your service (e.g. `192.168.1.10:3000`)
2. Add an HTTPS listener on port 443
3. Add a filter chain: domain = `app.example.com`, cluster = your cluster, TLS = your cert

### Multiple domains on one server

Add one filter chain per domain to your HTTPS listener. Each filter chain has its own SNI match, backend cluster, and TLS secret.

### HTTP → HTTPS redirect

Add a catch-all filter chain on the port-80 listener with a Lua HTTP filter that returns a 301 redirect.

## Blocked IPs

Blocked IPs are automatically injected as Envoy RBAC deny rules on every xDS push. You do not need to configure this.

## Troubleshooting

**"xDS NACK"** in the dashboard header means Envoy rejected the last config. The error message shows which resource failed. Fix the highlighted resource and save again.

**Changes not applying** — check that the xDS status is "synced" (green dot). If it shows "xDS …" (grey), Envoy is not connected — verify the `NODE_ID` env var matches the node ID in your bootstrap config.
