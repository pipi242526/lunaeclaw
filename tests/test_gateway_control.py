from __future__ import annotations

import time
from pathlib import Path

from orbitclaw.gateway.control import (
    compute_runtime_config_fingerprint,
    is_gateway_runtime_fresh,
    read_gateway_runtime_state,
    write_gateway_runtime_state,
)


def _prepare_home(monkeypatch, tmp_path: Path) -> Path:
    monkeypatch.setenv("HOME", str(tmp_path))
    root = tmp_path / ".orbitclaw"
    (root / "env").mkdir(parents=True, exist_ok=True)
    return root


def test_runtime_fingerprint_changes_with_config_update(monkeypatch, tmp_path):
    root = _prepare_home(monkeypatch, tmp_path)
    config = root / "config.json"
    config.write_text('{"agents":{"defaults":{"model":"a"}}}', encoding="utf-8")
    first = compute_runtime_config_fingerprint(config)
    config.write_text('{"agents":{"defaults":{"model":"b"}}}', encoding="utf-8")
    second = compute_runtime_config_fingerprint(config)
    assert first != second


def test_runtime_fingerprint_changes_with_env_helper_update(monkeypatch, tmp_path):
    root = _prepare_home(monkeypatch, tmp_path)
    config = root / "config.json"
    env_file = root / ".env"
    config.write_text('{"providers":{"openai":{"apiKey":"${OPENAI_API_KEY}"}}}', encoding="utf-8")
    env_file.write_text("OPENAI_API_KEY=a\n", encoding="utf-8")
    first = compute_runtime_config_fingerprint(config)
    env_file.write_text("OPENAI_API_KEY=b\n", encoding="utf-8")
    second = compute_runtime_config_fingerprint(config)
    assert first != second


def test_runtime_fingerprint_honors_explicit_env_files(monkeypatch, tmp_path):
    root = _prepare_home(monkeypatch, tmp_path)
    config = root / "config.json"
    explicit = tmp_path / "extra.env"
    config.write_text("{}", encoding="utf-8")
    explicit.write_text("X=1\n", encoding="utf-8")
    monkeypatch.setenv("ORBITCLAW_ENV_FILES", str(explicit))
    first = compute_runtime_config_fingerprint(config)
    explicit.write_text("X=2\n", encoding="utf-8")
    second = compute_runtime_config_fingerprint(config)
    assert first != second


def test_gateway_runtime_state_roundtrip(monkeypatch, tmp_path):
    root = _prepare_home(monkeypatch, tmp_path)
    config = root / "config.json"
    config.write_text("{}", encoding="utf-8")
    write_gateway_runtime_state(config, fingerprint="abc", status="running", note="ok")
    state = read_gateway_runtime_state(config)
    assert isinstance(state, dict)
    assert state["status"] == "running"
    assert state["fingerprint"] == "abc"


def test_gateway_runtime_state_freshness():
    assert is_gateway_runtime_fresh({"status": "running", "updatedAt": time.time()}, max_age_seconds=3)
    assert not is_gateway_runtime_fresh({"status": "stopped", "updatedAt": time.time()}, max_age_seconds=3)
    assert not is_gateway_runtime_fresh({"status": "running", "updatedAt": time.time() - 100}, max_age_seconds=3)
