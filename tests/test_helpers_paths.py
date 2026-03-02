from pathlib import Path

from orbitclaw.utils.helpers import get_data_path, get_workspace_path


def test_data_path_uses_env_override(monkeypatch, tmp_path):
    custom = tmp_path / "nb-data"
    monkeypatch.setenv("ORBITCLAW_DATA_DIR", str(custom))
    resolved = get_data_path()
    assert resolved == custom
    assert resolved.exists()


def test_workspace_defaults_under_data_dir(monkeypatch, tmp_path):
    custom = tmp_path / "nb-data"
    monkeypatch.setenv("ORBITCLAW_DATA_DIR", str(custom))
    workspace = get_workspace_path()
    assert workspace == custom / "workspace"
    assert workspace.exists()


def test_data_path_supports_relative_override(monkeypatch, tmp_path):
    monkeypatch.setenv("HOME", str(tmp_path))
    monkeypatch.setenv("ORBITCLAW_DATA_DIR", "orbitclaw-runtime")
    resolved = get_data_path()
    assert resolved == Path(tmp_path) / "orbitclaw-runtime"
