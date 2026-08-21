# Configuration Reference

Every setting the installer asks for, what it does, and what breaks if it is
wrong. Each one can also be supplied up front as an environment variable, so the
same install can be driven by hand or by a provisioning system.

```bash
curl -fsSL https://aegis.jerxie.com/install.sh | sh
```

The installer walks through the settings in the first table below. Press Enter to
accept the value in `[brackets]`. Nothing is written to disk until you confirm at
the summary, and nothing is written at all if a name or port collides and you
decline the alternative it offers.

---

## Installer settings

| Prompt | Environment variable | Default | What it does |
|---|---|---|---|
| Install directory | `AEGIS_DIR` | `./aegis` | Where `docker-compose.yml` is written. Holds **no data** — the database lives in a Docker volume — so it is safe to move or delete later. It is also where you edit everything below after install. |
| Admin username | `AEGIS_ADMIN_USER` | `admin` | The first account, created on first boot. |
| Admin password | `AEGIS_ADMIN_PASS` | *generated* | Random 20 characters. **Shown once**, and written into `docker-compose.yml` — that file is the only copy. There is no password-reset flow yet. |
| AGENT_HOST | `AEGIS_AGENT_HOST` | *this machine's LAN IP* | The address nodes dial back on. See [the warning below](#agent_host-the-one-that-fails-silently). |
| Hub UI port | `AEGIS_UI_PORT` | `8765` | Web interface and REST API. |
| Agent control channel | `AEGIS_AGENT_PORT` | `8766` | Nodes dial **in** here over mTLS. |
| Gateway HTTP | `AEGIS_HTTP_PORT` | `80` | Reverse proxy for apps you expose. |
| Gateway HTTPS | `AEGIS_HTTPS_PORT` | `443` | Same, with TLS. Must be free for certificate issuance. |
| Envoy admin UI | `AEGIS_ADMIN_PORT` | `9901` | Envoy diagnostics. Safe to move. |
| STUN | `AEGIS_STUN_PORT` | `3478/udp` | NAT traversal for nodes not on this LAN. |
| WireGuard | `AEGIS_WG_PORT` | `51820/udp` | Carries overlay traffic to remote nodes. |

Three more affect the installer itself rather than the install:

| Variable | Default | What it does |
|---|---|---|
| `AEGIS_YES` | unset | `1` accepts every default and asks nothing. Use for unattended installs. |
| `AEGIS_REPO` | GitHub raw | Where to fetch the compose files from. Point it at a fork, an internal mirror, or a local directory (`file:///path`) on a machine with no route to GitHub. |
| `NO_COLOR` | unset | Set to disable colour and the spinner. Colour is already suppressed automatically when output is not a terminal. |

### AGENT_HOST: the one that fails silently

When you enrol a machine, the join token **embeds this address**, and the node
dials it to reach the hub. Get it wrong and the installer on that node still
reports success — the node simply never appears in the fleet, with no error
pointing at the cause.

It must resolve **from the node**, not from the hub:

- **LAN nodes** — the hub's LAN IP, e.g. `192.168.1.10`.
- **Nodes across the internet** — a public DNS name that resolves publicly.
- **Gateway-only install**, never enrolling machines — leave it blank.

You can change it later in `docker-compose.yml` and `docker compose up -d`, but
tokens generated **before** the change still carry the old address. Reissue them.

---

## Hub settings

Everything in the `environment:` block of `docker-compose.yml`. Edit and
`docker compose up -d` to apply.

