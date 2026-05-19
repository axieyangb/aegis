# Changelog

All notable changes to Aegis are documented here.

## [1.0.0] — 2026-05-19

### Initial release

**Gateway**
- Envoy xDS control plane — manage listeners, clusters, filter chains, secrets via UI
- Visual filter chain editor with domain/SNI routing, TLS, WebSocket, and HTTP extension support
- Usage badges on clusters and extension configs showing how many filter chains reference them
- Import/export gateway configuration as JSON
- Topology view showing gateway layout

**Security**
- Real-time IP blocking with manual and automatic modes
- Detection rules: rate flood, 404 scan, path scan, bad user-agent, 5xx flood, attack path instant response
- Trusted IP whitelist (never auto-blocked)
- Delegated analysis mode — forward IPs to an external analysis server

**AI & Intelligence**
- Background IP classification using Gemini, Claude, GPT, DeepSeek, or Ollama
- Per-IP profiles with threat score, confidence, classification reasons, and AI summary
- IP enrichment: ASN/ISP, PTR record, VPN/proxy/Tor detection, AbuseIPDB reputation
- Owl AI chat assistant — ask about traffic, threats, and gateway configuration in plain language
- Owl Patrol — autonomous scheduled threat sweep with configurable notification on findings
- Ask Owl buttons on every dashboard card and config form for contextual AI help

**Certificates**
- ACME automation: Let's Encrypt, ZeroSSL, custom ACME CAs
- HTTP-01 and DNS-01 (Cloudflare, Route53, GoDaddy) challenges
- Manual PEM upload
- Auto-renewal 30 days before expiry, pushed to Envoy via SDS (zero downtime)

**Analytics**
- Live request feed with method, path, status, latency, country, user-agent
- Traffic timeline chart
- Top IPs panel with geo, ASN, and block status
- World map with request density
- Device type and HTTP status code breakdowns
- Domain traffic distribution
- Historical mode (daily summaries) for 30d, 90d, 180d, 1y ranges

**Notifications**
- Telegram bot and webhook (Discord, Slack, generic) channels
- Per-event toggle: IP blocked, DDoS pattern, error spike, cert expiry, daily digest
- Notification suppression / dedup with follow-up summary
- Event log with retry-on-failure
- Daily digest with optional AI narrative

**Auth**
- Built-in username/password login
- OIDC/SSO (Google, Authentik, Keycloak, any OIDC provider)
- Optional: disable password login (SSO-only mode)

**Geo**
- Remote geo lookup via ip-api.com (free, 45 req/min)
- Local geo lookup via MaxMind GeoLite2-City.mmdb (no rate limits)

**Other**
- Three UI themes: Dark, GitHub, Slate (light)
- Responsive design — works on mobile
- System resource monitor in sidebar (CPU, memory, network)
- WebMCP browser extension support (18 registered tools)
- Multi-arch Docker image: linux/amd64 + linux/arm64
