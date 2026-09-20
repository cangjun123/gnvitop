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
    --text-muted: #cbd5e1;
    --text-subtle: #94a3b8;
    --icon-muted: #94a3b8;
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
    --text-muted: #475569;
    --text-subtle: #526173;
    --icon-muted: #64748b;
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
    color: var(--text-strong);
    letter-spacing: -0.5px;
  }

  .header-right {
    display: flex;
    align-items: center;
    gap: 16px;
  }

  .header-right > .header-divider,
  .header-right > .theme-toggle,
  .header-right > .mode-toggle,
  .header-right > .toggle-switch,
  .header-right > .global-watch-btn,
  .header-right > .interval-select {
    display: none;
  }

  .status-text {
    font-size: 13px;
    color: var(--text-muted);
  }

  .header-divider {
    width: 1px;
    height: 20px;
    background: var(--border);
    flex-shrink: 0;
  }

  .btn-refresh {
    padding: 6px 14px;
    border: 1px solid var(--border);
    background: var(--surface);
    color: var(--text);
    border-radius: 8px;
    cursor: pointer;
    font-size: 13px;
    transition: all 0.2s;
    white-space: nowrap;
  }
  .btn-refresh:hover { background: var(--hover-soft); border-color: var(--border-hover); color: var(--text-strong); }
  .btn-refresh:disabled { opacity: 0.5; cursor: not-allowed; }
  @keyframes refreshPulse {
    0%   { box-shadow: 0 0 0 0 rgba(96,165,250,0.5); }
    50%  { box-shadow: 0 0 0 6px rgba(96,165,250,0); background: var(--refresh-pulse-bg); border-color: var(--local-text); }
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
    color: var(--icon-muted);
    transition: color 0.2s, transform 0.2s;
    line-height: 1;
  }
  .global-watch-btn:hover { color: var(--text-muted); transform: scale(1.1); }
  .global-watch-btn.watching { color: var(--warning-text); }

  /* Drag-and-drop */
  .host-card.dragging { opacity: 0.4; cursor: grabbing; }
  .host-card.drag-over { outline: 2px dashed #60a5fa; outline-offset: 2px; }
  .drag-handle {
    cursor: grab;
    color: var(--icon-muted);
    font-size: 14px;
    padding: 2px 4px;
    user-select: none;
    line-height: 1;
  }
  .drag-handle:hover { color: var(--text-muted); }
  .drag-handle:active { cursor: grabbing; }

  .summary-bar {
    display: flex;
    gap: 16px;
    margin-bottom: 16px;
    flex-wrap: wrap;
    position: sticky;
    top: 0;
    z-index: 50;
    background: var(--bg);
    padding: 10px 0 12px;
  }

  .summary-card {
    background: var(--surface);
    border: 1px solid var(--border);
    border-radius: 10px;
    padding: 16px 24px;
    min-width: 160px;
    flex: 1;
  }

  .summary-card .label {
    font-size: 12px;
    color: var(--text-muted);
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
    background: var(--surface);
    border: 1px solid var(--border);
    border-radius: 12px;
    overflow: hidden;
    transition: border-color 0.2s, transform 0.15s, box-shadow 0.2s;
  }
  .host-card:hover {
    border-color: var(--border-hover);
    transform: translateY(-2px);
    box-shadow: var(--shadow-card);
  }
  .host-header:hover {
    background: var(--hover-soft);
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
    border-bottom: 1px solid var(--border);
  }

  .host-name {
    font-size: 16px;
    font-weight: 600;
    color: var(--text-strong);
  }

  .host-info {
    font-size: 12px;
    color: var(--text-subtle);
  }

  .status-badge {
    font-size: 11px;
    padding: 3px 10px;
    border-radius: 12px;
    font-weight: 600;
    text-transform: uppercase;
    letter-spacing: 0.3px;
  }
  .badge-ok { background: var(--success-bg); color: var(--success-text); }
  .badge-no_gpu { background: var(--warning-bg); color: var(--warning-text); }
  .badge-error { background: var(--error-bg); color: var(--error-text); }
  .badge-tpu { background: var(--tpu-bg); color: var(--tpu-text); }

  .host-body { padding: 16px 20px; }

  .error-msg {
    color: var(--error-text);
    font-size: 13px;
    padding: 8px 0;
  }

  .no-gpu-msg {
    color: var(--warning-text);
    font-size: 13px;
    padding: 8px 0;
  }

  .gpu-item {
    padding: 12px 0;
  }
  .gpu-item + .gpu-item { border-top: 1px solid var(--border); }

  .system-panel {
    padding: 12px 0;
    border-bottom: 1px solid var(--border);
    margin-bottom: 4px;
  }
  .system-title {
    font-size: 13px;
    font-weight: 700;
    color: var(--text);
    margin-bottom: 10px;
  }
  .system-grid {
    display: grid;
    grid-template-columns: repeat(3, 1fr);
    gap: 8px;
  }
  .system-metric {
    background: var(--surface-muted);
    border-radius: 7px;
    padding: 9px;
  }
  .system-metric-name {
    color: var(--text-subtle);
    font-size: 10px;
    font-weight: 700;
    text-transform: uppercase;
    letter-spacing: 0.4px;
    margin-bottom: 4px;
  }
  .system-metric-value {
    color: var(--text);
    font-size: 15px;
    font-weight: 700;
  }
  .system-metric-sub {
    color: var(--text-subtle);
    font-size: 11px;
    margin-top: 3px;
  }

  .gpu-title {
    display: flex;
    justify-content: space-between;
    align-items: center;
    margin-bottom: 10px;
  }

  .gpu-name {
    font-size: 14px;
    font-weight: 600;
    color: var(--text);
  }

  .gpu-temp {
    font-size: 12px;
    padding: 2px 8px;
    border-radius: 6px;
    font-weight: 600;
  }
  .temp-cool { background: var(--success-bg); color: var(--success-text); }
  .temp-warm { background: var(--warning-bg); color: var(--warning-text); }
  .temp-hot { background: var(--error-bg); color: var(--error-text); }

  .bar-container {
    margin-bottom: 8px;
  }

  .bar-label {
    display: flex;
    justify-content: space-between;
    font-size: 12px;
    color: var(--text-muted);
    margin-bottom: 4px;
  }

  .bar-track {
    height: 8px;
    background: var(--surface-muted);
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
    background: var(--surface-muted);
    border-radius: 6px;
    padding: 8px;
  }

  .stat .stat-value {
    font-size: 16px;
    font-weight: 700;
    color: var(--text);
  }

  .stat .stat-label {
    font-size: 10px;
    color: var(--text-subtle);
    margin-top: 2px;
  }

  .loading {
    text-align: center;
    padding: 80px 20px;
    color: var(--text-muted);
    font-size: 16px;
  }

  .spinner {
    display: inline-block;
    width: 28px;
    height: 28px;
    border: 3px solid var(--border);
    border-top-color: var(--local-text);
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
    color: var(--text-muted);
    user-select: none;
    transition: color 0.2s;
  }
  .toggle-switch:hover { color: var(--text-strong); }
  .toggle-switch input { display: none; }
  .toggle-knob {
    width: 30px;
    height: 17px;
    background: var(--border);
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
    background: var(--text-muted);
    border-radius: 50%;
    top: 2px;
    left: 2px;
    transition: transform 0.2s, background 0.2s;
  }
  .toggle-switch input:checked ~ .toggle-knob { background: #1d4ed8; }
  .toggle-switch input:checked ~ .toggle-knob::after { transform: translateX(13px); background: #60a5fa; }
  .toggle-switch input:checked ~ .toggle-label { color: var(--text); }

  /* Universal tooltip */
  #ui-tooltip {
    position: fixed;
    background: var(--surface-muted);
    border: 1px solid var(--border);
    border-radius: 8px;
    padding: 7px 12px;
    font-size: 12px;
    color: var(--text);
    pointer-events: none;
    z-index: 9999;
    max-width: 260px;
    line-height: 1.5;
    box-shadow: var(--shadow-tooltip);
    opacity: 0;
    transition: opacity 0.15s ease;
  }
  #ui-tooltip.visible { opacity: 1; }

  .badge-local { background: var(--local-bg); color: var(--local-text); }

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
    background: var(--border);
    color: var(--text-muted);
    font-family: monospace;
  }

  .user-tag.current-user {
    background: var(--local-bg);
    color: var(--local-text);
    font-weight: 700;
    border: 1px solid #3b82f6;
  }

  .user-mem {
    color: var(--text-subtle);
    font-size: 10px;
    margin-left: 2px;
  }

  .mode-toggle {
    display: flex;
    background: var(--surface-muted);
    border: 1px solid var(--border);
    border-radius: 8px;
    overflow: hidden;
  }
  .mode-toggle button {
    padding: 5px 11px;
    border: none;
    background: transparent;
    color: var(--text-subtle);
    cursor: pointer;
    transition: all 0.2s;
    font-size: 13px;
    white-space: nowrap;
  }
  .mode-toggle button:hover { color: var(--text-muted); background: var(--hover-soft); }
  .mode-toggle button.active { background: var(--border); color: var(--text-strong); }

  .theme-toggle {
    display: flex;
    background: var(--surface-muted);
    border: 1px solid var(--border);
    border-radius: 8px;
    overflow: hidden;
  }
  .theme-toggle:hover { color: var(--text-strong); background: var(--hover-soft); }
  .theme-toggle button {
    padding: 5px 11px;
    border: none;
    background: transparent;
    color: var(--text-subtle);
    cursor: pointer;
    transition: all 0.2s;
    font-size: 13px;
    white-space: nowrap;
  }
  .theme-toggle button:hover { color: var(--text-muted); background: var(--hover-soft); }
  .theme-toggle button.active { background: var(--border); color: var(--text-strong); }

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
    background: var(--surface-muted);
    border: 1px solid var(--border);
    border-radius: 8px;
    color: var(--text-muted);
    font-size: 13px;
    padding: 5px 8px;
    cursor: pointer;
    outline: none;
    transition: border-color 0.2s, color 0.2s;
  }
  .interval-select:hover { border-color: var(--border-hover); color: var(--text-strong); }

  .settings-button {
    width: 34px;
    height: 34px;
    display: inline-flex;
    align-items: center;
    justify-content: center;
    border: 1px solid var(--border);
    background: var(--surface);
    color: var(--text);
    border-radius: 8px;
    cursor: pointer;
    transition: all 0.2s;
  }
  .settings-button:hover {
    border-color: var(--border-hover);
    background: var(--hover-soft);
    color: var(--text-strong);
  }
  .settings-button svg {
    width: 17px;
    height: 17px;
    fill: currentColor;
  }

  .settings-overlay {
    position: fixed;
    inset: 0;
    display: flex;
    justify-content: flex-end;
    background: rgba(2, 6, 23, 0.45);
    opacity: 0;
    pointer-events: none;
    transition: opacity 0.18s ease;
    z-index: 2000;
  }
  .settings-overlay.open {
    opacity: 1;
    pointer-events: auto;
  }
  .settings-panel {
    width: min(380px, calc(100vw - 28px));
    height: 100%;
    background: var(--surface);
    border-left: 1px solid var(--border);
    box-shadow: -16px 0 40px rgba(0,0,0,0.28);
    padding: 22px;
    transform: translateX(100%);
    transition: transform 0.22s ease;
    overflow-y: auto;
  }
  .settings-overlay.open .settings-panel { transform: translateX(0); }
  .settings-head {
    display: flex;
    justify-content: space-between;
    align-items: flex-start;
    gap: 16px;
    margin-bottom: 24px;
  }
  .settings-title {
    font-size: 20px;
    font-weight: 700;
    color: var(--text);
  }
  .settings-subtitle {
    font-size: 12px;
    color: var(--text-muted);
    margin-top: 4px;
  }
  .settings-close {
    width: 30px;
    height: 30px;
    border: 1px solid var(--border);
    background: var(--surface-muted);
    color: var(--text-muted);
    border-radius: 8px;
    cursor: pointer;
    font-size: 20px;
    line-height: 1;
  }
  .settings-close:hover {
    color: var(--text-strong);
    border-color: var(--border-hover);
    background: var(--hover-soft);
  }
  .settings-section {
    padding: 16px 0;
    border-top: 1px solid var(--border);
  }
  .settings-section-title {
    font-size: 11px;
    font-weight: 700;
    color: var(--text-subtle);
    letter-spacing: 0.7px;
    text-transform: uppercase;
    margin-bottom: 12px;
  }
  .settings-row {
    display: flex;
    align-items: center;
    justify-content: space-between;
    gap: 16px;
    min-height: 38px;
    color: var(--text);
    font-size: 13px;
  }
  .settings-row + .settings-row { margin-top: 12px; }
  .settings-note {
    color: var(--text-subtle);
    font-size: 12px;
    line-height: 1.45;
    margin-top: 8px;
  }
  .settings-global-watch {
    border: 1px solid var(--border);
    border-radius: 8px;
    width: 34px;
    height: 30px;
  }
  .server-toolbar {
    display: flex;
    gap: 8px;
    flex-wrap: wrap;
    margin-bottom: 12px;
  }
  .settings-action {
    padding: 6px 10px;
    border: 1px solid var(--border);
    border-radius: 8px;
    background: var(--surface-muted);
    color: var(--text);
    cursor: pointer;
    font-size: 12px;
    transition: all 0.2s;
  }
  .settings-action:hover {
    border-color: var(--border-hover);
    color: var(--text-strong);
  }
  html.theme-light .settings-action {
    color: #1e293b;
    background: #f8fafc;
    border-color: #cbd5e1;
  }
  html.theme-light .settings-action:hover {
    color: #0f172a;
    background: #f1f5f9;
    border-color: #94a3b8;
  }
  .server-list {
    display: grid;
    gap: 10px;
  }
  .server-card {
    border: 1px solid var(--border);
    background: var(--surface);
    border-radius: 10px;
    padding: 12px;
  }
  .server-card-head {
    display: flex;
    justify-content: space-between;
    align-items: center;
    gap: 10px;
    margin-bottom: 10px;
  }
  .server-head-actions {
    display: flex;
    align-items: center;
    gap: 10px;
    flex-shrink: 0;
  }
  .server-test {
    color: var(--local-text);
  }
  .server-test:disabled { opacity: 0.5; cursor: wait; }
  .server-test-status {
    display: none;
    font-size: 12px;
    line-height: 1.45;
    margin: -4px 0 10px;
  }
  .server-test-status:not(:empty) { display: block; }
  .server-test-status.ok { color: var(--success-text); }
  .server-test-status.warn { color: var(--warning-text); }
  .server-test-status.fail { color: var(--error-text); }
  .pw-label { min-height: 12px; }
  .tunnel-field {
    border-top: 1px dashed var(--border);
    padding-top: 10px;
    margin-top: 4px;
  }
  .tunnel-port-input { width: 90px; }
  .tunnel-status {
    font-size: 12px;
    margin-top: 6px;
    color: var(--text-subtle);
    min-height: 14px;
    word-break: break-all;
  }
  .tunnel-status.ok { color: var(--success-text); }
  .tunnel-status.fail { color: var(--error-text); }
  .server-card-title {
    font-weight: 700;
    color: var(--text);
    font-size: 13px;
  }
  .server-grid {
    display: grid;
    grid-template-columns: 1fr 1fr;
    gap: 8px;
  }
  .server-field {
    display: grid;
    gap: 4px;
  }
  .server-field.full { grid-column: 1 / -1; }
  .server-field label {
    color: var(--text-subtle);
    font-size: 10px;
    font-weight: 700;
    letter-spacing: 0.4px;
    text-transform: uppercase;
  }
  .server-metrics {
    display: flex;
    align-items: center;
    gap: 10px;
    flex-wrap: wrap;
  }
  .server-metrics .toggle-switch {
    font-size: 11px;
    min-height: 26px;
  }
  .server-input {
    width: 100%;
    border: 1px solid var(--border);
    border-radius: 7px;
    background: #1e293b;
    color: var(--text);
    padding: 7px 8px;
    font-size: 12px;
    outline: none;
  }
  .server-input:focus {
    border-color: #60a5fa;
  }
  html.theme-light .server-input {
    background: #f8fafc;
    color: #1e293b;
    border-color: #cbd5e1;
  }
  html.theme-light .server-test {
    color: var(--local-text);
    background: #f8fafc;
  }
  html.theme-light .server-input::placeholder {
    color: var(--text-subtle);
  }
  html.theme-light .server-input:focus {
    background: #f1f5f9;
    border-color: #60a5fa;
  }
  .settings-path-input {
    width: 170px;
    max-width: 56%;
  }
  .hidden-file-input { display: none; }
  .server-remove {
    border: none;
    background: transparent;
    color: var(--error-text);
    cursor: pointer;
    font-size: 12px;
  }
  .server-remove:hover { text-decoration: underline; }
  .server-empty {
    color: var(--text-subtle);
    font-size: 12px;
    padding: 12px;
    border: 1px dashed var(--border);
    border-radius: 10px;
  }
  .server-save-status {
    min-height: 16px;
    color: var(--text-subtle);
    font-size: 12px;
    margin-top: 10px;
  }

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
    color: var(--icon-muted);
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
    color: var(--icon-muted);
    transition: color 0.2s;
    line-height: 1;
    position: relative;
  }
  .watch-btn:hover { color: var(--text-muted); }
  .watch-btn.watching { color: var(--warning-text); }
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
    background: var(--surface-muted);
    border: 1px solid var(--border);
    border-radius: 8px;
    padding: 8px 12px;
    font-size: 12px;
    color: var(--text);
    white-space: nowrap;
    z-index: 100;
    pointer-events: none;
    box-shadow: var(--shadow-popover);
    min-width: 160px;
  }
  .watch-btn:hover .watch-tooltip { display: block; }
  .history-btn {
    background: transparent;
    border: 1px solid transparent;
    border-radius: 8px;
    color: var(--icon-muted);
    cursor: pointer;
    display: inline-flex;
    align-items: center;
    justify-content: center;
    width: 28px;
    height: 26px;
    transition: all 0.2s;
  }
  .history-btn:hover {
    color: #93c5fd;
    background: rgba(96, 165, 250, 0.08);
    border-color: rgba(96, 165, 250, 0.25);
  }
  .history-btn svg {
    width: 16px;
    height: 16px;
  }
  .collapsed-info {
    font-size: 11px;
    color: var(--text-subtle);
    margin-top: 2px;
  }

  .history-overlay {
    position: fixed;
    inset: 0;
    background: rgba(2, 6, 23, 0.72);
    backdrop-filter: blur(10px);
    z-index: 4000;
    display: none;
    align-items: center;
    justify-content: center;
    padding: 24px;
  }
  .history-overlay.open { display: flex; }
  .history-modal {
    width: min(920px, 96vw);
    max-height: 88vh;
    overflow: auto;
    background: var(--surface);
    color: var(--text);
    border: 1px solid var(--border);
    border-radius: 18px;
    box-shadow: var(--shadow-popover);
    padding: 20px;
  }
  .history-head {
    display: flex;
    align-items: flex-start;
    justify-content: space-between;
    gap: 14px;
    margin-bottom: 16px;
  }
  .history-title {
    font-size: 18px;
    font-weight: 800;
    color: var(--text-strong);
  }
  .history-subtitle {
    color: var(--text-subtle);
    font-size: 12px;
    margin-top: 4px;
  }
  .history-close {
    border: 1px solid var(--border);
    background: var(--surface-muted);
    color: var(--text-muted);
    border-radius: 10px;
    width: 32px;
    height: 30px;
    cursor: pointer;
    font-size: 18px;
    line-height: 1;
  }
  .history-controls {
    display: flex;
    gap: 8px;
    flex-wrap: wrap;
    margin-bottom: 14px;
  }
  .history-range {
    border: 1px solid var(--border);
    background: var(--surface-muted);
    color: var(--text-muted);
    border-radius: 999px;
    padding: 6px 11px;
    cursor: pointer;
    font-size: 12px;
  }
  .history-range.active {
    color: var(--text-strong);
    border-color: var(--border-hover);
    background: var(--hover-soft);
  }
  .history-chart {
    border: 1px solid var(--border);
    background: var(--surface-muted);
    border-radius: 14px;
    padding: 12px;
    min-height: 310px;
    position: relative;
  }
  .history-chart svg {
    width: 100%;
    height: 280px;
    display: block;
  }
  .history-hover {
    opacity: 0;
    pointer-events: none;
    transition: opacity 0.12s;
  }
  .history-chart:hover .history-hover { opacity: 1; }
  .history-tooltip {
    position: absolute;
    min-width: 170px;
    background: var(--surface);
    border: 1px solid var(--border);
    color: var(--text);
    border-radius: 12px;
    padding: 9px 10px;
    font-size: 12px;
    box-shadow: var(--shadow-popover);
    pointer-events: none;
    display: none;
    z-index: 2;
  }
  .history-tooltip-title {
    color: var(--text-strong);
    font-weight: 800;
    margin-bottom: 6px;
  }
  .history-tooltip-row {
    display: flex;
    align-items: center;
    justify-content: space-between;
    gap: 14px;
    margin-top: 3px;
  }
  .history-tooltip-label {
    display: inline-flex;
    align-items: center;
    gap: 6px;
    color: var(--text-muted);
  }
  .history-legend {
    display: flex;
    gap: 10px;
    flex-wrap: wrap;
    margin-top: 10px;
    color: var(--text-muted);
    font-size: 12px;
  }
  .history-legend-item {
    display: inline-flex;
    align-items: center;
    gap: 6px;
  }
  .history-dot {
    width: 9px;
    height: 9px;
    border-radius: 999px;
  }
  .history-empty {
    color: var(--text-muted);
    padding: 60px 16px;
    text-align: center;
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
    background: var(--border);
  }
  .folded-label {
    font-size: 11px;
    font-weight: 600;
    color: var(--text-subtle);
    text-transform: uppercase;
    letter-spacing: 0.8px;
    white-space: nowrap;
  }
  .host-grid-folded .host-card { opacity: 0.75; }
  .host-grid-folded .host-card:hover { opacity: 1; }

  /* Theme-aware overrides that differ from the base rules */
  .settings-section-title,
  .system-metric-name,
  .system-metric-sub,
  .server-field label,
  .server-empty,
  .server-save-status,
  .settings-subtitle,
  .settings-note { color: var(--icon-muted); }

  /* Responsive */
  @media (max-width: 960px) {
    body { padding: 16px; }
    .header { flex-wrap: wrap; gap: 10px; }
    .header-right { flex-wrap: wrap; gap: 8px; row-gap: 8px; }
    .host-grid, body.compact .host-grid { grid-template-columns: repeat(auto-fill, minmax(300px, 1fr)); }
  }
  @media (max-width: 640px) {
    body { padding: 10px; }
    .header h1 { font-size: 22px; }
    .host-grid, body.compact .host-grid { grid-template-columns: 1fr; }
    .summary-bar { gap: 10px; }
    .summary-card { min-width: calc(50% - 5px); padding: 12px 16px; }
    .summary-card .value { font-size: 22px; }
    .system-grid { grid-template-columns: 1fr; }
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
    <div class="theme-toggle" id="theme-toggle" data-tip="切换界面主题">
      <button onclick="setTheme('dark')" id="theme-dark">深色</button>
      <button onclick="setTheme('light')" id="theme-light">浅色</button>
    </div>
    <div class="header-divider"></div>
    <div class="mode-toggle" id="mode-toggle">
      <button onclick="setMode('compact')" id="mode-compact" data-tip="紧凑视图：卡片更小，隐藏主机详情">紧凑</button>
      <button onclick="setMode('normal')" id="mode-normal" data-tip="展开视图：完整卡片，显示全部 GPU 详情">展开</button>
    </div>
    <div class="header-divider"></div>
    <label class="toggle-switch" data-tip="开启 GPU 空闲通知。用每张卡片上的 🔔 铃铛选择要监控的主机。">
      <input type="checkbox" id="notify-toggle" onchange="setNotifyEnabled(this.checked)">
      <span class="toggle-knob"></span>
      <span class="toggle-label">&#128276; 通知</span>
    </label>
    <button class="global-watch-btn" id="global-watch-btn" onclick="toggleGlobalWatch()" data-tip="监控所有主机 — 任一 GPU 空闲时通知">&#128277;</button>
    <div class="header-divider"></div>
    <label class="toggle-switch" data-tip="自动刷新：按所选间隔自动获取最新 GPU 数据">
      <input type="checkbox" id="auto-refresh" checked>
      <span class="toggle-knob"></span>
      <span class="toggle-label">自动刷新</span>
    </label>
    <select class="interval-select" id="interval-select" onchange="setInterval_(this.value)" data-tip="自动刷新间隔">
      <option value="5">5 秒</option>
      <option value="10">10 秒</option>
      <option value="30" selected>30 秒</option>
      <option value="300">5 分钟</option>
    </select>
    <button class="btn-refresh" id="btn-refresh" onclick="refresh()">刷新</button>
    <button class="settings-button" id="settings-button" onclick="toggleSettings(true)" aria-label="打开设置" data-tip="打开设置">
      <svg viewBox="0 0 24 24" aria-hidden="true">
        <path d="M19.43 12.98c.04-.32.07-.65.07-.98s-.02-.66-.07-.98l2.11-1.65c.19-.15.24-.42.12-.64l-2-3.46c-.12-.22-.37-.31-.6-.22l-2.49 1a7.2 7.2 0 0 0-1.69-.98L14.5 2.42A.5.5 0 0 0 14 2h-4a.5.5 0 0 0-.49.42L9.13 5.07c-.6.24-1.17.57-1.69.98l-2.49-1a.5.5 0 0 0-.6.22l-2 3.46a.5.5 0 0 0 .12.64l2.11 1.65c-.04.32-.08.65-.08.98s.03.66.08.98l-2.11 1.65a.5.5 0 0 0-.12.64l2 3.46c.12.22.37.31.6.22l2.49-1c.52.4 1.08.73 1.69.98l.38 2.65c.04.24.25.42.49.42h4c.24 0 .45-.18.49-.42l.38-2.65c.6-.24 1.17-.57 1.69-.98l2.49 1c.23.08.48 0 .6-.22l2-3.46a.5.5 0 0 0-.12-.64l-2.11-1.65ZM12 15.5A3.5 3.5 0 1 1 12 8a3.5 3.5 0 0 1 0 7.5Z"/>
      </svg>
    </button>
  </div>
</div>

<div class="settings-overlay" id="settings-overlay" onmousedown="overlayMouseDown(event)" onclick="closeSettingsOnBackdrop(event)">
  <aside class="settings-panel" role="dialog" aria-modal="true" aria-labelledby="settings-title">
    <div class="settings-head">
      <div>
        <div class="settings-title" id="settings-title">设置</div>
        <div class="settings-subtitle">自定义界面显示与刷新行为。</div>
      </div>
      <button class="settings-close" onclick="toggleSettings(false)" aria-label="关闭设置">&times;</button>
    </div>

    <section class="settings-section">
      <div class="settings-section-title">外观</div>
      <div class="settings-row">
        <span>主题</span>
        <div class="theme-toggle">
          <button onclick="setSettingsTheme('dark')" id="settings-theme-dark">深色</button>
          <button onclick="setSettingsTheme('light')" id="settings-theme-light">浅色</button>
        </div>
      </div>
      <div class="settings-row">
        <span>布局</span>
        <div class="mode-toggle">
          <button onclick="setSettingsMode('compact')" id="settings-mode-compact">紧凑</button>
          <button onclick="setSettingsMode('normal')" id="settings-mode-normal">展开</button>
        </div>
      </div>
    </section>

    <section class="settings-section">
      <div class="settings-section-title">通知</div>
      <div class="settings-row">
        <span>GPU 空闲时通知</span>
        <label class="toggle-switch" data-tip="启用 GPU 空闲通知。可在每张卡片上用铃铛选择服务器。">
          <input type="checkbox" id="settings-notify-toggle" onchange="setSettingsNotify(this.checked)">
          <span class="toggle-knob"></span>
          <span class="toggle-label">通知</span>
        </label>
      </div>
      <div class="settings-row">
        <span>监控所有服务器</span>
        <button class="global-watch-btn settings-global-watch" id="settings-global-watch-btn" onclick="toggleGlobalWatch()" data-tip="监控所有服务器的空闲 GPU">&#128277;</button>
      </div>
      <div class="settings-note">启用通知后，仍可在每张服务器卡片上单独选择要监控的服务器。</div>
    </section>

    <section class="settings-section">
      <div class="settings-section-title">刷新</div>
      <div class="settings-row">
        <span>自动刷新</span>
        <label class="toggle-switch" data-tip="按所选间隔自动获取最新 GPU 数据">
          <input type="checkbox" id="settings-auto-refresh" onchange="setSettingsAutoRefresh(this.checked)" checked>
          <span class="toggle-knob"></span>
          <span class="toggle-label">启用</span>
        </label>
      </div>
      <div class="settings-row">
        <span>间隔</span>
        <select class="interval-select" id="settings-interval-select" onchange="setSettingsInterval(this.value)" data-tip="自动刷新间隔">
          <option value="5">5 秒</option>
          <option value="10">10 秒</option>
          <option value="30" selected>30 秒</option>
          <option value="300">5 分钟</option>
        </select>
      </div>
      <div class="settings-row">
        <span>监控本机</span>
        <label class="toggle-switch" data-tip="将本机作为 localhost 加入监控结果">
          <input type="checkbox" id="settings-monitor-local" onchange="setSettingsMonitorLocal(this.checked)" checked>
          <span class="toggle-knob"></span>
          <span class="toggle-label">本机</span>
        </label>
      </div>
    </section>

    <section class="settings-section">
      <div class="settings-section-title">默认指标</div>
      <div class="settings-row">
        <span>GPU</span>
        <label class="toggle-switch">
          <input type="checkbox" id="settings-metric-gpu" onchange="setMetricSetting('gpu', this.checked)" checked>
          <span class="toggle-knob"></span>
          <span class="toggle-label">GPU</span>
        </label>
      </div>
      <div class="settings-row">
        <span>CPU</span>
        <label class="toggle-switch">
          <input type="checkbox" id="settings-metric-cpu" onchange="setMetricSetting('cpu', this.checked)" checked>
          <span class="toggle-knob"></span>
          <span class="toggle-label">CPU</span>
        </label>
      </div>
      <div class="settings-row">
        <span>内存</span>
        <label class="toggle-switch">
          <input type="checkbox" id="settings-metric-memory" onchange="setMetricSetting('memory', this.checked)" checked>
          <span class="toggle-knob"></span>
          <span class="toggle-label">内存</span>
        </label>
      </div>
      <div class="settings-row">
        <span>硬盘</span>
        <label class="toggle-switch">
          <input type="checkbox" id="settings-metric-disk" onchange="setMetricSetting('disk', this.checked)" checked>
          <span class="toggle-knob"></span>
          <span class="toggle-label">硬盘</span>
        </label>
      </div>
      <div class="settings-row">
        <span>本机磁盘路径</span>
        <input class="server-input settings-path-input" id="settings-local-disk-path" value="~" placeholder="~, /, /data" oninput="setLocalDiskPath(this.value)" onblur="syncSettingsControls()" data-tip="监控 localhost 上包含此路径的文件系统">
      </div>
      <div class="settings-note">这些默认值用于本机以及新添加/导入的服务器。远程服务器可在各自卡片中覆盖指标和磁盘路径。</div>
    </section>

    <section class="settings-section">
      <div class="settings-section-title">服务器</div>
      <div class="server-toolbar">
        <button class="settings-action" onclick="addServerConfig()">添加服务器</button>
        <button class="settings-action" onclick="importSshConfig(false)">导入 SSH 配置</button>
        <button class="settings-action" onclick="exportServerConfig()">导出配置</button>
        <button class="settings-action" onclick="selectConfigImportFile()">导入配置</button>
      </div>
      <input class="hidden-file-input" id="config-import-file" type="file" accept="application/json,.json" onchange="importConfigFile(this.files[0]); this.value='';">
      <div class="settings-note">服务器配置独立于 SSH 配置保存。修改会自动保存。密码保存在本地 gnvitop 配置文件中，保存后会用本地密钥加密存储；导出的配置文件仍包含可用的密码。</div>
      <div class="server-save-status" id="server-save-status"></div>
      <div class="server-list" id="server-list">
        <div class="server-empty">正在加载服务器配置...</div>
      </div>
    </section>
  </aside>
</div>

<div class="history-overlay" id="history-overlay" onmousedown="overlayMouseDown(event)" onclick="closeHistoryOnBackdrop(event)">
  <div class="history-modal" onclick="event.stopPropagation()">
    <div class="history-head">
      <div>
        <div class="history-title" id="history-title">历史</div>
        <div class="history-subtitle" id="history-subtitle">采样数据保留 7 天。</div>
      </div>
      <button class="history-close" onclick="closeHistory()" aria-label="关闭历史">&times;</button>
    </div>
    <div class="history-controls">
      <button class="history-range active" data-range="1h" onclick="setHistoryRange('1h')">1 小时</button>
      <button class="history-range" data-range="6h" onclick="setHistoryRange('6h')">6 小时</button>
      <button class="history-range" data-range="24h" onclick="setHistoryRange('24h')">24 小时</button>
      <button class="history-range" data-range="7d" onclick="setHistoryRange('7d')">7 天</button>
    </div>
    <div class="history-chart" id="history-chart">
      <div class="history-empty">请选择一台主机查看历史。</div>
    </div>
  </div>
</div>

<div class="summary-bar" id="summary-bar"></div>
<div id="content">
  <div class="loading"><div class="spinner"></div><br>正在连接主机…</div>
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
let serverConfigs = [];
let monitorLocal = true;
let metricSettings = {gpu: true, cpu: true, memory: true, disk: true};
let localDiskPath = '~';
let serverSaveTimer = null;
let historyHost = null;
let historyRange = '1h';

function setTheme(theme) {
  currentTheme = theme === 'light' ? 'light' : 'dark';
  document.documentElement.classList.toggle('theme-light', currentTheme === 'light');
  localStorage.setItem('gnvitop-theme', currentTheme);
  const darkBtn = document.getElementById('theme-dark');
  const lightBtn = document.getElementById('theme-light');
  if (darkBtn) darkBtn.classList.toggle('active', currentTheme === 'dark');
  if (lightBtn) lightBtn.classList.toggle('active', currentTheme === 'light');
  syncSettingsControls();
}

function toggleTheme() {
  setTheme(currentTheme === 'light' ? 'dark' : 'light');
}

function toggleSettings(open) {
  const overlay = document.getElementById('settings-overlay');
  if (!overlay) return;
  syncSettingsControls();
  if (open && !serverConfigs.length) loadServerConfigs();
  overlay.classList.toggle('open', !!open);
  if (open) {
    refreshTunnelStatuses();
    if (!tunnelStatusTimer) tunnelStatusTimer = setInterval(refreshTunnelStatuses, 3000);
  } else if (tunnelStatusTimer) {
    clearInterval(tunnelStatusTimer);
    tunnelStatusTimer = null;
  }
}

let tunnelStatusTimer = null;
async function refreshTunnelStatuses() {
  try {
    const resp = await fetch('/api/tunnels');
    const data = await resp.json();
    document.querySelectorAll('.tunnel-status').forEach(el => {
      const idx = parseInt(el.dataset.tunnelIndex, 10);
      const host = serverConfigs[idx];
      if (!host) { el.textContent = ''; el.className = 'tunnel-status'; return; }
      const st = (data.tunnels || {})[host.alias];
      if (!host.tunnel_enabled || !st) { el.textContent = ''; el.className = 'tunnel-status'; return; }
      const port = st.port || host.tunnel_port || 7890;
      if (st.status === 'running') {
        el.textContent = '运行中：' + (host.hostname || host.alias) + ':' + port + ' → 本机:' + port;
        el.className = 'tunnel-status ok';
      } else if (st.status === 'reconnecting') {
        el.textContent = '重连中：' + (st.error || '未知原因');
        el.className = 'tunnel-status fail';
      } else if (st.status === 'starting') {
        el.textContent = '连接中…';
        el.className = 'tunnel-status';
      } else {
        el.textContent = '已停止';
        el.className = 'tunnel-status';
      }
    });
  } catch (e) {}
}

let _overlayMouseDown = false;
function overlayMouseDown(event) {
  _overlayMouseDown = event.target.id === 'settings-overlay' || event.target.id === 'history-overlay';
}
function closeSettingsOnBackdrop(event) {
  // Only close on a real click that started on the backdrop itself —
  // not when a text selection begun inside the panel is released outside it.
  if (_overlayMouseDown && event.target.id === 'settings-overlay') toggleSettings(false);
  _overlayMouseDown = false;
}

document.addEventListener('keydown', event => {
  if (event.key === 'Escape') {
    toggleSettings(false);
    closeHistory();
  }
});

function syncSettingsControls() {
  const stDark = document.getElementById('settings-theme-dark');
  const stLight = document.getElementById('settings-theme-light');
  const smCompact = document.getElementById('settings-mode-compact');
  const smNormal = document.getElementById('settings-mode-normal');
  const sNotify = document.getElementById('settings-notify-toggle');
  const sAuto = document.getElementById('settings-auto-refresh');
  const sInterval = document.getElementById('settings-interval-select');
  const sMonitorLocal = document.getElementById('settings-monitor-local');
  const sLocalDiskPath = document.getElementById('settings-local-disk-path');
  if (stDark) stDark.classList.toggle('active', currentTheme === 'dark');
  if (stLight) stLight.classList.toggle('active', currentTheme === 'light');
  if (smCompact) smCompact.classList.toggle('active', currentMode === 'compact');
  if (smNormal) smNormal.classList.toggle('active', currentMode === 'normal');
  if (sNotify) sNotify.checked = notifyEnabled;
  const auto = document.getElementById('auto-refresh');
  if (sAuto && auto) sAuto.checked = auto.checked;
  if (sInterval) sInterval.value = String(refreshIntervalSecs);
  if (sMonitorLocal) sMonitorLocal.checked = monitorLocal;
  if (sLocalDiskPath && document.activeElement !== sLocalDiskPath) sLocalDiskPath.value = localDiskPath || '~';
  Object.keys(metricSettings).forEach(key => {
    const el = document.getElementById('settings-metric-' + key);
    if (el) el.checked = metricSettings[key] !== false;
  });
  syncSettingsGlobalWatchBtn();
}

function setSettingsTheme(theme) {
  setTheme(theme);
}

function setSettingsMode(mode) {
  setMode(mode);
}

function setSettingsNotify(enabled) {
  const notify = document.getElementById('notify-toggle');
  if (notify) notify.checked = enabled;
  setNotifyEnabled(enabled);
  syncSettingsControls();
}

function setSettingsAutoRefresh(enabled) {
  const auto = document.getElementById('auto-refresh');
  if (auto) {
    auto.checked = enabled;
    if (typeof auto.onchange === 'function') auto.onchange();
  }
  syncSettingsControls();
}

function setSettingsInterval(secs) {
  const interval = document.getElementById('interval-select');
  if (interval) interval.value = secs;
  setInterval_(secs);
  syncSettingsControls();
}

async function setSettingsMonitorLocal(enabled) {
  monitorLocal = !!enabled;
  const status = document.getElementById('server-save-status');
  if (status) status.textContent = '正在保存本机监控设置...';
  syncSettingsControls();
  scheduleServerConfigSaveNow();
}

function setMetricSetting(metric, enabled) {
  metricSettings[metric] = !!enabled;
  const status = document.getElementById('server-save-status');
  if (status) status.textContent = '正在保存指标设置...';
  syncSettingsControls();
  scheduleServerConfigSaveNow();
}

function setLocalDiskPath(value) {
  localDiskPath = value;
  const status = document.getElementById('server-save-status');
  if (status) status.textContent = '正在保存本机磁盘路径...';
  scheduleServerConfigSaveNow();
}

function syncSettingsGlobalWatchBtn() {
  const source = document.getElementById('global-watch-btn');
  const target = document.getElementById('settings-global-watch-btn');
  if (!source || !target) return;
  target.textContent = source.textContent;
  target.classList.toggle('watching', source.classList.contains('watching'));
  target.title = target.classList.contains('watching') ? '取消监控所有服务器' : '监控所有服务器的空闲 GPU';
}

function escapeHtml(value) {
  return String(value ?? '').replace(/[&<>"']/g, c => ({
    '&': '&amp;', '<': '&lt;', '>': '&gt;', '"': '&quot;', "'": '&#39;'
  }[c]));
}