| Variable | Default | What it does |
|---|---|---|
| `ADMIN_USERNAME` | `admin` | First admin account. |
| `ADMIN_PASSWORD` | `changeme` | Its password. The installer replaces this with a generated one; change it by hand if you installed manually. |
| `AUTH_ENABLED` | `true` | Authentication for the UI and API. Turning this off makes the control plane fully open — only sane on an isolated bench. |
| `BLOCK_ENABLED` | `true` | Lets the anomaly detector actually block traffic rather than only report it. |
| `NODE_ID` | `home` | Identifier for this hub in multi-site setups. |
| `DATA_DIR` | `/data` | Database, artifacts and image cache inside the container. Backed by the `aegis_data` volume — back **this** up, not the install directory. |
| `HUB_EXTERNAL_HOST` | unset | The address nodes dial back on. Formerly `AGENT_HOST`, which is still honoured and logs a deprecation on every boot. |
| `HUB_EXTERNAL_PORT` | `443` | Port that goes with it, for nodes reaching the hub through a proxy or gateway. |
| `HUB_INTERNAL_PORT` | `8765` | Port the hub listens on **inside** the container. Changing the published port on the left of `8765:8765` does not require touching this. |
| `HUB_INTERNAL_AGENT_PORT` | `8766` | Same, for the agent mTLS channel. |
| `HUB_INTERNAL_HOSTS` | auto | Addresses the hub advertises to nodes on the local network, when auto-detection picks the wrong interface. |
| `AEGIS_JWT_SECRET` | generated | HS256 signing key for sessions. Set it explicitly to keep sessions valid across a rebuild, or to share it between hubs. |
| `LOG_PATH` | unset | Access log to ingest. Leave unset unless you are feeding Aegis an external log. |
| `SEED_DEFAULT_APPS` | `false` | Writes the built-in app definitions into the marketplace. A fresh hub ships an **empty** marketplace — you add what you want, when you want it. Set `true` for the old starter catalog. |
| `PREWARM_APP_IMAGES` | `false` | Pulls every catalog app's image at boot. Off by default because it cost a fresh install ~2.4 GB before the operator had asked for anything. Set `true` when staging a hub that is about to be disconnected. |

Older names — `PUBLIC_DOMAIN`, `HTTP_BASE`, `AGENT_ENDPOINTS`, `AGENT_PORT`,
`PORT` — are still accepted and log a deprecation naming their replacement.

---

## Ports

| Port | Protocol | Direction | Needed when |
|---|---|---|---|
| `8765` | TCP | you → hub | Always. UI and API. |
| `8766` | TCP | node → hub | Enrolling machines. Without it a join token is issued and can never be used. |
| `80` | TCP | internet → gateway | Exposing apps over HTTP. |
| `443` | TCP | internet → gateway | Exposing apps over HTTPS, and issuing certificates. |
| `9901` | TCP | you → Envoy | Diagnostics only. |
| `3478` | UDP | node ↔ hub | Nodes not on this LAN — discovers the network path. |
| `51820` | UDP | node ↔ hub | Nodes not on this LAN — carries the traffic. |

A single-host gateway install needs only `8765`, `80` and `443`.

---

## Examples

Unattended, everything specified:

```bash
curl -fsSL https://aegis.jerxie.com/install.sh -o install.sh
AEGIS_YES=1 \
AEGIS_DIR=/opt/aegis \
AEGIS_ADMIN_USER=ops \
AEGIS_ADMIN_PASS='...' \
AEGIS_AGENT_HOST=hub.example.com \
sh install.sh
```

Ports moved out of the way of an existing web server:

```bash
AEGIS_HTTP_PORT=8080 AEGIS_HTTPS_PORT=8443 \
  curl -fsSL https://aegis.jerxie.com/install.sh | sh
```

No route to GitHub — serve the compose files from anywhere:

```bash
AEGIS_REPO=file:///media/usb/aegis \
  sh install.sh
```

---

## Afterwards

- Settings live in `<install dir>/docker-compose.yml`; `docker compose up -d` applies changes.
- Data lives in the `aegis_data` Docker volume; that is what to back up.
- Logs: `docker compose logs aegis`.
- The marketplace starts empty — add apps from the **Add App** form, by pasting a
  `docker run` command or a compose file, or by asking Owl.
