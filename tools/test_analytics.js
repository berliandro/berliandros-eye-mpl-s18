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
const NS = new Function(m[1] + '; return {IMPACT_WEIGHTS,anMean,anQuantile,anWilson,anShrink,anPct,anMode,anLane,buildPlayerMetrics,anBT,buildTeamMetrics,buildDraftMetrics,buildBanRanking};')();
const { IMPACT_WEIGHTS, anMean, anQuantile, anWilson, anShrink, anPct, anMode, anLane, buildPlayerMetrics, anBT, buildTeamMetrics, buildDraftMetrics, buildBanRanking } = NS;

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

const A = buildPlayerMetrics(players, games, teamGames, classes, { dateOf, teamWinRate: { A: 0.8, B: 0.2 } });
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
eq(by.P1.close.n, 2, 'A1 close-game sample');
eq(by.P1.close.wins, 1, 'A1 close-game wins');
close(by.P1.close.winRate, 0.5, 1e-12, 'A1 close-game win rate');
eq(by.P1.oppTier.weak.n, 2, 'A1 P1 faces weak opponents');
eq(by.P1.oppTier.strong.n, 0, 'A1 P1 no strong opponents');
eq(by.P3.oppTier.strong.n, 2, 'A1 P3 faces strong opponents');
eq(by.P1.effectivePool, 1, 'A1 effective pool');
eq(by.P1.flexHeroes, 0, 'A1 flex heroes');
close(by.P1.dpg, 2.7222222, 1e-6, 'A1 damage per gold');
close(by.P1.towerPerGame, 3000, 1e-9, 'A1 tower damage per game');
close(by.P1.comfort, 0.5, 1e-12, 'A1 comfort index');
eq(by.P1.pool[0].hero, 'H1', 'A1 pool hero');
close(by.P1.pool[0].leagueWr, 0.5, 1e-12, 'A1 pool league WR');

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

