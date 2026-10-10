/* Refresh-merge tests (Area 2): mergeRefresh/validSnapshot/refreshStatus from
   the REFRESH markers in tools/templates/app.js, plus parseMvps final-block
   behavior. All API/data shapes are mocked; no network, no DOM.
   Usage: node tools/test_refresh.js (exit 0 = pass). */
'use strict';
const fs = require('fs');
const path = require('path');
const src = fs.readFileSync(path.join(__dirname, 'templates', 'app.js'), 'utf8');
const m = src.match(/\/\* REFRESH-START \*\/([\s\S]*?)\/\* REFRESH-END \*\//);
if (!m) { console.error('FAIL REFRESH markers missing'); process.exit(1); }
const NS = new Function(m[1] + '; return {keyGame, keyPro, keyBan, mergeRefresh, validSnapshot, refreshStatus};')();
const { keyGame, keyPro, keyBan, mergeRefresh, validSnapshot, refreshStatus } = NS;
// parseMvps lives outside the markers (DOM-free); extract by name.
const pm = src.match(/function parseMvps\(wt\)\{[\s\S]*?return out;\}/);
if (!pm) { console.error('FAIL parseMvps not found'); process.exit(1); }
const parseMvps = new Function(pm[0] + '; return parseMvps;')();

let fails = 0, count = 0;
function ok(cond, msg) {
  count++;
  console.log((cond ? 'PASS ' : 'FAIL ') + msg);
  if (!cond) fails++;
}
const G = (id, gn) => ({ match_detail_id: id, game_no: gn });
const P = (id, gn, team, player, hero) => ({ match_detail_id: id, game_no: gn, team, player, hero, kills: 0 });
const B = (id, gn, side, hero) => ({ match_detail_id: id, game_no: gn, side, hero });
const fresh = (rows) => ({ ok: true, games: [], pros: [], bans: [], ...rows });

// --- all succeed: merged equals fresh, no duplicates ---
{
  const oldG = [G('1', 1), G('1', 2)];
  const newG = [G('1', 1), G('1', 2), G('1', 3)];
  const out = mergeRefresh(oldG, { 1: fresh({ games: newG }) }, 'games', keyGame);
  ok(out.length === 3, 'R1 all-ok merged length 3 (got ' + out.length + ')');
  ok(new Set(out.map(keyGame)).size === 3, 'R1 no duplicated game keys');
}

// --- one fails: failed id keeps old rows, succeeded id updated ---
{
  const oldG = [G('1', 1), G('2', 1)];
  const out = mergeRefresh(oldG, { 1: fresh({ games: [G('1', 1), G('1', 9)] }), 2: { ok: false } }, 'games', keyGame);
  const keys = out.map(keyGame).sort();
  ok(JSON.stringify(keys) === JSON.stringify(['1:1', '1:9', '2:1']), 'R2 failed id keeps old, ok id replaced (' + keys + ')');
}

// --- several fail; retry success on next refresh ---
{
  const oldP = [P('1', 1, 'A', 'x', 'H'), P('2', 1, 'B', 'y', 'H'), P('3', 1, 'C', 'z', 'H')];
  const r1 = mergeRefresh(oldP, {
    1: fresh({ pros: [P('1', 1, 'A', 'x', 'H2')] }), 2: { ok: false }, 3: { ok: false }
  }, 'pros', keyPro);
  ok(r1.length === 3, 'R3 multi-fail keeps all 3 rows');
  ok(r1.some(r => r.hero === 'H2'), 'R3 succeeded id updated');
  const r2 = mergeRefresh(r1, {
    1: fresh({ pros: [P('1', 1, 'A', 'x', 'H2')] }),
    2: fresh({ pros: [P('2', 1, 'B', 'y', 'H9')] }),
    3: fresh({ pros: [P('3', 1, 'C', 'z', 'H')] })
  }, 'pros', keyPro);
  ok(r2.length === 3, 'R4 retry fills failed ids without dupes');
  ok(r2.some(r => r.hero === 'H9'), 'R4 retried id updated');
}

// --- bans: succeeded id replaced by key, failed id kept (old code duplicated) ---
{
  const oldB = [B('1', 1, 'A', 'H'), B('2', 1, 'A', 'H')];
  const out = mergeRefresh(oldB, {
    1: fresh({ bans: [B('1', 1, 'A', 'H'), B('1', 1, 'B', 'H2')] }), 2: { ok: false }
  }, 'bans', keyBan);
  const keys = out.map(keyBan).sort();
  ok(JSON.stringify(keys) === JSON.stringify(['1:1:A:H', '1:1:B:H2', '2:1:A:H']),
    'R5 bans replaced-per-key, failed kept, no dupes (' + keys + ')');
}

// --- idempotence: repeated identical refreshes do not grow collections ---
{
  const oldG = [G('1', 1)];
  const f = { 1: fresh({ games: [G('1', 1), G('1', 2)] }) };
  const once = mergeRefresh(oldG, f, 'games', keyGame);
  const twice = mergeRefresh(once, f, 'games', keyGame);
  ok(once.length === 2 && twice.length === 2, 'R6 repeated refresh stable at 2 rows');
}

// --- unknown/extra ids and empty inputs do not throw ---
{
  const out = mergeRefresh([], {}, 'games', keyGame);
  ok(Array.isArray(out) && out.length === 0, 'R7 empty merge ok');
  const out2 = mergeRefresh([G('9', 1)], { 9: { ok: true, games: null } }, 'games', keyGame);
  ok(out2.length === 1, 'R8 malformed fresh rows treated as failed, old kept');
}

// --- validSnapshot ---
{
  const good = { schedule: [{ schedule_id: 'x' }], standings: [{ team_slug: 'a', match_point: 1 }], season: [] };
  ok(validSnapshot(good).ok, 'R9 valid snapshot accepted');
  ok(!validSnapshot({ schedule: [], standings: good.standings, season: [] }).ok, 'R10 empty schedule rejected');
  ok(!validSnapshot({ schedule: good.schedule, standings: [], season: [] }).ok, 'R11 empty standings rejected');
  ok(validSnapshot({ schedule: good.schedule, standings: [{ team_slug: 'a' }], season: [] }).ok,
    'R12 standings row without points tolerated (null ok)');
  ok(!validSnapshot(null).ok && !validSnapshot({}).ok, 'R13 malformed snapshots rejected');
}

// --- refreshStatus distinguishes complete vs partial ---
{
  const c = refreshStatus({ complete: true, fails: 0, games: 144, mvpN: 60, newMsg: '' });
  const p = refreshStatus({ complete: false, fails: 3, games: 120, mvpN: 60, newMsg: '' });
  ok(c.indexOf('updated ') === 0 && c.indexOf('partially') === -1, 'R14 complete wording (' + c + ')');
  ok(p.indexOf('partially updated') === 0 && p.indexOf('3 failed') > -1, 'R15 partial wording (' + p + ')');
}

// --- parseMvps keeps the final block (regression lock for app parser) ---
{
  const wt = '|M1={{Match\n|opponent1={{TeamOpponent|A}}\n|opponent2={{TeamOpponent|B}}\n|date=Aug 1\n|mvp=X\n' +
    '|M2={{Match\n|opponent1={{TeamOpponent|C}}\n|opponent2={{TeamOpponent|D}}\n|date=Aug 2\n|mvp=Y\n';
  const out = parseMvps(wt);
  ok(out.length === 2, 'R16 two blocks parsed');
  ok(out[1].mvp === 'Y' && out[1].t1 === 'C', 'R17 final block intact (no trailing marker)');
  const nomvp = '|M1={{Match\n|opponent1={{TeamOpponent|A}}\n|opponent2={{TeamOpponent|B}}\n|date=Aug 1\n';
  ok(parseMvps(nomvp).length === 1 && parseMvps(nomvp)[0].mvp === '', 'R18 missing MVP tolerated');
  ok(parseMvps('').length === 0, 'R19 empty input ok');
}

console.log('\n' + (count - fails) + '/' + count + ' passed, ' + fails + ' failed');
process.exit(fails ? 1 : 0);
