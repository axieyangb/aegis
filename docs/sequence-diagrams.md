# Sequence Diagrams (Deployment Flow References)

These sequence diagrams illustrate the packet flow, bootstrapping, and dynamic xDS/ALS interactions under different deployment architectures.

You can paste the text below into your sequence diagram rendering tool to generate the visuals.

---

## 1. Direct Exposure Flow (Home Router Port Forwarding)

This diagram shows the standard flow where a home router forwards ports directly to the host, and Envoy streams live traffic data to Aegis.

```text
Title: Direct Exposure Flow (Home Router Port Forwarding) [fillcolor="white"]
participant Client as Client [fillcolor="lightgray"]
participant Router as Router [fillcolor="lightblue"]
participant Envoy as Envoy [fillcolor="yellow"]
participant Aegis as Aegis [fillcolor="pink"]

Note over Client, Aegis: Bootstrapping Phase [fillcolor="lightgreen"]
Envoy->Aegis: Connect via gRPC xDS (port 18000)
Aegis->Envoy: Push http_listener (port 10080) & static clusters
Note over Envoy: http_listener is now live inside container

Note over Client, Aegis: Traffic Flow (HTTP to HTTPS Redirect) [fillcolor="lightgreen"]
Client->Router: Request http://yourdomain.com (port 80)
Router->Envoy: Forward to Host Port 80 -> Container Port 10080
Envoy->Aegis: Stream Access Log (gRPC ALS) with Client IP
Aegis->Aegis: Log request to Database & update live dashboard
Envoy-->>Client: Redirect to HTTPS (https://yourdomain.com:443)
```

---

## 2. VPS Relay Flow (PROXY Protocol & AI Auto-Blocking)

This diagram demonstrates how the **PROXY Protocol** preserves the client's real IP across a WireGuard tunnel, allowing Aegis's AI Threat Engine to auto-block an attacker without accidentally banning the VPS relay itself.

```text
Title: VPS Relay Flow (PROXY Protocol & AI Auto-Blocking) [fillcolor="white"]
participant Client as Attacker [fillcolor="lightgray"]
participant VPS as VPS (Nginx) [fillcolor="lightblue"]
participant Tunnel as WG Tunnel [fillcolor="orange"]
participant Envoy as Envoy [fillcolor="yellow"]
participant Aegis as Aegis [fillcolor="pink"]

Note over Attacker, Aegis: Bootstrapping Phase [fillcolor="lightgreen"]
Envoy->Aegis: Connect via gRPC xDS (port 18000)
Aegis->Envoy: Push https_listener (10443) with PROXY Protocol filter enabled

Note over Attacker, Aegis: Traffic Flow (Exploit Attack & Auto-Block) [fillcolor="lightgreen"]
Attacker->VPS: Send Exploit to https://app.yourdomain.com (Client IP: 1.2.3.4)
Note over VPS: VPS prepends PROXY header: "Client: 1.2.3.4, Proxy: VPS_IP" [fillcolor="cyan"]
VPS->Tunnel: Forward TCP stream with PROXY header
Tunnel->Envoy: Deliver to Home Host (mapped to Container 10443)
Note over Envoy: PROXY filter parses header, restores Downstream IP to 1.2.3.4 [fillcolor="cyan"]
Envoy->Aegis: Stream Access Log (gRPC ALS) with Client IP = 1.2.3.4
Aegis->Aegis: AI Threat Engine detects exploit on 1.2.3.4
Aegis->Aegis: Auto-blocks 1.2.3.4 (saves block rule to DB) [fillcolor="red", fontcolor="white"]
Aegis->Envoy: Push updated xDS blocklist (dynamic_resources)
Note over Envoy: Envoy dynamically blocks 1.2.3.4 immediately [fillcolor="red", fontcolor="white"]

Note over Attacker, Aegis: Subsequent Request Blocked [fillcolor="lightyellow"]
Attacker->VPS: Send another request
VPS->Tunnel: Forward
Tunnel->Envoy: Deliver
Envoy--XAttacker: Drop Connection immediately (Client IP 1.2.3.4 is blocked)
Note over VPS: Legitimate users through VPS continue to work unaffected! [fillcolor="lightgreen"]
```

---

## 3. Cloudflare Tunnel Flow (HTTP Headers & AI Auto-Blocking)

This diagram illustrates how the **Cloudflare Tunnel** preserves client IPs using the **`CF-Connecting-IP`** (or `X-Forwarded-For`) HTTP header, enabling Aegis to block malicious actors without blocking the local `cloudflared` daemon container.

```text
Title: Cloudflare Tunnel Flow (HTTP Headers & AI Auto-Blocking) [fillcolor="white"]
participant Client as Attacker [fillcolor="lightgray"]
participant CF as Cloudflare Edge [fillcolor="orange"]
participant CFd as cloudflared [fillcolor="lightblue"]
participant Envoy as Envoy [fillcolor="yellow"]
participant Aegis as Aegis [fillcolor="pink"]

Note over Attacker, Aegis: Bootstrapping Phase [fillcolor="lightgreen"]
Envoy->Aegis: Connect via gRPC xDS (port 18000)
Aegis->Envoy: Push http_listener with XFF / CF Header extraction enabled

Note over Attacker, Aegis: Traffic Flow (Exploit & HTTP Header Extraction) [fillcolor="lightgreen"]
Attacker->CF: Send Exploit (Client IP: 1.2.3.4)
Note over CF: CF injects "CF-Connecting-IP: 1.2.3.4" header [fillcolor="cyan"]
CF->CFd: Forward request over outbound tunnel
CFd->Envoy: Forward HTTP request to local Envoy (Container 10080)
Note over Envoy: Envoy extracts Client IP from CF-Connecting-IP header [fillcolor="cyan"]
Envoy->Aegis: Stream Access Log (gRPC ALS) with Client IP = 1.2.3.4
Aegis->Aegis: AI Threat Engine detects exploit on 1.2.3.4
Aegis->Aegis: Auto-blocks 1.2.3.4 (saves block rule to DB) [fillcolor="red", fontcolor="white"]
Aegis->Envoy: Push updated xDS blocklist
Note over Envoy: Envoy dynamically blocks 1.2.3.4 immediately [fillcolor="red", fontcolor="white"]

Note over Attacker, Aegis: Subsequent Request Blocked [fillcolor="lightyellow"]
Attacker->CF: Send another request
CF->CFd: Forward
CFd->Envoy: Deliver
Envoy--XAttacker: Drop Connection immediately (Client IP 1.2.3.4 is blocked)
Note over CFd: Legitimate traffic passing through Cloudflare continues to work unaffected! [fillcolor="lightgreen"]
```

