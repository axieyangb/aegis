# Envoy Configuration

Aegis controls Envoy via xDS (specifically using the ADS - Aggregated Discovery Service - protocol). You configure everything through the Aegis UI — no manual YAML editing required.

## How it works

1.  Envoy starts using a static bootstrap file (`envoy.yaml`) pointing it to Aegis.
2.  Envoy connects to Aegis at `aegis:18000` (gRPC ADS).
3.  Aegis pushes listeners, clusters, and secrets dynamically from its database.
4.  Changes made in the Aegis UI take effect in Envoy within ~1 second.

## Static bootstrap (`envoy.yaml`)

Envoy needs a static bootstrap file to know where to find the xDS server. The provided `envoy/envoy.yaml` configures:

*   **xDS server:** `aegis:18000` (using gRPC).
*   **Node ID:** `home` (must match `NODE_ID` env var in Aegis).
*   **Admin interface:** bound to port `9901` (internal or public as mapped in docker-compose).

**Do not add listeners or clusters to this bootstrap file.** They should be managed entirely through the Aegis Gateway UI (and are stored in Aegis's database).

## Dynamic configuration (`starter.json`)

The `configs/starter.json` is **not** read by Envoy. It is an export of the Aegis database structure. When imported via the Aegis UI, it configures:

*   `http_listener` (port 10080): Redirects all standard HTTP traffic to HTTPS, but routes `/.well-known/acme-challenge` to the `acme-renewer` cluster.
*   `https_listener` (port 10443): Placeholder for your SSL traffic with SNI matching.
*   `acme-renewer` cluster: Points to Aegis's built-in ACME challenge responder.
*   `my-service` cluster: Placeholder for your actual backend application.

Once imported, Aegis dynamically translates these into Envoy-native config and pushes them to Envoy over the xDS channel.

## Exposing Envoy to Public Traffic (Port Mapping)

To make your gateway accept real public traffic from the internet, you must understand how ports are mapped between your host machine and the Envoy container.

### The Port Flow
```
Internet ──► Host Port 80  ──────(Docker Map)─────► Container Port 10080 (Envoy HTTP Listener)
Internet ──► Host Port 443 ──────(Docker Map)─────► Container Port 10443 (Envoy HTTPS Listener)
```

1.  **Docker Port Mapping:** In `docker-compose.yml`, the `envoy` service exposes ports `80` and `443` on the host, mapping them to `10080` and `10443` inside the container respectively.
    *   This is done because binding to privileged ports (< 1024) directly inside a container is restricted by default for security.
2.  **UI Port Binding:** When you create or edit Listeners in the **Aegis UI**, you must bind them to the **container port**, NOT the host port:
    *   Your HTTP listener (handling redirects and ACME challenge) must bind to **`10080`**.
    *   Your HTTPS listener (handling secure SSL traffic) must bind to **`10443`**.
3.  **Public Access:** Once the containers are running, simply point your domain's DNS `A` or `AAAA` records to your host machine's public IP address. Traffic arriving at port 80/443 will automatically flow through Envoy.