function normalizeMetricConfig(metrics) {
  return Object.assign({gpu: true, cpu: true, memory: true, disk: true}, metrics || {});
}

async function loadServerConfigs() {
  const list = document.getElementById('server-list');
  try {
    const resp = await fetch('/api/config/hosts');
    const data = await resp.json();
    serverConfigs = data.hosts || [];
    monitorLocal = data.monitor_local !== false;
    metricSettings = normalizeMetricConfig(data.metrics);
    localDiskPath = data.local_disk_path || data.disk_path || '~';
    syncSettingsControls();
    renderServerConfigs();
  } catch (e) {
    if (list) list.innerHTML = '<div class="server-empty">加载服务器配置失败。</div>';
  }
}

function renderServerMetricToggle(index, metrics, key, label) {
  return `
    <label class="toggle-switch">
      <input type="checkbox" ${metrics[key] !== false ? 'checked' : ''} onchange="updateServerMetric(${index}, '${key}', this.checked)">
      <span class="toggle-knob"></span>
      <span class="toggle-label">${label}</span>
    </label>
  `;
}

function renderServerMetricToggles(index, host) {
  const metrics = normalizeMetricConfig(host.metrics || metricSettings);
  return `
    <div class="server-field full">
      <label>指标</label>
      <div class="server-metrics">
        ${renderServerMetricToggle(index, metrics, 'gpu', 'GPU')}
        ${renderServerMetricToggle(index, metrics, 'cpu', 'CPU')}
        ${renderServerMetricToggle(index, metrics, 'memory', '内存')}
        ${renderServerMetricToggle(index, metrics, 'disk', '硬盘')}
      </div>
    </div>
  `;
}

