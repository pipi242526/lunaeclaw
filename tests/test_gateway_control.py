from __future__ import annotations

from pathlib import Path

from nanobot.gateway.control import compute_runtime_config_fingerprint


def _prepare_home(monkeypatch, tmp_path: Path) -> Path:
    monkeypatch.setenv("HOME", str(tmp_path))
    root = tmp_path / ".nanobot"
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
    monkeypatch.setenv("NANOBOT_ENV_FILES", str(explicit))
    first = compute_runtime_config_fingerprint(config)
    explicit.write_text("X=2\n", encoding="utf-8")
    second = compute_runtime_config_fingerprint(config)
    assert first != second
