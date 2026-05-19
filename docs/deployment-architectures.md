# Deployment Architectures (Exposing Envoy)

To make Aegis and Envoy accept real public traffic, you need to expose Envoy's ports (Host `80`/`443`) to the internet. Depending on your network setup (home lab, static IP, CGNAT, VPS), you should choose one of the two main architectures below.

---

## Architecture A: Direct Exposure (Home Router / Static IP)

Use this if you have a **public IPv4 address** (either static or dynamically updated via DDNS) and access to your home router.

```
Internet ──► Public IP (Router) ──(Port Forward)──► Home Host (Envoy:80/443) ──► backend
```

### 1. How to configure it:
1.  **Static IP / DDNS:** Ensure your router has a public WAN IP. If it's dynamic, configure a Dynamic DNS (DDNS) service (e.g., No-IP, DuckDNS) so your domain always points to your home IP.
2.  **Router Port Forwarding:** Open your home router's admin panel and configure Port Forwarding:
    *   Forward external TCP port **`80`** to your host machine's IP on port **`80`**.
    *   Forward external TCP port **`443`** to your host machine's IP on port **`443`**.
3.  **Aegis UI Listener Config:**
    *   Your HTTP listener must bind to port **`10080`** (mapped to `80` on the host).
    *   Your HTTPS listener must bind to port **`10443`** (mapped to `443` on the host).
    *   **Do NOT enable PROXY Protocol** on your listeners.

---

## Architecture B: VPS Relay Tunnel (Recommended for CGNAT / Privacy)

Use this if you are behind **CGNAT** (cannot port forward), do not have a public IPv4, or want to **hide your home public IP** for privacy/DDoS protection.

```
Internet ──► VPS (Public IP) ──(WireGuard Tunnel + PROXY Protocol)──► Home Host (Envoy) ──► backend
```

### The Client IP Preservation Problem (Crucial for AI Threat Analysis)
If you use a VPS to proxy traffic to your home Envoy (e.g., using standard Nginx reverse proxy or simple port forwarding), Envoy will see **all incoming traffic as originating from the VPS's internal tunnel IP** (e.g., `10.0.0.1`), rather than the real client's IP.

> [!WARNING]
> **Why this is dangerous in Aegis:** If an attacker launches a web exploit, Aegis's AI Threat Engine will detect the attack and **automatically block the offending IP**. If the client IP is not preserved, Aegis will **block your VPS tunnel IP**, instantly shutting down ALL public traffic to your gateway!

### How to solve it (PROXY Protocol):
To preserve the real client IP across the tunnel, you must use the **PROXY Protocol** on both your VPS forwarder and your home Envoy listeners.

#### 1. Configure the VPS (Nginx Stream Proxy example):
On your VPS, use Nginx's `stream` module (TCP layer forwarding) with `proxy_protocol on` enabled:

```nginx
stream {
    upstream home_envoy_https {
        server 10.0.0.2:443; # Home WireGuard IP
    }

    server {
        listen 443;
        proxy_pass home_envoy_https;
        proxy_protocol on; # THIS IS CRUCIAL! Prepends client IP header
    }
}
```

#### 2. Configure the Home Envoy (Aegis UI):
1.  Open the Aegis Dashboard -> **Gateway -> Listeners**.
2.  Edit your `https_listener` (port `10443`).
3.  Under **Listener Filters**, add the **`Proxy Protocol`** filter (`envoy.filters.listener.proxy_protocol`).
4.  Save and Sync.

This tells Envoy to expect and parse the PROXY protocol header prepended by the VPS, restoring the real client's IP. Aegis's AI engine can now correctly profile and block individual attackers without affecting legitimate users.

---

## Architecture C: Cloudflare Tunnel (HTTP Header IP Restoration)

Use this if you want to expose your gateway **without port forwarding** and benefit from Cloudflare's DDoS protection, CDN, and WAF.

```
Internet ──► Cloudflare Edge ──(cloudflared Tunnel)──► cloudflared Container ──(HTTP Headers)──► Home Envoy ──► backend
```

### The Client IP Preservation Problem (Headers vs. PROXY)
Unlike Nginx stream relays which forward TCP packets directly, Cloudflare Edge acts as an HTTP reverse proxy and terminates the SSL connection. By default, Cloudflare does **not** use the PROXY Protocol (unless you are on an Enterprise plan).

Instead, Cloudflare injects standard HTTP headers containing the client's real IP before forwarding the request over the tunnel to your local `cloudflared` daemon:
*   **`CF-Connecting-IP`** (contains the real client's IP, e.g., `1.2.3.4`).
*   **`X-Forwarded-For`** (contains the client IP + proxy IPs).

> [!WARNING]
> **Why this is dangerous in Aegis:** If you do not configure Envoy to extract the real client IP from these HTTP headers, Envoy will see all traffic as originating from the local `cloudflared` container's internal IP (e.g., `172.20.0.5`). If Aegis's AI Threat Engine auto-blocks an attacker, it will **block the `cloudflared` container IP**, instantly taking your entire gateway offline!

### How to solve it (HTTP Header Extraction):
To preserve the client IP in a Cloudflare setup, you must configure Envoy's `HttpConnectionManager` filter (via the Aegis UI) to extract the client IP from Cloudflare's custom header.

#### 1. Configure the Home Envoy (Aegis UI):
1.  Open the Aegis Dashboard -> **Gateway -> Listeners**.
2.  Edit your `https_listener` (or `http_listener` if `cloudflared` terminates SSL and forwards plain HTTP to Envoy).
3.  Under the **HTTP Connection Manager** filter settings:
    *   Set **`use_remote_address`** to `true`.
    *   Enable **`xff_num_trusted_hops`** and set it to `1` (this tells Envoy to trust the `X-Forwarded-For` header sent by `cloudflared`).
    *   *(Alternatively)* Configure the **`CF-Connecting-IP` header extraction** filter (using custom Envoy Lua or Header-to-Metadata extensions supported by Aegis) to override the downstream address with the value of the `CF-Connecting-IP` header.
4.  Save and Sync.

This ensures Envoy correctly reports the actual client's IP (`1.2.3.4`) in the access logs sent to Aegis, allowing the AI Threat Engine to block attackers individually while keeping your Cloudflare Tunnel connection fully operational.