function renderServerConfigs() {
  const list = document.getElementById('server-list');
  if (!list) return;
  if (!serverConfigs.length) {
    list.innerHTML = '<div class="server-empty">尚未配置远程服务器。可以添加服务器或从 SSH 配置导入。</div>';
    return;
  }
  list.innerHTML = serverConfigs.map((host, idx) => `
    <div class="server-card" data-index="${idx}">
      <div class="server-card-head">
        <label class="toggle-switch">
          <input type="checkbox" data-field="enabled" ${host.enabled !== false ? 'checked' : ''} onchange="updateServerField(${idx}, 'enabled', this.checked)">
          <span class="toggle-knob"></span>
          <span class="server-card-title">${escapeHtml(host.alias || '新服务器')}</span>
        </label>
        <div class="server-head-actions">
          <button class="settings-action server-test" onclick="testServerConfig(${idx})" data-tip="测试 SSH 连接并检测 GPU">测试</button>
          <button class="server-remove" onclick="removeServerConfig(${idx})">移除</button>
        </div>
      </div>
      <div class="server-test-status"></div>
      <div class="server-grid">
        <div class="server-field">
          <label>别名</label>
          <input class="server-input" value="${escapeHtml(host.alias)}" oninput="updateServerField(${idx}, 'alias', this.value)">
        </div>
        <div class="server-field">
          <label>主机名</label>
          <input class="server-input" value="${escapeHtml(host.hostname)}" oninput="updateServerField(${idx}, 'hostname', this.value)">
        </div>
        <div class="server-field">
          <label>用户名</label>
          <input class="server-input" value="${escapeHtml(host.user)}" oninput="updateServerField(${idx}, 'user', this.value)">
        </div>
        <div class="server-field">
          <label>端口</label>
          <input class="server-input" type="number" min="1" max="65535" value="${escapeHtml(host.port || 22)}" oninput="updateServerField(${idx}, 'port', this.value)">
        </div>
        <div class="server-field full">
          <label>磁盘路径</label>
          <input class="server-input" value="${escapeHtml(host.disk_path || '~')}" placeholder="~, /, /data" oninput="updateServerField(${idx}, 'disk_path', this.value)">
        </div>
        ${renderServerMetricToggles(idx, host)}
        <div class="server-field full">
          <label>密钥文件</label>
          <input class="server-input" value="${escapeHtml(host.identity_file)}" placeholder="~/.ssh/id_rsa" oninput="updateServerField(${idx}, 'identity_file', this.value)">
        </div>
        <div class="server-field full">
          <label class="pw-label">密码 ${host.has_password ? '（已保存，留空则保留）' : '（可选）'}</label>
          <input class="server-input pw-input" type="password" value="" placeholder="${host.has_password ? '保留已有密码' : '密码'}" oninput="updateServerField(${idx}, 'password', this.value)">
        </div>
        <div class="server-field">
          <label>ProxyJump</label>
          <input class="server-input" value="${escapeHtml(host.proxy_jump)}" oninput="updateServerField(${idx}, 'proxy_jump', this.value)">
        </div>
        <div class="server-field">
          <label>ProxyCommand</label>
          <input class="server-input" value="${escapeHtml(host.proxy_command)}" oninput="updateServerField(${idx}, 'proxy_command', this.value)">
        </div>
        <div class="server-field full tunnel-field">
          <label data-tip="在服务器上监听该端口，经 SSH 隧道转发到本机同端口（相当于 ssh -R）。本机需有对应服务，如 7890 代理">端口映射（服务器 → 本机）</label>
          <div class="server-metrics">
            <label class="toggle-switch">
              <input type="checkbox" ${host.tunnel_enabled ? 'checked' : ''} onchange="updateServerField(${idx}, 'tunnel_enabled', this.checked)">
              <span class="toggle-knob"></span>
              <span class="toggle-label">启用</span>
            </label>
            <input class="server-input tunnel-port-input" type="number" min="1" max="65535" value="${host.tunnel_port || 7890}" oninput="updateServerField(${idx}, 'tunnel_port', this.value)" data-tip="服务器上监听的端口，默认 7890">
          </div>
          <div class="tunnel-status" data-tunnel-index="${idx}"></div>
        </div>
      </div>
    </div>
  `).join('');
}

