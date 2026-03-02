"""Shared WebUI layout renderer."""

from __future__ import annotations

from html import escape


def render_page_shell(
    *,
    title: str,
    body: str,
    subtitle: str,
    nav_html: str,
    flash_html: str,
    ui_lang: str,
    lang_label: str,
    lang_options_html: str,
    copied_label: str,
    brand_name: str = "OrbitClaw Console",
) -> str:
    """Render the full HTML shell for WebUI pages."""
    return f"""<!doctype html>
<html lang="{escape(ui_lang)}">
<head>
  <meta charset="utf-8">
  <meta name="viewport" content="width=device-width, initial-scale=1">
  <title>{escape(title)} - {escape(brand_name)}</title>
  <style>
    :root {{
      --bg: #f2efe8;
      --card: #fffdf8;
      --ink: #1f2328;
      --muted: #5b6470;
      --line: #d7d0c2;
      --accent: #0f6c5c;
      --accent-2: #d96f2b;
      --err: #b42318;
      --ok: #067647;
      --shadow: 0 8px 28px rgba(31,35,40,.08);
      --mono: ui-monospace, SFMono-Regular, Menlo, Consolas, monospace;
      --sans: "Avenir Next", "PingFang SC", "Noto Sans SC", "Helvetica Neue", sans-serif;
    }}
    * {{ box-sizing: border-box; }}
    body {{
      margin: 0; padding: 0; font-family: var(--sans); color: var(--ink);
      background:
        radial-gradient(circle at 10% 10%, rgba(217,111,43,.10), transparent 40%),
        radial-gradient(circle at 90% 0%, rgba(15,108,92,.10), transparent 35%),
        var(--bg);
    }}
    .layout {{ max-width: 1200px; margin: 0 auto; padding: 18px; }}
    .top {{
      display:flex; align-items:flex-start; justify-content:space-between; gap:16px; margin-bottom:16px;
      background: linear-gradient(180deg, rgba(255,255,255,.7), rgba(255,255,255,.35));
      border:1px solid rgba(255,255,255,.9); box-shadow: var(--shadow); border-radius: 16px; padding: 14px;
      backdrop-filter: blur(6px);
    }}
    .brand h1 {{ margin:0; font-size: 22px; letter-spacing:.2px; }}
    .brand p {{ margin:6px 0 0; color: var(--muted); font-size: 13px; }}
    .nav {{ display:flex; gap:8px; flex-wrap:wrap; }}
    .nav-item {{
      text-decoration:none; color: var(--ink); border:1px solid var(--line);
      background: rgba(255,255,255,.55); padding:8px 12px; border-radius: 999px; font-size: 13px;
      transition: transform .12s ease, box-shadow .12s ease, background .12s ease;
    }}
    .nav-item:hover {{ transform: translateY(-1px); box-shadow: 0 4px 14px rgba(31,35,40,.08); }}
    .nav-item.active {{ background: var(--accent); color: #fff; border-color: var(--accent); }}
    .flash {{ border-radius: 10px; padding: 10px 12px; margin-bottom: 12px; font-size: 13px; }}
    .flash.ok {{ background: #ecfdf3; color: var(--ok); border:1px solid #abefc6; }}
    .flash.err {{ background: #fef3f2; color: var(--err); border:1px solid #fecdca; }}
    .grid {{ display:grid; gap: 14px; }}
    .grid.cols-2 {{ grid-template-columns: repeat(2, minmax(0, 1fr)); }}
    .grid.cols-3 {{ grid-template-columns: repeat(3, minmax(0, 1fr)); }}
    .card {{
      background: var(--card); border:1px solid var(--line); border-radius: 14px; box-shadow: var(--shadow);
      padding: 14px;
    }}
    .card h2 {{ margin:0 0 10px; font-size: 16px; }}
    .card h3 {{ margin:0 0 8px; font-size: 14px; }}
    .muted {{ color: var(--muted); font-size: 12px; }}
    .kpi {{ font-size: 28px; font-weight: 700; }}
    .row {{ display:flex; gap:10px; align-items:center; flex-wrap:wrap; }}
    .field {{ display:grid; gap:6px; margin-bottom:10px; }}
    .field label {{ font-size: 12px; color: var(--muted); }}
    input[type=text], input[type=number], textarea, select {{
      width:100%; border:1px solid var(--line); border-radius:10px; background:#fff; color:var(--ink);
      padding:10px 12px; font: inherit;
    }}
    textarea {{ min-height: 120px; font-family: var(--mono); font-size: 12px; line-height: 1.35; }}
    .mono {{ font-family: var(--mono); font-size: 12px; }}
    .btn {{
      border:1px solid var(--line); background:#fff; color: var(--ink); border-radius: 10px;
      padding:8px 12px; cursor:pointer; font-weight:600;
    }}
    .icon-btn {{ display:inline-flex; align-items:center; gap:6px; }}
    .btn.primary {{ background: var(--accent); color: #fff; border-color: var(--accent); }}
    .btn.warn {{ background: var(--accent-2); color: #fff; border-color: var(--accent-2); }}
    .btn.subtle {{ background: rgba(255,255,255,.55); }}
    .lang-switch {{
      display:inline-flex; align-items:center; gap:8px; border:1px solid var(--line);
      border-radius:10px; padding:6px 8px; background:rgba(255,255,255,.55);
    }}
    .lang-icon-btn {{
      width:28px; height:28px; display:inline-flex; align-items:center; justify-content:center;
      border:1px solid var(--line); border-radius:8px; background:#fff;
      font-size:14px; line-height:1;
    }}
    .lang-select {{
      border:none; background:transparent; padding:0 2px; min-width:120px;
      font: inherit; color: var(--ink);
    }}
    .lang-select:focus {{ outline:none; }}
    table {{ width:100%; border-collapse: collapse; font-size: 13px; }}
    th, td {{ border-bottom:1px solid #ece7dc; text-align:left; vertical-align: top; padding:8px 6px; }}
    th {{ color: var(--muted); font-weight:600; }}
    tbody tr:hover td {{ background: rgba(15,108,92,.03); }}
    code {{ font-family: var(--mono); background:#f4f1ea; padding:2px 4px; border-radius:4px; }}
    .pill {{ display:inline-block; border-radius:999px; padding:2px 8px; font-size:11px; border:1px solid var(--line); }}
    .pill.ok {{ border-color:#abefc6; color: var(--ok); background:#f0fdf4; }}
    .pill.off {{ border-color:#fecdca; color: var(--err); background:#fef2f2; }}
    .split {{ display:grid; grid-template-columns: 1.15fr .85fr; gap: 14px; }}
    .small {{ font-size: 12px; }}
    .list {{ margin:0; padding-left: 18px; }}
    .list li {{ margin: 4px 0; }}
    .endpoint-card {{ border:1px solid #ece7dc; border-radius: 12px; padding: 12px; margin-bottom:10px; background:#fff; }}
    .endpoint-head {{ display:flex; justify-content:space-between; gap:8px; align-items:center; }}
    .endpoint-fields {{ display:grid; grid-template-columns: repeat(2, minmax(0,1fr)); gap:10px; margin-top:10px; }}
    .endpoint-fields .field.full {{ grid-column: 1 / -1; }}
    .toast {{
      position: fixed; right: 16px; bottom: 16px; background: #122b24; color: #fff; border-radius: 10px;
      padding: 10px 12px; font-size: 12px; opacity: 0; transform: translateY(8px); pointer-events:none;
      transition: all .18s ease;
    }}
    .toast.show {{ opacity: .96; transform: translateY(0); }}
    @media (max-width: 900px) {{
      .grid.cols-2, .grid.cols-3, .split, .endpoint-fields {{ grid-template-columns: 1fr; }}
      .top {{ flex-direction: column; }}
    }}
  </style>
</head>
<body>
  <div class="layout">
    <div class="top">
      <div class="brand">
        <h1>{escape(brand_name)}</h1>
        <p>{subtitle}</p>
      </div>
      <div style="display:grid; gap:8px;">
        <div class="row" style="justify-content:flex-end">
          <span class="muted">{lang_label}</span>
          <div class="lang-switch" title="{lang_label}">
            <span class="lang-icon-btn" aria-hidden="true">🌐</span>
            <select id="nb-lang-picker" class="lang-select" aria-label="{lang_label}">
              {lang_options_html}
            </select>
          </div>
        </div>
        <nav class="nav">{nav_html}</nav>
      </div>
    </div>
    {flash_html}
    {body}
  </div>
  <script>
    async function nbCopy(text) {{
      try {{
        await navigator.clipboard.writeText(text);
      }} catch (e) {{
        const ta = document.createElement('textarea');
        ta.value = text;
        document.body.appendChild(ta);
        ta.select();
        document.execCommand('copy');
        ta.remove();
      }}
      const toast = document.getElementById('nb-toast');
      if (toast) {{
        toast.textContent = '{escape(copied_label)}';
        toast.classList.add('show');
        window.clearTimeout(window.__nbToastTimer);
        window.__nbToastTimer = window.setTimeout(() => toast.classList.remove('show'), 1200);
      }}
    }}
    function nbSelectAll(form, checked) {{
      if (!form) return;
      for (const box of form.querySelectorAll('input[name="selected_name"]')) {{
        box.checked = !!checked;
      }}
    }}
    (function bindLangPicker() {{
      const picker = document.getElementById('nb-lang-picker');
      if (!picker) return;
      picker.addEventListener('change', () => {{
        const u = new URL(window.location.href);
        u.searchParams.set('lang', picker.value);
        window.location.href = u.pathname + u.search;
      }});
    }})();
    (function bindUiLang() {{
      const uiLang = "{escape(ui_lang)}";
      for (const form of document.querySelectorAll('form')) {{
        if (!form.querySelector('input[name="ui_lang"]')) {{
          const hidden = document.createElement('input');
          hidden.type = 'hidden';
          hidden.name = 'ui_lang';
          hidden.value = uiLang;
          form.appendChild(hidden);
        }}
      }}
      for (const a of document.querySelectorAll('a[href^="/"]')) {{
        try {{
          const u = new URL(a.getAttribute('href'), window.location.origin);
          if (!u.searchParams.get('lang')) {{
            u.searchParams.set('lang', uiLang);
            a.setAttribute('href', u.pathname + u.search);
          }}
        }} catch (e) {{}}
      }}
    }})();
  </script>
  <div id="nb-toast" class="toast" aria-live="polite"></div>
</body>
</html>"""
