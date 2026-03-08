"""Embedded dashboard HTML."""

DASHBOARD_HTML = r"""<!DOCTYPE html>
<html lang="zh-CN">
<head>
<meta charset="UTF-8">
<meta name="viewport" content="width=device-width, initial-scale=1.0">
<title>gnvitop</title>
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
    justify-content: space-between;
    align-items: center;
    margin-bottom: 28px;
    flex-wrap: wrap;
    gap: 12px;
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
    grid-template-columns: repeat(auto-fill, minmax(420px, 1fr));
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
</style>
</head>
<body>

<div class="header">
  <h1>gnvitop -- global nvitop, monitoring GPU usage across all your remote servers</h1>
  <div class="header-right">
    <span class="status-text" id="update-time"></span>
    <label class="auto-refresh-toggle">
      <input type="checkbox" id="auto-refresh" checked>
      Auto (30s)
    </label>
    <button class="btn-refresh" id="btn-refresh" onclick="refresh()">Refresh</button>
  </div>
</div>

<div class="summary-bar" id="summary-bar"></div>
<div id="content">
  <div class="loading"><div class="spinner"></div><br>Connecting to hosts...</div>
</div>

<script>
let autoRefreshTimer = null;

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

function renderGPU(gpu) {
  const memPct = gpu.memory_usage_pct;
  const gpuPct = gpu.gpu_utilization_pct;
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
    container.innerHTML = '<div class="loading">No hosts found in SSH config.</div>';
    return;
  }

  container.innerHTML = '<div class="host-grid">' + hosts.map(host => {
    let body = '';
    if (host.status === 'ok') {
      body = host.gpus.map(renderGPU).join('');
    } else if (host.status === 'no_gpu') {
      body = `<div class="no-gpu-msg">${host.error || 'No NVIDIA GPU detected'}</div>`;
    } else {
      body = `<div class="error-msg">${host.error || 'Unknown error'}</div>`;
    }

    const badgeClass = host.status === 'ok' ? 'badge-ok' : host.status === 'no_gpu' ? 'badge-no_gpu' : 'badge-error';
    const badgeText = host.status === 'ok' ? 'Online' : host.status === 'no_gpu' ? 'No GPU' : 'Offline';

    return `
      <div class="host-card status-${host.status}">
        <div class="host-header">
          <div>
            <div class="host-name">${host.alias}</div>
            <div class="host-info">${host.user}@${host.hostname}:${host.port}</div>
          </div>
          <span class="status-badge ${badgeClass}">${badgeText}</span>
        </div>
        <div class="host-body">${body}</div>
      </div>
    `;
  }).join('') + '</div>';
}

async function fetchData(force) {
  const url = force ? '/api/refresh' : '/api/gpus';
  const resp = await fetch(url);
  return await resp.json();
}

async function refresh() {
  const btn = document.getElementById('btn-refresh');
  btn.disabled = true;
  btn.textContent = 'Refreshing...';
  try {
    const data = await fetchData(true);
    renderSummary(data.hosts);
    renderHosts(data.hosts);
    updateTime(data.updated_at);
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
  try {
    const data = await fetchData(false);
    renderSummary(data.hosts);
    renderHosts(data.hosts);
    updateTime(data.updated_at);
  } catch (e) {
    document.getElementById('content').innerHTML =
      '<div class="loading" style="color:#f87171">Failed to connect to server.</div>';
  }
}

function setupAutoRefresh() {
  const checkbox = document.getElementById('auto-refresh');
  function doRefresh() {
    fetchData(false).then(data => {
      renderSummary(data.hosts);
      renderHosts(data.hosts);
      updateTime(data.updated_at);
    }).catch(() => {});
  }
  checkbox.addEventListener('change', () => {
    if (checkbox.checked) {
      autoRefreshTimer = setInterval(doRefresh, 30000);
    } else {
      clearInterval(autoRefreshTimer);
    }
  });
  autoRefreshTimer = setInterval(doRefresh, 30000);
}

init();
setupAutoRefresh();
</script>
</body>
</html>"""
