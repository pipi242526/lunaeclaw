"""Reusable WebUI service helpers."""

from __future__ import annotations

import os
from pathlib import Path

from nanobot.gateway.control import (
    is_gateway_runtime_fresh,
    read_gateway_runtime_state,
)


def safe_positive_int(raw: str | None, *, default: int = 1, minimum: int = 1) -> int:
    try:
        value = int((raw or "").strip())
    except Exception:
        return default
    return value if value >= minimum else default


def evaluate_gateway_runtime_status(cfg_path: Path) -> tuple[bool, str, str]:
    """
    Validate whether WebUI and gateway share the same active runtime directory.

    Returns:
      (ready, reason_en, reason_zh)
    """
    state = read_gateway_runtime_state(cfg_path)
    if not state:
        return (
            False,
            "no gateway runtime state found in this config directory",
            "当前配置目录未发现 gateway 运行状态文件",
        )
    expected_dir = str(cfg_path.expanduser().resolve().parent)
    actual_dir = str(state.get("dataDir") or "").strip()
    if not actual_dir or actual_dir != expected_dir:
        return (
            False,
            "gateway data directory mismatch",
            "gateway 数据目录不一致",
        )
    raw_poll = (os.environ.get("NANOBOT_GATEWAY_RELOAD_POLL_SECONDS") or "2.0").strip()
    try:
        poll_seconds = max(0.5, float(raw_poll))
    except ValueError:
        poll_seconds = 2.0
    max_age = max(6.0, poll_seconds * 3.0 + 2.0)
    if not is_gateway_runtime_fresh(state, max_age_seconds=max_age):
        status = str(state.get("status") or "unknown")
        return (
            False,
            f"gateway not alive in this directory (status={status})",
            f"当前目录内 gateway 未在线（status={status}）",
        )
    return (True, "ok", "正常")
