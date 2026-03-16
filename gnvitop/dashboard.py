"""Embedded dashboard HTML."""

DASHBOARD_HTML = r"""<!DOCTYPE html>
<html lang="zh-CN">
<head>
<meta charset="UTF-8">
<meta name="viewport" content="width=device-width, initial-scale=1.0">
<title>gnvitop — {{GNVITOP_HOST_INFO}}</title>
<link rel="icon" type="image/svg+xml" href="data:image/svg+xml,%3Csvg xmlns='http://www.w3.org/2000/svg' viewBox='0 0 64 64'%3E%3Cdefs%3E%3ClinearGradient id='g' x1='0' y1='0' x2='1' y2='1'%3E%3Cstop offset='0%25' stop-color='%2338bdf8'/%3E%3Cstop offset='100%25' stop-color='%23a78bfa'/%3E%3C/linearGradient%3E%3C/defs%3E%3Crect x='4' y='4' width='56' height='56' rx='16' fill='url(%23g)'/%3E%3Cpath d='M12 34 L22 34 L27 18 L33 46 L38 28 L43 34 L52 34' fill='none' stroke='white' stroke-width='4' stroke-linecap='round' stroke-linejoin='round'/%3E%3C/svg%3E">
<style>
  * { margin: 0; padding: 0; box-sizing: border-box; }

  body {
    font-family: -apple-system, BlinkMacSystemFont, 'Segoe UI', Roboto, sans-serif;
    background: #0f172a;
    color: #e2e8f0;
    min-height: 100vh;
    padding: 24px;
  }

  .header {
    display: flex;
    align-items: center;
    justify-content: center;
    margin-bottom: 28px;
    position: relative;
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
    position: absolute;
    right: 0;
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

  .btn-refresh {
    padding: 8px 20px;
    border: 1px solid #334155;
    background: #1e293b;
    color: #e2e8f0;
    border-radius: 8px;
    cursor: pointer;
    font-size: 14px;
    transition: all 0.2s;
  }
  .btn-refresh:hover { background: #334155; border-color: #475569; }
  .btn-refresh:disabled { opacity: 0.5; cursor: not-allowed; }
  @keyframes refreshPulse {
    0%   { box-shadow: 0 0 0 0 rgba(96,165,250,0.5); }
    50%  { box-shadow: 0 0 0 6px rgba(96,165,250,0); background: #1e3a5f; border-color: #60a5fa; }
    100% { box-shadow: 0 0 0 0 rgba(96,165,250,0); }
  }
  .btn-refresh.refreshing { animation: refreshPulse 0.8s ease; }

  /* Drag-and-drop */
  .host-card.dragging { opacity: 0.4; cursor: grabbing; }
  .host-card.drag-over { outline: 2px dashed #60a5fa; outline-offset: 2px; }
  .host-header { cursor: grab; }
  .host-header:active { cursor: grabbing; }

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
    transition: border-color 0.2s;
  }
  .host-card:hover { border-color: #475569; }

  .host-card.status-ok { border-left: 3px solid #22c55e; }
  .host-card.status-no_gpu { border-left: 3px solid #eab308; }
  .host-card.status-error { border-left: 3px solid #ef4444; }
  .host-card.is-local { border-left: 3px solid #60a5fa; }

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

  .auto-refresh-toggle {
    display: flex;
    align-items: center;
    gap: 6px;
    font-size: 13px;
    color: #94a3b8;
    cursor: pointer;
    user-select: none;
  }

  .auto-refresh-toggle input { cursor: pointer; }

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
    font-size: 12px;
  }
  .mode-toggle button {
    padding: 5px 12px;
    border: none;
    background: transparent;
    color: #64748b;
    cursor: pointer;
    transition: all 0.2s;
    font-size: 12px;
  }
  .mode-toggle button.active {
    background: #334155;
    color: #e2e8f0;
  }

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
    font-size: 12px;
    padding: 5px 8px;
    cursor: pointer;
    outline: none;
  }
  .interval-select:hover { border-color: #475569; }

  /* Compact mode */
  body.compact .summary-bar { display: none; }
  body.compact .host-grid { grid-template-columns: repeat(auto-fill, minmax(380px, 1fr)); gap: 12px; }
  body.compact .host-header { padding: 12px 16px; }
  body.compact .host-info { display: none; }
  body.compact .host-body { padding: 12px 16px; }

  /* Collapse */
  .host-header {
    cursor: pointer;
    user-select: none;
  }
  .host-header-left {
    display: flex;
    align-items: center;
    gap: 8px;
    min-width: 0;
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
  .host-card.collapsed .collapse-arrow { transform: rotate(-90deg); }
  .host-card.collapsed .host-body { display: none; }
  .host-card.collapsed .host-header { border-bottom: none; }
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
    <div class="mode-toggle" id="mode-toggle">
      <button onclick="setMode('compact')" id="mode-compact">Compact</button>
      <button onclick="setMode('normal')" id="mode-normal">Normal</button>
    </div>
    <label class="auto-refresh-toggle">
      <input type="checkbox" id="auto-refresh" checked>
      Auto
    </label>
    <select class="interval-select" id="interval-select" onchange="setInterval_(this.value)">
      <option value="5">5s</option>
      <option value="10">10s</option>
      <option value="30" selected>30s</option>
      <option value="300">5min</option>
    </select>
    <a class="github-link" href="https://github.com/Linwei94/gnvitop" target="_blank" title="Star on GitHub">
      <svg viewBox="0 0 16 16" xmlns="http://www.w3.org/2000/svg">
        <path d="M8 0C3.58 0 0 3.58 0 8c0 3.54 2.29 6.53 5.47 7.59.4.07.55-.17.55-.38 0-.19-.01-.82-.01-1.49-2.01.37-2.53-.49-2.69-.94-.09-.23-.48-.94-.82-1.13-.28-.15-.68-.52-.01-.53.63-.01 1.08.58 1.23.82.72 1.21 1.87.87 2.33.66.07-.52.28-.87.51-1.07-1.78-.2-3.64-.89-3.64-3.95 0-.87.31-1.59.82-2.15-.08-.2-.36-1.02.08-2.12 0 0 .67-.21 2.2.82.64-.18 1.32-.27 2-.27.68 0 1.36.09 2 .27 1.53-1.04 2.2-.82 2.2-.82.44 1.1.16 1.92.08 2.12.51.56.82 1.27.82 2.15 0 3.07-1.87 3.75-3.65 3.95.29.25.54.73.54 1.48 0 1.07-.01 1.93-.01 2.2 0 .21.15.46.55.38A8.013 8.013 0 0016 8c0-4.42-3.58-8-8-8z"/>
      </svg>
    </a>
    <button class="btn-refresh" id="btn-refresh" onclick="refresh()">Refresh</button>
  </div>
</div>

<div class="summary-bar" id="summary-bar"></div>
<div id="content">
  <div class="loading"><div class="spinner"></div><br>Connecting to hosts...</div>
</div>

<script>
let autoRefreshTimer = null;
let currentMode = 'normal';
let lastData = null;
let isFirstRender = true;
let refreshIntervalSecs = parseInt(localStorage.getItem('gnvitop-interval') || '30');
let hostOrder = JSON.parse(localStorage.getItem('gnvitop-order') || '[]'); // pinned manual order

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
    card.setAttribute('draggable', 'true');
    card.addEventListener('dragstart', e => {
      dragSrc = card;
      card.classList.add('dragging');
      e.dataTransfer.effectAllowed = 'move';
    });
    card.addEventListener('dragend', () => {
      card.classList.remove('dragging');
      grid.querySelectorAll('.host-card').forEach(c => c.classList.remove('drag-over'));
      // Save new order
      hostOrder = [...grid.querySelectorAll('.host-card')].map(c => c.dataset.alias);
      localStorage.setItem('gnvitop-order', JSON.stringify(hostOrder));
    });
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

function toggleCollapse(alias) {
  if (collapsedHosts.has(alias)) { collapsedHosts.delete(alias); } else { collapsedHosts.add(alias); }
  localStorage.setItem('gnvitop-collapsed', JSON.stringify([...collapsedHosts]));
  if (lastData) renderHosts(lastData.hosts);
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
      <div class="value" style="color:#4ade80">${online.length}<span style="color:#64748b;font-size:16px"> / ${hosts.length}</span></div>
    </div>
    <div class="summary-card">
      <div class="label">Total GPUs</div>
      <div class="value" style="color:#60a5fa">${totalGPUs}</div>
    </div>
    <div class="summary-card">
      <div class="label">Idle GPUs (< 10%)</div>
      <div class="value" style="color:#4ade80">${idleGPUs}</div>
    </div>
    <div class="summary-card">
      <div class="label">Total Free Memory</div>
      <div class="value" style="color:#a78bfa">${formatMB(totalFree)}</div>
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
  const memPct = gpu.memory_usage_pct;
  const gpuPct = gpu.gpu_utilization_pct;

  if (currentMode === 'compact') {
    return `
      <div class="gpu-item">
        <div class="gpu-title">
          <span class="gpu-name">GPU ${gpu.index}: ${gpu.name}</span>
        </div>
        <div class="bar-container">
          <div class="bar-label">
            <span>Memory</span>
            <span>${formatMB(gpu.memory_used_mb)} / ${formatMB(gpu.memory_total_mb)}</span>
          </div>
          <div class="bar-track">
            <div class="bar-fill ${usageClass(memPct)}" style="width:${memPct}%"></div>
          </div>
        </div>
        ${renderProcessUsers(gpu.processes, hostUser)}
      </div>
    `;
  }

  // Normal: full details
  return `
    <div class="gpu-item">
      <div class="gpu-title">
        <span class="gpu-name">GPU ${gpu.index}: ${gpu.name}</span>
        <span class="gpu-temp ${tempClass(gpu.temperature_c)}">${gpu.temperature_c}&deg;C</span>
      </div>
      <div class="bar-container">
        <div class="bar-label">
          <span>GPU Utilization</span>
          <span>${gpuPct}%</span>
        </div>
        <div class="bar-track">
          <div class="bar-fill ${usageClass(gpuPct)}" style="width:${gpuPct}%"></div>
        </div>
      </div>
      <div class="bar-container">
        <div class="bar-label">
          <span>Memory</span>
          <span>${formatMB(gpu.memory_used_mb)} / ${formatMB(gpu.memory_total_mb)}</span>
        </div>
        <div class="bar-track">
          <div class="bar-fill ${usageClass(memPct)}" style="width:${memPct}%"></div>
        </div>
      </div>
      ${renderProcessUsers(gpu.processes, hostUser)}
      <div class="gpu-stats">
        <div class="stat">
          <div class="stat-value" style="color:${gpuPct < 10 ? '#4ade80' : gpuPct < 50 ? '#facc15' : '#f87171'}">${gpuPct}%</div>
          <div class="stat-label">Utilization</div>
        </div>
        <div class="stat">
          <div class="stat-value">${formatMB(gpu.memory_free_mb)}</div>
          <div class="stat-label">Free Memory</div>
        </div>
        <div class="stat">
          <div class="stat-value">${gpu.temperature_c}&deg;C</div>
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
    const isCollapsed = collapsedHosts.has(host.alias);
    const badgeClass = isLocal ? 'badge-local' : host.status === 'ok' ? 'badge-ok' : host.status === 'no_gpu' ? 'badge-no_gpu' : 'badge-error';
    const badgeText  = isLocal ? 'Local' : host.status === 'ok' ? 'Online' : host.status === 'no_gpu' ? 'No GPU' : 'Offline';
    const cardClass  = `host-card status-${host.status}${isLocal ? ' is-local' : ''}${isCollapsed ? ' collapsed' : ''}${wasFirst ? ' first-render' : ''}`;
    const collapsedInfo = (isCollapsed && host.status === 'ok')
      ? `<div class="collapsed-info">${host.gpus.length} GPU${host.gpus.length !== 1 ? 's' : ''} &nbsp;·&nbsp; Free: ${formatMB(host.gpus.reduce((s, g) => s + g.memory_free_mb, 0))}</div>`
      : '';
    const alias = host.alias.replace(/'/g, "\\'");
    return `
      <div class="${cardClass}" data-alias="${alias}">
        <div class="host-header" onclick="toggleCollapse('${alias}')">
          <div class="host-header-left">
            <div>
              <div class="host-name">${host.alias}</div>
              <div class="host-info">${host.user}@${host.hostname}${host.port ? ':' + host.port : ''}</div>
              ${collapsedInfo}
            </div>
          </div>
          <div class="host-header-right">
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
