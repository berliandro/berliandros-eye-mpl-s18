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
const m = src.match(/\/\* CHANCES-START \*\/([\s\S]*?)\/\* CHANCES-END \*\//);
if (!m) { console.error('FAIL CHANCES markers missing'); process.exit(1); }
const NS = new Function(m[1] + '; return {calcChances, normalizeFixtures, normTeam, isPORow};')();
const { calcChances, normalizeFixtures } = NS;

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
  eq(r.diag.sweepP, 2 / 3, 'W sweepP calibrated 2/3');
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

console.log('\n' + (count - fails) + '/' + count + ' passed, ' + fails + ' failed');
process.exit(fails ? 1 : 0);
