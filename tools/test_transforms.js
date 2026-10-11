/* Data-transform + fetch-retry tests (P0 coverage audit): srt sorting,
   normLive API normalization, agg aggregation, fetchJSON retry behavior.
   Extracted from tools/templates/app.js by name; API tests use a mocked
   global fetch (no network). Usage: node tools/test_transforms.js (exit 0). */
'use strict';
const fs = require('fs');
const path = require('path');
const src = fs.readFileSync(path.join(__dirname, 'templates', 'app.js'), 'utf8');
// Brace-matched function extraction (quote/backtick/comment aware).
// Precondition: the target contains no regex literal with unbalanced braces
// (true for srt/normLive/agg/fetchJSON — verified by the behavior tests
// below, which fail loudly on a bad extraction).
function grabFn(sig) {
  const start = src.indexOf(sig);
  if (start < 0) { console.error('FAIL extract ' + sig); process.exit(1); }
  let i = src.indexOf('{', start);
  let depth = 0, q = null, esc = false, lineC = false, blockC = false;
  for (; i < src.length; i++) {
    const c = src[i], n = src[i + 1];
    if (lineC) { if (c === '\n') lineC = false; continue; }
    if (blockC) { if (c === '*' && n === '/') { blockC = false; i++; } continue; }
    if (q) {
      if (esc) esc = false;
      else if (c === '\\') esc = true;
      else if (c === q) q = null;
      else if (q === '`' && c === '$' && n === '{') { depth++; i++; }
      continue;
    }
    if (c === '/' && n === '/') { lineC = true; i++; continue; }
    if (c === '/' && n === '*') { blockC = true; i++; continue; }
    if (c === "'" || c === '"' || c === '`') { q = c; continue; }
    if (c === '{') depth++;
    else if (c === '}') {
      depth--;
      if (depth === 0) return src.slice(start, i + 1);
    }
  }
  console.error('FAIL unbalanced ' + sig); process.exit(1);
}
const grabLine = (name) => {
  const m = src.match(new RegExp('^function ' + name + '\\(.*$', 'm'));
  if (!m) { console.error('FAIL extract ' + name); process.exit(1); }
  return m[0];
};
const prelude = grabLine('eqId') + '\n' + grabLine('itemRef') + '\n' + grabLine('durSec') + '\n' +
  grabLine('srt') + '\n' +
  grabFn('function normLive(d)') + '\n' +
  grabFn('function agg()') + '\n' +
  grabFn('async function fetchJSON(url,ms)');
const NS = new Function('S', 'DATA', prelude + '; return {srt, normLive, agg, fetchJSON};');

let fails = 0, count = 0;
function ok(cond, msg) {
  count++;
  console.log((cond ? 'PASS ' : 'FAIL ') + msg);
  if (!cond) fails++;
}
function eq(a, b, msg) { ok(JSON.stringify(a) === JSON.stringify(b), msg + ' (got ' + JSON.stringify(a) + ')'); }

const S1 = { tsort: { d: 1 } };
const NS1 = NS(S1, { players: [], season: [] });

// --- srt: numeric asc/desc + string mode ---
{
  const { srt } = NS1;
  eq(srt([{ v: 2 }, { v: 10 }], x => x.v).map(x => x.v), [2, 10], 'T1 numeric ascending (d=1)');
  const NSd = NS({ tsort: { d: -1 } }, { players: [], season: [] });
  eq(NSd.srt([{ v: 2 }, { v: 10 }], x => x.v).map(x => x.v), [10, 2], 'T1 numeric descending (d=-1)');
  eq(NS1.srt([{ t: 'b' }, { t: 'a' }], x => x.t, true).map(x => x.t), ['a', 'b'], 'T1 string sort');
}

// --- normLive: shape + numeric coercion ---
{
  const { normLive } = NS1;
  const d = {
    match_id: 1099, games: [{
      game: 1, team_a: 'A', team_b: 'B', team_a_kills: '16', team_b_kills: 8,
      winner: 'team_a', duration: '16:05', team_a_side: 'blue', team_b_side: 'red',
      bans_a: ['H1'], bans_b: [],
      players: [{
        team: 'A', player: 'P', lane: 'MID', hero: 'H', kill: '5', death: null,
        assist: '7', kda: '10.0', gold: '9000', hero_damage: 'x', damage_taken: 100,
        tower_damage: 50, emblem: 'xemblem/3.png', talents: [], items: []
      }]
    }]
  };
  const n = normLive(d);
  eq(n.games.length, 1, 'T2 one game normalized');
  const g = n.games[0];
  eq([g.match_detail_id, g.team_a_kills, g.team_b_kills, g.duration_sec],
    ['1099', 16, 8, 965], 'T2 kills coerced, duration parsed');
  const p = n.pros[0];
  eq([p.kills, p.deaths, p.assists, p.gold, p.hero_damage], [5, 0, 7, 9000, 0],
    'T2 string/null/garbage numerics coerced');
  eq(n.bans, [{ match_detail_id: '1099', game_no: 1, side: 'A', hero: 'H1' }], 'T2 bans split by side');
  const empty = normLive({});
  eq([empty.games.length, empty.pros.length, empty.bans.length], [0, 0, 0], 'T2 empty payload ok');
}

// --- agg: string kills sum numerically; season override wins ---
{
  const DATA = {
    players: [
      { player: 'X', team: 'A', kills: '2', deaths: 1, assists: 1, gold_per_min: 500, hero: 'H' },
      { player: 'X', team: 'A', kills: '3', deaths: 2, assists: 0, gold_per_min: 600, hero: 'H2' }
    ],
    season: []
  };
  const { agg } = NS(S1, DATA);
  const o = agg().find(x => x.player === 'X');
  eq([o.k, o.d, o.a, o.gp], [5, 3, 1, 2], 'T3 string kills sum to 5, not "023"');
  const DATA2 = {
    players: [{ player: 'Y', team: 'B', kills: 99, deaths: 0, assists: 0, gold_per_min: 0, hero: 'H' }],
    season: [{ player: 'Y', total_games: 7, total_kills: 70, total_deaths: 7, total_assists: 70, avg_kda: 20 }]
  };
  const o2 = NS(S1, DATA2).agg().find(x => x.player === 'Y');
  eq([o2.gp, o2.k, o2.avgkda], [7, 70, 20], 'T3 season row overrides computed row');
  eq(NS(S1, { players: [], season: [] }).agg(), [], 'T3 empty players ok');
}

// --- fetchJSON: retry then success; persistent failure throws after 2 tries ---
(async () => {
  const { fetchJSON } = NS1;
  const realFetch = global.fetch;
  try {
    let calls = 0;
    global.fetch = async () => {
      calls++;
      if (calls === 1) throw new Error('down');
      return { ok: true, json: async () => ({ fine: true }) };
    };
    const r = await fetchJSON('http://x/', 50);
    eq(r, { fine: true }, 'T4 retry-then-success returns data');
    eq(calls, 2, 'T4 retried exactly once');
    let bad = 0;
    global.fetch = async () => { bad++; return { ok: false, status: 500, json: async () => ({}) }; };
    let threw = false;
    try { await fetchJSON('http://x/', 40); } catch (e) { threw = /http 500/.test(e.message); }
    ok(threw, 'T4 persistent HTTP failure throws after retries');
    eq(bad, 2, 'T4 exactly 2 attempts');
  } finally {
    global.fetch = realFetch;
  }
  console.log('\n' + (count - fails) + '/' + count + ' passed, ' + fails + ' failed');
  process.exit(fails ? 1 : 0);
})().catch(e => { console.error('FAIL harness: ' + (e && e.message)); process.exit(1); });