// --- team ratings, form, side, tempo, clutch, dominance ---
{
  const TG2 = (mid, team, opp, win, k, g, d, tw, sec, map) => ({ match_detail_id: String(mid), game_no: 1, team, opponent: opp, win, kills: k, gold: g, hero_damage: d, damage_taken: 0, tower_damage: tw, duration_sec: sec, map_mode: map });
  const tg = [
    TG2(1, 'A', 'B', 1, 10, 60000, 70000, 6000, 1000, 'Prime'),
    TG2(1, 'B', 'A', 0, 5, 50000, 45000, 2000, 1000, 'Prime'),
    TG2(2, 'A', 'B', 1, 8, 55000, 60000, 5000, 1200, 'Prime'),
    TG2(2, 'B', 'A', 0, 6, 52000, 50000, 3000, 1200, 'Prime'),
    TG2(3, 'B', 'C', 1, 12, 58000, 65000, 7000, 900, 'Prime'),
    TG2(3, 'C', 'B', 0, 4, 42000, 40000, 1000, 900, 'Prime'),
    TG2(4, 'A', 'C', 0, 7, 48000, 52000, 2500, 1500, 'Prime'),
    TG2(4, 'C', 'A', 1, 9, 56000, 60000, 5000, 1500, 'Prime'),
    TG2(5, 'B', 'C', 0, 3, 40000, 38000, 1200, 1800, 'Prime'),
    TG2(5, 'C', 'B', 1, 11, 62000, 68000, 6500, 1800, 'Prime'),
    TG2(6, 'A', 'C', 1, 9, 58000, 61000, 4500, 1400, 'Prime'),
    TG2(6, 'C', 'A', 0, 8, 54000, 55000, 3500, 1400, 'Prime'),
  ];
  const dg = [
    { match_detail_id: '1', game_no: 1, team_a: 'A', team_b: 'B', winner: 'team_a', team_a_side: 'blue', team_b_side: 'red', map_mode: 'Prime', duration_sec: 1000 },
    { match_detail_id: '2', game_no: 1, team_a: 'A', team_b: 'B', winner: 'team_a', team_a_side: 'red', team_b_side: 'blue', map_mode: 'Prime', duration_sec: 1200 },
    { match_detail_id: '3', game_no: 1, team_a: 'B', team_b: 'C', winner: 'team_a', team_a_side: 'blue', team_b_side: 'red', map_mode: 'Prime', duration_sec: 900 },
    { match_detail_id: '4', game_no: 1, team_a: 'A', team_b: 'C', winner: 'team_b', team_a_side: 'blue', team_b_side: 'red', map_mode: 'Prime', duration_sec: 1500 },
    { match_detail_id: '5', game_no: 1, team_a: 'B', team_b: 'C', winner: 'team_b', team_a_side: 'red', team_b_side: 'blue', map_mode: 'Prime', duration_sec: 1800 },
    { match_detail_id: '6', game_no: 1, team_a: 'A', team_b: 'C', winner: 'team_a', team_a_side: 'red', team_b_side: 'blue', map_mode: 'Prime', duration_sec: 1400 },
  ];
  const teams = [{ team: 'A', team_name: 'Alpha' }, { team: 'B', team_name: 'Bravo' }, { team: 'C', team_name: 'Charlie' }];
  const dateOf = mid => ({ '1': '2026-08-01', '2': '2026-08-02', '3': '2026-08-03', '4': '2026-08-04', '5': '2026-08-05', '6': '2026-08-06' })[mid] || '';
  const TM = buildTeamMetrics(tg, teams, dg, { bootstraps: 50, seed: 7, dateOf });
  const bt = Object.fromEntries(TM.teams.map(t => [t.team, t]));
  eq(TM.teams.length, 3, 'TM1 three teams');
  eq(bt.A.games, 4, 'TM1 A games');
  eq(bt.A.wins, 3, 'TM1 A wins');
  close(bt.A.winRate, 0.75, 1e-12, 'TM1 A win rate');
  eq(bt.A.winCI.n, 4, 'TM1 A win CI n');
  close(bt.A.form5, 0.75, 1e-12, 'TM2 A form5');
  close(bt.A.form5Series, 0.75, 1e-12, 'TM2 A form5 series');
  eq(bt.A.series, 4, 'TM2 A series count');
  eq(bt.A.h2h.B.n, 2, 'TM2b A vs B games');
  eq(bt.A.h2h.B.w, 2, 'TM2b A vs B wins');
  eq(bt.A.h2h.C.n, 2, 'TM2b A vs C games');
  eq(bt.A.h2h.C.w, 1, 'TM2b A vs C wins');
  eq(bt.A.side.blue.n, 2, 'TM3 A blue games');
  eq(bt.A.side.blue.w, 1, 'TM3 A blue wins');
  eq(bt.A.side.red.n, 2, 'TM3 A red games');
  eq(bt.A.side.red.w, 2, 'TM3 A red wins');
  close(bt.A.tempo.winSec, 1200, 1e-9, 'TM4 A avg win duration');
  close(bt.A.tempo.lossSec, 1500, 1e-9, 'TM4 A avg loss duration');
  eq(bt.A.tempo.lateWins, 1, 'TM4 A late win count');
  eq(bt.A.clutch.decider.n, 4, 'TM5 A decider games');
  eq(bt.A.clutch.decider.w, 3, 'TM5 A decider wins');
  close(bt.A.dominance.killDiff, 1.5, 1e-9, 'TM6 A kill diff');
  close(bt.A.dominance.goldDiff, 2250, 1e-9, 'TM6 A gold diff');
  eq(bt.A.maps[0].map, 'Prime', 'TM7 A map');
  eq(bt.A.maps[0].n, 4, 'TM7 A map games');
  ok(bt.A.rating > bt.C.rating && bt.C.rating > bt.B.rating, 'TM8 ratings ordered A>C>B (A ' + bt.A.rating.toFixed(0) + ', C ' + bt.C.rating.toFixed(0) + ', B ' + bt.B.rating.toFixed(0) + ')');
  ok(bt.A.ratingCI[0] <= bt.A.ratingCI[1], 'TM8 A CI ordered');
  eq(TM.method.prior, 1, 'TM9 prior pinned');
  const TM2 = buildTeamMetrics(tg, teams, dg, { bootstraps: 50, seed: 7, dateOf });
  eq(bt.A.rating, TM2.teams.find(t => t.team === 'A').rating, 'TM9 deterministic bootstrap');
  const E = buildTeamMetrics([], [{ team: 'A', team_name: 'A' }], [], { bootstraps: 5 });
  eq(E.teams.length, 1, 'TM10 empty one team');
  eq(E.teams[0].games, 0, 'TM10 empty games');
  eq(E.teams[0].sos, 0, 'TM10 empty SOS is 0');
  eq(E.teams[0].rating, 1500, 'TM10 empty rating is neutral');
}

