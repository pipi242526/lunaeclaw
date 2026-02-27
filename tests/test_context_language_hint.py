from pathlib import Path
from unittest.mock import MagicMock

from nanobot.agent.context import ContextBuilder


def test_detect_reply_language_prefers_chinese_for_cjk_text():
    code, rule = ContextBuilder._detect_reply_language("请读取这个pdf并总结")
    assert code == "zh-CN"
    assert "Chinese" in rule


def test_runtime_context_contains_language_hint():
    ctx = ContextBuilder._build_runtime_context("telegram", "123", current_message="帮我看天气")
    assert "Reply Language Hint: zh-CN" in ctx
    assert "Channel: telegram" in ctx
    assert "Chat ID: 123" in ctx


def test_runtime_context_contains_japan_search_locale_hint():
    ctx = ContextBuilder._build_runtime_context(None, None, current_message="帮我查一下日本AI政策最新消息")
    assert "Search Locale Hint:" in ctx
    assert "Japan-related" in ctx


def test_explicit_reply_language_preference_overrides_detection():
    ctx = ContextBuilder._build_runtime_context(
        None,
        None,
        current_message="请总结这份pdf",
        reply_language_preference="ja",
    )
    assert "Reply Language Hint: ja" in ctx


def test_detect_reply_language_prefers_japanese_when_kana_present():
    code, _ = ContextBuilder._detect_reply_language("日本のAI政策をまとめて")
    assert code == "ja"


def test_detect_reply_language_uses_fallback_when_ambiguous():
    code, _ = ContextBuilder._detect_reply_language("12345 ???", fallback_language="en")
    assert code == "en"


def test_runtime_context_contains_korea_search_locale_hint():
    ctx = ContextBuilder._build_runtime_context(None, None, current_message="帮我查韩国半导体最新政策")
    assert "Search Locale Hint:" in ctx
    assert "Korea-related" in ctx


def test_build_messages_trims_history_by_char_budget(tmp_path: Path):
    ctx = ContextBuilder(tmp_path, max_history_chars=360, system_prompt_cache_ttl_seconds=0)
    history = [
        {"role": "user", "content": "u1 " * 40},
        {"role": "assistant", "content": "a1 " * 40},
        {"role": "user", "content": "u2 " * 40},
        {"role": "assistant", "content": "a2 " * 40},
    ]
    messages = ctx.build_messages(history=history, current_message="new message")
    trimmed_history = messages[1:-1]
    assert len(trimmed_history) == 2
    assert trimmed_history[0]["role"] == "user"
    assert "u2" in trimmed_history[0]["content"]


def test_build_user_content_skips_oversized_inline_image(tmp_path: Path):
    img = tmp_path / "large.png"
    img.write_bytes(b"0" * 64)
    ctx = ContextBuilder(tmp_path, max_inline_image_bytes=10)
    content = ctx._build_user_content("read this", [str(img)])
    assert isinstance(content, str)
    assert "Large images skipped for inline vision" in content
    assert str(img) in content


def test_system_prompt_uses_ttl_cache(tmp_path: Path):
    ctx = ContextBuilder(tmp_path, system_prompt_cache_ttl_seconds=60)
    ctx._load_bootstrap_files = MagicMock(return_value="")
    ctx.memory.get_memory_context = MagicMock(return_value="")
    ctx.skills.get_always_skills = MagicMock(return_value=[])
    ctx.skills.build_skills_summary = MagicMock(return_value="")

    first = ctx.build_system_prompt()
    second = ctx.build_system_prompt()

    assert first == second
    assert ctx._load_bootstrap_files.call_count == 1


def test_compact_background_text_uses_structural_summary(tmp_path: Path):
    ctx = ContextBuilder(
        tmp_path,
        max_background_context_chars=220,
        auto_compact_background=True,
        system_prompt_cache_ttl_seconds=0,
    )
    text = "\n".join(
        [
            "# Title",
            "IMPORTANT: this line should remain",
            "- bullet one",
            "do not skip this policy",
            "plain text " * 40,
        ]
    )
    compacted = ctx._compact_background_text(text, 220, label="test background")
    assert len(compacted) <= 220
    assert "auto-compacted" in compacted
    assert "IMPORTANT" in compacted