function updateServerField(index, field, value) {
  if (!serverConfigs[index]) return;
  serverConfigs[index][field] = field === 'enabled' ? !!value : value;
  scheduleServerConfigSaveNow();
}

async function testServerConfig(index) {
  const host = serverConfigs[index];
  if (!host) return;
  const card = document.querySelector('#server-list .server-card[data-index="' + index + '"]');
  const button = card ? card.querySelector('.server-test') : null;
  const statusEl = card ? card.querySelector('.server-test-status') : null;
  if (button) { button.disabled = true; button.textContent = '测试中...'; }
  if (statusEl) { statusEl.className = 'server-test-status'; statusEl.textContent = '正在连接 ' + (host.hostname || host.alias) + ' ...'; }
  try {
    const resp = await fetch('/api/config/test', {
      method: 'POST',
      headers: {'Content-Type': 'application/json'},
      body: JSON.stringify({host: serializeServerConfig(host)}),
    });
    const data = await resp.json().catch(() => ({}));
    if (!resp.ok) throw new Error(data.error || '测试请求失败');
    if (!statusEl) return;
    if (data.status === 'ok') {
      const count = (data.gpus || []).length;
      const unit = data.is_tpu ? ' 个 TPU 芯片' : ' 个 GPU';
      const first = data.gpus && data.gpus[0] ? data.gpus[0].name : '';
      statusEl.textContent = '连接成功 · ' + count + unit + (first ? ' · ' + first : '');
      statusEl.classList.add('ok');
    } else if (data.status === 'no_gpu') {
      statusEl.textContent = '连接成功，但未检测到加速器：' + (data.error || '未知原因');
      statusEl.classList.add('warn');
    } else {
      statusEl.textContent = '连接失败：' + (data.error || '未知错误');
      statusEl.classList.add('fail');
    }
  } catch (e) {
    if (statusEl) { statusEl.textContent = '测试失败：' + e.message; statusEl.classList.add('fail'); }
  } finally {
    if (button) { button.disabled = false; button.textContent = '测试'; }
  }
}

