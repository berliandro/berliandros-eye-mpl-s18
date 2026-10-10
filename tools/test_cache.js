/* Cache versioning tests (Area 5): helpers from the CACHE markers in
   tools/templates/app.js. Pure logic only (no localStorage/DOM); reload and
   migration scenarios are simulated by composing the helpers exactly as the
   startup wiring does. Usage: node tools/test_cache.js (exit 0 = pass). */
'use strict';
const fs = require('fs');
const path = require('path');
const src = fs.readFileSync(path.join(__dirname, 'templates', 'app.js'), 'utf8');
const m = src.match(/\/\* CACHE-START \*\/([\s\S]*?)\/\* CACHE-END \*\//);
if (!m) { console.error('FAIL CACHE markers missing'); process.exit(1); }
const NS = new Function(m[1] + '; return {cacheKeyFor, fingerprintSnapshot, countDecidedSet, makeCacheEntry, validateCacheEntry, selectSnapshot};')();
const { cacheKeyFor, fingerprintSnapshot, countDecidedSet, makeCacheEntry, validateCacheEntry, selectSnapshot } = NS;

let fails = 0, count = 0;
function ok(cond, msg) {
  count++;
  console.log((cond ? 'PASS ' : 'FAIL ') + msg);
  if (!cond) fails++;
}
// minimal schedule rows; decided = completed or terminal score, minus playoffs
const C = (id, a, b, sa, sb, st) => ({ schedule_id: id, team_a: a, team_b: b, score_a: sa, score_b: sb, status: st });
const PO = (id) => ({ schedule_id: id, team_a: 'TBD', team_b: 'TBD', status: 'upcoming' });
const poRow = (r) => String(r.schedule_id || '').indexOf('playoffs') > -1 || (r.team_a === 'TBD' && r.team_b === 'TBD');
const isTerm = (sa, sb) => (sa === 2 && (sb === 0 || sb === 1)) || (sb === 2 && (sa === 0 || sa === 1));
const ST = (slug, pts) => ({ team_slug: slug, match_point: pts, match_win: pts, match_lose: 0, game_win: 0, game_lose: 0, net_game_win: 0 });
const snap = (standings, schedule) => ({ standings, schedule, season: [], players: [], games: [], bans: [], matches: [], heroes: [], playoffs: {} });
const OPTS = { seasonId: 's18', schema: 1 };

{
  ok(cacheKeyFor('s18', 1) === 'mpl-board:s18:v1', 'C1 namespaced key format');
  ok(cacheKeyFor('s19', 2) !== cacheKeyFor('s18', 1), 'C1 seasons do not share keys');
}

// --- fingerprint: deterministic, sensitive, ignores volatile fields ---
{
  const s = snap([ST('a', 1)], [C('x', 'A', 'B', 2, 0, 'completed'), PO('id-playoffs-0')]);
  ok(fingerprintSnapshot(s) === fingerprintSnapshot(JSON.parse(JSON.stringify(s))), 'C2 fingerprint deterministic');
  const s2 = snap([ST('a', 2)], [C('x', 'A', 'B', 2, 0, 'completed'), PO('id-playoffs-0')]);
  ok(fingerprintSnapshot(s) !== fingerprintSnapshot(s2), 'C2 fingerprint sensitive to standings');
  const s3 = snap([ST('a', 1)], [C('x', 'A', 'B', 2, 1, 'completed'), PO('id-playoffs-0')]);
  ok(fingerprintSnapshot(s) !== fingerprintSnapshot(s3), 'C2 fingerprint sensitive to scores');
}

// --- countDecidedSet follows fixture rules ---
{
  const sched = [C('c1', 'A', 'B', 2, 0, 'completed'), C('l1', 'C', 'D', 1, 2, 'live'),
    C('u1', 'E', 'F', '', '', 'upcoming'), PO('id-playoffs-0')];
  ok(countDecidedSet(sched, poRow, isTerm) === 2, 'C3 completed + live-decisive counted, upcoming/playoffs not');
}

// --- validateCacheEntry ---
{
  const s = snap([ST('a', 1)], [C('x', 'A', 'B', 2, 0, 'completed')]);
  const good = makeCacheEntry(s, { seasonId: 's18', schema: 1, decided: 1, complete: true, refreshedAt: 123 });
  ok(validateCacheEntry(good, OPTS).ok, 'C4 valid entry accepted');
  ok(good.v === 1 && good.source === 'refresh', 'C4 entry carries version + source');
  ok(!validateCacheEntry({ ...good, seasonId: 's19' }, OPTS).ok, 'C5 other season rejected');
  ok(!validateCacheEntry({ ...good, schema: 0 }, OPTS).ok, 'C6 older schema rejected');
  ok(!validateCacheEntry({ ...good, schema: 2 }, OPTS).ok, 'C6 unknown schema rejected');
  ok(!validateCacheEntry({ ...good, data: { standings: [] } }, OPTS).ok, 'C7 malformed data rejected');
  ok(!validateCacheEntry({ ...good, fp: 'deadbeef' }, OPTS).ok, 'C7 fingerprint mismatch rejected');
  ok(!validateCacheEntry(null, OPTS).ok && !validateCacheEntry('x', OPTS).ok, 'C7 non-entries rejected');
}

// --- selectSnapshot ---
{
  const emb = { fp: 'aaaa', decided: 61, complete: true };
  ok(selectSnapshot(emb, null).use === 'embedded', 'C8 no cache -> embedded');
  ok(selectSnapshot(emb, { fp: 'aaaa', decided: 61, complete: true }).use === 'embedded', 'C8 identical -> embedded');
  const older = selectSnapshot(emb, { fp: 'bbbb', decided: 51, complete: true });
  ok(older.use === 'embedded', 'C8 older cache -> embedded');
  const newer = selectSnapshot(emb, { fp: 'cccc', decided: 66, complete: true, refreshedAt: 9 });
  ok(newer.use === 'cache' && newer.partial === false, 'C8 newer cache -> cache');
  // newer PARTIAL still wins (its gaps stay explicit), but is labelled
  const newerPartial = selectSnapshot(emb, { fp: 'dddd', decided: 66, complete: false, refreshedAt: 9 });
  ok(newerPartial.use === 'cache' && newerPartial.partial === true, 'C8 newer partial -> cache, labelled partial');
  // equal progress, different content: timestamped side wins
  const tieCache = selectSnapshot({ fp: 'aaaa', decided: 61 }, { fp: 'eeee', decided: 61, complete: true, refreshedAt: 9 });
  ok(tieCache.use === 'cache', 'C8 tied progress resolves to timestamped cache');
  const tieNone = selectSnapshot({ fp: 'aaaa', decided: 61 }, { fp: 'eeee', decided: 61, complete: true });
  ok(tieNone.use === 'embedded', 'C8 tied progress without timestamps -> embedded');
}

// --- reload scenarios: serialize -> parse -> validate -> select ---
{
  const s = snap([ST('a', 5)], [C('x', 'A', 'B', 2, 0, 'completed')]);
  // complete refresh then reload: cache adopted
  const e = makeCacheEntry(s, { seasonId: 's18', schema: 1, decided: 1, complete: true, refreshedAt: 100 });
  const reloaded = JSON.parse(JSON.stringify(e));
  ok(validateCacheEntry(reloaded, OPTS).ok, 'C9 complete refresh reload validates');
  ok(selectSnapshot({ fp: 'old', decided: 0 }, reloaded).use === 'cache', 'C9 newer complete cache adopted on reload');
  // partial refresh then reload: adopted but labelled
  const pe = makeCacheEntry(s, { seasonId: 's18', schema: 1, decided: 1, complete: false, failedIds: ['7'], refreshedAt: 101 });
  const pick = selectSnapshot({ fp: 'old', decided: 0 }, JSON.parse(JSON.stringify(pe)));
  ok(pick.use === 'cache' && pick.partial === true, 'C9 partial reload adopted + labelled');
  ok(JSON.parse(JSON.stringify(pe)).failedIds.length === 1, 'C9 failed IDs recorded');
  // corrupt cache on reload: embedded survives
  const bad = JSON.parse(JSON.stringify(e));
  bad.data.standings = [];
  ok(!validateCacheEntry(bad, OPTS).ok, 'C9 corrupt reload rejected');
  ok(selectSnapshot({ fp: 'e', decided: 1 }, null).use === 'embedded', 'C9 fallback is embedded');
}

console.log('\n' + (count - fails) + '/' + count + ' passed, ' + fails + ' failed');
process.exit(fails ? 1 : 0);
