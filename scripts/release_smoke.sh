#!/usr/bin/env bash
set -euo pipefail

ROOT_DIR="$(cd "$(dirname "${BASH_SOURCE[0]}")/.." && pwd)"
cd "$ROOT_DIR"

echo "==> release smoke: compile checks"
python3 -m py_compile \
  orbitclaw/agent/context.py \
  orbitclaw/agent/loop.py \
  orbitclaw/agent/subagent.py \
  orbitclaw/agent/tools/media.py \
  orbitclaw/agent/tools/export.py \
  orbitclaw/agent/tools/web.py \
  orbitclaw/cli/commands.py \
  orbitclaw/config/schema.py \
  orbitclaw/webui/server.py

echo "==> release smoke: focused tests"
if command -v uv >/dev/null 2>&1; then
  uv run --extra dev pytest -q \
    tests/test_budget_utils.py \
    tests/test_context_language_hint.py \
    tests/test_files_hub_tool.py \
    tests/test_export_file_tool.py \
    tests/test_web_fetch_tool.py
else
  python3 -m pytest -q \
    tests/test_budget_utils.py \
    tests/test_context_language_hint.py \
    tests/test_files_hub_tool.py \
    tests/test_export_file_tool.py \
    tests/test_web_fetch_tool.py
fi

echo "==> release smoke: config/status sanity"
if command -v orbitclaw >/dev/null 2>&1; then
  orbitclaw status >/tmp/orbitclaw_status_smoke.txt
  orbitclaw doctor >/tmp/orbitclaw_doctor_smoke.txt
  echo "status: /tmp/orbitclaw_status_smoke.txt"
  echo "doctor: /tmp/orbitclaw_doctor_smoke.txt"
else
  echo "orbitclaw CLI not found in PATH, skipped status/doctor runtime checks."
fi

echo "==> release smoke: PASS"
