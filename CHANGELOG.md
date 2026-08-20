# Changelog

All notable changes to Aegis are documented here.

## [1.3] — 2026-08-20

The release where Aegis stopped being a gateway with extras and became a
platform. Three months of work; the highlights only.

### Fleet & provisioning

- **Bare metal, end to end** — Redfish/BMC power control, UEFI HTTP Boot with no
  L2 adjacency required, serial console, and libvirt/KVM provisioning with
  cloud-init. Power on an unracked server and finish with it in a cluster.
- **BMC discovery that discriminates** — a sweep no longer lists every host with
  443 open. Candidates are labelled with the fleet member already at that
  address, and proven negatives fold out of the way.
- **Node join tells the truth** — enrolment is recorded as an event, rejected
  agents are reported with the reason and the fix instead of failing silently
  every 30 seconds, and re-running the installer archives the old identity
  rather than fighting it.
- **Idempotent repair** — `curl -fsSL https://<hub>/reinstall.sh | sudo bash` is
  safe to run anywhere: it compares digests and does nothing if the node is
  already current. Agent upgrades verify the download and arm a systemd
  auto-rollback before replacing the binary.
- **Fleet activity log** with per-row prune, and location badges that classify
  every node as LAN, cloud, mesh, remote or pending.

### Kubernetes

- **Full lifecycle via a reconciler** — create, scale, upgrade, back up, restore
  and tear down, on k3s or kubeadm.
- **Air-gapped installs validated live** — a 5-node HA cluster brought up with no
  egress at all.
- In-browser kubectl console and one-click Expose.

### Models & data (Depot)

- **Catalogue** for models and datasets with versions, digests, lineage and
  per-owner quotas; HuggingFace and URL pull-through ingest with progress and
  gated-model secrets.
- **LAN staging** — the hub egresses once and nodes pull from the hub, so a node
  with no internet access can still receive a 57.9 GB model.
- **Pluggable storage backends** — keep artifact bytes on the hub's own disk, a
  mounted NAS share, or your own cloud bucket. Switched at runtime from
  Settings → Storage, no redeploy, and previously used backends stay readable so
  a switch never orphans what you already had.
- **Reference-only artifacts** — catalogue what you already hold without copying
  it. A 57 GB repository registers in seconds having downloaded nothing, and
  costs nothing against quota.

### Workloads

- GPU-aware scheduling with eviction and sweeps, managed volumes with a file
  browser and write API, notebooks, serving, and promote-a-result into the
  catalogue.

### Owl / AI operations

- Owl acts through **risk-classified tools** with indirect prompt-injection
  defences, and has deployed and configured Prometheus end to end unattended.
- Owl affordances hide themselves when no model key is configured, rather than
  offering actions that cannot work.

### Security

- **Auth middleware rewritten.** The old public-route list matched by path
  prefix and ignored the HTTP method, which silently exempted every sub-path and
  every method beneath a public entry. Public routes are now exact
  (method, prefix) pairs. Regression tests lock this in and run on every push.
- Per-node client certificates issued by the hub's own CA, with the agent
  pinning the CA fingerprint; encrypted secret store for tokens and credentials.

### Project

- CI on every push: build, vet and the full Go test suite, plus a frontend
  type-check and a check that fails the build if a React component nothing
  imports would ship unreachable.
- Public documentation site at **[aegis.jerxie.com](https://aegis.jerxie.com)**,
  with an assistant that answers from this documentation — including the parts
  about what Aegis cannot do yet.

### Known gaps

Stated plainly rather than left to be discovered: single operator account (no
multi-user or RBAC), no control-plane HA, training not yet modelled as a managed
workload, and scale validated at nine nodes.

## [1.1.0] — 2026-05-23

### Gateway — Protection

- **Styled error pages** — 403 (RBAC block) and 429 (rate limit) responses now serve a dark HTML page instead of a bare status code. Customisable contact / appeal message. Can be previewed inline before saving.
- **Maintenance mode** — Put any listener (or individual SNI filter chains) into a 503 "We'll be back shortly" page with one click. Full per-domain granularity: `https_listener:app.example.com` puts only that domain into maintenance while leaving every other domain online.
- **Dynamic preview** — Block page and maintenance page previews render in an inline iframe that auto-refreshes as you type the contact message. No save required to see the result.
- **Multi-SNI display** — Maintenance panel now shows all SNI names for each filter chain (e.g. `nas, nas.example.com`) so multi-SNI chains are fully visible.
- **Protection section** moved above Topology in the Gateway navigation.

### Owl / MCP

- `gateway_set_maintenance` now understands three key formats:
  - `["*"]` — every listener
  - `["<listener>"]` — every filter chain in that listener
  - `["<listener>:<sni>"]` — a single filter chain by SNI/domain
- `gateway_list_listeners` returns `filter_chains` with per-chain `sni_domains` so Owl can discover exact SNI keys before targeting a domain.
- MCP tool descriptions and incident response procedure updated; setup-specific defaults removed.

### Bug fixes

- Fixed Envoy NACK caused by invalid `ResponseFlagFilter` flag values (`"RBAC"`, `"RL"`) not present in Envoy 1.35's allowlist — replaced with `StatusCodeFilter` matching by HTTP status code.
- Fixed `SubstitutionFormatString` deprecation warning in Envoy 1.35 — migrated from `text_format` to `text_format_source` / `DataSource_InlineString`.

### UI

- All hardcoded hex colors in the Gateway panel replaced with CSS theme variables — Protection cards, rate limit panel, block pages panel, and maintenance panel now adapt correctly to dark, dim, slate, and light themes.

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
