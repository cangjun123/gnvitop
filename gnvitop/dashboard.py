"""Embedded dashboard HTML."""

DASHBOARD_HTML = r"""<!DOCTYPE html>
<html lang="zh-CN">
<head>
<meta charset="UTF-8">
<meta name="viewport" content="width=device-width, initial-scale=1.0">
<title>gnvitop — {{GNVITOP_HOST_INFO}}</title>
<link rel="icon" type="image/svg+xml" href="data:image/svg+xml,%3Csvg xmlns='http://www.w3.org/2000/svg' viewBox='0 0 64 64'%3E%3Cdefs%3E%3ClinearGradient id='g' x1='0' y1='0' x2='1' y2='1'%3E%3Cstop offset='0%25' stop-color='%2338bdf8'/%3E%3Cstop offset='100%25' stop-color='%23a78bfa'/%3E%3C/linearGradient%3E%3C/defs%3E%3Crect x='4' y='4' width='56' height='56' rx='16' fill='url(%23g)'/%3E%3Cpath d='M12 34 L22 34 L27 18 L33 46 L38 28 L43 34 L52 34' fill='none' stroke='white' stroke-width='4' stroke-linecap='round' stroke-linejoin='round'/%3E%3C/svg%3E">
<script>
  try {
    if (localStorage.getItem('gnvitop-theme') === 'light') {
      document.documentElement.classList.add('theme-light');
    }
  } catch (e) {}
</script>
<style>
  * { margin: 0; padding: 0; box-sizing: border-box; }

  :root {
    color-scheme: dark;
    --bg: #0f172a;
    --surface: #1e293b;
    --surface-muted: #0f172a;
    --border: #334155;
    --border-hover: #475569;
    --text: #e2e8f0;
    --text-strong: #f1f5f9;
    --text-muted: #94a3b8;
    --text-subtle: #64748b;
    --icon-muted: #475569;
    --hover-soft: rgba(255,255,255,0.03);
    --shadow-card: 0 8px 24px rgba(0,0,0,0.3);
    --shadow-tooltip: 0 4px 16px rgba(0,0,0,0.5);
    --shadow-popover: 0 4px 12px rgba(0,0,0,0.4);
    --success-bg: #052e16;
    --success-text: #4ade80;
    --warning-bg: #422006;
    --warning-text: #facc15;
    --error-bg: #450a0a;
    --error-text: #f87171;
    --tpu-bg: #2e1065;
    --tpu-text: #a78bfa;
    --local-bg: #172554;
    --local-text: #60a5fa;
    --refresh-pulse-bg: #1e3a5f;
  }

  html.theme-light {
    color-scheme: light;
    --bg: #e9eef5;
    --surface: #f1f5f9;
    --surface-muted: #e2e8f0;
    --border: #d4dde8;
    --border-hover: #aebccd;
    --text: #334155;
    --text-strong: #0f172a;
    --text-muted: #64748b;
    --text-subtle: #738095;
    --icon-muted: #94a3b8;
    --hover-soft: rgba(15,23,42,0.04);
    --shadow-card: 0 10px 26px rgba(15,23,42,0.10);
    --shadow-tooltip: 0 10px 26px rgba(15,23,42,0.16);
    --shadow-popover: 0 8px 20px rgba(15,23,42,0.14);
    --success-bg: #dcfce7;
    --success-text: #15803d;
    --warning-bg: #fef3c7;
    --warning-text: #a16207;
    --error-bg: #fee2e2;
    --error-text: #b91c1c;
    --tpu-bg: #ede9fe;
    --tpu-text: #7c3aed;
    --local-bg: #dbeafe;
    --local-text: #2563eb;
    --refresh-pulse-bg: #dbeafe;
  }

  body {
    font-family: -apple-system, BlinkMacSystemFont, 'Segoe UI', Roboto, sans-serif;
    background: var(--bg);
    color: var(--text);
    min-height: 100vh;
    padding: 24px;
    transition: background 0.2s, color 0.2s;
  }

  .header {
    display: flex;
    align-items: center;
    justify-content: space-between;
    margin-bottom: 28px;
  }

  .header h1 {
    font-size: 28px;
    font-weight: 700;
    color: #f1f5f9;
    letter-spacing: -0.5px;
  }

  .header-right {
    display: flex;
    align-items: center;
    gap: 16px;
  }

  .status-text {
    font-size: 13px;
    color: #94a3b8;
  }

  .github-link {
    display: flex;
    align-items: center;
    color: #94a3b8;
    text-decoration: none;
    transition: color 0.2s;
  }
  .github-link:hover { color: #f1f5f9; }
  .github-link svg { width: 22px; height: 22px; fill: currentColor; }
  .github-link .version-tag {
    font-size: 12px;
    margin-left: 5px;
    opacity: 0.8;
  }

  .header-divider {
    width: 1px;
    height: 20px;
    background: #334155;
    flex-shrink: 0;
  }

  .btn-refresh {
    padding: 6px 14px;
    border: 1px solid #334155;
    background: #1e293b;
    color: #e2e8f0;
    border-radius: 8px;
    cursor: pointer;
    font-size: 13px;
    transition: all 0.2s;
    white-space: nowrap;
  }
  .btn-refresh:hover { background: #334155; border-color: #475569; color: #f1f5f9; }
  .btn-refresh:disabled { opacity: 0.5; cursor: not-allowed; }
  @keyframes refreshPulse {
    0%   { box-shadow: 0 0 0 0 rgba(96,165,250,0.5); }
    50%  { box-shadow: 0 0 0 6px rgba(96,165,250,0); background: #1e3a5f; border-color: #60a5fa; }
    100% { box-shadow: 0 0 0 0 rgba(96,165,250,0); }
  }
  .btn-refresh.refreshing { animation: refreshPulse 0.8s ease; }

  body.notify-off .global-watch-btn,
  body.notify-off .watch-btn { display: none; }

  .global-watch-btn {
    background: transparent;
    border: none;
    cursor: pointer;
    font-size: 15px;
    padding: 0 4px;
    color: #475569;
    transition: color 0.2s, transform 0.2s;
    line-height: 1;
  }
  .global-watch-btn:hover { color: #94a3b8; transform: scale(1.1); }
  .global-watch-btn.watching { color: #facc15; }

  /* Drag-and-drop */
  .host-card.dragging { opacity: 0.4; cursor: grabbing; }
  .host-card.drag-over { outline: 2px dashed #60a5fa; outline-offset: 2px; }
  .drag-handle {
    cursor: grab;
    color: #475569;
    font-size: 14px;
    padding: 2px 4px;
    user-select: none;
    line-height: 1;
  }
  .drag-handle:hover { color: #94a3b8; }
  .drag-handle:active { cursor: grabbing; }

  .summary-bar {
    display: flex;
    gap: 16px;
    margin-bottom: 24px;
    flex-wrap: wrap;
  }

  .summary-card {
    background: #1e293b;
    border: 1px solid #334155;
    border-radius: 10px;
    padding: 16px 24px;
    min-width: 160px;
    flex: 1;
  }

  .summary-card .label {
    font-size: 12px;
    color: #94a3b8;
    text-transform: uppercase;
    letter-spacing: 0.5px;
    margin-bottom: 4px;
  }

  .summary-card .value {
    font-size: 28px;
    font-weight: 700;
  }

  .host-grid {
    display: grid;
    grid-template-columns: repeat(auto-fill, minmax(380px, 1fr));
    gap: 16px;
  }

  .host-card {
    background: #1e293b;
    border: 1px solid #334155;
    border-radius: 12px;
    overflow: hidden;
    transition: border-color 0.2s, transform 0.15s, box-shadow 0.2s;
  }
  .host-card:hover {
    border-color: #475569;
    transform: translateY(-2px);
    box-shadow: 0 8px 24px rgba(0,0,0,0.3);
  }
  .host-header:hover {
    background: rgba(255,255,255,0.03);
  }

  .host-card.status-ok { border-left: 3px solid #22c55e; }
  .host-card.status-no_gpu { border-left: 3px solid #eab308; }
  .host-card.status-error { border-left: 3px solid #ef4444; }
  .host-card.is-local { border-left: 3px solid #60a5fa; }
  .host-card.is-tpu { border-left: 3px solid #a78bfa; }

  .host-header {
    padding: 16px 20px;
    display: flex;
    justify-content: space-between;
    align-items: center;
    border-bottom: 1px solid #334155;
  }

  .host-name {
    font-size: 16px;
    font-weight: 600;
    color: #f1f5f9;
  }

  .host-info {
    font-size: 12px;
    color: #64748b;
  }

  .status-badge {
    font-size: 11px;
    padding: 3px 10px;
    border-radius: 12px;
    font-weight: 600;
    text-transform: uppercase;
    letter-spacing: 0.3px;
  }
  .badge-ok { background: #052e16; color: #4ade80; }
  .badge-no_gpu { background: #422006; color: #facc15; }
  .badge-error { background: #450a0a; color: #f87171; }
  .badge-tpu { background: #2e1065; color: #a78bfa; }

  .host-body { padding: 16px 20px; }

  .error-msg {
    color: #f87171;
    font-size: 13px;
    padding: 8px 0;
  }

  .no-gpu-msg {
    color: #facc15;
    font-size: 13px;
    padding: 8px 0;
  }

  .gpu-item {
    padding: 12px 0;
  }
  .gpu-item + .gpu-item { border-top: 1px solid #1e293b; }

  .gpu-title {
    display: flex;
    justify-content: space-between;
    align-items: center;
    margin-bottom: 10px;
  }

  .gpu-name {
    font-size: 14px;
    font-weight: 600;
    color: #cbd5e1;
  }

  .gpu-temp {
    font-size: 12px;
    padding: 2px 8px;
    border-radius: 6px;
    font-weight: 600;
  }
  .temp-cool { background: #052e16; color: #4ade80; }
  .temp-warm { background: #422006; color: #facc15; }
  .temp-hot { background: #450a0a; color: #f87171; }

  .bar-container {
    margin-bottom: 8px;
  }

  .bar-label {
    display: flex;
    justify-content: space-between;
    font-size: 12px;
    color: #94a3b8;
    margin-bottom: 4px;
  }

  .bar-track {
    height: 8px;
    background: #0f172a;
    border-radius: 4px;
    overflow: hidden;
  }

  .bar-fill {
    height: 100%;
    border-radius: 4px;
    transition: width 0.5s ease;
  }

  .bar-fill.usage-low { background: linear-gradient(90deg, #22c55e, #4ade80); }
  .bar-fill.usage-mid { background: linear-gradient(90deg, #eab308, #facc15); }
  .bar-fill.usage-high { background: linear-gradient(90deg, #ef4444, #f87171); }

  .gpu-stats {
    display: grid;
    grid-template-columns: repeat(3, 1fr);
    gap: 8px;
    margin-top: 8px;
  }

  .stat {
    text-align: center;
    background: #0f172a;
    border-radius: 6px;
    padding: 8px;
  }

  .stat .stat-value {
    font-size: 16px;
    font-weight: 700;
    color: #f1f5f9;
  }

  .stat .stat-label {
    font-size: 10px;
    color: #64748b;
    margin-top: 2px;
  }

  .loading {
    text-align: center;
    padding: 80px 20px;
    color: #94a3b8;
    font-size: 16px;
  }

  .spinner {
    display: inline-block;
    width: 28px;
    height: 28px;
    border: 3px solid #334155;
    border-top-color: #60a5fa;
    border-radius: 50%;
    animation: spin 0.8s linear infinite;
    margin-bottom: 12px;
  }

  @keyframes spin { to { transform: rotate(360deg); } }

  /* iOS-style toggle switch */
  .toggle-switch {
    display: inline-flex;
    align-items: center;
    gap: 7px;
    cursor: pointer;
    font-size: 13px;
    color: #94a3b8;
    user-select: none;
    transition: color 0.2s;
  }
  .toggle-switch:hover { color: #cbd5e1; }
  .toggle-switch input { display: none; }
  .toggle-knob {
    width: 30px;
    height: 17px;
    background: #334155;
    border-radius: 9px;
    position: relative;
    transition: background 0.2s;
    flex-shrink: 0;
  }
  .toggle-knob::after {
    content: '';
    position: absolute;
    width: 13px;
    height: 13px;
    background: #94a3b8;
    border-radius: 50%;
    top: 2px;
    left: 2px;
    transition: transform 0.2s, background 0.2s;
  }
  .toggle-switch input:checked ~ .toggle-knob { background: #1d4ed8; }
  .toggle-switch input:checked ~ .toggle-knob::after { transform: translateX(13px); background: #60a5fa; }
  .toggle-switch input:checked ~ .toggle-label { color: #cbd5e1; }

  /* Universal tooltip */
  #ui-tooltip {
    position: fixed;
    background: #0f172a;
    border: 1px solid #334155;
    border-radius: 8px;
    padding: 7px 12px;
    font-size: 12px;
    color: #cbd5e1;
    pointer-events: none;
    z-index: 9999;
    max-width: 260px;
    line-height: 1.5;
    box-shadow: 0 4px 16px rgba(0,0,0,0.5);
    opacity: 0;
    transition: opacity 0.15s ease;
  }
  #ui-tooltip.visible { opacity: 1; }

  .badge-local { background: #172554; color: #60a5fa; }

  .gpu-users {
    display: flex;
    flex-wrap: wrap;
    gap: 4px;
    margin-top: 8px;
  }

  .user-tag {
    font-size: 11px;
    padding: 2px 8px;
    border-radius: 4px;
    background: #334155;
    color: #94a3b8;
    font-family: monospace;
  }

  .user-tag.current-user {
    background: #172554;
    color: #60a5fa;
    font-weight: 700;
    border: 1px solid #3b82f6;
  }

  .user-mem {
    color: #64748b;
    font-size: 10px;
    margin-left: 2px;
  }

  .mode-toggle {
    display: flex;
    background: #0f172a;
    border: 1px solid #334155;
    border-radius: 8px;
    overflow: hidden;
  }
  .mode-toggle button {
    padding: 5px 11px;
    border: none;
    background: transparent;
    color: #64748b;
    cursor: pointer;
    transition: all 0.2s;
    font-size: 13px;
    white-space: nowrap;
  }
  .mode-toggle button:hover { color: #94a3b8; background: #1e293b; }
  .mode-toggle button.active { background: #334155; color: #e2e8f0; }

  .theme-toggle {
    display: flex;
    background: #0f172a;
    border: 1px solid #334155;
    border-radius: 8px;
    overflow: hidden;
  }
  .theme-toggle button {
    padding: 5px 11px;
    border: none;
    background: transparent;
    color: #64748b;
    cursor: pointer;
    transition: all 0.2s;
    font-size: 13px;
    white-space: nowrap;
  }
  .theme-toggle button:hover { color: #94a3b8; background: #1e293b; }
  .theme-toggle button.active { background: #334155; color: #e2e8f0; }

  /* Initial load animation only */
  .host-card.first-render {
    animation: fadeSlideIn 0.3s ease;
  }
  @keyframes fadeSlideIn {
    from { opacity: 0; transform: translateY(8px); }
    to { opacity: 1; transform: translateY(0); }
  }

  /* Interval selector */
  .interval-select {
    background: #0f172a;
    border: 1px solid #334155;
    border-radius: 8px;
    color: #94a3b8;
    font-size: 13px;
    padding: 5px 8px;
    cursor: pointer;
    outline: none;
    transition: border-color 0.2s, color 0.2s;
  }
  .interval-select:hover { border-color: #475569; color: #cbd5e1; }

  /* Compact mode */
  body.compact .summary-bar { display: none; }
  body.compact .host-grid { grid-template-columns: repeat(auto-fill, minmax(380px, 1fr)); gap: 12px; }
  body.compact .host-header { padding: 12px 16px; }
  body.compact .host-info { display: none; }
  body.compact .host-body { padding: 12px 16px; }

  /* Collapse */
  .host-header {
    transition: background 0.15s;
  }
  .host-header-left {
    display: flex;
    align-items: center;
    gap: 8px;
    min-width: 0;
    cursor: pointer;
    user-select: none;
    flex: 1;
  }
  .host-header-right {
    display: flex;
    align-items: center;
    gap: 10px;
    flex-shrink: 0;
  }
  .collapse-arrow {
    font-size: 11px;
    color: #475569;
    transition: transform 0.2s;
    display: inline-block;
  }
  .host-body {
    max-height: 2000px;
    overflow: hidden;
    transition: max-height 0.15s ease, opacity 0.1s ease;
    opacity: 1;
  }
  .host-card.collapsed .collapse-arrow { transform: rotate(-90deg); }
  .host-card.collapsed .host-body { max-height: 0; opacity: 0; }
  .host-card.collapsed .host-header { border-bottom: none; }
  .watch-btn {
    background: transparent;
    border: none;
    cursor: pointer;
    font-size: 15px;
    padding: 2px 4px;
    color: #475569;
    transition: color 0.2s;
    line-height: 1;
    position: relative;
  }
  .watch-btn:hover { color: #94a3b8; }
  .watch-btn.watching { color: #facc15; }
  @keyframes watchPop {
    0%   { transform: scale(1); }
    35%  { transform: scale(1.5) rotate(-15deg); }
    65%  { transform: scale(0.9) rotate(10deg); }
    100% { transform: scale(1) rotate(0deg); }
  }
  .watch-btn.watch-pop, .global-watch-btn.watch-pop { animation: watchPop 0.4s ease; }
  .watch-btn .watch-tooltip {
    display: none;
    position: absolute;
    right: 0;
    top: calc(100% + 6px);
    background: #0f172a;
    border: 1px solid #334155;
    border-radius: 8px;
    padding: 8px 12px;
    font-size: 12px;
    color: #cbd5e1;
    white-space: nowrap;
    z-index: 100;
    pointer-events: none;
    box-shadow: 0 4px 12px rgba(0,0,0,0.4);
    min-width: 160px;
  }
  .watch-btn:hover .watch-tooltip { display: block; }
  .collapsed-info {
    font-size: 11px;
    color: #64748b;
    margin-top: 2px;
  }

  /* Folded section divider */
  .folded-divider {
    display: flex;
    align-items: center;
    gap: 12px;
    margin: 28px 0 16px;
  }
  .folded-divider::before,
  .folded-divider::after {
    content: '';
    flex: 1;
    height: 1px;
    background: #334155;
  }
  .folded-label {
    font-size: 11px;
    font-weight: 600;
    color: #475569;
    text-transform: uppercase;
    letter-spacing: 0.8px;
    white-space: nowrap;
  }
  .host-grid-folded .host-card { opacity: 0.75; }
  .host-grid-folded .host-card:hover { opacity: 1; }

  /* Theme-aware color overrides */
  .header h1,
  .host-name,
  .stat .stat-value { color: var(--text-strong); }

  .status-text,
  .github-link,
  .summary-card .label,
  .bar-label,
  .loading,
  .toggle-switch,
  .drag-handle:hover,
  .global-watch-btn:hover,
  .watch-btn:hover { color: var(--text-muted); }

  .host-info,
  .stat .stat-label,
  .user-mem,
  .collapsed-info,
  .mode-toggle button,
  .theme-toggle button,
  .folded-label { color: var(--text-subtle); }

  .github-link:hover,
  .toggle-switch:hover,
  .interval-select:hover,
  .mode-toggle button.active,
  .theme-toggle button.active,
  .theme-toggle:hover,
  .btn-refresh:hover { color: var(--text-strong); }

  .summary-card,
  .host-card,
  .btn-refresh {
    background: var(--surface);
    border-color: var(--border);
  }

  .host-card:hover {
    border-color: var(--border-hover);
    box-shadow: var(--shadow-card);
  }

  .host-header:hover,
  .mode-toggle button:hover,
  .theme-toggle button:hover,
  .btn-refresh:hover,
  .theme-toggle:hover { background: var(--hover-soft); }

  .header-divider,
  .host-header,
  .spinner,
  .mode-toggle,
  .theme-toggle,
  .interval-select,
  #ui-tooltip,
  .watch-btn .watch-tooltip,
  .folded-divider::before,
  .folded-divider::after { border-color: var(--border); }

  .header-divider,
  .folded-divider::before,
  .folded-divider::after { background: var(--border); }

  .gpu-item + .gpu-item { border-top-color: var(--border); }
  .gpu-name,
  #ui-tooltip,
  .watch-btn .watch-tooltip { color: var(--text); }
  .bar-track,
  .stat,
  .mode-toggle,
  .theme-toggle,
  .interval-select,
  #ui-tooltip,
  .watch-btn .watch-tooltip { background: var(--surface-muted); }
  .interval-select { color: var(--text-muted); }
  .toggle-knob,
  .mode-toggle button.active,
  .theme-toggle button.active,
  .user-tag { background: var(--border); }
  .toggle-knob::after { background: var(--text-muted); }
  .toggle-switch input:checked ~ .toggle-label { color: var(--text); }
  .global-watch-btn,
  .drag-handle,
  .collapse-arrow,
  .watch-btn { color: var(--icon-muted); }
  .badge-ok,
  .temp-cool { background: var(--success-bg); color: var(--success-text); }
  .badge-no_gpu,
  .temp-warm { background: var(--warning-bg); color: var(--warning-text); }
  .badge-error,
  .temp-hot { background: var(--error-bg); color: var(--error-text); }
  .badge-tpu { background: var(--tpu-bg); color: var(--tpu-text); }
  .badge-local,
  .user-tag.current-user { background: var(--local-bg); color: var(--local-text); }
  .error-msg { color: var(--error-text); }
  .no-gpu-msg { color: var(--warning-text); }
  .user-tag { color: var(--text-muted); }
  #ui-tooltip { box-shadow: var(--shadow-tooltip); }
  .watch-btn .watch-tooltip { box-shadow: var(--shadow-popover); }
  .btn-refresh { color: var(--text); }
  .spinner {
    border-color: var(--border);
    border-top-color: var(--local-text);
  }

</style>
</head>
<body>

<div class="header">
  <h1>
    <svg xmlns="http://www.w3.org/2000/svg" viewBox="0 0 64 64" width="32" height="32" style="vertical-align: middle; margin-right: 10px;">
      <defs>
        <linearGradient id="logo-grad" x1="0" y1="0" x2="1" y2="1">
          <stop offset="0%" stop-color="#38bdf8"/>
          <stop offset="100%" stop-color="#a78bfa"/>
        </linearGradient>
      </defs>
      <rect x="4" y="4" width="56" height="56" rx="16" fill="url(#logo-grad)"/>
      <path d="M12 34 L22 34 L27 18 L33 46 L38 28 L43 34 L52 34" fill="none" stroke="white" stroke-width="4" stroke-linecap="round" stroke-linejoin="round"/>
    </svg>
    gnvitop <span style="font-size: 0.5em; font-weight: 400; opacity: 0.7; margin-left: 8px;">{{GNVITOP_HOST_INFO}}</span>
  </h1>
  <div class="header-right">
    <span class="status-text" id="update-time"></span>
    <div class="header-divider"></div>
    <div class="theme-toggle" id="theme-toggle" data-tip="Switch dashboard theme">
      <button onclick="setTheme('dark')" id="theme-dark">Dark</button>
      <button onclick="setTheme('light')" id="theme-light">Light</button>
    </div>
    <div class="header-divider"></div>
    <div class="mode-toggle" id="mode-toggle">
      <button onclick="setMode('compact')" id="mode-compact" data-tip="Compact view: smaller cards, hide host details">Compact</button>
      <button onclick="setMode('normal')" id="mode-normal" data-tip="Expand view: full cards with all GPU details">Expand</button>
    </div>
    <div class="header-divider"></div>
    <label class="toggle-switch" data-tip="Enable GPU availability notifications. Use the 🔔 bell on each card to select which hosts to watch.">
      <input type="checkbox" id="notify-toggle" onchange="setNotifyEnabled(this.checked)">
      <span class="toggle-knob"></span>
      <span class="toggle-label">&#128276; Notify</span>
    </label>
    <button class="global-watch-btn" id="global-watch-btn" onclick="toggleGlobalWatch()" data-tip="Watch all hosts — notify when any GPU becomes free">&#128277;</button>
    <div class="header-divider"></div>
    <label class="toggle-switch" data-tip="Auto-refresh: automatically fetch latest GPU data at the selected interval">
      <input type="checkbox" id="auto-refresh" checked>
      <span class="toggle-knob"></span>
      <span class="toggle-label">Auto Refresh</span>
    </label>
    <select class="interval-select" id="interval-select" onchange="setInterval_(this.value)" data-tip="Auto-refresh interval">
      <option value="5">5s</option>
      <option value="10">10s</option>
      <option value="30" selected>30s</option>
      <option value="300">5min</option>
    </select>
    <a class="github-link" href="https://github.com/Linwei94/gnvitop" target="_blank" title="Star on GitHub">
      <svg viewBox="0 0 16 16" xmlns="http://www.w3.org/2000/svg">
        <path d="M8 0C3.58 0 0 3.58 0 8c0 3.54 2.29 6.53 5.47 7.59.4.07.55-.17.55-.38 0-.19-.01-.82-.01-1.49-2.01.37-2.53-.49-2.69-.94-.09-.23-.48-.94-.82-1.13-.28-.15-.68-.52-.01-.53.63-.01 1.08.58 1.23.82.72 1.21 1.87.87 2.33.66.07-.52.28-.87.51-1.07-1.78-.2-3.64-.89-3.64-3.95 0-.87.31-1.59.82-2.15-.08-.2-.36-1.02.08-2.12 0 0 .67-.21 2.2.82.64-.18 1.32-.27 2-.27.68 0 1.36.09 2 .27 1.53-1.04 2.2-.82 2.2-.82.44 1.1.16 1.92.08 2.12.51.56.82 1.27.82 2.15 0 3.07-1.87 3.75-3.65 3.95.29.25.54.73.54 1.48 0 1.07-.01 1.93-.01 2.2 0 .21.15.46.55.38A8.013 8.013 0 0016 8c0-4.42-3.58-8-8-8z"/>
      </svg>
      <span class="version-tag">v{{GNVITOP_VERSION}}</span>
    </a>
    <button class="btn-refresh" id="btn-refresh" onclick="refresh()">Refresh</button>
  </div>
</div>

<div id="ui-tooltip"></div>
<div class="summary-bar" id="summary-bar"></div>
<div id="content">
  <div class="loading"><div class="spinner"></div><br>Connecting to hosts...</div>
</div>

<script>
// Universal tooltip for [data-tip] elements
(function() {
  const tip = document.createElement('div');
  tip.id = 'ui-tooltip';
  document.body.appendChild(tip);
  let hideTimer;
  document.addEventListener('mouseover', e => {
    const el = e.target.closest('[data-tip]');
    if (!el) return;
    clearTimeout(hideTimer);
    tip.textContent = el.dataset.tip;
    tip.classList.add('visible');
  });
  document.addEventListener('mousemove', e => {
    if (!tip.classList.contains('visible')) return;
    const x = e.clientX + 14, y = e.clientY + 14;
    const r = tip.getBoundingClientRect();
    tip.style.left = (x + r.width > window.innerWidth ? x - r.width - 20 : x) + 'px';
    tip.style.top  = (y + r.height > window.innerHeight ? y - r.height - 20 : y) + 'px';
  });
  document.addEventListener('mouseout', e => {
    const el = e.target.closest('[data-tip]');
    if (!el) return;
    hideTimer = setTimeout(() => tip.classList.remove('visible'), 100);
  });
})();

let autoRefreshTimer = null;
let currentMode = 'normal';
let lastData = null;
let isFirstRender = true;
let refreshIntervalSecs = parseInt(localStorage.getItem('gnvitop-interval') || '30');
let hostOrder = JSON.parse(localStorage.getItem('gnvitop-order') || '[]'); // pinned manual order
let currentTheme = localStorage.getItem('gnvitop-theme') || 'dark';

function setTheme(theme) {
  currentTheme = theme === 'light' ? 'light' : 'dark';
  document.documentElement.classList.toggle('theme-light', currentTheme === 'light');
  localStorage.setItem('gnvitop-theme', currentTheme);
  document.getElementById('theme-dark').classList.toggle('active', currentTheme === 'dark');
  document.getElementById('theme-light').classList.toggle('active', currentTheme === 'light');
}

function toggleTheme() {
  setTheme(currentTheme === 'light' ? 'dark' : 'light');
}

function _applyHostOrder(list) {
  if (!hostOrder.length) return list;
  const orderMap = {};
  hostOrder.forEach((alias, i) => { orderMap[alias] = i; });
  return [...list].sort((a, b) => {
    const ai = orderMap[a.alias] ?? 9999;
    const bi = orderMap[b.alias] ?? 9999;
    return ai - bi;
  });
}

function _setupDrag(grid) {
  let dragSrc = null;
  grid.querySelectorAll('.host-card').forEach(card => {
    const handle = card.querySelector('.drag-handle');
    if (handle) {
      handle.setAttribute('draggable', 'true');
      handle.addEventListener('dragstart', e => {
        dragSrc = card;
        card.classList.add('dragging');
        e.dataTransfer.effectAllowed = 'move';
        e.dataTransfer.setDragImage(card, 0, 0);
        e.stopPropagation();
      });
      handle.addEventListener('dragend', () => {
        card.classList.remove('dragging');
        grid.querySelectorAll('.host-card').forEach(c => c.classList.remove('drag-over'));
        hostOrder = [...grid.querySelectorAll('.host-card')].map(c => c.dataset.alias);
        localStorage.setItem('gnvitop-order', JSON.stringify(hostOrder));
      });
    }
    card.addEventListener('dragover', e => {
      e.preventDefault();
      e.dataTransfer.dropEffect = 'move';
      if (card !== dragSrc) {
        grid.querySelectorAll('.host-card').forEach(c => c.classList.remove('drag-over'));
        card.classList.add('drag-over');
      }
    });
    card.addEventListener('drop', e => {
      e.preventDefault();
      if (dragSrc && dragSrc !== card) {
        const cards = [...grid.querySelectorAll('.host-card')];
        const srcIdx = cards.indexOf(dragSrc);
        const dstIdx = cards.indexOf(card);
        if (srcIdx < dstIdx) {
          grid.insertBefore(dragSrc, card.nextSibling);
        } else {
          grid.insertBefore(dragSrc, card);
        }
      }
    });
  });
}
let collapsedHosts = new Set(JSON.parse(localStorage.getItem('gnvitop-collapsed') || '[]'));
let watchedHosts = new Set(JSON.parse(localStorage.getItem('gnvitop-watched') || '[]'));
let prevAvailability = {}; // "alias||gpuIndex" -> bool, tracks last known state
let notifyEnabled = localStorage.getItem('gnvitop-notify') === 'true';

function setNotifyEnabled(enabled) {
  notifyEnabled = enabled;
  localStorage.setItem('gnvitop-notify', enabled);
  document.body.classList.toggle('notify-off', !enabled);
  if (enabled && Notification.permission === 'default') Notification.requestPermission();
}

function toggleWatch(alias) {
  if (watchedHosts.has(alias)) {
    watchedHosts.delete(alias);
  } else {
    watchedHosts.add(alias);
    if (Notification.permission === 'default') {
      Notification.requestPermission();
    }
  }
  localStorage.setItem('gnvitop-watched', JSON.stringify([...watchedHosts]));
  let card = null;
  document.querySelectorAll('.host-card').forEach(c => { if (c.dataset.alias === alias) card = c; });
  if (card) {
    const btn = card.querySelector('.watch-btn');
    if (btn) {
      const watching = watchedHosts.has(alias);
      btn.classList.toggle('watching', watching);
      btn.childNodes[0].textContent = watching ? '\uD83D\uDD14' : '\uD83D\uDD15';
      // Update tooltip content to reflect new state
      const tooltip = btn.querySelector('.watch-tooltip');
      if (tooltip && lastData) {
        const host = lastData.hosts.find(h => h.alias === alias);
        if (host && host.status === 'ok') {
          const free = host.gpus.filter(g => _gpuAvailable(g));
          if (free.length > 0) {
            const label = free.map(g => 'GPU ' + g.index + ' (' + Math.round(g.memory_free_mb/1024*10)/10 + 'GB free)').join('<br>');
            tooltip.style.color = 'var(--success-text)';
            tooltip.innerHTML = free.length + ' GPU' + (free.length>1?'s':'') + ' available:<br>' + label + '<br><span style="color:var(--text-muted)">' + (watching ? 'Click to stop watching' : 'Click to watch') + '</span>';
          } else {
            tooltip.style.color = '';
            tooltip.innerHTML = watching ? 'Watching \u2014 notify on free GPU<br><span style="color:var(--text-muted)">Click to stop</span>' : 'Watch for free GPUs';
          }
        }
      }
      btn.classList.remove('watch-pop');
      void btn.offsetWidth;
      btn.classList.add('watch-pop');
    }
  }
}

function _gpuAvailable(gpu) {
  return gpu.gpu_utilization_pct < 10 && gpu.memory_used_mb < gpu.memory_total_mb * 0.1;
}

function checkWatchedNotifications(hosts) {
  if (!notifyEnabled || Notification.permission !== 'granted') return;
  hosts.forEach(host => {
    if (!watchedHosts.has(host.alias) || host.status !== 'ok') return;
    host.gpus.forEach(gpu => {
      const key = host.alias + '||' + gpu.index;
      const nowAvail = _gpuAvailable(gpu);
      const wasAvail = prevAvailability[key];
      if (nowAvail && wasAvail === false) {
        new Notification('GPU Available — ' + host.alias, {
          body: 'GPU ' + gpu.index + ' (' + gpu.name + ')  ' + Math.round(gpu.memory_free_mb / 1024 * 10) / 10 + ' GB free',
          tag: 'gnvitop-' + host.alias + '-' + gpu.index,
        });
      }
      prevAvailability[key] = nowAvail;
    });
  });
}

function toggleCollapse(alias) {
  const collapsing = !collapsedHosts.has(alias);
  if (collapsing) {
    // Animate first, then re-render to move card to Folded section
    let card = null;
    document.querySelectorAll('.host-card').forEach(c => { if (c.dataset.alias === alias) card = c; });
    if (card) card.classList.add('collapsed');
    collapsedHosts.add(alias);
    localStorage.setItem('gnvitop-collapsed', JSON.stringify([...collapsedHosts]));
    setTimeout(() => { if (lastData) renderHosts(lastData.hosts); }, 150);
  } else {
    // Re-render first (card moves to expanded section), then animate open
    collapsedHosts.delete(alias);
    localStorage.setItem('gnvitop-collapsed', JSON.stringify([...collapsedHosts]));
    if (lastData) renderHosts(lastData.hosts);
    let card = null;
    document.querySelectorAll('.host-card').forEach(c => { if (c.dataset.alias === alias) card = c; });
    if (card) {
      card.classList.add('collapsed');
      getComputedStyle(card.querySelector('.host-body')).maxHeight; // force reflow
      card.classList.remove('collapsed');
    }
  }
}

function toggleGlobalWatch() {
  if (!lastData) return;
  const aliases = lastData.hosts.map(h => h.alias);
  const allWatched = aliases.every(a => watchedHosts.has(a));
  if (allWatched) {
    aliases.forEach(a => watchedHosts.delete(a));
  } else {
    aliases.forEach(a => watchedHosts.add(a));
    if (Notification.permission === 'default') Notification.requestPermission();
  }
  localStorage.setItem('gnvitop-watched', JSON.stringify([...watchedHosts]));
  _updateGlobalWatchBtn();
  const btn = document.getElementById('global-watch-btn');
  if (btn) {
    btn.classList.remove('watch-pop');
    void btn.offsetWidth;
    btn.classList.add('watch-pop');
  }
  if (lastData) renderHosts(lastData.hosts);
}

function _updateGlobalWatchBtn() {
  const btn = document.getElementById('global-watch-btn');
  if (!btn || !lastData) return;
  const aliases = lastData.hosts.map(h => h.alias);
  const allWatched = aliases.length > 0 && aliases.every(a => watchedHosts.has(a));
  btn.classList.toggle('watching', allWatched);
  btn.textContent = allWatched ? '\uD83D\uDD14' : '\uD83D\uDD15';
  btn.title = allWatched ? 'Unwatch all hosts' : 'Watch all hosts for free GPUs';
}

function setInterval_(secs) {
  refreshIntervalSecs = parseInt(secs);
  localStorage.setItem('gnvitop-interval', secs);
  setupAutoRefresh();
}

function setMode(mode) {
  currentMode = mode;
  document.body.classList.toggle('compact', mode === 'compact');
  document.getElementById('mode-normal').classList.toggle('active', mode === 'normal');
  document.getElementById('mode-compact').classList.toggle('active', mode === 'compact');
  localStorage.setItem('gnvitop-mode', mode);
  if (lastData) { renderSummary(lastData.hosts); renderHosts(lastData.hosts); }
}
currentMode = localStorage.getItem('gnvitop-mode') || 'normal';
setMode(currentMode);

// Restore interval selector
(function() {
  const sel = document.getElementById('interval-select');
  if (sel) {
    const saved = localStorage.getItem('gnvitop-interval');
    if (saved) { sel.value = saved; refreshIntervalSecs = parseInt(saved); }
  }
})();

function usageClass(pct) {
  if (pct < 50) return 'usage-low';
  if (pct < 80) return 'usage-mid';
  return 'usage-high';
}

function tempClass(t) {
  if (t < 50) return 'temp-cool';
  if (t < 75) return 'temp-warm';
  return 'temp-hot';
}

function formatMB(mb) {
  if (mb >= 1024) return (mb / 1024).toFixed(1) + ' GB';
  return mb.toFixed(0) + ' MB';
}

function renderSummary(hosts) {
  const online = hosts.filter(h => h.status === 'ok');
  const totalGPUs = online.reduce((s, h) => s + h.gpus.length, 0);
  const totalFree = online.reduce((s, h) => s + h.gpus.reduce((gs, g) => gs + g.memory_free_mb, 0), 0);
  const idleGPUs = online.reduce((s, h) => s + h.gpus.filter(g => g.gpu_utilization_pct < 10).length, 0);

  document.getElementById('summary-bar').innerHTML = `
    <div class="summary-card">
      <div class="label">Online Hosts</div>
      <div class="value" style="color:var(--success-text)">${online.length}<span style="color:var(--text-subtle);font-size:16px"> / ${hosts.length}</span></div>
    </div>
    <div class="summary-card">
      <div class="label">Total GPUs</div>
      <div class="value" style="color:var(--local-text)">${totalGPUs}</div>
    </div>
    <div class="summary-card">
      <div class="label">Idle GPUs (< 10%)</div>
      <div class="value" style="color:var(--success-text)">${idleGPUs}</div>
    </div>
    <div class="summary-card">
      <div class="label">Total Free Memory</div>
      <div class="value" style="color:var(--tpu-text)">${formatMB(totalFree)}</div>
    </div>
  `;
}

function renderProcessUsers(processes, hostUser) {
  if (!processes || !processes.length) return '';
  // Aggregate memory per user
  const userMem = {};
  for (const p of processes) {
    const u = p.user || 'unknown';
    userMem[u] = (userMem[u] || 0) + (p.gpu_memory_mb || 0);
  }
  const tags = Object.entries(userMem).map(([user, mem]) => {
    const isCurrent = user === hostUser;
    const cls = isCurrent ? 'user-tag current-user' : 'user-tag';
    return `<span class="${cls}">${user}<span class="user-mem">${formatMB(mem)}</span></span>`;
  }).join('');
  return `<div class="gpu-users">${tags}</div>`;
}

function renderGPU(gpu, hostUser) {
  const isTpu = gpu.gpu_utilization_pct < 0;
  const memPct = isTpu ? 0 : gpu.memory_usage_pct;
  const gpuPct = isTpu ? 0 : gpu.gpu_utilization_pct;
  const chipLabel = isTpu ? 'Chip' : 'GPU';
  const gpuPctColor = gpuPct < 10 ? 'var(--success-text)' : gpuPct < 50 ? 'var(--warning-text)' : 'var(--error-text)';
  const memLabel = isTpu
    ? `? / ${formatMB(gpu.memory_total_mb)}`
    : `${formatMB(gpu.memory_used_mb)} / ${formatMB(gpu.memory_total_mb)}`;

  if (currentMode === 'compact') {
    return `
      <div class="gpu-item">
        <div class="gpu-title">
          <span class="gpu-name">${chipLabel} ${gpu.index}: ${gpu.name}</span>
        </div>
        <div class="bar-container">
          <div class="bar-label">
            <span>HBM</span>
            <span>${memLabel}</span>
          </div>
          ${isTpu ? '' : `<div class="bar-track"><div class="bar-fill ${usageClass(memPct)}" style="width:${memPct}%"></div></div>`}
        </div>
        ${renderProcessUsers(gpu.processes, hostUser)}
      </div>
    `;
  }

  // Normal: full details
  return `
    <div class="gpu-item">
      <div class="gpu-title">
        <span class="gpu-name">${chipLabel} ${gpu.index}: ${gpu.name}</span>
        ${isTpu ? '' : `<span class="gpu-temp ${tempClass(gpu.temperature_c)}">${gpu.temperature_c}&deg;C</span>`}
      </div>
      <div class="bar-container">
        <div class="bar-label">
          <span>${isTpu ? 'Utilization' : 'GPU Utilization'}</span>
          <span>${isTpu ? 'N/A (install torch_xla)' : gpuPct + '%'}</span>
        </div>
        ${isTpu ? '' : `<div class="bar-track"><div class="bar-fill ${usageClass(gpuPct)}" style="width:${gpuPct}%"></div></div>`}
      </div>
      <div class="bar-container">
        <div class="bar-label">
          <span>HBM Memory</span>
          <span>${memLabel}</span>
        </div>
        ${isTpu ? '' : `<div class="bar-track"><div class="bar-fill ${usageClass(memPct)}" style="width:${memPct}%"></div></div>`}
      </div>
      ${renderProcessUsers(gpu.processes, hostUser)}
      <div class="gpu-stats">
        <div class="stat">
          <div class="stat-value" style="color:var(--text-muted)">${isTpu ? 'N/A' : `<span style="color:${gpuPctColor}">${gpuPct}%</span>`}</div>
          <div class="stat-label">Utilization</div>
        </div>
        <div class="stat">
          <div class="stat-value">${isTpu ? formatMB(gpu.memory_total_mb) : formatMB(gpu.memory_free_mb)}</div>
          <div class="stat-label">${isTpu ? 'HBM Total' : 'Free Memory'}</div>
        </div>
        <div class="stat">
          <div class="stat-value" style="color:var(--text-muted)">${isTpu ? 'N/A' : `${gpu.temperature_c}&deg;C`}</div>
          <div class="stat-label">Temperature</div>
        </div>
      </div>
    </div>
  `;
}

function renderHosts(hosts) {
  const container = document.getElementById('content');
  if (!hosts.length) {
    if (isFirstRender) return; // keep showing the initial loading spinner
    container.innerHTML = '<div class="loading">No hosts found in SSH config.</div>';
    return;
  }

  let filtered = currentMode === 'compact' ? hosts.filter(h => h.status === 'ok') : hosts;

  // Apply manual drag order if set, otherwise auto-sort
  if (hostOrder.length) {
    filtered = _applyHostOrder(filtered);
    // Still put collapsed at end within their manual position is preserved
  } else {
  // Sort: active user first, then normal, collapsed always last
  filtered.sort((a, b) => {
    const aCollapsed = collapsedHosts.has(a.alias);
    const bCollapsed = collapsedHosts.has(b.alias);
    if (aCollapsed !== bCollapsed) return aCollapsed - bCollapsed;
    const aHasMe = a.status === 'ok' && a.gpus.some(g => g.processes && g.processes.some(p => p.user === a.user));
    const bHasMe = b.status === 'ok' && b.gpus.some(g => g.processes && g.processes.some(p => p.user === b.user));
    if (aHasMe !== bHasMe) return bHasMe - aHasMe;
    return 0;
  });
  } // end else (no manual order)


  const wasFirst = isFirstRender;
  isFirstRender = false;

  const expanded  = filtered.filter(h => !collapsedHosts.has(h.alias));
  const collapsed = filtered.filter(h =>  collapsedHosts.has(h.alias));

  function renderCard(host) {
    let body = '';
    if (host.status === 'ok') {
      body = host.gpus.map(g => renderGPU(g, host.user)).join('');
    } else if (host.status === 'no_gpu') {
      body = `<div class="no-gpu-msg">${host.error || 'No NVIDIA GPU detected'}</div>`;
    } else {
      body = `<div class="error-msg">${host.error || 'Unknown error'}</div>`;
    }
    const isLocal    = host.is_local;
    const isTpu      = !!host.is_tpu;
    const isCollapsed = collapsedHosts.has(host.alias);
    const badgeClass = isLocal ? 'badge-local' : isTpu ? 'badge-tpu' : host.status === 'ok' ? 'badge-ok' : host.status === 'no_gpu' ? 'badge-no_gpu' : 'badge-error';
    const badgeText  = isLocal ? 'Local' : isTpu ? 'TPU' : host.status === 'ok' ? 'Online' : host.status === 'no_gpu' ? 'No GPU' : 'Offline';
    const cardClass  = `host-card status-${host.status}${isLocal ? ' is-local' : ''}${isTpu ? ' is-tpu' : ''}${isCollapsed ? ' collapsed' : ''}${wasFirst ? ' first-render' : ''}`;
    const collapsedInfo = (isCollapsed && host.status === 'ok')
      ? isTpu
        ? `<div class="collapsed-info">${host.gpus.length} chip${host.gpus.length !== 1 ? 's' : ''} &nbsp;·&nbsp; ${formatMB(host.gpus[0].memory_total_mb * host.gpus.length)} HBM</div>`
        : `<div class="collapsed-info">${host.gpus.length} GPU${host.gpus.length !== 1 ? 's' : ''} &nbsp;·&nbsp; Free: ${formatMB(host.gpus.reduce((s, g) => s + g.memory_free_mb, 0))}</div>`
      : '';
    const alias = host.alias.replace(/'/g, "\\'");
    return `
      <div class="${cardClass}" data-alias="${alias}">
        <div class="host-header" onclick="toggleCollapse('${alias}')">
          <div class="host-header-left" draggable="false">
            <span class="drag-handle" title="Drag to reorder" onclick="event.stopPropagation()">&#8942;&#8942;</span>
            <div>
              <div class="host-name">${host.alias}</div>
              <div class="host-info">${host.user}@${host.hostname}${host.port ? ':' + host.port : ''}</div>
              ${collapsedInfo}
            </div>
          </div>
          <div class="host-header-right">
            <button class="watch-btn${watchedHosts.has(host.alias) ? ' watching' : ''}" draggable="false" onclick="event.stopPropagation(); toggleWatch('${alias}')">${watchedHosts.has(host.alias) ? '&#128276;' : '&#128277;'}${(() => {
              if (host.status !== 'ok') return '<span class="watch-tooltip">Watch this host</span>';
              const free = host.gpus.filter(g => _gpuAvailable(g));
              const watching = watchedHosts.has(host.alias);
              if (free.length > 0) {
                const label = free.map(g => 'GPU ' + g.index + ' (' + Math.round(g.memory_free_mb/1024*10)/10 + 'GB free)').join('<br>');
                return '<span class="watch-tooltip" style="color:var(--success-text)">' + free.length + ' GPU' + (free.length>1?'s':'') + ' available:<br>' + label + (watching ? '<br><span style="color:var(--text-muted)">Click to stop watching</span>' : '<br><span style="color:var(--text-muted)">Click to watch</span>') + '</span>';
              }
              return '<span class="watch-tooltip">' + (watching ? 'Watching — notify on free GPU<br><span style="color:#94a3b8">Click to stop</span>' : 'Watch for free GPUs') + '</span>';
            })()}</button>
            <span class="status-badge ${badgeClass}">${badgeText}</span>
            <span class="collapse-arrow">&#9660;</span>
          </div>
        </div>
        <div class="host-body">${body}</div>
      </div>
    `;
  }

  let html = '<div class="host-grid">' + expanded.map(renderCard).join('') + '</div>';

  if (collapsed.length) {
    html += `
      <div class="folded-divider">
        <span class="folded-label">&#9660; Folded (${collapsed.length})</span>
      </div>
      <div class="host-grid host-grid-folded">` + collapsed.map(renderCard).join('') + '</div>';
  }

  container.innerHTML = html;
  container.querySelectorAll('.host-grid').forEach(g => _setupDrag(g));
  _updateGlobalWatchBtn();
}

async function fetchData(force) {
  const url = force ? '/api/refresh' : '/api/gpus';
  const resp = await fetch(url);
  return await resp.json();
}

// SSE-based streaming init: renders each host as it arrives
function initStream() {
  const es = new EventSource('/api/stream');
  const streamingHosts = [];
  let receivedDone = false;

  es.onmessage = function(e) {
    const msg = JSON.parse(e.data);
    if (msg.done) {
      receivedDone = true;
      es.close();
      // Replace lastData with complete sorted set from cache
      lastData = { hosts: streamingHosts, updated_at: msg.updated_at };
      updateTime(msg.updated_at);
      renderSummary(streamingHosts);
      renderHosts(streamingHosts);
      return;
    }
    streamingHosts.push(msg.host);
    // Re-render incrementally as hosts arrive
    renderSummary(streamingHosts);
    renderHosts(streamingHosts);
  };

  es.onerror = function() {
    es.close();
    if (!receivedDone && streamingHosts.length === 0) {
      // SSE failed before any data — fall back to regular fetch
      fetchData(false).then(data => {
        lastData = data;
        renderSummary(data.hosts);
        renderHosts(data.hosts);
        updateTime(data.updated_at);
      }).catch(() => {
        document.getElementById('content').innerHTML =
          '<div class="loading" style="color:#f87171">Failed to connect to server.</div>';
      });
    }
  };
}

function flashRefreshBtn() {
  const btn = document.getElementById('btn-refresh');
  btn.classList.remove('refreshing');
  void btn.offsetWidth; // reflow to restart animation
  btn.classList.add('refreshing');
  setTimeout(() => btn.classList.remove('refreshing'), 900);
}

async function refresh() {
  const btn = document.getElementById('btn-refresh');
  btn.disabled = true;
  btn.textContent = 'Refreshing...';
  flashRefreshBtn();
  try {
    lastData = await fetchData(true);
    renderSummary(lastData.hosts);
    renderHosts(lastData.hosts);
    updateTime(lastData.updated_at);
  } catch (e) {
    console.error(e);
  } finally {
    btn.disabled = false;
    btn.textContent = 'Refresh';
  }
}

function updateTime(ts) {
  const d = new Date(ts * 1000);
  document.getElementById('update-time').textContent = 'Updated: ' + d.toLocaleTimeString();
}

async function init() {
  setTheme(currentTheme);
  // Restore notify toggle state
  const notifyChk = document.getElementById('notify-toggle');
  if (notifyChk) {
    notifyChk.checked = notifyEnabled;
    document.body.classList.toggle('notify-off', !notifyEnabled);
  }
  // Try fast-path: if cache is warm, show data instantly then start SSE for next full refresh
  try {
    const cached = await fetchData(false);
    if (cached.hosts && cached.hosts.length > 0 && cached.updated_at > 0) {
      lastData = cached;
      renderSummary(cached.hosts);
      renderHosts(cached.hosts);
      updateTime(cached.updated_at);
      return; // cache was warm, no need for SSE on initial load
    }
  } catch (e) { /* ignore, fall through to SSE */ }

  // Cache empty or unavailable — use SSE for progressive load
  initStream();
}

function setupAutoRefresh() {
  clearInterval(autoRefreshTimer);
  const checkbox = document.getElementById('auto-refresh');
  function doRefresh() {
    flashRefreshBtn();
    fetchData(false).then(data => {
      lastData = data;
      renderSummary(data.hosts);
      renderHosts(data.hosts);
      updateTime(data.updated_at);
      checkWatchedNotifications(data.hosts);
    }).catch(() => {});
  }
  if (checkbox.checked) {
    autoRefreshTimer = setInterval(doRefresh, refreshIntervalSecs * 1000);
  }
  checkbox.onchange = () => {
    clearInterval(autoRefreshTimer);
    if (checkbox.checked) {
      autoRefreshTimer = setInterval(doRefresh, refreshIntervalSecs * 1000);
    }
  };
}

init();
setupAutoRefresh();
</script>
</body>
</html>"""
