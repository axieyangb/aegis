# Envoy Configuration

Aegis controls Envoy via xDS (specifically using the ADS — Aggregated Discovery Service — protocol). You configure everything through the Aegis UI — no manual YAML editing required.

## How it works

1. Envoy starts using a static bootstrap file (`envoy.yaml`) pointing it to Aegis.
2. Envoy connects to Aegis at `aegis:18000` (gRPC ADS).
3. Aegis pushes listeners, clusters, and secrets dynamically from its database.
4. Changes made in the Aegis UI take effect in Envoy within ~1 second.

## Static bootstrap (`envoy.yaml`)

Envoy needs a static bootstrap file to know where to find the xDS server. The provided `envoy/envoy.yaml` configures:

- **xDS server:** `aegis:18000` (using gRPC ADS)
- **Node ID:** `home` (must match `NODE_ID` env var in Aegis)
- **Admin interface:** bound to port `9901`

**Do not add listeners or clusters to this bootstrap file.** They are managed entirely through the Aegis Gateway UI and stored in Aegis's database.

## Auto-bootstrap on first run

When Aegis starts with an empty database, it automatically seeds a standard baseline configuration:

| Resource | Name | Purpose |
|---|---|---|
| Listener | `http_listener` | Port 10080 — redirects HTTP to HTTPS, routes `/.well-known/acme-challenge/` to `acme-renewer` |
| Listener | `https_listener` | Port 10443 — SNI-based TLS termination, ready for filter chains |
| Cluster | `acme-renewer` | Routes ACME HTTP-01 challenge traffic back to Aegis |

This means on first boot you get a working gateway skeleton immediately — no file import required.

## Adding your own resources

After the baseline is seeded, add your configuration through the Aegis UI:

- **Gateway → Clusters** — add upstream services
- **Gateway → Listeners → https_listener** — add filter chains (SNI + cluster + TLS secret) per domain
- **Certificates** — issue certs via ACME or Local CA; they are pushed to Envoy as SDS secrets automatically

## Advanced: importing a custom baseline

If you need a non-standard starting configuration (e.g. a VPS relay setup with PROXY protocol), you can import a JSON configuration snapshot via **Gateway → Import**. The `configs/` directory in the repo contains example configurations.
