"""Gateway runtime control helpers."""

from __future__ import annotations

import hashlib
import os
from pathlib import Path


def discover_runtime_env_files() -> list[Path]:
    """Return env helper files that affect config interpolation."""
    explicit = os.environ.get("NANOBOT_ENV_FILES", "").strip()
    files: list[Path] = []
    if explicit:
        for raw in explicit.split(os.pathsep):
            p = Path(raw).expanduser()
            if p.exists() and p.is_file():
                files.append(p)
        return files

    from nanobot.utils.helpers import get_env_dir, get_env_file

    primary = get_env_file()
    if primary.exists() and primary.is_file():
        files.append(primary)
    env_dir = get_env_dir()
    if env_dir.exists() and env_dir.is_dir():
        files.extend(sorted(p for p in env_dir.glob("*.env") if p.is_file()))
    return files


def compute_runtime_config_fingerprint(config_path: Path) -> str:
    """
    Build a stable fingerprint from config.json and env helper files.

    The gateway uses this to detect runtime-affecting changes and trigger a
    safe in-process reload.
    """
    hasher = hashlib.sha256()
    seen: set[Path] = set()
    files = [config_path, *discover_runtime_env_files()]
    for raw_path in files:
        path = raw_path.expanduser().resolve()
        if path in seen:
            continue
        seen.add(path)
        hasher.update(str(path).encode("utf-8"))
        hasher.update(b"\0")
        if not path.exists() or not path.is_file():
            hasher.update(b"MISSING")
            hasher.update(b"\0")
            continue
        try:
            hasher.update(hashlib.sha256(path.read_bytes()).digest())
        except OSError as e:
            hasher.update(f"READ_ERROR:{e}".encode("utf-8", errors="replace"))
        hasher.update(b"\0")
    return hasher.hexdigest()

