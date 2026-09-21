// Run with: node --test tests/test_history_dashboard.js (no npm dependencies).
const assert = require('node:assert/strict');
const fs = require('node:fs');
const path = require('node:path');
const vm = require('node:vm');
const {test} = require('node:test');

const source = fs.readFileSync(path.join(__dirname, '../gnvitop/dashboard.py'), 'utf8');
const scripts = [...source.matchAll(/<script>([\s\S]*?)<\/script>/g)].map(match => match[1]);
scripts.forEach(script => new vm.Script(script)); // Check syntax of all dashboard scripts.
const script = scripts.find(script => script.includes('function closeHistory()'));
const historyScript = script.slice(script.indexOf('function closeHistory()'), script.indexOf('function renderSummary('));

function dashboard(fetch = () => {}) {
  const elements = new Map();
  const getElementById = id => {
    if (!elements.has(id)) elements.set(id, {innerHTML: '', style: {}, classList: {remove() {}}});
    return elements.get(id);
  };
  const context = vm.createContext({
    document: {getElementById}, fetch, AbortController,
    historyRange: '1h', historyHost: 'host-a', historyRequest: null, escapeHtml: value => value,
  });
  vm.runInContext(historyScript, context);
  return {context, getElementById};
}

test('missing data is absent, while real zeros remain valid', () => {
  const {context} = dashboard();
  assert.equal(context.historySeries([{cpu_pct: null, gpu_temperatures_c: {0: null, 1: -1}}]).length, 0);
  assert.equal(context.historySeries([{cpu_pct: 0}])[0].key, 'cpu_pct');
  assert.equal(context.historySeries([{gpu_util_avg: 50}]).length, 1);
  assert.equal(context.historyValue({gpu_temperatures_c: {0: 0}}, 'gpu_temp:0'), 0);
});

test('temperature uses Celsius and its own scale, with gaps for missing samples', () => {
  const {context, getElementById} = dashboard();
  context.renderHistory({points: [
    {timestamp: 1, cpu_pct: 25, gpu_temperatures_c: {0: 90, 2: 120}},
    {timestamp: 2, cpu_pct: null, gpu_temperatures_c: {0: null}},
    {timestamp: 3, cpu_pct: 50, gpu_temperatures_c: {2: 120, 0: 90}},
  ]});
  const html = getElementById('history-chart').innerHTML;
  assert.match(html, /GPU 0 温度: 90\.0°C/);
  assert.match(html, /GPU 2 温度: 120\.0°C/);
  assert.doesNotMatch(html, /平均温度|最高温度/);
  assert.match(html, /CPU: 50\.0%/);
  assert.match(html, />120<\/text>/);
  assert.match(html, /cy="79\.5"/); // 90°C is 75% of the 120°C right axis.
  assert.doesNotMatch(html, /<polyline/); // Missing readings split the line.
  context.renderHistory({points: [{timestamp: 1, cpu_pct: null}]});
  assert.match(getElementById('history-chart').innerHTML, /未记录/);
});

test('each GPU has a stable color and numeric order even when cards appear or disappear', () => {
  const {context, getElementById} = dashboard();
  const points = [
    {timestamp: 1, gpu_temperatures_c: {10: 80, 2: 60}},
    {timestamp: 2, gpu_temperatures_c: {0: 50, 10: 81}},
  ];
  const defs = context.historySeries(points);
  assert.deepEqual(Array.from(defs, def => def.label), ['GPU 0 温度', 'GPU 2 温度', 'GPU 10 温度']);
  assert.equal(new Set(defs.map(def => def.color)).size, 3);
  const onlyGpu10 = context.historySeries([{gpu_temperatures_c: {10: 82}}]);
  assert.equal(onlyGpu10[0].color, defs[2].color);
  context.renderHistory({points});
  assert.match(getElementById('history-chart').innerHTML, /GPU 2 温度: N\/A/);
  assert.equal(context.historySeries([{gpu_temperatures_c: {'<script>': 90}}]).length, 0);
});

test('legacy aggregate data never becomes a per-GPU reading', () => {
  const {context, getElementById} = dashboard();
  const old = {timestamp: 1, gpu_temp_avg_c: 60, gpu_temp_max_c: 70};
  context.renderHistory({points: [old]});
  assert.match(getElementById('history-chart').innerHTML, /平均温度（旧记录）/);
  context.renderHistory({points: [old, {timestamp: 2, gpu_temperatures_c: {0: 55, 1: 65}}]});
  const html = getElementById('history-chart').innerHTML;
  assert.match(html, /GPU 0 温度: 55\.0°C/);
  assert.doesNotMatch(html, /平均温度|最高温度|<polyline/);
});

test('a late response cannot replace a newer range or reopen a closed chart', async () => {
  const pending = [];
  const {context, getElementById} = dashboard((url, options) => new Promise(resolve => pending.push({url, options, resolve})));
  const first = context.loadHistory('host-a');
  context.historyRange = '7d';
  const second = context.loadHistory('host-b');
  assert.equal(pending[0].options.signal.aborted, true);
  assert.match(pending[1].url, /host=host-b&range=7d/);
  pending[1].resolve({ok: true, json: async () => ({points: [{timestamp: 2, gpu_temperatures_c: {0: 72}}]})});
  await second;
  const html = getElementById('history-chart').innerHTML;
  pending[0].resolve({ok: true, json: async () => ({points: []})});
  await first;
  assert.equal(getElementById('history-chart').innerHTML, html);
  const third = context.loadHistory('host-c');
  context.closeHistory();
  assert.equal(pending[2].options.signal.aborted, true);
  pending[2].resolve({ok: true, json: async () => ({points: [{timestamp: 3, cpu_pct: 42}]})});
  await third;
  assert.doesNotMatch(getElementById('history-chart').innerHTML, /CPU: 42/);
});