function updateServerMetric(index, metric, enabled) {
  if (!serverConfigs[index]) return;
  serverConfigs[index].metrics = normalizeMetricConfig(serverConfigs[index].metrics || metricSettings);
  serverConfigs[index].metrics[metric] = !!enabled;
  const status = document.getElementById('server-save-status');
  if (status) status.textContent = '正在保存服务器指标设置...';
  scheduleServerConfigSaveNow();
}

function addServerConfig() {
  const nextIndex = serverConfigs.length + 1;
  serverConfigs.push({
    alias: 'new-server-' + nextIndex,
    hostname: '',
    user: '',
    port: 22,
    identity_file: '',
    password: '',
    proxy_jump: '',
    proxy_command: '',
    enabled: true,
    disk_path: '~',
    metrics: normalizeMetricConfig(metricSettings),
  });
  renderServerConfigs();
  const status = document.getElementById('server-save-status');
  if (status) status.textContent = '已添加服务器，正在自动保存...';
  scheduleServerConfigSaveNow();
}

function removeServerConfig(index) {
  const host = serverConfigs[index];
  const label = host && host.alias ? host.alias : '此服务器';
  if (!confirm('确定要从监控服务器中移除 "' + label + '" 吗？')) return;
  serverConfigs.splice(index, 1);
  renderServerConfigs();
  const status = document.getElementById('server-save-status');
  if (status) status.textContent = '已移除服务器，正在自动保存...';
  scheduleServerConfigSaveNow();
}

function serializeServerConfig(host) {
  const out = {
    alias: host.alias || '',
    hostname: host.hostname || '',
    user: host.user || '',
    port: parseInt(host.port || 22),
    identity_file: host.identity_file || '',
    proxy_jump: host.proxy_jump || '',
    proxy_command: host.proxy_command || '',
    enabled: host.enabled !== false,
    disk_path: host.disk_path || '~',
    metrics: normalizeMetricConfig(host.metrics || metricSettings),
    tunnel_enabled: host.tunnel_enabled === true,
    tunnel_port: parseInt(host.tunnel_port || 7890),
  };
  out.password = host.password ? host.password : (host.has_password ? '__KEEP__' : '');
  return out;
}

function serializeServerConfigs() {
  return serverConfigs.map(serializeServerConfig);
}

function scheduleServerConfigSave(delay = 700) {
  clearTimeout(serverSaveTimer);
  const status = document.getElementById('server-save-status');
  if (status) status.textContent = delay ? '有未保存的修改，正在自动保存...' : '正在保存...';
  serverSaveTimer = setTimeout(() => {
    serverSaveTimer = null;
    saveServerConfigs();
  }, delay);
}

function scheduleServerConfigSaveNow() {
  // Preserve focus and in-progress edits: save silently, don't re-render the list.
  clearTimeout(serverSaveTimer);
  serverSaveTimer = null;
  const focusInfo = captureServerInputFocus();
  const status = document.getElementById('server-save-status');
  if (status) status.textContent = '正在保存...';
  fetch('/api/config/hosts', {
    method: 'POST',
    headers: {'Content-Type': 'application/json'},
    body: JSON.stringify({hosts: serializeServerConfigs(), monitor_local: monitorLocal, metrics: metricSettings, local_disk_path: localDiskPath}),
  })
    .then(resp => {
      if (!resp.ok) throw new Error('保存失败');
      return resp.json();
    })
    .then(data => {
      serverConfigs = data.hosts || [];
      monitorLocal = data.monitor_local !== false;
      metricSettings = normalizeMetricConfig(data.metrics);
      localDiskPath = data.local_disk_path || data.disk_path || '~';
      syncSettingsControls();
      if (status) status.textContent = '已保存。';
      restoreServerInputFocus(focusInfo);
    })
    .catch(e => {
      if (status) status.textContent = '保存失败：' + e.message;
    });
}

function captureServerInputFocus() {
  const el = document.activeElement;
  if (!el || !el.classList || !el.classList.contains('server-input')) return null;
  const card = el.closest('.server-card');
  if (!card) return null;
  const field = el.parentElement.querySelector('label');
  const fields = card.querySelectorAll('.server-field');
  let fieldIndex = -1;
  fields.forEach((f, i) => { if (f.contains(el)) fieldIndex = i; });
  const input = fields[fieldIndex] ? fields[fieldIndex].querySelector('.server-input') : null;
  const pos = el.selectionStart != null ? el.selectionStart : (input ? input.value.length : 0);
  return {index: parseInt(card.dataset.index), fieldIndex, selectionStart: pos, selectionEnd: el.selectionEnd != null ? el.selectionEnd : pos};
}

function restoreServerInputFocus(focusInfo) {
  if (!focusInfo) return;
  const card = document.querySelector('#server-list .server-card[data-index="' + focusInfo.index + '"]');
  if (!card) return;
  const fields = card.querySelectorAll('.server-field');
  const field = fields[focusInfo.fieldIndex];
  const input = field ? field.querySelector('.server-input') : null;
  if (!input) return;
  input.focus();
  try {
    input.setSelectionRange(focusInfo.selectionStart, focusInfo.selectionEnd);
  } catch (e) {}
}

function saveServerConfigs() {
  if (serverSaveTimer) {
    clearTimeout(serverSaveTimer);
    serverSaveTimer = null;
  }
  const status = document.getElementById('server-save-status');
  if (status) status.textContent = '正在保存...';
  return fetch('/api/config/hosts', {
    method: 'POST',
    headers: {'Content-Type': 'application/json'},
    body: JSON.stringify({hosts: serializeServerConfigs(), monitor_local: monitorLocal, metrics: metricSettings, local_disk_path: localDiskPath}),
  })
    .then(resp => {
      if (!resp.ok) throw new Error('保存失败');
      return resp.json();
    })
    .then(data => {
      serverConfigs = data.hosts || [];
      monitorLocal = data.monitor_local !== false;
      metricSettings = normalizeMetricConfig(data.metrics);
      localDiskPath = data.local_disk_path || data.disk_path || '~';
      renderServerConfigs();
      syncSettingsControls();
      if (status) status.textContent = '已保存，正在刷新监控服务器...';
      refresh();
      return true;
    })
    .catch(e => {
      if (status) status.textContent = '保存失败：' + e.message;
      return false;
    });
}

