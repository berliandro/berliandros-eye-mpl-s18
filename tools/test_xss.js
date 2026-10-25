/* XSS sink unit tests: the esc() HTML-escaper from tools/templates/app.js.
   Browser exploit-path coverage lives in tools/test_xss.py (Playwright,
   local-only like shots.py — it needs system Chrome, so it is intentionally
   NOT part of verify.py/CI). Usage: node tools/test_xss.js (exit 0 = pass). */
'use strict';
const fs = require('fs');
const path = require('path');
const src = fs.readFileSync(path.join(__dirname, 'templates', 'app.js'), 'utf8');
const m = src.match(/^const esc=.*$/m);
if (!m) { console.error('FAIL esc not found'); process.exit(1); }
const esc = new Function(m[0] + '; return esc;')();

let fails = 0, count = 0;
function ok(cond, msg) {
  count++;
  console.log((cond ? 'PASS ' : 'FAIL ') + msg);
  if (!cond) fails++;
}

ok(esc('<img src=x onerror=alert(1)>') === '&lt;img src=x onerror=alert(1)&gt;', 'X1 angle brackets escaped');
ok(esc('a"b&c<d>e') === 'a&quot;b&amp;c&lt;d&gt;e', 'X1 quotes/ampersands escaped');
ok(esc('"><svg onload=alert(1)>') === '&quot;&gt;&lt;svg onload=alert(1)&gt;', 'X1 attribute-breakout neutralized');
ok(esc('plain text 123') === 'plain text 123', 'X1 benign text untouched');
ok(esc(9) === '9' && esc(0) === '0', 'X1 numbers render identically');
ok(esc(null) === '' && esc(undefined) === '', 'X1 nullish renders empty');
ok(esc('65%') === '65%', 'X1 percent strings untouched');
// esc() is the mechanism every external string sink must use: spot-check that
// each reviewed sink site in app.js actually routes through it.
const sinks = [
  ['initials fallback', /\$\{esc\(init\)\}/],
  ['item data-eq', /data-eq="\$\{esc\(o\.eq\|\|''\)\}"/],
  ['standings cells', /\$\{esc\(s\.match_point\)\}/],
  ['match scores', /\$\{esc\(m\.score_a\?\?/],
  ['game-row KDA', /\$\{esc\(k\)\}\/\$\{esc\(d\)\}\/\$\{esc\(a\)\}/],
  ['scoreboard KDA', /\$\{esc\(r\.kills\)\}\/\$\{esc\(r\.deaths\)\}\/\$\{esc\(r\.assists\)\}/],
  ['game tabs', /data-gtab="\$\{esc\(String\(g\.game_no\)\)\}"/],
  ['team kills', /\$\{esc\(g\.team_a_kills\)\}/],
  ['hero counts', /\$\{esc\(h\.pick\)\}/],
];
sinks.forEach(([name, re]) => ok(re.test(src), 'X2 sink hardened: ' + name));
// Two sites contain '??' which is regex-hostile; verify them with exact
// substring checks (String.includes handles them deterministically).
ok(src.includes("${esc(m.score_a??'')}") && src.includes("${esc(m.score_b??'')}"),
  'X2 sink hardened: history scores');
ok(src.includes("<b>${esc(sc??'')}</b>"), 'X2 sink hardened: bracket scores');
ok(src.includes('<span class="k">${esc(kills)} kills</span>'), 'X2 sink hardened: scoreboard kills header');
ok(src.includes('data-gtab="${esc(String(g.game))}"'), 'X2 sink hardened: live game tabs');
ok(src.includes('<span class="k">${esc(kills)} kills</span>'), 'X2 sink hardened: scoreboard kills header');

console.log('\n' + (count - fails) + '/' + count + ' passed, ' + fails + ' failed');
process.exit(fails ? 1 : 0);
