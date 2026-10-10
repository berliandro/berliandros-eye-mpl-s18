/* Season config tests, JS side (Area 6): the committed Season 18 config is
   pinned, validSeasonCfg behaves, the unified team-code mapping resolves
   every historically seen spelling, and calcChances defaults match the
   configured Beta(2,2) prior. Usage: node tools/test_config.js (exit 0). */
'use strict';
const fs = require('fs');
const path = require('path');
const SEASON = JSON.parse(fs.readFileSync(path.join(__dirname, '..', 'data', 'season.json'), 'utf8'));
const src = fs.readFileSync(path.join(__dirname, 'templates', 'app.js'), 'utf8');
const cm = src.match(/\/\* CFG-START \*\/([\s\S]*?)\/\* CFG-END \*\//);
if (!cm) { console.error('FAIL CFG markers missing'); process.exit(1); }
const CFGNS = new Function(cm[1] + '; return {validSeasonCfg};')();
const { validSeasonCfg } = CFGNS;
const hm = src.match(/\/\* CHANCES-START \*\/([\s\S]*?)\/\* CHANCES-END \*\//);
const HNS = new Function('SEASON', hm[1] + '; return {calcChances, normTeam};')(SEASON);
const { calcChances, normTeam } = HNS;

let fails = 0, count = 0;
function ok(cond, msg) {
  count++;
  console.log((cond ? 'PASS ' : 'FAIL ') + msg);
  if (!cond) fails++;
}
function eq(a, b, msg) { ok(JSON.stringify(a) === JSON.stringify(b), msg + ' (got ' + JSON.stringify(a) + ')'); }

// --- committed Season 18 values pinned ---
eq(SEASON.seasonId, 's18', 'G1 season id');
eq(SEASON.teams, ['AE', 'BTR', 'DEWA', 'EVOS', 'GEEK', 'NAVI', 'ONIC', 'RRQ', 'TLID'], 'G1 teams');
eq([SEASON.playoffSlots, SEASON.upperBracketSlots], [6, 2], 'G1 slots');
eq(SEASON.tiebreakers, ['match_point', 'net_game_win', 'h2h'], 'G1 tiebreakers');
eq([SEASON.model.priorWins, SEASON.model.priorGames], [2, 4], 'G1 prior');
eq([SEASON.model.trials, SEASON.model.seed], [2000, 20907], 'G1 trials/seed');
eq(SEASON.cacheNamespace + ':' + SEASON.seasonId + ':v' + SEASON.cacheSchema, 'mpl-board:s18:v1', 'G1 cache id');

// --- validSeasonCfg ---
ok(validSeasonCfg(SEASON), 'G2 committed config passes runtime guard');
ok(!validSeasonCfg(null) && !validSeasonCfg({}) && !validSeasonCfg([]), 'G2 garbage rejected');
ok(!validSeasonCfg({ ...SEASON, teams: [] }), 'G2 empty teams rejected');
ok(!validSeasonCfg({ ...SEASON, totalTeams: 8 }), 'G2 team-count mismatch rejected');
ok(!validSeasonCfg({ ...SEASON, playoffSlots: 9 }), 'G2 slots>=teams rejected');
ok(!validSeasonCfg({ ...SEASON, upperBracketSlots: 7 }), 'G2 upper>playoff rejected');
ok(!validSeasonCfg({ ...SEASON, seriesPerTeam: 15 }), 'G2 series math rejected');
ok(!validSeasonCfg({ ...SEASON, aliases: {} }), 'G2 empty aliases rejected');
ok(!validSeasonCfg({ ...SEASON, cacheSchema: 0 }), 'G2 bad schema rejected');

// --- unified mapping battery: every historically seen spelling ---
const battery = [
  ['NAVI', 'navi'], ['navi', 'navi'], ['Navi', 'navi'], ['Natus Vincere', 'navi'],
  ['TLID', 'tlid'], ['Team Liquid ID', 'tlid'], ['team liquid id', 'tlid'],
  ['AE', 'ae'], ['Alter Ego', 'ae'], ['Alter Ego Esports', 'ae'],
  ['BTR', 'btr'], ['Bigetron', 'btr'], ['Bigetron by Vitality', 'btr'],
  ['DEWA', 'dewa'], ['Dewa United', 'dewa'], ['Dewa United Esports', 'dewa'],
  ['ONIC', 'onic'], ['EVOS', 'evos'],
  ['RRQ', 'rrq'], ['RRQ Hoshi', 'rrq'],
  ['GEEK', 'geek'], ['Geek Fam', 'geek'], ['Geek Fam ID', 'geek'],
  ['TBD', 'tbd'], ['', ''], ['Foo Bar', 'foobar']
];
battery.forEach(([input, want]) => eq(normTeam(input), want, 'G3 map ' + JSON.stringify(input)));

// --- calcChances defaults equal the configured prior ---
{
  const st = [{ key: 'a', pts: 1, won: 1, lost: 0, diff: 1 }, { key: 'b', pts: 0, won: 0, lost: 1, diff: -1 }];
  const fx = [{ a: 'a', b: 'b', decided: true, winner: 'a', sweep: true }];
  const o = { totalSeries: 2, playoffSlots: 1, upperSlots: 1, exact: true };
  const dflt = calcChances(st, fx, o);
  const expl = calcChances(st, fx, { ...o, priorW: 2, priorN: 4 });
  eq(dflt.diag.sweepP, expl.diag.sweepP, 'G4 default prior == configured Beta(2,2)');
  const bad = calcChances(st, fx, { ...o, priorW: 99, priorN: 1 });
  eq(bad.diag.sweepP, expl.diag.sweepP, 'G4 invalid prior clamps to 2/4');
}

console.log('\n' + (count - fails) + '/' + count + ' passed, ' + fails + ' failed');
process.exit(fails ? 1 : 0);
