# Aegis Traffic Demo Generator

This directory contains the **Aegis Traffic Demo Generator** (`demo_generator.py`), a self-contained Python utility designed to simulate realistic, dynamic global traffic to your Envoy gateway.

It is designed to populate the Aegis monitoring dashboard with live metrics, world map indicators, device breakdowns, and to showcase **Aegis's AI Auto-Blocking capabilities** in real-time without requiring real external traffic.

---

## How It Works

The script is completely self-contained and has **zero external dependencies** (it runs using standard Python built-in libraries). 

Instead of using high-level HTTP clients which hide connection layers, the generator opens raw TCP connections directly to Envoy (host port `80`/container port `10080`) and injects **PROXY Protocol v1 headers** before sending the HTTP payload.

### The Packet Flow
```
[demo_generator.py] 
       │ 
       ├─ 1. Open Raw TCP socket to localhost:80 (Envoy:10080)
       ├─ 2. Prepend: "PROXY TCP4 <random_global_ip> 127.0.0.1 <random_port> 10080\r\n"
       └─ 3. Send HTTP payload: "GET /api/v1/products HTTP/1.1\r\nHost: app.yourdomain.com\r\n..."
```

*   **World Map Populating (GeoIP Spoofing):** By injecting the PROXY header, Envoy is forced to override the downstream client IP with our fake global IP at the connection layer. This enables MaxMind GeoIP to plot requests from USA, Germany, Japan, Brazil, and Australia on your dashboard map.
*   **Realistic UI Metrics:** Randomly cycles through various User-Agents (iPhone Safari, Android Chrome, Desktop Chrome, Googlebot, curl) to populate the device breakdown charts.

---

## The Three Simulated Traffic Scenarios

The script spins up three concurrent, background threads running distinct scenarios to create a realistic traffic profile:

### 1. Legitimate Traffic Loop (🟢 Green Dashboard)
*   Simulates normal, global users browsing your site.
*   Sends steady requests to healthy endpoints (`/`, `/index.html`, `/api/v1/products`) with random Poisson intervals (0.1s to 0.8s) so the real-time UI graphs look wavy and natural.

### 2. The Vulnerability Scanner Bot (🟡 Yellow Dashboard)
*   Simulates a noisy malicious bot crawling your server looking for common administrative vulnerabilities.
*   Rapidly probes endpoints like `/wp-admin`, `/phpmyadmin`, `/.env`, and `/secrets.json` from a dedicated German hosting IP.
*   Generates `403 Forbidden` and `404 Not Found` status code spikes in the charts.

### 3. The Hacker Attack (🔴 Red Dashboard - AI Auto-Blocking)
*   An attacker IP (`99.99.99.99`) launches a web exploit (e.g., SQL Injection, Path Traversal, or Log4Shell).
*   **Watch the Dashboard:**
    1.  Aegis logs the attack via the Access Log Service (ALS).
    2.  Aegis's AI Threat Engine detects the exploit pattern on `99.99.99.99`.
    3.  Aegis dynamically **creates a block rule and pushes it to Envoy via xDS**.
    4.  The script continues to send requests from `99.99.99.99`.
    5.  **Instant Block Visualized:** You will see the attacker's requests immediately start failing (`connection dropped`) in the dashboard, proving the real-time, reactive protection works!

---

## Prerequisites & Running

1.  Ensure your gateway is running:
    ```bash
    docker compose up -d
    ```
2.  Import the **`configs/demo.json`** baseline configuration in your Aegis Dashboard (`http://localhost:8765 -> Gateway -> Import`).
    *   *Note: Do not use `starter.json` for this test. `demo.json` has the PROXY Protocol filter pre-enabled on Envoy's HTTP listener so it expects and parses the generator's spoofed IP headers.*
3.  Run the generator:
    ```bash
    python3 scripts/demo_generator.py
    ```
4.  Open the Aegis dashboard and enjoy the show! Press `Ctrl+C` in your terminal to stop the generator at any time.