// --- draft: heroes, synergy, counters, fingerprints, maps, compositions ---
{
  const cls2 = {
    H1: { primary_role: 'Tank', damage_type: 'physical', specialties: ['Crowd Control'] },
    H2: { primary_role: 'Mage', damage_type: 'magic', specialties: ['Burst'] },
    H3: { primary_role: 'Fighter', damage_type: 'physical', specialties: ['Initiator'] },
    H4: { primary_role: 'Marksman', damage_type: 'physical', specialties: [] },
    H5: { primary_role: 'Support', damage_type: 'magic', specialties: ['Crowd Control', 'Heal'] },
    H6: { primary_role: 'Tank', damage_type: 'physical', specialties: ['Crowd Control'] },
    H7: { primary_role: 'Mage', damage_type: 'magic', specialties: ['Burst'] },
    H8: { primary_role: 'Assassin', damage_type: 'physical', specialties: [] },
    H9: { primary_role: 'Marksman', damage_type: 'physical', specialties: [] },
    H10: { primary_role: 'Support', damage_type: 'magic', specialties: ['Engage'] },
  };
  const DG = [
    { match_detail_id: '1', game_no: 1, team_a: 'A', team_b: 'B', winner: 'team_a', team_a_side: 'blue', team_b_side: 'red', map_mode: 'Prime', duration_sec: 1000 },
    { match_detail_id: '2', game_no: 1, team_a: 'B', team_b: 'A', winner: 'team_a', team_a_side: 'blue', team_b_side: 'red', map_mode: 'Prime', duration_sec: 1200 },
  ];
  const mkP = (mid, team, side, lane, hero) => ({ match_detail_id: String(mid), game_no: 1, team, side, slot: 1, lane, hero, player: 'P' + hero });
  const dpicks = [
    mkP(1, 'A', 'blue', 'EXP', 'H1'), mkP(1, 'A', 'blue', 'MID', 'H2'), mkP(1, 'A', 'blue', 'JUNGLE', 'H3'), mkP(1, 'A', 'blue', 'GOLD', 'H4'), mkP(1, 'A', 'blue', 'ROAM', 'H5'),
    mkP(1, 'B', 'red', 'EXP', 'H6'), mkP(1, 'B', 'red', 'MID', 'H7'), mkP(1, 'B', 'red', 'JUNGLE', 'H8'), mkP(1, 'B', 'red', 'GOLD', 'H9'), mkP(1, 'B', 'red', 'ROAM', 'H10'),
    mkP(2, 'B', 'blue', 'JUNGLE', 'H1'), mkP(2, 'B', 'blue', 'MID', 'H7'), mkP(2, 'B', 'blue', 'JUNGLE', 'H8'), mkP(2, 'B', 'blue', 'GOLD', 'H9'), mkP(2, 'B', 'blue', 'ROAM', 'H10'),
    mkP(2, 'A', 'red', 'EXP', 'H6'), mkP(2, 'A', 'red', 'MID', 'H2'), mkP(2, 'A', 'red', 'JUNGLE', 'H3'), mkP(2, 'A', 'red', 'GOLD', 'H4'), mkP(2, 'A', 'red', 'ROAM', 'H5'),
  ];
  const mkB = (mid, side, order, hero) => ({ match_detail_id: String(mid), game_no: 1, side, ban_order: order, hero });
  const dbans = [
    mkB(1, 'A', 1, 'H11'), mkB(1, 'A', 2, 'H12'), mkB(1, 'B', 1, 'H13'), mkB(1, 'B', 2, 'H14'),
    mkB(2, 'A', 1, 'H12'), mkB(2, 'A', 2, 'H11'), mkB(2, 'B', 1, 'H14'), mkB(2, 'B', 2, 'H13'),
  ];
  const DM = buildDraftMetrics(dpicks, dbans, DG, cls2, { minPair: 1 });
  const hero = h => DM.heroes.find(x => x.hero === h);
  const pair = (a, b) => DM.pairs.find(p => p.a === a && p.b === b);
  const ctr = (a, b) => DM.counters.find(p => p.a === a && p.b === b);
  const team = t => DM.teams.find(x => x.team === t);

  eq(DM.heroes.length, 14, 'DM1 14 heroes including ban-only');
  eq(hero('H1').picks, 2, 'DM1 H1 picks');
  eq(hero('H1').wins, 2, 'DM1 H1 wins');
  eq(hero('H1').flex, 2, 'DM1 H1 flex across EXP/JUNGLE');
  eq(hero('H1').lanes.EXP, 1, 'DM1 H1 EXP lane count');
  eq(hero('H1').lanes.JUNGLE, 1, 'DM1 H1 JUNGLE lane count');
  eq(hero('H1').sides.blue.n, 2, 'DM1 H1 blue games');
  eq(hero('H6').wins, 0, 'DM1 H6 winless');
  eq(hero('H11').picks, 0, 'DM1 ban-only hero picks=0');
  eq(hero('H11').bans, 2, 'DM1 ban-only hero bans=2');

  eq(DM.pairs.length, 28, 'DM2 28 unique same-team pairs');
  eq(pair('H2', 'H3').n, 2, 'DM2 H2+H3 pair n');
  eq(pair('H2', 'H3').w, 1, 'DM2 H2+H3 pair wins');
  close(pair('H2', 'H3').wr, 0.5, 1e-12, 'DM2 H2+H3 pair WR');
  close(pair('H2', 'H3').delta, 0, 1e-12, 'DM2 H2+H3 delta vs baseline');
  eq(pair('H1', 'H2').n, 1, 'DM2 H1+H2 pair n');
  close(pair('H1', 'H2').expected, 0.75, 1e-12, 'DM2 H1+H2 expected baseline');
  close(pair('H1', 'H2').delta, 0.25, 1e-12, 'DM2 H1+H2 synergy delta');

  eq(DM.counters.length, 33, 'DM3 33 counter pairs (12 pairs never opposed)');
  eq(ctr('H1', 'H6').n, 2, 'DM3 H1 vs H6 n');
  eq(ctr('H1', 'H6').w, 2, 'DM3 H1 vs H6 wins');
  eq(ctr('H2', 'H7').n, 2, 'DM3 H2 vs H7 n');
  eq(ctr('H2', 'H7').w, 1, 'DM3 H2 vs H7 split');
  close(ctr('H2', 'H7').delta, 0, 1e-12, 'DM3 H2 vs H7 delta');

  eq(team('A').picks, 10, 'DM4 A picks');
  close(team('A').hhi, 0.18, 1e-12, 'DM4 A pick HHI');
  eq(team('A').topPicks.length, 5, 'DM4 A top picks length');
  eq(team('A').topPicks[0].n, 2, 'DM4 A top pick count');
  close(team('A').topPicks[0].share, 1, 1e-12, 'DM4 A top pick rate per game');
  eq(team('A').firstBanBlue[0].hero, 'H11', 'DM5 A blue first ban');
  eq(team('A').firstBanRed[0].hero, 'H14', 'DM5 A red first ban');
  eq(team('B').firstBanBlue[0].hero, 'H12', 'DM5 B blue first ban');
  eq(team('B').firstBanRed[0].hero, 'H13', 'DM5 B red first ban');
  eq(team('A').pocketPicks.length, 0, 'DM6 no pocket picks');

  eq(DM.maps.length, 1, 'DM7 one map');
  eq(DM.maps[0].games, 2, 'DM7 map games');
  close(DM.maps[0].blueWR, 1, 1e-12, 'DM7 map blue WR');
  close(DM.maps[0].avgSec, 1100, 1e-9, 'DM7 map avg duration');
  eq(DM.maps[0].topHeroes[0].hero, 'H1', 'DM7 map top hero tie-break');

  eq(DM.compositions.length, 2, 'DM8 two composition archetypes');
  const c2 = DM.compositions.find(c => c.damage === 'mixed' && c.frontline === 2);
  eq(c2.n, 2, 'DM8 frontline-2 n');
  eq(c2.w, 1, 'DM8 frontline-2 wins');
  close(c2.wr, 0.5, 1e-12, 'DM8 frontline-2 WR');
  close(c2.avgCC, 3, 1e-12, 'DM8 frontline-2 CC');
  const c1 = DM.compositions.find(c => c.damage === 'mixed' && c.frontline === 1);
  close(c1.avgCC, 2, 1e-12, 'DM8 frontline-1 CC');
  eq(DM.method.minPair, 1, 'DM9 minPair echoed');
  const BR = buildBanRanking('A', DM, 1);
  eq(BR.length, 6, 'BR1 six picked heroes');
  const br = BR.find(x => x.hero === 'H2');
  close(br.presence, 1, 1e-12, 'BR1 H2 presence per game');
  close(br.wr, 0.5, 1e-12, 'BR1 H2 win rate');
  close(br.score, 0.5, 1e-12, 'BR1 H2 score');
  ok(BR[0].score >= BR[BR.length - 1].score, 'BR1 sorted by score');
  eq(buildBanRanking('Z', DM).length, 0, 'BR1 missing team returns empty');
}

