/* Independent tests for the season-final derivation (seasonFinal, cpTarget,
   teamRoster in tools/templates/app.js, between SEASON-FINAL-START/END).
   No DOM, no UI, no network. Covers: the Bo target, the 4-win trigger, the
   refused cases (tie, over-target anomaly, TBD, missing grand final),
   champion/runner-up orientation when the winner is team_b, score-known
   gating, the clinch game, trace withholding when the game set is
   incomplete, and roster ordering without invention.
   Usage: node tools/test_season_final.js (exit 0 = pass). */
'use strict';
const fs = require('fs');
const path = require('path');
const src = fs.readFileSync(path.join(__dirname, 'templates', 'app.js'), 'utf8');
const m = src.match(/\/\* SEASON-FINAL-START \*\/([\s\S]*?)\/\* SEASON-FINAL-END \*\//);
if (!m) { console.error('FAIL SEASON-FINAL markers missing'); process.exit(1); }

let fails = 0, count = 0;
function ok(cond, msg) {
  count++;
  console.log((cond ? 'PASS ' : 'FAIL ') + msg);
  if (!cond) fails++;
}
function eq(a, b, msg) {
  count++;
  const same = a === b;
  console.log((same ? 'PASS ' : 'FAIL ') + msg + (same ? '' : ' (got ' + JSON.stringify(a) + ', want ' + JSON.stringify(b) + ')'));
  if (!same) fails++;
}

function build(data) {
  const NS = new Function('DATA', 'canonicalPlayer', m[1] + '; return {seasonFinal, cpTarget, cpRealTeam, teamRoster};')(data, n => n);
  return NS;
}

function gfRow(over) {
  return Object.assign({
    match_id: 'id-playoffs-7', round: 'Grand Finals',
    team_a: 'TLID', team_b: 'NAVI', score_a: null, score_b: null,
    iso_date: '2026-11-08', status: 'upcoming', winner: null,
    series_format: 'Bo7', match_detail_id: null
  }, over || {});
}

function dataFor(over, extra) {
  const d = {
    playoffs: { matches: [gfRow(over)] },
    schedule: [],
    games: [],
    matches: [],
    players: [],
    standings: [],
    team_season: []
  };
  return Object.assign(d, extra || {});
}

/* --- 1. target comes from series_format, never a literal 4 --- */
{
  const { cpTarget } = build(dataFor());
  eq(cpTarget('Bo7'), 4, 'Bo7 -> 4 wins');
  eq(cpTarget('Bo5'), 3, 'Bo5 -> 3 wins');
  eq(cpTarget('bo3'), 2, 'Bo3 -> 2 wins (case-insensitive)');
  eq(cpTarget(null), 4, 'missing format falls back to a Bo7 final');
  eq(cpTarget(''), 4, 'empty format falls back to a Bo7 final');
}

/* --- 2. a completed 4-2 with game rows: champion, score, trace, clinch --- */
{
  const games = ['team_a','team_b','team_a','team_a','team_b','team_a'].map((w, i) => ({
    match_detail_id: 'gf1', game_no: i + 1, team_a: 'TLID', team_b: 'NAVI', winner: w
  }));
  const d = dataFor({ match_a: null, score_a: 4, score_b: 2, status: 'completed', match_detail_id: 'gf1' },
                    { games });
  const sf = build(d).seasonFinal();
  eq(sf.done, true, '4-2 completed declares a champion');
  eq(sf.champion, 'TLID', 'champion is team_a');
  eq(sf.runnerUp, 'NAVI', 'runner-up is team_b');
  eq(sf.scoreKnown, true, 'score is known at the target');
  eq(sf.champScore, 4, 'champion score oriented first');
  eq(sf.oppScore, 2, 'opponent score oriented second');
  eq(sf.trace.length, 6, 'trace carries every game');
  eq(sf.clinch, 6, 'clinch game is the fourth win');
  eq(sf.trace.filter(t => t.won).length, 4, 'trace marks exactly four wins');
}

/* --- 3. a sweep: clinch in game 4 --- */
{
  const games = [1,2,3,4].map(i => ({ match_detail_id: 'gf2', game_no: i, team_a: 'TLID', team_b: 'NAVI', winner: 'team_a' }));
  const sf = build(dataFor({ score_a: 4, score_b: 0, status: 'completed', match_detail_id: 'gf2' }, { games })).seasonFinal();
  eq(sf.done, true, '4-0 declares a champion');
  eq(sf.clinch, 4, '4-0 clinches in game 4');
}

/* --- 4. a seven-game final: clinch in game 7 --- */
{
  const games = ['team_b','team_a','team_a','team_b','team_a','team_b','team_a']
    .map((w, i) => ({ match_detail_id: 'gf3', game_no: i + 1, team_a: 'TLID', team_b: 'NAVI', winner: w }));
  const sf = build(dataFor({ score_a: 4, score_b: 3, status: 'completed', match_detail_id: 'gf3' }, { games })).seasonFinal();
  eq(sf.done, true, '4-3 declares a champion');
  eq(sf.clinch, 7, '4-3 clinches in game 7');
}

/* --- 5. refused: a 3-3 "completed" series is not a championship --- */
{
  const sf = build(dataFor({ score_a: 3, score_b: 3, status: 'completed' })).seasonFinal();
  eq(sf.done, false, '3-3 never renders a champion');
  eq(sf.champion, '', 'no champion is named at 3-3');
}

/* --- 6. refused: a 4-4 anomaly is not a championship --- */
{
  const sf = build(dataFor({ score_a: 4, score_b: 4, status: 'completed' })).seasonFinal();
  eq(sf.done, false, '4-4 never renders a champion');
  eq(sf.scoreKnown, false, '4-4 has no trustworthy score');
}

/* --- 7. refused: a TBD side is not a team --- */
{
  const sf = build(dataFor({ team_b: 'TBD', score_a: 4, score_b: 0, status: 'completed' })).seasonFinal();
  eq(sf.done, false, 'TBD opponent never renders a champion');
}

/* --- 8. missing grand final: no season-final state at all --- */
{
  const d = dataFor();
  d.playoffs.matches = [{ round: 'Upper Bracket Finals', team_a: 'TLID', team_b: 'NAVI' }];
  eq(build(d).seasonFinal(), null, 'no grand-final row -> null');
}

/* --- 9. winner recorded without a valid score --- */
{
  const sf = build(dataFor({ status: 'completed', winner: 'TLID' })).seasonFinal();
  eq(sf.done, true, 'an explicit winner still ends the season');
  eq(sf.scoreKnown, false, 'a missing score is not fabricated');
  eq(sf.trace.length, 0, 'no trace without a score');
  eq(sf.clinch, null, 'no clinch line without a score');
}

/* --- 10. orientation: the champion can be team_b --- */
{
  const sf = build(dataFor({ score_a: 1, score_b: 4, status: 'completed', winner: 'NAVI' })).seasonFinal();
  eq(sf.champion, 'NAVI', 'team_b can be champion');
  eq(sf.runnerUp, 'TLID', 'runner-up is the other side');
  eq(sf.champScore, 4, 'champion score still reads first');
  eq(sf.oppScore, 1, 'opponent score still reads second');
}

/* --- 11. Bo5 target of 3 --- */
{
  const sf = build(dataFor({ score_a: 3, score_b: 1, status: 'completed', series_format: 'Bo5' })).seasonFinal();
  eq(sf.done, true, 'Bo5 declares a champion at three wins');
  eq(sf.scoreKnown, true, 'Bo5 score is known');
}

/* --- 12. trace withheld when the game set does not match the score --- */
{
  const games = [1,2,3].map(i => ({ match_detail_id: 'gf4', game_no: i, winner: 'team_a' }));
  const sf = build(dataFor({ score_a: 4, score_b: 2, status: 'completed', match_detail_id: 'gf4' }, { games })).seasonFinal();
  eq(sf.done, true, 'a short game set still declares the champion');
  eq(sf.trace.length, 0, 'a short game set withholds the trace');
  eq(sf.clinch, null, 'a short game set withholds the clinch line');
}

/* --- 13. trace withheld when a game has no winner --- */
{
  const games = [
    { match_detail_id: 'gf5', game_no: 1, team_a: 'TLID', team_b: 'NAVI', winner: 'team_a' },
    { match_detail_id: 'gf5', game_no: 2, team_a: 'TLID', team_b: 'NAVI', winner: '' }
  ];
  const sf = build(dataFor({ score_a: 4, score_b: 2, status: 'completed', match_detail_id: 'gf5' }, { games })).seasonFinal();
  eq(sf.trace.length, 0, 'an undecided game withholds the trace');
}

/* --- 15. orientation: a detail row stored in the opposite team order --- */
{
  /* Real Grand Final (detail 1115): the bracket lists NAVI 3-4 BTR, while
     the detail match stores BTR 4-3 NAVI and every game swaps order. */
  const gf = { match_id: 'id-playoffs-7', round: 'Grand Finals', team_a: 'NAVI',
               team_b: 'BTR', score_a: 3, score_b: 4, status: 'completed',
               winner: 'team_b', series_format: null, match_detail_id: '1115' };
  const detail = { match_detail_id: '1115', team_a: 'BTR', team_b: 'NAVI',
                   score_a: 4, score_b: 3, status: 'completed', winner: 'team_a' };
  const games = [
    { match_detail_id: '1115', game_no: 1, team_a: 'BTR', team_b: 'NAVI', winner: 'team_a' },
    { match_detail_id: '1115', game_no: 2, team_a: 'NAVI', team_b: 'BTR', winner: 'team_a' },
    { match_detail_id: '1115', game_no: 3, team_a: 'BTR', team_b: 'NAVI', winner: 'team_a' },
    { match_detail_id: '1115', game_no: 4, team_a: 'NAVI', team_b: 'BTR', winner: 'team_a' },
    { match_detail_id: '1115', game_no: 5, team_a: 'BTR', team_b: 'NAVI', winner: 'team_b' },
    { match_detail_id: '1115', game_no: 6, team_a: 'BTR', team_b: 'NAVI', winner: 'team_a' },
    { match_detail_id: '1115', game_no: 7, team_a: 'NAVI', team_b: 'BTR', winner: 'team_b' }
  ];
  const d = {
    playoffs: { matches: [gf] }, schedule: [], matches: [detail], games,
    players: [], standings: [], team_season: []
  };
  const sf = build(d).seasonFinal();
  eq(sf.done, true, 'flipped detail still ends the season');
  eq(sf.champion, 'BTR', 'champion follows the bracket side, not detail order');
  eq(sf.runnerUp, 'NAVI', 'runner-up is the bracket team_a');
  eq(sf.champScore, 4, 'champion score is mapped onto the bracket order');
  eq(sf.oppScore, 3, 'opponent score is mapped onto the bracket order');
  eq(sf.trace.length, 7, 'every game appears in the trace');
  eq(sf.trace.filter(t => t.won).length, 4, 'game winners follow each game team order');
  eq(sf.clinch, 7, 'the clinching game is the seventh');
}

/* --- 16. roster: distinct players, most-played first, never invented --- */
{
  const players = [
    { team: 'TLID', player: 'Lyoni', lane: 'MID' }, { team: 'TLID', player: 'Lyoni', lane: 'MID' },
    { team: 'TLID', player: 'Kevinn', lane: 'JUNGLE' }, { team: 'TLID', player: 'Kevinn', lane: 'JUNGLE' },
    { team: 'TLID', player: 'Kevinn', lane: 'JUNGLE' },
    { team: 'TLID', player: 'Aran', lane: 'EXP' },
    { team: 'NAVI', player: 'Zeonn', lane: 'MID' }
  ];
  const roster = build(dataFor({}, { players })).teamRoster('TLID');
  eq(roster.length, 3, 'roster holds each player once');
  eq(roster[0].player, 'Aran', 'lane order puts EXP first');
  eq(roster[1].player, 'Kevinn', 'JUNGLE follows EXP');
  eq(roster[2].player, 'Lyoni', 'MID follows JUNGLE');
  eq(roster[1].gp, 3, 'appearance count is preserved');
  ok(roster.every(p => p.team === undefined && p.player !== 'Zeonn'), 'the other club is never in the roster');
}

/* --- 15. determinism: the same data yields the same answer --- */
{
  const d = dataFor({ score_a: 4, score_b: 2, status: 'completed' });
  const a = build(d).seasonFinal(), b = build(d).seasonFinal();
  eq(JSON.stringify(a), JSON.stringify(b), 'derivation is deterministic');
}

console.log();
if (fails) {
  console.log('FAIL season-final: ' + fails + '/' + count + ' assertions failed');
  process.exit(1);
}
console.log('PASS season-final: ' + count + ' assertions');
