/* Independent tests for the analytics engine (ANALYTICS-START/END block in
   tools/templates/app.js). No DOM, no DATA globals. Covers Wilson intervals,
   shrinkage, quantiles, percentiles, per-player aggregation, lane percentiles,
   the documented impact weights, canonicalisation, empty/missing inputs and
   determinism.
   Usage: node tools/test_analytics.js (exit 0 = pass). */
'use strict';
const fs = require('fs');
const path = require('path');
const src = fs.readFileSync(path.join(__dirname, 'templates', 'app.js'), 'utf8');
const m = src.match(/\/\* ANALYTICS-START \*\/([\s\S]*?)\/\* ANALYTICS-END \*\//);
if (!m) { console.error('FAIL ANALYTICS markers missing'); process.exit(1); }
const NS = new Function(m[1] + '; return {IMPACT_WEIGHTS,anMean,anQuantile,anWilson,anShrink,anPct,anMode,anLane,buildPlayerMetrics};')();
const { IMPACT_WEIGHTS, anMean, anQuantile, anWilson, anShrink, anPct, anMode, anLane, buildPlayerMetrics } = NS;

let fails = 0, count = 0;
function ok(cond, msg) {
  count++;
  console.log((cond ? 'PASS ' : 'FAIL ') + msg);
  if (!cond) fails++;
}
function eq(a, b, msg) { ok(a === b, msg + ' (got ' + a + ', want ' + b + ')'); }
function close(a, b, tol, msg) {
  ok(Math.abs(a - b) <= tol, msg + ' (got ' + a + ', want ' + b + ' +/-' + tol + ')');
}

// --- primitives ---
{
  const w = anWilson(5, 10);
  close(w.p, 0.5, 1e-12, 'W1 wilson p=0.5');
  close(w.lo, 0.2366, 0.001, 'W1 wilson lower');
  close(w.hi, 0.7634, 0.001, 'W1 wilson upper');
  eq(anWilson(0, 0).n, 0, 'W1 empty wilson n=0');
  eq(anWilson(0, 10).lo, 0, 'W1 zero wins lower=0');
}
{
  close(anShrink(1, 1, 0.5, 5), 0.5833333, 1e-6, 'S1 shrink one game toward 0.5');
  close(anShrink(0.8, 20, 0.5, 5), (16 + 2.5) / 25, 1e-12, 'S1 shrink weights by n');
  eq(anShrink(0.9, 0, 0.5, 5), 0.5, 'S1 shrink with n=0 returns prior');
}
{
  eq(anQuantile([1, 2, 3, 4], 0.5), 2.5, 'Q1 median interpolates');
  close(anQuantile([1, 2, 3, 4], 0.1), 1.3, 1e-12, 'Q1 p10 interpolates');
  eq(anQuantile([], 0.5), 0, 'Q1 empty=0');
  eq(anPct([1, 2, 3], 2), 0.5, 'P1 percentile midpoint');
  eq(anPct([1, 2, 3], 3), 1, 'P1 percentile max');
  eq(anPct([1, 2, 3], 0), 0, 'P1 percentile below');
  eq(anMode(['a', 'b', 'a']), 'a', 'M1 mode');
  eq(anMode(['b', 'a']), 'a', 'M1 deterministic tie-break');
  close(anMean([1, 2, 3]), 2, 1e-12, 'M1 mean');
}

// --- fixture: two games, two lanes, four players ---
const G = (mid, a, b, w, sa, sb) => ({ match_detail_id: String(mid), game_no: 1, team_a: a, team_b: b, winner: w, team_a_side: sa, team_b_side: sb });
const games = [G(1, 'A', 'B', 'team_a', 'blue', 'red'), G(2, 'B', 'A', 'team_a', 'blue', 'red')];
const TG = (mid, team, k, g, d, t, tw) => ({ match_detail_id: String(mid), game_no: 1, team, kills: k, gold: g, hero_damage: d, damage_taken: t, tower_damage: tw });
const teamGames = [
  TG(1, 'A', 7, 22000, 70000, 30000, 6000),
  TG(1, 'B', 3, 17000, 45000, 50000, 2500),
  TG(2, 'B', 7, 24000, 80000, 30000, 5500),
  TG(2, 'A', 6, 20000, 60000, 43000, 1800),
];
const P = (mid, team, player, lane, hero, k, d, a, gold, gpm, dmg, taken, tower) => ({
  match_detail_id: String(mid), game_no: 1, team, player, lane, hero,
  kills: k, deaths: d, assists: a, gold, gold_per_min: gpm,
  hero_damage: dmg, damage_taken: taken, tower_damage: tower,
});
const players = [
  P(1, 'A', 'P1', 'EXP', 'H1', 5, 1, 5, 10000, 600, 30000, 20000, 5000),
  P(1, 'A', 'P2', 'MID', 'H2', 2, 2, 8, 12000, 700, 40000, 10000, 1000),
  P(1, 'B', 'P3', 'EXP', 'H3', 1, 5, 2, 8000, 500, 20000, 30000, 2000),
  P(1, 'B', 'P4', 'MID', 'H4', 2, 4, 3, 9000, 550, 25000, 25000, 500),
  P(2, 'B', 'P3', 'EXP', 'H3', 4, 2, 6, 11000, 650, 35000, 18000, 4000),
  P(2, 'B', 'P4', 'MID', 'H4', 3, 3, 7, 13000, 750, 45000, 12000, 1500),
  P(2, 'A', 'P1', 'EXP', 'H1', 2, 4, 3, 9000, 550, 22000, 28000, 1000),
  P(2, 'A', 'P2', 'MID', 'H2', 4, 3, 4, 11000, 650, 38000, 15000, 800),
];
const classes = { H1: { primary_role: 'Fighter' }, H2: { primary_role: 'Mage' }, H3: { primary_role: 'Fighter' }, H4: { primary_role: 'Mage' } };
const dateOf = mid => (mid === '1' ? '2026-08-01' : '2026-08-02');

const A = buildPlayerMetrics(players, games, teamGames, classes, { dateOf });
const by = Object.fromEntries(A.players.map(p => [p.player, p]));
eq(A.players.length, 4, 'A1 four players');
eq(A.lanes.join(','), 'EXP,MID', 'A1 lanes sorted');
eq(by.P1.games, 2, 'A1 P1 games');
eq(by.P1.wins, 1, 'A1 P1 wins');
eq(by.P1.lane, 'EXP', 'A1 P1 lane');
eq(by.P1.team, 'A', 'A1 P1 team');
close(by.P1.kda, 5.625, 1e-9, 'A1 P1 KDA');
close(by.P2.kda, 3.8333333, 1e-6, 'A1 P2 KDA');
close(by.P3.kda, 2.8, 1e-9, 'A1 P3 KDA');
close(by.P4.kda, 2.2916667, 1e-6, 'A1 P4 KDA');
close(by.P1.damageShare, 0.3976190, 1e-6, 'A1 P1 damage share');
close(by.P1.kp, 1.1309524, 1e-6, 'A1 P1 kill participation');
close(by.P1.goldShare, 0.4522727, 1e-6, 'A1 P1 gold share');
close(by.P1.towerShare, 0.6944444, 1e-6, 'A1 P1 tower share');
eq(by.P1.heroes, 1, 'A1 P1 unique heroes');
eq(by.P1.small, true, 'A1 small sample flagged (2 < 5)');
eq(by.P1.winCI.n, 2, 'A1 win CI carries n');
close(by.P1.kdaP50, 5.625, 1e-9, 'A1 median of two KDA values');
close(by.P1.kdaIQR, 4.375, 1e-9, 'A1 KDA IQR');
close(by.P1.formDelta, 0, 1e-12, 'A1 form delta for two-game sample');
eq(by.P1.offLaneGames, 0, 'A1 no off-lane games');
eq(by.P1.offLaneDelta, null, 'A1 off-lane delta null without off-lane games');

// Lane percentiles: higher KDA ranks first within lane.
close(by.P1.pct.kda, 1, 1e-12, 'L1 EXP KDA percentile 1');
close(by.P3.pct.kda, 0, 1e-12, 'L1 EXP KDA percentile 0');
close(by.P2.pct.kda, 1, 1e-12, 'L1 MID KDA percentile 1');
close(by.P4.pct.kda, 0, 1e-12, 'L1 MID KDA percentile 0');
close(by.P1.pct.gpm, 0.5, 1e-12, 'L1 equal GPM percentiles tie at 0.5');

// Impact is exactly the documented weighted sum of percentiles.
A.players.forEach(p => {
  const expected = 100 * (IMPACT_WEIGHTS.damageShare * p.pct.damageShare +
    IMPACT_WEIGHTS.kp * p.pct.kp + IMPACT_WEIGHTS.goldShare * p.pct.goldShare +
    IMPACT_WEIGHTS.towerShare * p.pct.towerShare + IMPACT_WEIGHTS.deathShare * p.pct.deathShare);
  close(p.impact, expected, 1e-9, 'I1 impact formula ' + p.player);
});
eq(A.players[0].impact >= A.players[A.players.length - 1].impact, true, 'I1 descending impact');
eq(JSON.stringify(A.weights), JSON.stringify({ damageShare: 0.35, kp: 0.25, goldShare: 0.20, towerShare: 0.10, deathShare: -0.10 }), 'I1 weights pinned');

// Canonicalisation and date ordering.
{
  const C = buildPlayerMetrics(players, games, teamGames, classes, { dateOf, canon: s => s.toLowerCase() });
  eq(C.players.map(p => p.player).sort().join(','), 'p1,p2,p3,p4', 'C1 canonical names applied');
}
// Missing team aggregates: no crash, zero shares.
{
  const Z = buildPlayerMetrics(players, games, [], classes, { dateOf });
  eq(Z.players.length, 4, 'E1 missing team rows still yields players');
  eq(Z.players.every(p => p.damageShare === 0 && p.kp === 0), true, 'E1 missing team rows yield zero shares');
}
// Empty input.
{
  const E = buildPlayerMetrics([], [], [], {}, {});
  eq(E.players.length, 0, 'E1 empty input');
  eq(E.lanes.length, 0, 'E1 empty lanes');
}
// Determinism.
{
  const A2 = buildPlayerMetrics(players, games, teamGames, classes, { dateOf });
  const slim = x => x.players.map(p => [p.player, p.games, p.kda, p.impact]);
  eq(JSON.stringify(slim(A)), JSON.stringify(slim(A2)), 'D1 deterministic output');
}

console.log('\n' + (count - fails) + '/' + count + ' passed, ' + fails + ' failed');
process.exit(fails ? 1 : 0);
