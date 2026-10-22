/* Snapshot derivation tests: every analytics input must be rebuildable from
   one raw snapshot after refresh, and missing enrichment fields must survive
   a live merge. No DOM, no network. Usage: node tools/test_snapshot.js */
'use strict';
const fs = require('fs');
const path = require('path');
const src = fs.readFileSync(path.join(__dirname, 'templates', 'app.js'), 'utf8');
const m = src.match(/\/\* SNAPSHOT-START \*\/([\s\S]*?)\/\* SNAPSHOT-END \*\//);
if (!m) { console.error('FAIL SNAPSHOT markers missing'); process.exit(1); }
const NS = new Function(m[1] + '; return {preserveFields,derivePicks,deriveTeamGames,deriveTeamSeason,deriveAnalyticsSnapshot};')();
const { preserveFields, derivePicks, deriveTeamGames, deriveTeamSeason, deriveAnalyticsSnapshot } = NS;

let fails = 0, count = 0;
function ok(cond, msg) { count++; console.log((cond ? 'PASS ' : 'FAIL ') + msg); if (!cond) fails++; }
function eq(a, b, msg) { ok(JSON.stringify(a) === JSON.stringify(b), msg + ' (got ' + JSON.stringify(a) + ', want ' + JSON.stringify(b) + ')'); }
function close(a, b, tol, msg) { ok(Math.abs(a - b) <= tol, msg + ' (got ' + a + ', want ' + b + ')'); }

const games = [
  { match_detail_id: '1', game_no: 1, team_a: 'A', team_b: 'B', winner: 'team_a', team_a_side: 'blue', team_b_side: 'red', map_mode: 'Prime', duration_sec: 1000 },
  { match_detail_id: '2', game_no: 1, team_a: 'B', team_b: 'A', winner: 'team_a', team_a_side: 'blue', team_b_side: 'red', map_mode: '', duration_sec: 1200 },
];
const P = (mid, team, player, lane, hero, k, d, a, gold) => ({ match_detail_id: mid, game_no: 1, team, player, lane, hero, kills: k, deaths: d, assists: a, gold, hero_damage: gold, damage_taken: 10, tower_damage: 100 });
const players = [
  P('1', 'A', 'p1', 'EXP', 'H1', 5, 1, 2, 1000), P('1', 'A', 'p2', 'MID', 'H2', 3, 2, 4, 1200),
  P('1', 'B', 'p3', 'EXP', 'H3', 1, 5, 1, 800), P('1', 'B', 'p4', 'MID', 'H4', 2, 3, 2, 900),
  P('2', 'B', 'p3', 'EXP', 'H3', 6, 2, 5, 1300), P('2', 'B', 'p4', 'MID', 'H2', 4, 1, 6, 1400),
  P('2', 'A', 'p1', 'EXP', 'H1', 2, 4, 1, 850), P('2', 'A', 'p2', 'MID', 'H4', 3, 3, 2, 950),
];
const standings = [{ team_slug: 'a', team_name: 'Alpha', match_win: 1, match_lose: 0, game_win: 1, game_lose: 0 },
  { team_slug: 'b', team_name: 'Bravo', match_win: 1, match_lose: 1, game_win: 1, game_lose: 1 }];
const oldPicks = [{ match_detail_id: '1', game_no: 1, team: 'A', player: 'p1', hero: 'H1', side: 'blue', lane: 'EXP', slot: 1 }];
const oldSeason = [{ team: 'A', team_name: 'Alpha', team_slug: 'a', games: 1, wins: 1, losses: 0 },
  { team: 'B', team_name: 'Bravo', team_slug: 'b', games: 1, wins: 0, losses: 1 }];

const picks = derivePicks(players, games, oldPicks);
eq(picks.length, 8, 'S1 one pick per player row');
eq(picks.filter(p => p.team === 'A' && p.game_no === 1)[0].side, 'blue', 'S1 side comes from game row');
eq(picks.find(p => p.player === 'p1' && p.match_detail_id === '1').slot, 1, 'S1 old slot preserved');
eq(picks.find(p => p.player === 'p2' && p.match_detail_id === '1').slot, 3, 'S1 lane-order slot for new pick');

const tg = deriveTeamGames(players, games, []);
eq(tg.length, 4, 'S2 two team rows per game');
eq(tg.filter(t => t.match_detail_id === '1' && t.team === 'A')[0].win, 1, 'S2 winner from game row');
eq(tg.filter(t => t.match_detail_id === '1' && t.team === 'B')[0].opponent, 'A', 'S2 opponent');
close(tg.filter(t => t.team === 'A')[0].kda, (8 + 6) / Math.max(1, 3), 1e-9, 'S2 team KDA from summed players');

const season = deriveTeamSeason(tg, oldSeason, standings);
eq(season.length, 2, 'S3 one row per team');
eq(season.find(t => t.team === 'A').games, 2, 'S3 games refreshed from raw rows');
eq(season.find(t => t.team === 'A').wins, 1, 'S3 wins refreshed from raw rows');
eq(season.find(t => t.team === 'A').team_name, 'Alpha', 'S3 official team name');
eq(season.find(t => t.team === 'B').team_slug, 'b', 'S3 official team slug');

const stale = [{ match_detail_id: '1', game_no: 1, team: 'A', opponent: 'B', win: 1, kills: 999, deaths: 0, gold: 1 }];
const derived = deriveAnalyticsSnapshot({ players, games, picks: oldPicks, team_games: stale, team_season: oldSeason, standings });
eq(derived.team_games.length, 4, 'S4 refresh derives aggregates, never keeps stale rows');
eq(derived.team_games.find(t => t.match_detail_id === '1' && t.team === 'A').kills, 8, 'S4 stale aggregate is replaced by raw sums');
eq(derived.team_season.find(t => t.team === 'A').games, 2, 'S4 standings/team aggregates use same raw snapshot');
eq(derived.picks.length, 8, 'S4 picks use same raw snapshot');
ok(JSON.stringify(deriveAnalyticsSnapshot({ players, games, picks: oldPicks, team_games: stale, team_season: oldSeason, standings })) === JSON.stringify(derived), 'S4 deterministic');

// Live refresh: fresh rows omit enrichment fields; preserve last-known-good.
const oldGames = [{ match_detail_id: '2', game_no: 1, team_a: 'B', team_b: 'A', winner: 'team_b', map_mode: 'Prime', duration_sec: 1200 }];
const freshGames = [{ match_detail_id: '2', game_no: 1, team_a: 'B', team_b: 'A', winner: 'team_b', map_mode: undefined, duration_sec: 1200 }];
eq(preserveFields(freshGames, oldGames, g => g.match_detail_id + ':' + g.game_no, ['map_mode'])[0].map_mode, 'Prime', 'S5 map mode survives live refresh');
const oldBans = [{ match_detail_id: '1', game_no: 1, side: 'A', hero: 'H9', ban_order: 1 }];
const freshBans = [{ match_detail_id: '1', game_no: 1, side: 'A', hero: 'H9' }];
eq(preserveFields(freshBans, oldBans, b => b.match_detail_id + ':' + b.game_no + ':' + b.side + ':' + b.hero, ['ban_order'])[0].ban_order, 1, 'S5 ban order survives live refresh');
const oldPros = [{ match_detail_id: '1', game_no: 1, team: 'A', player: 'p1', hero: 'H1', lane: 'EXP' }];
const freshPros = [{ match_detail_id: '1', game_no: 1, team: 'A', player: 'p1', hero: 'H1', lane: null }];
eq(preserveFields(freshPros, oldPros, p => p.match_detail_id + ':' + p.game_no + ':' + p.team + ':' + p.player + ':' + p.hero, ['lane'])[0].lane, 'EXP', 'S5 lane survives live refresh');

// Fallback row prevents a transient missing player response from dropping a
// team-game entirely; failed match IDs therefore retain last-good detail.
const fallback = [{ match_detail_id: '9', game_no: 1, team: 'A', opponent: 'B', win: 1, kills: 1, deaths: 0, gold: 1 }];
eq(deriveTeamGames([], [{ match_detail_id: '9', game_no: 1, team_a: 'A', team_b: 'B', winner: 'team_a' }], fallback).length, 1, 'S6 fallback retains failed/idle match aggregate');
{
  const empty = deriveAnalyticsSnapshot({ players: [], games: [], picks: [], team_games: [], team_season: [], standings: [] });
  eq([empty.picks.length, empty.team_games.length, empty.team_season.length], [0, 0, 0], 'S7 empty snapshot is empty, not invented');
  const totals = derived.team_season.reduce((n, t) => n + t.games, 0);
  eq(totals, derived.team_games.length, 'S7 team-season games equal team-game rows');
  eq(derived.team_season.reduce((n, t) => n + t.wins, 0), derived.team_games.filter(t => t.win === 1).length, 'S7 team-season wins equal winning team rows');
}

console.log('\n' + (count - fails) + '/' + count + ' passed, ' + fails + ' failed');
process.exit(fails ? 1 : 0);