// --- meta movement (week over week) ---
{
  const mg = [
    { match_detail_id: '1', game_no: 1, team_a: 'A', team_b: 'B', winner: 'team_a', team_a_side: 'blue', team_b_side: 'red', map_mode: 'Prime' },
    { match_detail_id: '2', game_no: 1, team_a: 'A', team_b: 'B', winner: 'team_a', team_a_side: 'blue', team_b_side: 'red', map_mode: 'Prime' },
  ];
  const mp = [
    { match_detail_id: '1', game_no: 1, team: 'A', side: 'blue', lane: 'EXP', hero: 'H1' },
    { match_detail_id: '1', game_no: 1, team: 'A', side: 'blue', lane: 'MID', hero: 'H2' },
    { match_detail_id: '2', game_no: 1, team: 'A', side: 'blue', lane: 'EXP', hero: 'H1' },
    { match_detail_id: '2', game_no: 1, team: 'A', side: 'blue', lane: 'MID', hero: 'H3' },
  ];
  const MM = buildDraftMetrics(mp, [], mg, {}, { minPair: 1, dateOf: mid => (mid === '1' ? '2026-08-01' : '2026-08-10') });
  const mv = h => MM.movement.find(x => x.hero === h);
  eq(MM.movement.length, 3, 'MM1 movement covers seen heroes');
  eq(mv('H3').delta, 1, 'MM1 rising hero delta');
  eq(mv('H2').delta, -1, 'MM1 falling hero delta');
  eq(mv('H1').delta, 0, 'MM1 stable hero delta');
  eq(MM.movement[0].hero, 'H3', 'MM1 sorted by rising delta');
  eq(mv('H3').games, 1, 'MM1 recent-week games');
}

console.log('\n' + (count - fails) + '/' + count + ' passed, ' + fails + ' failed');
process.exit(fails ? 1 : 0);
