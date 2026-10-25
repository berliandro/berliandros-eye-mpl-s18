/* Independent tests for the playoff-chance engine (calcChances +
   normalizeFixtures in tools/templates/app.js, between CHANCES-START/END).
   No DOM, no UI. Covers: guarantees (100/0), partial chances, tied points,
   diff and H2H tiebreakers, uneven remaining counts, no-remaining exactness,
   UB<=PC, aggregate 600/200 invariants, invalid data, determinism, MC-vs-exact
   agreement, and hand-computed tiny leagues with known answers.
   Usage: node tools/test_chances.js (exit 0 = pass). */
'use strict';
const fs = require('fs');
const path = require('path');
const src = fs.readFileSync(path.join(__dirname, 'templates', 'app.js'), 'utf8');
const SEASON = JSON.parse(fs.readFileSync(path.join(__dirname, '..', 'data', 'season.json'), 'utf8'));
const m = src.match(/\/\* CHANCES-START \*\/([\s\S]*?)\/\* CHANCES-END \*\//);
if (!m) { console.error('FAIL CHANCES markers missing'); process.exit(1); }
const NS = new Function('SEASON', m[1] + '; return {calcChances, normalizeFixtures, normTeam, isPORow, rankTeams, wilson};')(SEASON);
const { calcChances, normalizeFixtures, rankTeams, wilson } = NS;

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
// standings row helper: key, pts, won, lost, diff
const T = (key, pts, w, l, d) => ({ key, pts, won: w, lost: l, diff: d });
const FX = (a, b) => ({ a, b, decided: false });
const DX = (a, b, winner, sweep) => ({ a, b, decided: true, winner, sweep });
const pc = (r, k) => r.chances[k].pc.v;
const ub = (r, k) => r.chances[k].ub.v;

// --- E1: coin flip, hand-computed 50/50 (1 slot, 1 fixture, even odds) ---
{
  const st = [T('x', 5, 3, 3, 0), T('y', 5, 3, 3, 0)];
  const fx = [FX('x', 'y')];
  const o = { totalSeries: 7, playoffSlots: 1, upperSlots: 1, winProb: 'even', sweepP: 0.5, exact: true };
  const r = calcChances(st, fx, o);
  eq(pc(r, 'x'), 50, 'E1 X playoff 50');
  eq(pc(r, 'y'), 50, 'E1 Y playoff 50');
  eq(ub(r, 'x'), 50, 'E1 X upper 50');
  eq(ub(r, 'y'), 50, 'E1 Y upper 50');
  close(pc(r, 'x') + pc(r, 'y'), 100, 1e-9, 'E1 playoff sum 100');
  close(ub(r, 'x') + ub(r, 'y'), 100, 1e-9, 'E1 upper sum 100');
}

// --- E2: game diff decides a 3-way tie (hand-computed X=100, Y=50, Z=50) ---
{
  const st = [T('x', 5, 5, 0, 10), T('y', 5, 5, 0, -10), T('z', 4, 4, 1, 0), T('w', 0, 0, 5, -20)];
  const fx = [FX('z', 'w')];
  const o = { totalSeries: 6, playoffSlots: 2, upperSlots: 1, winProb: 'even', sweepP: 0.5, exact: true };
  const r = calcChances(st, fx, o);
  eq(pc(r, 'x'), 100, 'E2 X playoff 100 (diff lock)');
  eq(pc(r, 'y'), 50, 'E2 Y playoff 50');
  eq(pc(r, 'z'), 50, 'E2 Z playoff 50');
  eq(pc(r, 'w'), 0, 'E2 W playoff 0');
  eq(ub(r, 'x'), 100, 'E2 X upper 100');
  eq(ub(r, 'y'), 0, 'E2 Y upper 0');
  eq(ub(r, 'z'), 0, 'E2 Z upper 0');
  close(pc(r, 'x') + pc(r, 'y') + pc(r, 'z') + pc(r, 'w'), 200, 1e-9, 'E2 playoff sum 200');
}

// --- E3: H2H beats slug order (zzz beat aaa; correct: zzz 100, aaa 0) ---
{
  const st = [T('aaa', 5, 5, 1, 0), T('zzz', 5, 5, 1, 0)];
  const fx = [DX('aaa', 'zzz', 'b', true)]; // decided: zzz won
  const o = { totalSeries: 6, playoffSlots: 1, upperSlots: 1, winProb: 'even', sweepP: 0.5, trials: 500, seed: 7 };
  const r = calcChances(st, fx, o); // MC path, zero remaining -> deterministic
  eq(pc(r, 'zzz'), 100, 'E3 zzz playoff 100 via H2H');
  eq(pc(r, 'aaa'), 0, 'E3 aaa playoff 0 via H2H');
  eq(ub(r, 'zzz'), 100, 'E3 zzz upper 100 via H2H');
}

// --- E6: uneven remaining counts (A idle on bubble: 100/50/50, UB 100/50/50) ---
{
  const st = [T('a', 6, 6, 0, 5), T('b', 5, 5, 1, 0), T('c', 4, 4, 2, 0)];
  const fx = [FX('b', 'c')];
  const o = { totalSeries: 7, playoffSlots: 2, upperSlots: 1, winProb: 'even', sweepP: 0.5, exact: true };
  const r = calcChances(st, fx, o);
  eq(pc(r, 'a'), 100, 'E6 A playoff 100');
  eq(pc(r, 'b'), 50, 'E6 B playoff 50');
  eq(pc(r, 'c'), 50, 'E6 C playoff 50');
  eq(ub(r, 'a'), 100, 'E6 A upper 100');
  eq(ub(r, 'b'), 0, 'E6 B upper 0 (A tops both branches on diff)');
  eq(ub(r, 'c'), 0, 'E6 C upper 0 (A tops both branches on diff)');
}

// --- Guarantees: clinched top2, eliminated bottom ---
{
  const st = [T('a', 12, 12, 0, 20), T('b', 11, 11, 1, 15), T('c', 6, 6, 6, 0),
              T('d', 6, 6, 6, -2), T('e', 5, 5, 7, -5), T('f', 1, 1, 11, -20)];
  const fx = [FX('c', 'd'), FX('e', 'f')];
  const o = { totalSeries: 14, playoffSlots: 3, upperSlots: 2, trials: 1000, seed: 0x51ab };
  const r = calcChances(st, fx, o);
  eq(pc(r, 'a'), 100, 'G A clinched playoffs');
  eq(ub(r, 'a'), 100, 'G A clinched upper');
  eq(ub(r, 'b'), 100, 'G B clinched upper');
  eq(pc(r, 'f'), 0, 'G F eliminated playoffs');
  eq(ub(r, 'f'), 0, 'G F eliminated upper');
  ok(pc(r, 'c') > 0 && pc(r, 'c') < 100, 'G C partial playoff (' + pc(r, 'c') + ')');
  ok(ub(r, 'c') <= pc(r, 'c'), 'G C UB<=PC');
}

// --- No remaining: exact 0/100 from the table (diff + H2H order) ---
{
  const st = [T('a', 9, 9, 2, 11), T('b', 9, 9, 3, 11), T('c', 2, 2, 9, -11)];
  const o = { totalSeries: 16, playoffSlots: 2, upperSlots: 1, trials: 500, seed: 3 };
  const r = calcChances(st, [], o);
  eq(pc(r, 'a'), 100, 'N A in');
  eq(pc(r, 'b'), 100, 'N B in');
  eq(pc(r, 'c'), 0, 'N C out');
  eq(ub(r, 'a'), 100, 'N A top1 (key fallback over b, documented)');
}

// --- Realistic 9-team replica: invariants, bounds, determinism ---
function snapshot9() {
  return {
    st: [T('navi', 9, 9, 2, 11), T('tlid', 9, 9, 3, 11), T('ae', 8, 8, 4, 9),
         T('btr', 7, 7, 5, 0), T('evos', 5, 5, 5, -1), T('dewa', 5, 5, 6, -4),
         T('onic', 4, 4, 7, -2), T('rrq', 2, 2, 9, -11), T('geek', 2, 2, 10, -13)],
    fx: [FX('ae', 'tlid'), FX('rrq', 'evos'), FX('onic', 'navi'), FX('evos', 'dewa'),
         FX('ae', 'btr'), FX('navi', 'tlid'), FX('evos', 'onic'), FX('rrq', 'tlid'),
         FX('dewa', 'navi'), FX('evos', 'geek'), FX('rrq', 'onic'), FX('dewa', 'btr'),
         FX('navi', 'rrq'), FX('geek', 'ae'), FX('onic', 'dewa'), FX('btr', 'evos'),
         FX('rrq', 'geek'), FX('evos', 'ae'), FX('navi', 'btr'), FX('onic', 'tlid'),
         FX('geek', 'dewa')]
  };
}
{
  const { st, fx } = snapshot9();
  const o = { totalSeries: 16, playoffSlots: 6, upperSlots: 2, trials: 2000, seed: 0x51ab };
  const r1 = calcChances(st, fx, o);
  const r2 = calcChances(st, fx, o);
  let sPC = 0, sUB = 0;
  st.forEach(t => {
    const a = pc(r1, t.key), b = ub(r1, t.key);
    sPC += a; sUB += b;
    ok(a >= 0 && a <= 100, 'S ' + t.key + ' PC in range (' + a.toFixed(2) + ')');
    ok(b >= 0 && b <= 100, 'S ' + t.key + ' UB in range (' + b.toFixed(2) + ')');
    ok(b <= a + 1e-9, 'S ' + t.key + ' UB<=PC');
    eq(a, pc(r2, t.key), 'S ' + t.key + ' deterministic PC');
    eq(b, ub(r2, t.key), 'S ' + t.key + ' deterministic UB');
  });
  close(sPC, 600, 1e-6, 'S playoff sum 600');
  close(sUB, 200, 1e-6, 'S upper sum 200');
  console.log('INFO snapshot chances: ' + st.map(t =>
    t.key + '=' + pc(r1, t.key).toFixed(1) + '/' + ub(r1, t.key).toFixed(1)).join(' '));
  console.log('INFO sweepP=' + r1.diag.sweepP + ' maxSplitErr=' + r1.diag.maxSplitErr.toFixed(2) + 'pp');
  ok(isFinite(r1.diag.maxSplitErr) && r1.diag.maxSplitErr < 10, 'S converged (split err < 10pp)');
}

// --- MC vs exact agreement on a small league ---
{
  const st = [T('a', 3, 3, 0, 0), T('b', 3, 3, 0, 0), T('c', 2, 2, 1, 0), T('d', 2, 2, 1, 0)];
  const fx = [FX('a', 'b'), FX('c', 'd')];
  const base = { totalSeries: 4, playoffSlots: 2, upperSlots: 1, winProb: 'even', sweepP: 0.5 };
  const e = calcChances(st, fx, Object.assign({ exact: true }, base));
  const m = calcChances(st, fx, Object.assign({ trials: 20000, seed: 0x51ab }, base));
  st.forEach(t => {
    close(pc(m, t.key), pc(e, t.key), 2.5, 'X ' + t.key + ' MC~=exact PC');
    close(ub(m, t.key), ub(e, t.key), 2.5, 'X ' + t.key + ' MC~=exact UB');
  });
  let s = 0; st.forEach(t => { s += pc(e, t.key); });
  close(s, 200, 1e-9, 'X exact playoff sum 200');
}

// --- Exact/MC cross-check of hard 100/0 on random small leagues ---
{
  let seed = 12345;
  const rnd = () => (seed = (seed + 0x6D2B79F5) | 0, ((seed ^ (seed >>> 15)) >>> 0) / 4294967296);
  let checked100 = 0, checked0 = 0;
  for (let L = 0; L < 15; L++) {
    const names = ['a', 'b', 'c', 'd', 'e'];
    const st = names.map((k, i) => {
      const p = Math.floor(rnd() * 7), w = Math.floor(rnd() * (p + 1)), l = p - w;
      return T(k, 2 + p, w, l, Math.floor(rnd() * 21) - 10);
    });
    st.sort((x, y) => (y.pts - x.pts) || (y.diff - x.diff));
    const fx = [];
    for (let i = 0; i < 3; i++) {
      const a = names[Math.floor(rnd() * 5)];
      let b = names[Math.floor(rnd() * 5)];
      if (a === b) continue;
      fx.push(FX(a, b));
    }
    const o = { totalSeries: 12, playoffSlots: 3, upperSlots: 1, trials: 1500, seed: 9 };
    const mres = calcChances(st, fx, o);
    const eres = calcChances(st, fx, Object.assign({}, o, { exact: true, trials: undefined }));
    st.forEach(t => {
      if (mres.chances[t.key].pc.v === 100) { checked100++; close(eres.chances[t.key].pc.v, 100, 1e-6, 'F league' + L + ' ' + t.key + ' exact confirms PC 100'); }
      if (mres.chances[t.key].pc.v === 0) { checked0++; close(eres.chances[t.key].pc.v, 0, 1e-6, 'F league' + L + ' ' + t.key + ' exact confirms PC 0'); }
      if (mres.chances[t.key].ub.v === 100) { checked100++; close(eres.chances[t.key].ub.v, 100, 1e-6, 'F league' + L + ' ' + t.key + ' exact confirms UB 100'); }
      if (mres.chances[t.key].ub.v === 0) { checked0++; close(eres.chances[t.key].ub.v, 0, 1e-6, 'F league' + L + ' ' + t.key + ' exact confirms UB 0'); }
    });
  }
  console.log('INFO fuzz hard-limit cross-checks: ' + checked100 + 'x100, ' + checked0 + 'x0');
  ok(checked100 > 0 && checked0 > 0, 'F fuzz hit both 100 and 0 cases');
}

// --- Invalid / incomplete data: no throw, logged, survivors still valid ---
{
  const st = [T('a', 5, 5, 0, 3), T('b', 4, 4, 1, 0), { key: 'c' }, T('a', 9, 9, 9, 9)];
  const fx = [FX('a', 'b'), FX('a', 'zzz'), FX('a', 'a'), DX('a', 'b', 'c', 'x')];
  const o = { totalSeries: 6, playoffSlots: 1, upperSlots: 1, trials: 300, seed: 5 };
  let r = null, threw = false;
  try { r = calcChances(st, fx, o); } catch (e) { threw = true; }
  ok(!threw, 'V no throw on invalid data');
  ok(r && r.diag.invalid.length >= 3, 'V invalid rows logged (' + (r ? r.diag.invalid.length : 0) + ')');
  if (r) {
    ok(isFinite(pc(r, 'a')) && isFinite(pc(r, 'b')), 'V survivors have finite chances');
    close(pc(r, 'a') + pc(r, 'b') + pc(r, 'c'), 100, 1e-6, 'V playoff sum still 100');
  }
  const e2 = calcChances([T('solo', 3, 9, 9, 0)], [], { totalSeries: 4, playoffSlots: 1, upperSlots: 1 });
  ok(e2.diag.invalid.length > 0, 'V played-over flagged');
}

// --- Sweep calibration ---
{
  const st = [T('a', 1, 1, 0, 0), T('b', 0, 0, 1, 0)];
  const fx = [DX('a', 'b', 'a', true), DX('a', 'b', 'a', true), DX('a', 'b', 'a', false)];
  const r = calcChances(st, fx, { totalSeries: 4, playoffSlots: 1, upperSlots: 1, exact: true });
  eq(r.diag.sweepP, 4 / 7, 'W sweepP Beta(2,2)-smoothed (2+2)/(3+4)');
  const r2 = calcChances(st, [], { totalSeries: 4, playoffSlots: 1, upperSlots: 1 });
  eq(r2.diag.sweepP, 0.5, 'W sweepP default 0.5 without data');
}

// --- Strength model: same points, different win rates ---
{
  const st = [T('s', 5, 8, 2, 0), T('w', 5, 2, 8, 0)];
  const fx = [FX('s', 'w')];
  const base = { totalSeries: 11, playoffSlots: 1, upperSlots: 1, sweepP: 0.5, trials: 4000, seed: 11 };
  const meven = calcChances(st, fx, Object.assign({ winProb: 'even' }, base));
  const mstr = calcChances(st, fx, Object.assign({ winProb: 'bradley-terry' }, base));
  close(pc(meven, 's'), 50, 2.5, 'M even odds ~50/50');
  ok(pc(mstr, 's') > 70 && pc(mstr, 's') < 92, 'M BT favours 8-2 over 2-8 (' + pc(mstr, 's').toFixed(1) + ')');
}

// --- normalizeFixtures: live-decisive excluded, upcoming kept once, cap ---
{
  const sched = [
    { schedule_id: 'c1', team_a: 'NAVI', team_b: 'AE', score_a: 2, score_b: 0, status: 'completed', winner: 'team_a' },
    { schedule_id: 'live-dec', team_a: 'AE', team_b: 'NAVI', score_a: 1, score_b: 2, status: 'live', winner: '' },
    { schedule_id: 'live-mid', team_a: 'GEEK', team_b: 'DEWA', score_a: 1, score_b: 1, status: 'live', winner: '' },
    { schedule_id: 'up1', team_a: 'AE', team_b: 'TLID', score_a: '', score_b: '', status: 'upcoming', winner: '' },
    { schedule_id: 'po1', team_a: 'TBD', team_b: 'TBD', score_a: '', score_b: '', status: 'upcoming', winner: '' },
    { schedule_id: 'po2', team_a: 'X', team_b: 'Y', score_a: '', score_b: '', status: 'upcoming', winner: '' },
    { schedule_id: 'bad', team_a: 'AE', team_b: 'ZZZ', score_a: '', score_b: '', status: 'upcoming', winner: '' }
  ];
  sched[5].schedule_id = 'id-playoffs-0';
  const known = { navi: 1, ae: 1, geek: 1, dewa: 1, tlid: 1 };
  const played = { navi: 11, ae: 12, geek: 12, dewa: 11, tlid: 12 };
  const nf = normalizeFixtures(sched, known, played, 16);
  const rem = nf.fixtures.filter(f => !f.decided);
  eq(rem.length, 2, 'R two remaining (live-mid + up1)');
  ok(nf.fixtures.some(f => f.decided && f.id === 'live-dec' && f.winner === 'b'), 'R live-decisive treated decided (navi)');
  eq(nf.decidedLive, 1, 'R decidedLive counted');
  ok(!nf.fixtures.some(f => f.id === 'po1' || f.id === 'id-playoffs-0' || f.id === 'bad'), 'R playoffs/unknown dropped');
  // every upcoming exactly once
  const ids = nf.fixtures.map(f => f.id);
  eq(new Set(ids).size, ids.length, 'R no duplicated fixtures');
}

// --- Rounding vs certainty: raw nonzero rounds to displayed 0% ---
{
  // A wins its only remaining fixture with q = 20/5000 = 0.4% (rigged but
  // legal records: 20-4980 vs 4980-20). Exact mode gives raw 0.4 -> displays 0.
  const st = [T('a', 5, 20, 4980, 0), T('b', 5, 4980, 20, 0), T('c', 9, 9, 0, 0)];
  const fx = [FX('a', 'b')];
  const o = { totalSeries: 5001, playoffSlots: 2, upperSlots: 1, sweepP: 0.5, exact: true };
  const r = calcChances(st, fx, o);
  const raw = pc(r, 'a');
  ok(raw > 0 && raw < 0.5, 'D1 raw PC in (0, 0.5): ' + raw);
  eq(Math.round(raw), 0, 'D1 displayed PC rounds to 0');
  // smoothed q(A) = (22/5004)/((22+4982)/5004) = 22/5004
  close(raw, 22 / 5004 * 100, 1e-9, 'D1 raw PC equals hand-computed Beta(2,2) value');
}

// --- Rounding vs certainty: raw below 100% rounds to displayed 100% ---
{
  // Mirror: A wins with q = 1 - 20/5000 = 99.6% -> displays 100, not guaranteed.
  const st = [T('a', 5, 4980, 20, 0), T('b', 5, 20, 4980, 0), T('c', 9, 9, 0, 0)];
  const fx = [FX('a', 'b')];
  const o = { totalSeries: 5001, playoffSlots: 2, upperSlots: 1, sweepP: 0.5, exact: true };
  const r = calcChances(st, fx, o);
  const raw = pc(r, 'a');
  ok(raw < 100 && raw > 99.5, 'D2 raw PC in (99.5, 100): ' + raw);
  eq(Math.round(raw), 100, 'D2 displayed PC rounds to 100');
  // smoothed q(A) = 1 - 22/5004
  close(raw, (1 - 22 / 5004) * 100, 1e-9, 'D2 raw PC equals hand-computed Beta(2,2) value');
}

// --- H2H mini-league (3-way, non-cyclic): A beat B and C -> A top ---
{
  const st = [T('a', 5, 5, 1, 0), T('b', 5, 5, 1, 0), T('c', 5, 5, 1, 0)];
  const fx = [DX('a', 'b', 'a', true), DX('a', 'c', 'a', false), DX('b', 'c', 'a', true)];
  const o = { totalSeries: 6, playoffSlots: 1, upperSlots: 1, trials: 400, seed: 21 };
  const r = calcChances(st, fx, o);
  eq(pc(r, 'a'), 100, 'H A tops H2H mini-league (2-0 in group)');
  eq(pc(r, 'b'), 0, 'H B out via mini-league');
  eq(pc(r, 'c'), 0, 'H C out via mini-league');
}

// --- rankTeams direct: points, then diff, then H2H, then key fallback ---
{
  const keys = ['m', 'n'];
  const P = { m: 5, n: 5 }, D = { m: 0, n: 0 };
  eq(rankTeams(keys, P, D, null, {})[0], 'm', 'K key fallback deterministic');
  eq(rankTeams(keys, P, D, [{ a: 'm', b: 'n', w: 'n' }], {})[0], 'n', 'K in-group sim H2H decides (n beat m)');
}

// --- Wilson 95% CI unit checks ---
{
  const [l0, h0] = wilson(0, 2000);
  eq(l0, 0, 'W zero-event lower bound 0');
  ok(h0 > 0 && h0 < 0.5, 'W zero-event upper bound small but nonzero (' + h0.toFixed(3) + ')');
  const [l1, h1] = wilson(2000, 2000);
  eq(h1, 100, 'W all-event upper bound 100');
  ok(l1 > 99.5 && l1 < 100, 'W all-event lower bound below 100 (' + l1.toFixed(3) + ')');
  const [lm, hm] = wilson(1000, 2000);
  ok(lm > 47 && lm < 48 && hm > 52 && hm < 53, 'W coin-flip CI ~[47.8,52.2]');
}

// --- Early-season smoothing: Beta(2,2) prior keeps estimates interior ---
{
  // S1: no completed series anywhere -> neutral 0.5 sweep baseline, even splits
  const st = [T('a', 0, 0, 0, 0), T('b', 0, 0, 0, 0), T('c', 0, 0, 0, 0), T('d', 0, 0, 0, 0)];
  const fx = [FX('a', 'b'), FX('c', 'd')];
  const o = { totalSeries: 1, playoffSlots: 2, upperSlots: 1, exact: true };
  const r = calcChances(st, fx, o);
  eq(r.diag.sweepP, 0.5, 'S1 sweepP neutral 0.5 with no data');
  eq(pc(r, 'a'), 50, 'S1 even split PC');
  close(pc(r, 'a') + pc(r, 'b') + pc(r, 'c') + pc(r, 'd'), 200, 1e-9, 'S1 PC sum 200');
  close(ub(r, 'a') + ub(r, 'b') + ub(r, 'c') + ub(r, 'd'), 100, 1e-9, 'S1 UB sum 100');
  const r2 = calcChances(st, fx, o);
  eq(pc(r2, 'a'), pc(r, 'a'), 'S1 deterministic');
}
{
  // S2: single decided series must not fixate the sweep estimate
  const st = [T('a', 1, 1, 0, 1), T('b', 0, 0, 1, -1)];
  const sw = calcChances(st, [DX('a', 'b', 'a', true)],
    { totalSeries: 2, playoffSlots: 1, upperSlots: 1, exact: true });
  close(sw.diag.sweepP, 3 / 5, 1e-12, 'S2 one 2-0 -> (1+2)/(1+4)=0.6, not 1.0');
  const dc = calcChances(st, [DX('a', 'b', 'a', false)],
    { totalSeries: 2, playoffSlots: 1, upperSlots: 1, exact: true });
  close(dc.diag.sweepP, 2 / 5, 1e-12, 'S2 one 2-1 -> (0+2)/(1+4)=0.4, not 0.0');
  // sweep estimate moves toward the data as samples accumulate
  const many = [];
  for (let i = 0; i < 10; i++) many.push(DX('a', 'b', 'a', true));
  const sw10 = calcChances(st, many, { totalSeries: 12, playoffSlots: 1, upperSlots: 1, exact: true });
  close(sw10.diag.sweepP, 12 / 14, 1e-12, 'S2 ten 2-0s -> 12/14, closer to 1.0 than 0.6');
}
{
  // S3: undefeated 5-0 vs winless 0-5 -> exact 7/9 vs 2/9 matchup, interior
  // smoothed: pa=(5+2)/9=7/9, pb=(0+2)/9=2/9, q=7/9. B qualifies (PC and UB)
  // iff B wins its fixture, so both are exactly 200/9 ~= 22.22%.
  const st = [T('a', 5, 5, 0, 5), T('b', 5, 0, 5, -5), T('c', 5, 5, 0, 0)];
  const r = calcChances(st, [FX('a', 'b')],
    { totalSeries: 6, playoffSlots: 2, upperSlots: 1, exact: true });
  close(pc(r, 'b'), 200 / 9, 1e-9, 'S3 winless team PC exactly 200/9, not 0');
  close(ub(r, 'b'), 200 / 9, 1e-9, 'S3 winless team UB exactly 200/9, not 0');
  ok(pc(r, 'b') > 0 && pc(r, 'b') < 100, 'S3 strictly interior');
}
{
  // S4: 0-0 vs 0-0 single fixture -> exact 50/50
  const st = [T('a', 0, 0, 0, 0), T('b', 0, 0, 0, 0)];
  const r = calcChances(st, [FX('a', 'b')],
    { totalSeries: 1, playoffSlots: 1, upperSlots: 1, exact: true });
  eq(pc(r, 'a'), 50, 'S4 blank records split 50/50');
  eq(pc(r, 'b'), 50, 'S4 blank records split 50/50');
}
{
  // S5: 1-0 vs 0-1 with a third team on 1pt; hand-computed PC(A) = 80%.
  // q(A) = (3/5)/((3/5)+(2/5)) = 0.6. A-wins branch: A (2pts) qualifies.
  // B-wins branch: A, B, C tie at 1pt. On a 2-1 decider all three share
  // diff 0 and the A-B sim H2H puts B first, A second (A qualifies); on a
  // 2-0 sweep B (+1) and C (0) both sit above A (-1), so A misses. With
  // sweepP 0.5 the branch splits 50/50. Total: 0.6 + 0.4*0.5 = 0.8.
  const st = [T('a', 1, 1, 0, 1), T('b', 0, 0, 1, -1), T('c', 1, 1, 0, 0)];
  const r = calcChances(st, [FX('a', 'b')],
    { totalSeries: 2, playoffSlots: 2, upperSlots: 1, sweepP: 0.5, exact: true });
  close(pc(r, 'a'), 80, 1e-9, 'S5 hand-computed PC(A)=80');
}
{
  // S6: four identical 2-2 records, symmetric fixtures -> 50 each
  const st = [T('a', 2, 2, 2, 0), T('b', 2, 2, 2, 0), T('c', 2, 2, 2, 0), T('d', 2, 2, 2, 0)];
  const r = calcChances(st, [FX('a', 'b'), FX('c', 'd')],
    { totalSeries: 5, playoffSlots: 2, upperSlots: 1, exact: true });
  ['a', 'b', 'c', 'd'].forEach(k => eq(pc(r, k), 50, 'S6 identical records PC=50 (' + k + ')'));
  close(ub(r, 'a') + ub(r, 'b') + ub(r, 'c') + ub(r, 'd'), 100, 1e-9, 'S6 UB sum 100');
}
{
  // S7: same observed rate (75%) with more data -> stronger estimate.
  // Synthetic leagues decouple table points (standings) from form records
  // (predictive signal): A is the bubble team in both. L1: A 3-1 vs B 2-2
  // gives q1 = (5/8)/(5/8+4/8) = 5/9. L2: A 6-2 vs B 4-4 gives
  // q2 = (8/12)/(8/12+6/12) = 4/7. A wins -> A takes the last slot;
  // B wins -> A misses, so PC(A) equals q exactly in both leagues.
  const mk = (aw, al, bw, bl, ts) => calcChances(
    [T('x', 9, 8, 0, 9), T('a', 2, aw, al, 0), T('b', 2, bw, bl, 0), T('d', 0, 0, 0, -9)],
    [FX('a', 'b')], { totalSeries: ts, playoffSlots: 2, upperSlots: 1, exact: true });
  const r1 = mk(3, 1, 2, 2, 5), r2 = mk(6, 2, 4, 4, 9);
  close(pc(r1, 'a'), 500 / 9, 1e-9, 'S7 small-sample PC hand value');
  close(pc(r2, 'a'), 400 / 7, 1e-9, 'S7 large-sample PC hand value');
  ok(pc(r2, 'a') > pc(r1, 'a'), 'S7 more data at same rate -> stronger estimate');
}

// --- Tooltip honesty: simulated entries carry counts + CI; proven stay proven ---
{
  const st = [T('lock', 12, 10, 0, 20), T('mid', 5, 5, 5, 0), T('chaser', 4, 4, 6, 0), T('out', 0, 2, 8, -20)];
  const fx = [FX('chaser', 'out')];
  const o = { totalSeries: 12, playoffSlots: 2, upperSlots: 1, trials: 500, seed: 0x51ab };
  const r = calcChances(st, fx, o);
  eq(r.chances.lock.pc.why, 'Clinched on points', 'Y lock tooltip claims proven certainty');
  eq(r.chances.out.pc.why, 'Eliminated on points', 'Y out tooltip claims proven impossibility');
  ok(/trials/.test(r.chances.mid.pc.why) && /CI/.test(r.chances.mid.pc.why),
    'Y mid tooltip shows counts + CI (' + r.chances.mid.pc.why + ')');
  ok(r.chances.mid.pc.q >= 0 && r.chances.mid.pc.n === 500, 'Y counts exposed (q/n)');
}

console.log('\n' + (count - fails) + '/' + count + ' passed, ' + fails + ' failed');
process.exit(fails ? 1 : 0);
