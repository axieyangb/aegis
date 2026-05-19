# AI Setup

Aegis has two AI features: **Intelligence Review** (background IP threat classification) and **Owl Chat** (conversational assistant).

Both are optional. If no API key is configured, all other Aegis features work normally.

## Supported providers

| Provider | Model examples | Notes |
|---|---|---|
| **Gemini** (Google) | `gemini-2.0-flash`, `gemini-1.5-pro` | Free tier available |
| **Claude** (Anthropic) | `claude-haiku-4-5-20251001`, `claude-sonnet-4-6` | Fast haiku models work well |
| **OpenAI** | `gpt-4o-mini`, `gpt-4o` | GPT-4o-mini is cost-effective |
| **DeepSeek** | `deepseek-chat` | Good value |
| **Ollama** | `qwen2.5:7b`, `llama3.2:3b` | Fully local, no API key |

## Intelligence Review

Runs background sweeps every N minutes. Any IP with enough requests gets sent to the AI for classification:

- **Type**: `human`, `bot`, `crawler`, `scanner`, `attacker`
- **Threat score**: 0.0–1.0
- **Auto-block**: IPs above the block threshold are blocked automatically

### Configure in Settings → AI → Intelligence Review

1. Toggle **Enable AI Review**
2. Select provider and model
3. Enter API key
4. Set sweep interval (default: 5 min)
5. Set alert threshold (default: 0.35) and block threshold (default: 0.65)
   - Alert < Block is required

### IP Enrichment

Aegis optionally queries external databases before sending data to the AI, improving classification accuracy:

| Source | Data | Cost |
|---|---|---|
| DNS PTR | Reverse DNS, verifies Googlebot etc. | Free |
| ip-api.com | ASN, ISP, VPN/proxy/Tor/datacenter flags | Free, 45 req/min |
| Known bot CIDRs | Google, Bing crawler ranges | Free |
| AbuseIPDB | Community abuse reports, confidence score | Free tier: 1,000/day |

## Owl Chat

A conversational assistant that can read your live gateway state and take actions (block IPs, explain traffic, review configs, walk through setup procedures).

### Configure in Settings → AI → Owl Chat Agent

- Toggle **Enable Owl Chat**
- Leave provider/model/key blank to reuse Intelligence Review settings
- Or set a separate provider (e.g. a faster/cheaper model for chat)

### What Owl can do

- Answer questions about traffic patterns and security events
- Look up IP profiles, explain threat scores
- Block or unblock IPs
- Review gateway configuration for issues
- Walk you through procedures (add a domain, set up HTTP-01, configure OIDC)
- Analyse patrol sweep results

### Custom knowledge

Mount a file at `/data/skills/site.md` to inject custom context into every Owl conversation — useful for documenting your server layout, special rules, or preferred procedures.

## Owl Patrol

Autonomous scheduled sweeps. Owl analyses recent traffic patterns and sends a notification if it finds something concerning.

Configure in **Integrations → Owl Patrol** (requires at least one notification channel).
