# Upstream Patch Audit Policy

This project is now an independent fork and uses **scheduled upstream sync windows**.

## Goal

Apply only high-value upstream patches (security, correctness, data integrity, context safety) while preserving fork-specific product direction.

## Cadence

- Run one audit window per month.
- Optional emergency window for disclosed security issues.

## Required Inputs

- Upstream base ref (for example: `origin/main`)
- Fork ref (for example: `codex/dev`)
- Upstream release notes since last audit

## Decision Rules

A patch is `ACCEPT` when at least one condition holds:

1. Security hardening or data corruption prevention
2. Reduces hallucination risk via context/session correctness
3. Fixes protocol-level compatibility issues
4. Improves reliability without large architecture drift

A patch is `REJECT` when any condition holds:

1. Conflicts with fork iron laws (resource/output/interface/config/extension)
2. Introduces heavy dependencies or runtime bloat
3. Requires broad product behavior changes without matching value

`DEFER` means revisit in next audit window.

## Output Requirement

Every release must include one audit report file under:

- `release/upstream-audits/YYYY-MM.md`

Each audited patch must include:

- status: `ACCEPT` / `REJECT` / `DEFER`
- reason
- risk note
- follow-up action (if any)

## Helper Command

Generate monthly audit skeleton:

```bash
python scripts/upstream_patch_audit.py --upstream origin/main --target codex/dev --month 2026-03
```