function selectConfigImportFile() {
  const input = document.getElementById('config-import-file');
  if (input) input.click();
}

async function exportServerConfig() {
  const status = document.getElementById('server-save-status');
  if (status) status.textContent = '正在准备导出配置...';
  try {
    if (serverSaveTimer) {
      const saved = await saveServerConfigs();
      if (!saved) throw new Error('导出前保存失败');
    }    const resp = await fetch('/api/config/export');
    if (!resp.ok) throw new Error('导出失败');
    const blob = await resp.blob();
    const url = URL.createObjectURL(blob);
    const date = new Date().toISOString().slice(0, 10);
    const link = document.createElement('a');
    link.href = url;
    link.download = `gnvitop-config-${date}.json`;
    document.body.appendChild(link);
    link.click();
    link.remove();
    URL.revokeObjectURL(url);
    if (status) status.textContent = '配置已导出。如果包含密码，请妥善保管。';
  } catch (e) {
    if (status) status.textContent = '导出失败：' + e.message;
  }
}

async function importConfigFile(file) {
  if (!file) return;
  if (!confirm('导入此配置文件并替换当前服务器和设置配置？')) return;
  if (serverSaveTimer) {
    clearTimeout(serverSaveTimer);
    serverSaveTimer = null;
  }
  const status = document.getElementById('server-save-status');
  if (status) status.textContent = '正在导入配置文件...';
  try {
    const payload = JSON.parse(await file.text());
    const resp = await fetch('/api/config/import', {
      method: 'POST',
      headers: {'Content-Type': 'application/json'},
      body: JSON.stringify(payload),
    });
    const data = await resp.json().catch(() => ({}));
    if (!resp.ok) throw new Error(data.error || '导入失败');
    serverConfigs = data.hosts || [];
    monitorLocal = data.monitor_local !== false;
    metricSettings = normalizeMetricConfig(data.metrics);
    localDiskPath = data.local_disk_path || data.disk_path || '~';
    renderServerConfigs();
    syncSettingsControls();
    if (status) status.textContent = '配置已导入，正在刷新监控服务器...';
    refresh();
  } catch (e) {
    if (status) status.textContent = '导入失败：' + e.message;
  }
}

