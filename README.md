<div align="center">
  <img src="assets/orbitclaw-banner.svg" alt="OrbitClaw banner" width="900" />
</div>

# OrbitClaw

OrbitClaw is a lightweight, Chinese-first agent runtime for practical personal automation.

- TG-first channel experience
- MCP/Skill extensibility with low coupling
- Resource-budgeted runtime for small servers (1C1G oriented)
- Web console for day-to-day ops

## 1. Project Identity

OrbitClaw is an independently maintained project built on top of upstream work.

- Current brand: **OrbitClaw**
- Web UI brand: **OrbitClaw Console**
- Python package namespace: `orbitclaw`
- CLI command: `orbitclaw`
- Default runtime home: `~/.orbitclaw`

## 2. Upstream Attribution

This project is based on [HKUDS/nanobot](https://github.com/HKUDS/nanobot) and continues under MIT-compatible terms.

- Upstream project: `HKUDS/nanobot`
- License: MIT (`LICENSE`)
- Attribution notice: `NOTICE`

## 3. Core Design Rules (Iron Laws)

- Resource law: memory/token/timeout/queue all have explicit budgets.
- Output law: unified language policy, no internal tool-call leakage, actionable failure replies.
- Interface law: one message contract; channels map protocol only.
- Config law: env-first secrets, plaintext minimized, changes rollbackable.
- Extension law: new channels/MCP/skills should avoid invasive core-loop edits.
- Evolution law: every release includes upstream patch audit decisions.
- Quality law: new/changed code must pass tests and incremental lint.

## 4. Install

```bash
git clone <your-orbitclaw-repo-url>
cd orbitclaw
pip install -e .
```

## 5. Quick Start

### 5.1 Bootstrap

```bash
orbitclaw onboard
```

### 5.2 Configure model endpoint

Edit `~/.orbitclaw/config.json`:

```json
{
  "providers": {
    "endpoints": {
      "ohmygpt": {
        "type": "openai_compatible",
        "apiBase": "${OHMYGPT_API_BASE}",
        "apiKey": "${OHMYGPT_API_KEY}",
        "models": ["gemini-2.5-flash-lite"]
      }
    }
  },
  "agents": {
    "defaults": {
      "model": "ohmygpt/gemini-2.5-flash-lite",
      "temperature": 0.1
    }
  }
}
```

Put secrets in `~/.orbitclaw/.env`:

```bash
OHMYGPT_API_BASE=https://api.ohmygpt.com/v1
OHMYGPT_API_KEY=sk-xxx
```

### 5.3 Run gateway

```bash
orbitclaw gateway
```

### 5.4 Open Web UI

```bash
orbitclaw webui --host 0.0.0.0 --port 18791
```

Web UI uses URL path-token access (no password popup).

## 6. Recommended Runtime Stack

- Primary channel: Telegram
- Search: Exa MCP (`EXA_API_KEY`)
- Document parsing: Document Loader MCP
- Deployment: Docker or systemd

## 7. Runtime Directory Layout

- Config: `~/.orbitclaw/config.json`
- Env file: `~/.orbitclaw/.env`
- Env helper dir: `~/.orbitclaw/env/`
- Workspace: `~/.orbitclaw/workspace`
- MCP home: `~/.orbitclaw/mcp`
- Skills dir: `~/.orbitclaw/skills`
- Media dir: `~/.orbitclaw/media`
- Exports dir: `~/.orbitclaw/exports`

## 8. Governance and Release Process

- Upstream audit policy: `release/UPSTREAM_PATCH_AUDIT.md`
- Monthly upstream audit records: `release/upstream-audits/`
- Incremental quality gate: `release/QUALITY_GATE.md`
- Release checklist: `release/RELEASE_CHECKLIST.md`

## 9. Branding Assets

- Icon: `assets/orbitclaw-icon.svg`
- Banner: `assets/orbitclaw-banner.svg`

## 10. License

MIT. See `LICENSE` and `NOTICE`.
