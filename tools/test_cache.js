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
const sm = src.match(/\/\* SNAPSHOT-START \*\/([\s\S]*?)\/\* SNAPSHOT-END \*\//);
if (!sm) { console.error('FAIL SNAPSHOT markers missing'); process.exit(1); }
const NS = new Function(sm[1] + '\n' + m[1] + '; return {cacheKeyFor, fingerprintSnapshot, countDecidedSet, makeCacheEntry, validateCacheEntry, selectSnapshot, derivePicks, snapshotCompleteness};')();
const { cacheKeyFor, fingerprintSnapshot, countDecidedSet, makeCacheEntry, validateCacheEntry, selectSnapshot, derivePicks, snapshotCompleteness } = NS;

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
const snap = (standings, schedule) => ({ standings, schedule, season: [], players: [], games: [], bans: [], picks: [], team_games: [], team_season: [], matches: [], heroes: [], playoffs: {} });
const OPTS = { seasonId: 's18', schema: 4 };

{
  ok(cacheKeyFor('s18', 4) === 'mpl-board:s18:v4', 'C1 namespaced key format');
  ok(cacheKeyFor('s19', 4) !== cacheKeyFor('s18', 4), 'C1 seasons do not share keys');
}

// --- fingerprint: deterministic, sensitive, ignores volatile fields ---
{
  const s = snap([ST('a', 1)], [C('x', 'A', 'B', 2, 0, 'completed'), PO('id-playoffs-0')]);
  ok(fingerprintSnapshot(s) === fingerprintSnapshot(JSON.parse(JSON.stringify(s))), 'C2 fingerprint deterministic');
  const s2 = snap([ST('a', 2)], [C('x', 'A', 'B', 2, 0, 'completed'), PO('id-playoffs-0')]);
  ok(fingerprintSnapshot(s) !== fingerprintSnapshot(s2), 'C2 fingerprint sensitive to standings');
  const s3 = snap([ST('a', 1)], [C('x', 'A', 'B', 2, 1, 'completed'), PO('id-playoffs-0')]);
  ok(fingerprintSnapshot(s) !== fingerprintSnapshot(s3), 'C2 fingerprint sensitive to scores');
  const s4 = snap([ST('a', 1)], [C('x', 'A', 'B', 2, 0, 'completed')]);
  s4.players = [{ match_detail_id: 'x', game_no: 1, team: 'A', player: 'P', hero: 'H', kills: 1 }];
  ok(fingerprintSnapshot(s) !== fingerprintSnapshot(s4), 'C2 fingerprint covers raw analytics inputs');
  const s5 = snap([ST('a', 1)], [C('x', 'A', 'B', 2, 0, 'completed')]);
  s5.team_games = [{ match_detail_id: 'x', game_no: 1, team: 'A', win: 1 }];
  ok(fingerprintSnapshot(s) !== fingerprintSnapshot(s5), 'C2 fingerprint covers derived aggregates');
}

// --- explicit completeness: successful requests are not enough ---
{
  const schedule = [
    { schedule_id: 'r1', team_a: 'A', team_b: 'B', score_a: 2, score_b: 0, status: 'completed', match_detail_id: '1' },
    { schedule_id: 'r2', team_a: 'B', team_b: 'A', score_a: 1, score_b: 2, status: 'completed', match_detail_id: '2' },
    PO('id-playoffs-0'),
  ];
  const matches = [{ match_detail_id: '1' }, { match_detail_id: '2' }];
  const standings = [{ match_win: 2, game_win: 5 }];
  const full = snapshotCompleteness({ schedule, matches, standings }, 2);
  ok(full.complete && full.status === 'final', 'C10 complete 2-match snapshot is final');
  const missing = snapshotCompleteness({ schedule, matches: [{ match_detail_id: '1' }], standings }, 2);
  ok(!missing.complete && missing.missingIds[0] === 'r2', 'C10 missing completed detail makes snapshot partial');
  const short = snapshotCompleteness({ schedule: schedule.slice(0, 1), matches: [{ match_detail_id: '1' }], standings: [{ match_win: 2, game_win: 5 }] }, 2);
  ok(!short.complete && short.completed === 1, 'C10 fewer completed fixtures than expected is partial');
  const mismatch = snapshotCompleteness({ schedule, matches, standings: [{ match_win: 2, game_win: 4 }] }, 2);
  ok(!mismatch.complete && mismatch.officials.games === 4, 'C10 standings/game total mismatch is partial');
  const dSched = [{ schedule_id: 'r1', team_a: 'A', team_b: 'B', score_a: 2, score_b: 0, status: 'completed', match_detail_id: '1' }];
  const dGames = [
    { match_detail_id: '1', game_no: 1, team_a: 'A', team_b: 'B', team_a_side: 'blue', team_b_side: 'red' },
    { match_detail_id: '1', game_no: 2, team_a: 'A', team_b: 'B', team_a_side: 'red', team_b_side: 'blue' },
  ];
  const dPicks = dGames.flatMap(g => Array.from({ length: 10 }, () => ({ match_detail_id: '1', game_no: g.game_no })));
  const dTg = dGames.flatMap(g => Array.from({ length: 2 }, () => ({ match_detail_id: '1', game_no: g.game_no })));
  const dBans = dGames.flatMap(g => Array.from({ length: 10 }, () => ({ match_detail_id: '1', game_no: g.game_no })));
  const dBase = { schedule: dSched, matches: [{ match_detail_id: '1' }],
    standings: [{ match_win: 1, game_win: 2 }], games: dGames, picks: dPicks,
    team_games: dTg, bans: dBans };
  ok(snapshotCompleteness(dBase, 1).complete, 'C10 complete draft rows support a final snapshot');
  const dNoBans = { ...dBase, bans: dBans.filter(b => b.game_no !== 2) };
  const dNoBansResult = snapshotCompleteness(dNoBans, 1);
  ok(!dNoBansResult.complete && dNoBansResult.draftIssues.some(x => x.startsWith('bans:')),
    'C10 a game losing all enriched bans is partial');
  const dSides = JSON.parse(JSON.stringify(dBase));
  dSides.games[0].team_a_side = null;
  ok(!snapshotCompleteness(dSides, 1).complete, 'C10 missing recorded side is partial');
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
  const good = makeCacheEntry(s, { seasonId: 's18', schema: 4, decided: 1, complete: true, refreshedAt: 123 });
  ok(validateCacheEntry(good, OPTS).ok, 'C4 valid entry accepted');
  ok(good.v === 2 && good.source === 'refresh', 'C4 entry carries version + source');
  ok(!validateCacheEntry({ ...good, seasonId: 's19' }, OPTS).ok, 'C5 other season rejected');
  ok(!validateCacheEntry({ ...good, schema: 0 }, OPTS).ok, 'C6 older schema rejected');
  ok(!validateCacheEntry({ ...good, schema: 5 }, OPTS).ok, 'C6 unknown schema rejected');
  ok(!validateCacheEntry({ ...good, data: { standings: [] } }, OPTS).ok, 'C7 malformed data rejected');
  const noAnalytics = JSON.parse(JSON.stringify(good)); delete noAnalytics.data.team_games;
  ok(!validateCacheEntry(noAnalytics, OPTS).ok, 'C7 cache without derived analytics rejected');
  const mixed = JSON.parse(JSON.stringify(good));
  mixed.data.games = [{ match_detail_id: 'x', game_no: 1, team_a: 'A', team_b: 'B', winner: 'team_a' }];
  mixed.data.players = [{ match_detail_id: 'x', game_no: 1, team: 'A', player: 'P', hero: 'H', lane: 'MID', kills: 1 }];
  mixed.data.picks = derivePicks(mixed.data.players, mixed.data.games, []);
  mixed.data.team_games = [{ match_detail_id: 'x', game_no: 1, team: 'A', opponent: 'B', win: 1, kills: 1, deaths: 0, gold: 1 }];
  mixed.data.team_season = [];
  mixed.fp = fingerprintSnapshot(mixed.data);
  ok(!validateCacheEntry(mixed, OPTS).ok, 'C7 cache with aggregates not derived from its raw rows rejected');
  ok(!validateCacheEntry({ ...good, fp: 'deadbeef' }, OPTS).ok, 'C7 fingerprint mismatch rejected');
  const incomplete = makeCacheEntry(s, { seasonId: 's18', schema: 4, decided: 1, complete: true,
    expected: 2, completed: 1, missingIds: ['missing'], refreshedAt: 123 });
  ok(!validateCacheEntry(incomplete, OPTS).ok, 'C7 cache claiming complete with missing results rejected');
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
  const e = makeCacheEntry(s, { seasonId: 's18', schema: 4, decided: 1, complete: true, refreshedAt: 100 });
  const reloaded = JSON.parse(JSON.stringify(e));
  ok(validateCacheEntry(reloaded, OPTS).ok, 'C9 complete refresh reload validates');
  ok(selectSnapshot({ fp: 'old', decided: 0 }, reloaded).use === 'cache', 'C9 newer complete cache adopted on reload');
  // partial refresh then reload: adopted but labelled
  const pe = makeCacheEntry(s, { seasonId: 's18', schema: 4, decided: 1, complete: false, failedIds: ['7'], refreshedAt: 101 });
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