async function importSshConfig(replace) {
  const message = replace
    ? '用 SSH 配置中的服务器替换当前服务器配置？'
    : '从 SSH 配置导入服务器？不会覆盖已有相同主机名/IP 和端口的服务器。';
  if (!confirm(message)) return;
  const status = document.getElementById('server-save-status');
  if (status) status.textContent = '正在导入 SSH 配置...';
  try {
    const resp = await fetch('/api/config/import-ssh', {
      method: 'POST',
      headers: {'Content-Type': 'application/json'},
      body: JSON.stringify({replace: !!replace}),
    });
    if (!resp.ok) throw new Error('导入失败');
    const data = await resp.json();
    serverConfigs = data.hosts || [];
    monitorLocal = data.monitor_local !== false;
    metricSettings = normalizeMetricConfig(data.metrics);
    localDiskPath = data.local_disk_path || data.disk_path || '~';
    renderServerConfigs();
    syncSettingsControls();
    if (status) status.textContent = '已从 SSH 配置导入，正在刷新监控服务器...';
    refresh();
  } catch (e) {
    if (status) status.textContent = '导入失败：' + e.message;
  }
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

let _dragSrc = null;
function _attachDrag(card) {
  const handle = card.querySelector('.drag-handle');
  if (handle) {
    handle.setAttribute('draggable', 'true');
    handle.addEventListener('dragstart', e => {
      _dragSrc = card;
      card.classList.add('dragging');
      e.dataTransfer.effectAllowed = 'move';
      e.dataTransfer.setDragImage(card, 0, 0);
      e.stopPropagation();
    });
    handle.addEventListener('dragend', () => {
      card.classList.remove('dragging');
      const grid = card.parentElement;
      if (grid) grid.querySelectorAll('.host-card').forEach(c => c.classList.remove('drag-over'));
      if (grid && grid.classList.contains('host-grid')) {
        hostOrder = [...grid.querySelectorAll('.host-card')].map(c => c.dataset.alias);
        localStorage.setItem('gnvitop-order', JSON.stringify(hostOrder));
      }
      _dragSrc = null;
    });
  }
  card.addEventListener('dragover', e => {
    e.preventDefault();
    e.dataTransfer.dropEffect = 'move';
    const grid = card.parentElement;
    if (_dragSrc && card !== _dragSrc && grid && _dragSrc.parentElement === grid) {
      grid.querySelectorAll('.host-card').forEach(c => c.classList.remove('drag-over'));
      card.classList.add('drag-over');
    }
  });
  card.addEventListener('drop', e => {
    e.preventDefault();
    const grid = card.parentElement;
    if (_dragSrc && _dragSrc !== card && grid && _dragSrc.parentElement === grid) {
      const cards = [...grid.querySelectorAll('.host-card')];
      const srcIdx = cards.indexOf(_dragSrc);
      const dstIdx = cards.indexOf(card);
      if (srcIdx < dstIdx) {
        grid.insertBefore(_dragSrc, card.nextSibling);
      } else {
        grid.insertBefore(_dragSrc, card);
      }
    }
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
  syncSettingsControls();
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
            const label = free.map(g => 'GPU ' + g.index + '（空闲 ' + Math.round(g.memory_free_mb/1024*10)/10 + 'GB）').join('<br>');
            tooltip.style.color = 'var(--success-text)';
            tooltip.innerHTML = free.length + ' 个空闲 GPU：<br>' + label + '<br><span style="color:var(--text-muted)">' + (watching ? '点击停止监控' : '点击监控') + '</span>';
          } else {
            tooltip.style.color = '';
            tooltip.innerHTML = watching ? '监控中 — GPU 空闲时通知<br><span style="color:var(--text-muted)">点击停止</span>' : '监控空闲 GPU';
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
        new Notification('GPU 空闲 — ' + host.alias, {
          body: 'GPU ' + gpu.index + '（' + gpu.name + '）空闲 ' + Math.round(gpu.memory_free_mb / 1024 * 10) / 10 + ' GB',
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
  const settingsBtn = document.getElementById('settings-global-watch-btn');
  if (settingsBtn) {
    settingsBtn.classList.remove('watch-pop');
    void settingsBtn.offsetWidth;
    settingsBtn.classList.add('watch-pop');
  }
  if (lastData) renderHosts(lastData.hosts);
  syncSettingsControls();
}

function _updateGlobalWatchBtn() {
  const btn = document.getElementById('global-watch-btn');
  if (!btn || !lastData) return;
  const aliases = lastData.hosts.map(h => h.alias);
  const allWatched = aliases.length > 0 && aliases.every(a => watchedHosts.has(a));
  btn.classList.toggle('watching', allWatched);
  btn.textContent = allWatched ? '\uD83D\uDD14' : '\uD83D\uDD15';
  btn.title = allWatched ? '取消监控所有主机' : '监控所有主机的空闲 GPU';
  syncSettingsGlobalWatchBtn();
}

function setInterval_(secs) {
  refreshIntervalSecs = parseInt(secs);
  localStorage.setItem('gnvitop-interval', secs);
  setupAutoRefresh();
}

function setMode(mode) {
  currentMode = mode;
  document.body.classList.toggle('compact', mode === 'compact');
  const normalBtn = document.getElementById('mode-normal');
  const compactBtn = document.getElementById('mode-compact');
  if (normalBtn) normalBtn.classList.toggle('active', mode === 'normal');
  if (compactBtn) compactBtn.classList.toggle('active', mode === 'compact');
  localStorage.setItem('gnvitop-mode', mode);
  if (lastData) { renderSummary(lastData.hosts); renderHosts(lastData.hosts); }
  syncSettingsControls();
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

function formatBytes(bytes) {
  if (bytes == null || isNaN(bytes)) return 'N/A';
  const gb = bytes / (1024 * 1024 * 1024);
  if (gb >= 1) return gb.toFixed(1) + ' GB';
  const mb = bytes / (1024 * 1024);
  return mb.toFixed(0) + ' MB';
}

function renderSystemMetric(name, pct, value, sub) {
  const safePct = Math.max(0, Math.min(100, Number(pct) || 0));
  return `
    <div class="system-metric">
      <div class="system-metric-name">${name}</div>
      <div class="system-metric-value">${value}</div>
      ${sub ? `<div class="system-metric-sub">${sub}</div>` : ''}
      <div class="bar-track" style="margin-top:8px"><div class="bar-fill ${usageClass(safePct)}" style="width:${safePct}%"></div></div>
    </div>
  `;
}

function renderSystem(system) {
  if (!system || (!system.cpu && !system.memory && !system.disk)) return '';
  const items = [];
  if (system.cpu) {
    const c = system.cpu;
    const sub = currentMode === 'compact'
      ? `${c.cores || 0} 核`
      : `${c.cores || 0} 核 · 负载 ${c.load1 ?? 'N/A'} / ${c.load5 ?? 'N/A'} / ${c.load15 ?? 'N/A'}`;
    items.push(renderSystemMetric('CPU', c.usage_pct, `${c.usage_pct ?? 0}%`, sub));
  }
  if (system.memory) {
    const m = system.memory;
    const sub = currentMode === 'compact'
      ? `空闲 ${formatBytes(m.available_bytes)}`
      : `${formatBytes(m.used_bytes)} / ${formatBytes(m.total_bytes)}`;
    items.push(renderSystemMetric('内存', m.usage_pct, `${m.usage_pct ?? 0}%`, sub));
  }
  if (system.disk) {
    const d = system.disk;
    const sub = currentMode === 'compact'
      ? `空闲 ${formatBytes(d.free_bytes)}`
      : `${formatBytes(d.used_bytes)} / ${formatBytes(d.total_bytes)} · ${d.mount || d.path || '~'}`;
    items.push(renderSystemMetric('硬盘', d.usage_pct, `${d.usage_pct ?? 0}%`, sub));
  }
  if (!items.length) return '';
  return `<div class="system-panel"><div class="system-title">系统</div><div class="system-grid">${items.join('')}</div></div>`;
}

function compactSystemText(system) {
  if (!system) return '';
  const parts = [];
  if (system.cpu) parts.push(`CPU ${system.cpu.usage_pct ?? 0}%`);
  if (system.memory) parts.push(`内存 ${system.memory.usage_pct ?? 0}%`);
  if (system.disk) parts.push(`硬盘 ${system.disk.usage_pct ?? 0}%`);
  return parts.join(' · ');
}

function historyButtonIcon() {
  return `<svg viewBox="0 0 24 24" aria-hidden="true" fill="none" stroke="currentColor" stroke-width="2" stroke-linecap="round" stroke-linejoin="round">
    <path d="M4 19h16"></path>
    <path d="M5 16l4-5 4 3 6-8"></path>
  </svg>`;
}

function closeHistory() {
  const overlay = document.getElementById('history-overlay');
  if (overlay) overlay.classList.remove('open');
}

function closeHistoryOnBackdrop(event) {
  if (_overlayMouseDown && event.target.id === 'history-overlay') closeHistory();
  _overlayMouseDown = false;
}

function setHistoryRange(range) {
  historyRange = ['1h', '6h', '24h', '7d'].includes(range) ? range : '1h';
  document.querySelectorAll('.history-range').forEach(btn => {
    btn.classList.toggle('active', btn.dataset.range === historyRange);
  });
  if (historyHost) loadHistory(historyHost);
}

function openHistory(alias) {
  historyHost = alias;
  const overlay = document.getElementById('history-overlay');
  const title = document.getElementById('history-title');
  const subtitle = document.getElementById('history-subtitle');
  const chart = document.getElementById('history-chart');
  const host = lastData && lastData.hosts ? lastData.hosts.find(h => h.alias === alias) : null;
  if (title) title.textContent = alias + ' 历史';
  if (subtitle) subtitle.textContent = host ? `${host.user}@${host.hostname || alias}` : '采样数据保留 7 天。';
  if (chart) chart.innerHTML = '<div class="history-empty">正在加载历史…</div>';
  if (overlay) overlay.classList.add('open');
  setHistoryRange(historyRange);
}

async function loadHistory(alias) {
  const chart = document.getElementById('history-chart');
  if (chart) chart.innerHTML = '<div class="history-empty">正在加载历史…</div>';
  try {
    const resp = await fetch(`/api/history?host=${encodeURIComponent(alias)}&range=${encodeURIComponent(historyRange)}`);
    const data = await resp.json();
    if (!resp.ok) throw new Error(data.error || '历史请求失败');
    renderHistory(data);
  } catch (e) {
    if (chart) chart.innerHTML = `<div class="history-empty">历史加载失败：${escapeHtml(e.message)}</div>`;
  }
}

function formatHistoryTime(ts) {
  const d = new Date(ts * 1000);
  if (historyRange === '7d' || historyRange === '24h') {
    return d.toLocaleString([], {month: 'short', day: 'numeric', hour: '2-digit'});
  }
  return d.toLocaleTimeString([], {hour: '2-digit', minute: '2-digit'});
}

function historySeries(points) {
  const defs = [
    {key: 'gpu_util_avg', label: 'GPU 利用率', color: '#60a5fa'},
    {key: 'gpu_memory_free_pct', label: 'GPU 空闲', color: '#22c55e'},
    {key: 'cpu_pct', label: 'CPU', color: '#f59e0b'},
    {key: 'memory_pct', label: '内存', color: '#a78bfa'},
    {key: 'disk_pct', label: '硬盘', color: '#f87171'},
  ];
  return defs.filter(def => points.some(p => Number.isFinite(Number(p[def.key]))));
}

function formatHistoryTooltipTime(ts) {
  return new Date(ts * 1000).toLocaleString([], {
    month: 'short',
    day: 'numeric',
    hour: '2-digit',
    minute: '2-digit',
    second: '2-digit',
  });
}

function updateHistoryHover(event, hoverData) {
  const svg = document.getElementById('history-svg');
  const tooltip = document.getElementById('history-tooltip');
  if (!svg || !tooltip || !hoverData || !hoverData.points.length) return;
  const matrix = svg.getScreenCTM();
  if (!matrix) return;
  const point = svg.createSVGPoint();
  point.x = event.clientX;
  point.y = event.clientY;
  const svgPoint = point.matrixTransform(matrix.inverse());
  const svgX = Math.max(hoverData.left, Math.min(hoverData.width - hoverData.right, svgPoint.x));
  let best = hoverData.points[0];
  let bestDist = Infinity;
  hoverData.points.forEach(point => {
    const dist = Math.abs(hoverData.xFor(point.timestamp) - svgX);
    if (dist < bestDist) {
      best = point;
      bestDist = dist;
    }
  });

  const x = hoverData.xFor(best.timestamp);
  const hoverGroup = document.getElementById('history-hover-group');
  const hoverLine = document.getElementById('history-hover-line');
  const hoverDots = document.getElementById('history-hover-dots');
  if (hoverGroup) hoverGroup.style.opacity = '1';
  if (hoverLine) {
    hoverLine.setAttribute('x1', x);
    hoverLine.setAttribute('x2', x);
  }
  if (hoverDots) {
    hoverDots.innerHTML = hoverData.series.map(def => {
      const value = Number(best[def.key]);
      if (!Number.isFinite(value)) return '';
      return `<circle cx="${x.toFixed(1)}" cy="${hoverData.yFor(value).toFixed(1)}" r="4.2" fill="${def.color}" stroke="var(--surface)" stroke-width="2"></circle>`;
    }).join('');
  }

  const rows = hoverData.series.map(def => {
    const value = Number(best[def.key]);
    if (!Number.isFinite(value)) return '';
    return `<div class="history-tooltip-row">
      <span class="history-tooltip-label"><span class="history-dot" style="background:${def.color}"></span>${def.label}</span>
      <strong>${value.toFixed(1)}%</strong>
    </div>`;
  }).join('');
  tooltip.innerHTML = `<div class="history-tooltip-title">${formatHistoryTooltipTime(best.timestamp)}</div>${rows}`;
  tooltip.style.display = 'block';

  const chart = document.getElementById('history-chart');
  const chartRect = chart.getBoundingClientRect();
  const tooltipWidth = tooltip.offsetWidth || 180;
  const tooltipHeight = tooltip.offsetHeight || 120;
  let left = event.clientX - chartRect.left + 14;
  let top = event.clientY - chartRect.top + 14;
  if (left + tooltipWidth > chartRect.width - 8) left = event.clientX - chartRect.left - tooltipWidth - 14;
  if (top + tooltipHeight > chartRect.height - 8) top = event.clientY - chartRect.top - tooltipHeight - 14;
  tooltip.style.left = Math.max(8, left) + 'px';
  tooltip.style.top = Math.max(8, top) + 'px';
}

function hideHistoryHover() {
  const hoverGroup = document.getElementById('history-hover-group');
  const tooltip = document.getElementById('history-tooltip');
  if (hoverGroup) hoverGroup.style.opacity = '0';
  if (tooltip) tooltip.style.display = 'none';
}

function renderHistory(data) {
  const chart = document.getElementById('history-chart');
  if (!chart) return;
  const points = data.points || [];
  if (!points.length) {
    chart.innerHTML = '<div class="history-empty">暂无历史数据，将在下次刷新采样后显示。</div>';
    return;
  }
  const series = historySeries(points);
  if (!series.length) {
    chart.innerHTML = '<div class="history-empty">该主机已有历史数据，但未记录已启用的数值指标。</div>';
    return;
  }

  const width = 760, height = 280;
  const left = 42, right = 18, top = 18, bottom = 34;
  const plotW = width - left - right;
  const plotH = height - top - bottom;
  const times = points.map(p => Number(p.timestamp)).filter(Number.isFinite);
  if (!times.length) {
    chart.innerHTML = '<div class="history-empty">历史数据缺少时间戳。</div>';
    return;
  }
  const minT = Math.min(...times);
  const maxT = Math.max(...times);
  const span = Math.max(maxT - minT, 1);
  const xFor = ts => left + ((Number(ts) - minT) / span) * plotW;
  const yFor = value => top + (100 - Math.max(0, Math.min(100, Number(value)))) / 100 * plotH;
  const validPoints = points.filter(p => Number.isFinite(Number(p.timestamp)));
  const grid = [0, 25, 50, 75, 100].map(v => {
    const y = yFor(v);
    return `<line x1="${left}" y1="${y}" x2="${width - right}" y2="${y}" stroke="var(--border)" stroke-width="1"></line>
      <text x="${left - 10}" y="${y + 4}" text-anchor="end" fill="var(--text-subtle)" font-size="11">${v}</text>`;
  }).join('');
  const xLabels = [minT, minT + span / 2, maxT].map((ts, i) => {
    const x = i === 0 ? left : i === 2 ? width - right : xFor(ts);
    const anchor = i === 0 ? 'start' : i === 2 ? 'end' : 'middle';
    return `<text x="${x}" y="${height - 10}" text-anchor="${anchor}" fill="var(--text-subtle)" font-size="11">${formatHistoryTime(ts)}</text>`;
  }).join('');
  const lines = series.map(def => {
    const coords = points
      .filter(p => Number.isFinite(Number(p.timestamp)) && Number.isFinite(Number(p[def.key])))
      .map(p => `${xFor(p.timestamp).toFixed(1)},${yFor(p[def.key]).toFixed(1)}`);
    if (coords.length === 1) {
      const [x, y] = coords[0].split(',');
      return `<circle cx="${x}" cy="${y}" r="3" fill="${def.color}"></circle>`;
    }
    return `<polyline points="${coords.join(' ')}" fill="none" stroke="${def.color}" stroke-width="2.3" stroke-linecap="round" stroke-linejoin="round"></polyline>`;
  }).join('');
  const latest = points[points.length - 1] || {};
  const legend = series.map(def => {
    const value = Number.isFinite(Number(latest[def.key])) ? `${Number(latest[def.key]).toFixed(1)}%` : 'N/A';
    return `<span class="history-legend-item"><span class="history-dot" style="background:${def.color}"></span>${def.label}: ${value}</span>`;
  }).join('');

  chart.innerHTML = `
    <svg id="history-svg" viewBox="0 0 ${width} ${height}" role="img" aria-label="历史趋势图">
      <rect x="${left}" y="${top}" width="${plotW}" height="${plotH}" fill="transparent"></rect>
      ${grid}
      ${xLabels}
      ${lines}
      <g class="history-hover" id="history-hover-group">
        <line id="history-hover-line" x1="${left}" y1="${top}" x2="${left}" y2="${height - bottom}" stroke="var(--text-subtle)" stroke-width="1.3" stroke-dasharray="4 4"></line>
        <g id="history-hover-dots"></g>
      </g>
      <rect x="${left}" y="${top}" width="${plotW}" height="${plotH}" fill="transparent" style="cursor:crosshair" id="history-hit-area"></rect>
    </svg>
    <div class="history-tooltip" id="history-tooltip"></div>
    <div class="history-legend">${legend}</div>
  `;
  const hitArea = document.getElementById('history-hit-area');
  const hoverData = {points: validPoints, series, width, left, right, xFor, yFor};
  if (hitArea) {
    hitArea.onmousemove = event => updateHistoryHover(event, hoverData);
    hitArea.onmouseleave = hideHistoryHover;
  }
}

function renderSummary(hosts) {
  const online = hosts.filter(h => h.status === 'ok');
  const totalGPUs = online.reduce((s, h) => s + h.gpus.length, 0);
  const totalFree = online.reduce((s, h) => s + h.gpus.reduce((gs, g) => gs + g.memory_free_mb, 0), 0);
  const idleGPUs = online.reduce((s, h) => s + h.gpus.filter(g => g.gpu_utilization_pct < 10).length, 0);

  document.getElementById('summary-bar').innerHTML = `
    <div class="summary-card">
      <div class="label">在线主机</div>
      <div class="value" style="color:var(--success-text)">${online.length}<span style="color:var(--text-subtle);font-size:16px"> / ${hosts.length}</span></div>
    </div>
    <div class="summary-card">
      <div class="label">GPU 总数</div>
      <div class="value" style="color:var(--local-text)">${totalGPUs}</div>
    </div>
    <div class="summary-card">
      <div class="label">空闲 GPU（&lt; 10%）</div>
      <div class="value" style="color:var(--success-text)">${idleGPUs}</div>
    </div>
    <div class="summary-card">
      <div class="label">总空闲显存</div>
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
  const chipLabel = isTpu ? '芯片' : 'GPU';
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
          <span>${isTpu ? '利用率' : 'GPU 利用率'}</span>
          <span>${isTpu ? 'N/A（需安装 torch_xla）' : gpuPct + '%'}</span>
        </div>
        ${isTpu ? '' : `<div class="bar-track"><div class="bar-fill ${usageClass(gpuPct)}" style="width:${gpuPct}%"></div></div>`}
      </div>
      <div class="bar-container">
        <div class="bar-label">
          <span>HBM 显存</span>
          <span>${memLabel}</span>
        </div>
        ${isTpu ? '' : `<div class="bar-track"><div class="bar-fill ${usageClass(memPct)}" style="width:${memPct}%"></div></div>`}
      </div>
      ${renderProcessUsers(gpu.processes, hostUser)}
      <div class="gpu-stats">
        <div class="stat">
          <div class="stat-value" style="color:var(--text-muted)">${isTpu ? 'N/A' : `<span style="color:${gpuPctColor}">${gpuPct}%</span>`}</div>
          <div class="stat-label">利用率</div>
        </div>
        <div class="stat">
          <div class="stat-value">${isTpu ? formatMB(gpu.memory_total_mb) : formatMB(gpu.memory_free_mb)}</div>
          <div class="stat-label">${isTpu ? 'HBM 总量' : '空闲显存'}</div>
        </div>
        <div class="stat">
          <div class="stat-value" style="color:var(--text-muted)">${isTpu ? 'N/A' : `${gpu.temperature_c}&deg;C`}</div>
          <div class="stat-label">温度</div>
        </div>
      </div>
    </div>
  `;
}

// Persistent card cache: reuse DOM nodes when a card's rendered HTML is
// unchanged so refreshes don't wipe hover state, tooltips or drag sessions.
const _cardCache = new Map(); // alias -> {el, html}
let _gridMain = null;
let _gridFolded = null;
let _foldedDivider = null;

function _cardElement(alias, html, fresh) {
  const cached = _cardCache.get(alias);
  if (cached && cached.html === html) return cached.el;
  // Content changed: detach the old element before swapping the cache entry,
  // otherwise the stale card stays mounted and duplicates accumulate.
  if (cached && cached.el && cached.el.parentElement) {
    cached.el.parentElement.removeChild(cached.el);
  }
  const tpl = document.createElement('template');
  tpl.innerHTML = html.trim();
  const el = tpl.content.firstElementChild;
  if (fresh) el.classList.add('first-render');
  _attachDrag(el);
  _cardCache.set(alias, {el, html});
  return el;
}

function _syncGrid(grid, items) {
  const wanted = new Set(items.map(i => i.alias));
  [...grid.children].forEach(child => {
    if (!wanted.has(child.dataset.alias)) child.remove();
  });
  items.forEach(item => {
    // appendChild moves existing nodes too, so iterating in desired
    // order also repairs ordering without re-creating any card.
    grid.appendChild(_cardElement(item.alias, item.html, item.fresh));
  });
}

function _resetContentSkeleton() {
  _gridMain = null;
  _gridFolded = null;
  _foldedDivider = null;
}

function renderHosts(hosts) {
  const container = document.getElementById('content');
  if (!hosts.length) {
    if (isFirstRender) return; // keep showing the initial loading spinner
    container.innerHTML = '<div class="loading">未找到可监控的主机。</div>';
    _resetContentSkeleton();
    _cardCache.clear();
    return;
  }

  let filtered = currentMode === 'compact'
    ? hosts.filter(h => h.status === 'ok' || (h.system && Object.keys(h.system).length))
    : hosts;

  if (!filtered.length) {
    container.innerHTML = '<div class="loading">没有可显示的主机。</div>';
    _resetContentSkeleton();
    return;
  }

  // Apply manual drag order if set, otherwise auto-sort
  if (hostOrder.length) {
    filtered = _applyHostOrder(filtered);
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
    const systemHtml = renderSystem(host.system);
    if (host.status === 'ok') {
      const gpuHtml = (host.gpus || []).map(g => renderGPU(g, host.user)).join('');
      body = systemHtml + gpuHtml;
    } else if (host.status === 'no_gpu') {
      body = systemHtml + `<div class="no-gpu-msg">${host.error || '未检测到 NVIDIA GPU'}</div>`;
    } else {
      body = systemHtml + `<div class="error-msg">${host.error || '未知错误'}</div>`;
    }
    const isLocal    = host.is_local;
    const isTpu      = !!host.is_tpu;
    const isCollapsed = collapsedHosts.has(host.alias);
    const badgeClass = isLocal ? 'badge-local' : isTpu ? 'badge-tpu' : host.status === 'ok' ? 'badge-ok' : host.status === 'no_gpu' ? 'badge-no_gpu' : 'badge-error';
    const badgeText  = isLocal ? '本机' : isTpu ? 'TPU' : host.status === 'ok' ? '在线' : host.status === 'no_gpu' ? '无 GPU' : '离线';
    const cardClass  = `host-card status-${host.status}${isLocal ? ' is-local' : ''}${isTpu ? ' is-tpu' : ''}${isCollapsed ? ' collapsed' : ''}`;
    const collapsedInfo = (isCollapsed && host.status === 'ok')
      ? isTpu
        ? `<div class="collapsed-info">${host.gpus.length} 个芯片 &nbsp;·&nbsp; ${formatMB(host.gpus[0].memory_total_mb * host.gpus.length)} HBM</div>`
        : `<div class="collapsed-info">${host.gpus.length} 个 GPU &nbsp;·&nbsp; 空闲：${formatMB(host.gpus.reduce((s, g) => s + g.memory_free_mb, 0))}</div>`
      : '';
    const fallbackCollapsedInfo = (isCollapsed && !collapsedInfo && compactSystemText(host.system))
      ? `<div class="collapsed-info">${compactSystemText(host.system)}</div>`
      : '';
    const alias = host.alias.replace(/'/g, "\\'");
    return `
      <div class="${cardClass}" data-alias="${alias}">
        <div class="host-header" onclick="toggleCollapse('${alias}')">
          <div class="host-header-left" draggable="false">
            <span class="drag-handle" title="拖拽排序" onclick="event.stopPropagation()">&#8942;&#8942;</span>
            <div>
              <div class="host-name">${host.alias}</div>
              <div class="host-info">${host.user}@${host.hostname}${host.port ? ':' + host.port : ''}</div>
              ${collapsedInfo || fallbackCollapsedInfo}
            </div>
          </div>
          <div class="host-header-right">
            <button class="history-btn" draggable="false" data-tip="查看 7 天历史趋势" onclick="event.stopPropagation(); openHistory('${alias}')">${historyButtonIcon()}</button>
            <button class="watch-btn${watchedHosts.has(host.alias) ? ' watching' : ''}" draggable="false" onclick="event.stopPropagation(); toggleWatch('${alias}')">${watchedHosts.has(host.alias) ? '&#128276;' : '&#128277;'}${(() => {
              if (host.status !== 'ok') return '<span class="watch-tooltip">监控此主机</span>';
              const free = host.gpus.filter(g => _gpuAvailable(g));
              const watching = watchedHosts.has(host.alias);
              if (free.length > 0) {
                const label = free.map(g => 'GPU ' + g.index + '（空闲 ' + Math.round(g.memory_free_mb/1024*10)/10 + 'GB）').join('<br>');
                return '<span class="watch-tooltip" style="color:var(--success-text)">' + free.length + ' 个空闲 GPU：<br>' + label + (watching ? '<br><span style="color:var(--text-muted)">点击停止监控</span>' : '<br><span style="color:var(--text-muted)">点击监控</span>') + '</span>';
              }
              return '<span class="watch-tooltip">' + (watching ? '监控中 — GPU 空闲时通知<br><span style="color:var(--text-muted)">点击停止</span>' : '监控空闲 GPU') + '</span>';
            })()}</button>
            <span class="status-badge ${badgeClass}">${badgeText}</span>
            <span class="collapse-arrow">&#9660;</span>
          </div>
        </div>
        <div class="host-body">${body}</div>
      </div>
    `;
  }

  // Ensure the persistent skeleton (main grid + optional folded section)
  if (!_gridMain || !container.contains(_gridMain)) {
    container.innerHTML = '';
    _gridMain = document.createElement('div');
    _gridMain.className = 'host-grid';
    container.appendChild(_gridMain);
    _foldedDivider = null;
    _gridFolded = null;
  }

  _syncGrid(_gridMain, expanded.map(h => ({alias: h.alias, html: renderCard(h), fresh: wasFirst})));

  if (collapsed.length) {
    if (!_foldedDivider) {
      _foldedDivider = document.createElement('div');
      _foldedDivider.className = 'folded-divider';
      _foldedDivider.innerHTML = '<span class="folded-label"></span>';
      container.appendChild(_foldedDivider);
    }
    _foldedDivider.firstElementChild.innerHTML = '&#9660; 已折叠 (' + collapsed.length + ')';
    if (!_gridFolded) {
      _gridFolded = document.createElement('div');
      _gridFolded.className = 'host-grid host-grid-folded';
      container.appendChild(_gridFolded);
    }
    _syncGrid(_gridFolded, collapsed.map(h => ({alias: h.alias, html: renderCard(h), fresh: wasFirst})));
  } else {
    if (_foldedDivider) { _foldedDivider.remove(); _foldedDivider = null; }
    if (_gridFolded) { _gridFolded.remove(); _gridFolded = null; }
  }

  // Drop cache entries for hosts that no longer exist
  const alive = new Set(hosts.map(h => h.alias));
  _cardCache.forEach((_, alias) => { if (!alive.has(alias)) _cardCache.delete(alias); });

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
          '<div class="loading" style="color:var(--error-text)">无法连接到服务器。</div>';
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
  btn.textContent = '刷新中…';
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
    btn.textContent = '刷新';
  }
}

function updateTime(ts) {
  const d = new Date(ts * 1000);
  document.getElementById('update-time').textContent = '更新于 ' + d.toLocaleTimeString();
}

async function init() {
  setTheme(currentTheme);
  loadServerConfigs();
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
