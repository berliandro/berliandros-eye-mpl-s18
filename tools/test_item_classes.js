/* Equipment-category classifier tests.
   The item breakdown used to be grouped by usage frequency (count > 2), which
   mixed completed items, footwear and components in one list. Grouping is now
   driven by data/item_classes.json - an explicit identity->category map - so a
   category can never change because an item happened to be built more often.

   Extracts itemClass/itemName/groupItemsByClass/itemGroups/assetRowsHTML from
   tools/templates/app.js by name and drives them with deterministic fixtures
   plus the committed mapping. No network. Usage: node tools/test_item_classes.js
   (exit 0 = pass). */
'use strict';
const fs = require('fs');
const path = require('path');

const ROOT = path.join(__dirname, '..');
const appSrc = fs.readFileSync(path.join(__dirname, 'templates', 'app.js'), 'utf8');
const doc = JSON.parse(fs.readFileSync(path.join(ROOT, 'data', 'global', 'item_classes.json'), 'utf8'));
const MAP = doc.items;

let fails = 0, count = 0;
function ok(cond, msg) {
  count++;
  console.log((cond ? 'PASS ' : 'FAIL ') + msg);
  if (!cond) fails++;
}
function eq(a, b, msg) {
  ok(JSON.stringify(a) === JSON.stringify(b), msg + ' (got ' + JSON.stringify(a) + ')');
}

// --- extract the helpers under test straight out of app.js ---
function grabFn(sig) {
  const start = appSrc.indexOf(sig);
  if (start < 0) { console.error('FAIL extract ' + sig); process.exit(1); }
  let i = appSrc.indexOf('{', start);
  let depth = 0, q = null, esc = false, lineC = false, blockC = false;
  for (; i < appSrc.length; i++) {
    const c = appSrc[i], n = appSrc[i + 1];
    if (lineC) { if (c === '\n') lineC = false; continue; }
    if (blockC) { if (c === '*' && n === '/') { blockC = false; i++; } continue; }
    if (q) {
      if (esc) esc = false;
      else if (c === '\\') esc = true;
      else if (c === q) q = null;
      else if (q === '`' && c === '$' && n === '{') { depth++; i++; }
      continue;
    }
    if (c === '/' && n === '/') { lineC = true; i++; continue; }
    if (c === '/' && n === '*') { blockC = true; i++; continue; }
    if (c === "'" || c === '"' || c === '`') { q = c; continue; }
    if (c === '{') depth++;
    else if (c === '}') { depth--; if (depth === 0) return appSrc.slice(start, i + 1); }
  }
  console.error('FAIL unbalanced ' + sig); process.exit(1);
}
const grabConst = (name) => {
  const m = appSrc.match(new RegExp('^const ' + name + '=.*$', 'm'));
  if (!m) { console.error('FAIL extract const ' + name); process.exit(1); }
  return m[0];
};

/* Only the pure classification/grouping logic is extracted from app.js. The
   chip renderers (itemCell/itemBtn/embBadge/talBadge) use nested template
   literals that a brace-matcher cannot tokenise, so deterministic stubs stand
   in for them - the assertions care about which id lands in which group and
   which label wraps it, not about icon markup. */
const STUBS = [
  'function itemCell(id,c){return `<i data-item="${esc(id)}">${esc(id)}</i>x${c}`;}',
  'function itemBtn(id,c,scope){return `<b data-item="${esc(id)}">${esc(id)}</b>x${c}`;}',
  'function embBadge(id,c){return `<u>e${esc(id)}</u>x${c}`;}',
  'function talBadge(id,c){return `<u>t${esc(id)}</u>x${c}`;}',
].join('\n');

/* assetRowsHTML nests template literals, which the quote-aware matcher above
   cannot tokenise. Raw brace counting is safe here because its template
   strings contain no literal braces, and the result is verified by compiling
   it - if the extraction is ever wrong the test fails loudly, it cannot
   silently pass against the wrong code. */
function grabFnBrace(sig) {
  const start = appSrc.indexOf(sig);
  if (start < 0) { console.error('FAIL extract ' + sig); process.exit(1); }
  let depth = 0;
  for (let i = appSrc.indexOf('{', start); i < appSrc.length; i++) {
    if (appSrc[i] === '{') depth++;
    else if (appSrc[i] === '}') { depth--; if (depth === 0) return appSrc.slice(start, i + 1); }
  }
  console.error('FAIL unbalanced ' + sig); process.exit(1);
}

const PRELUDE = [
  grabConst('esc'), STUBS,
  grabFn('function embIdOf(x)'), grabFn('function talIdsOf(x)'), grabFn('function itemIdsOf(x)'),
  grabFn('function heroUseCounts(list)'), grabFn('function topEntries(obj,n)'),
  grabFn('function itemClass(id)'), grabFn('function itemName(id)'),
  grabFn('function groupItemsByClass(counts)'), grabFn('function itemGroups(counts)'),
  grabFnBrace('function assetRowsHTML(u,scope)'),
].join('\n');

const NS = new Function('__W', '__ORDER',
  'const window={ITEM_CLASSES:__W,ASSETS:{}};\n'
  + PRELUDE + '\nconst ITEM_CLASSES=window.ITEM_CLASSES;\n'
  + 'const ITEM_CLS_ORDER=__ORDER;\n'
  + '; return {itemClass, itemName, groupItemsByClass, itemGroups, assetRowsHTML};');

/* Read the app's declared category order straight out of app.js so the test
   fails if the render order ever changes. The captured text is an array
   literal; it is evaluated rather than passed as a string. */
const CATEGORY_ORDER = new Function('return ' + appSrc
  .match(/^const ITEM_CLS_ORDER=(.*)$/m)[1].replace(/;$/, ''))();
const mkNS = (map) => NS(map || {}, CATEGORY_ORDER);
const A = mkNS(MAP);
const VALID = ['major', 'shoes', 'small'];

// --- C1: representative items land in the right category, from the real map ---
{
  const cases = [
    ['3004', 'major'], ['3105', 'major'], ['3203', 'major'], ['3210', 'major'],
    ['1301', 'shoes'], ['2301', 'shoes'], ['2302', 'shoes'], ['2306', 'shoes'],
    ['3462', 'shoes'], ['3561', 'shoes'],
    ['1001', 'small'], ['1201', 'small'], ['2008', 'small'], ['2201', 'small'],
  ];
  const wrong = cases.filter(([id, want]) => A.itemClass(id) !== want);
  eq(wrong, [], 'C1 representative completed/footwear/component items classified correctly');
}

// --- C2: base boots AND upgraded footwear are always Shoes ---
{
  // Every footwear family in the map - base boots (13xx/23xx) and every
  // upgraded variant (34xx/35xx) - must be Shoes.
  const notShoes = Object.keys(MAP).filter(id => MAP[id].cls === 'shoes')
    .filter(id => A.itemClass(id) !== 'shoes');
  eq(notShoes, [], 'C2 every footwear id in the map classifies as shoes');
  const shoeIds = Object.keys(MAP).filter(id => MAP[id].cls === 'shoes');
  const base = shoeIds.filter(id => /^13|^23/.test(id));
  const upgraded = shoeIds.filter(id => /^34|^35/.test(id));
  ok(base.length > 0 && base.every(id => A.itemClass(id) === 'shoes'),
    'C2 base boots (' + base.length + ') are shoes');
  ok(upgraded.length > 0 && upgraded.every(id => A.itemClass(id) === 'shoes'),
    'C2 upgraded footwear variants (' + upgraded.length + ') are shoes');
  ok(base.every(id => A.itemClass(id) === 'shoes') &&
     upgraded.every(id => A.itemClass(id) === 'shoes'),
    'C2 footwear never leaks into major or small');
}

// --- C3: usage count never changes an item's category ---
{
  const sample = ['3004', '2301', '3462', '1001', '2208'];
  let changed = null;
  sample.forEach(id => {
    const baseline = A.itemClass(id);
    [0, 1, 2, 3, 50, 999].forEach(c => {
      const g = A.groupItemsByClass({ [id]: c });
      const placed = ['major', 'shoes', 'small', 'unknown'].filter(k => g[k].length);
      if (placed.length !== 1 || placed[0] !== baseline) changed = id + '@' + c;
    });
  });
  eq(changed, null, 'C3 category is independent of usage count');
}

// --- C4: every observed item classified exactly once; no missing/duplicates ---
{
  const html = fs.readFileSync(path.join(ROOT, 'mpl_id_s18_dark.html'), 'utf8');
  const m = html.match(/const DATA = (\{.*?\});/s);
  ok(!!m, 'C4 built HTML exposes DATA');
  const DATA = JSON.parse(m[1]);
  const observed = new Set();
  DATA.players.forEach(p => (p.i || []).forEach(i => observed.add(i)));
  const missing = [...observed].filter(id => !MAP[id]);
  eq(missing, [], 'C4 every observed item has a mapping (' + observed.size + ' items)');
  const dupes = Object.entries(MAP).filter(([, v]) => !VALID.includes(v.cls));
  eq(dupes, [], 'C4 no mapping entry has an invalid category');
  const oneCategory = Object.values(MAP).every(v => VALID.includes(v.cls));
  ok(oneCategory, 'C4 each item holds exactly one valid category');
}

// --- C5: categorized usage counts sum to the original total ---
{
  const html = fs.readFileSync(path.join(ROOT, 'mpl_id_s18_dark.html'), 'utf8');
  const DATA = JSON.parse(html.match(/const DATA = (\{.*?\});/s)[1]);
  const counts = {};
  DATA.players.forEach(p => (p.i || []).forEach(i => { counts[i] = (counts[i] || 0) + 1; }));
  const g = A.groupItemsByClass(counts);
  const sum = ['major', 'shoes', 'small', 'unknown']
    .reduce((t, k) => t + g[k].reduce((s, e) => s + e[1], 0), 0);
  const total = Object.values(counts).reduce((a, b) => a + b, 0);
  eq(sum, total, 'C5 categorized usage counts sum to the original total');
  eq(g.unknown.length, 0, 'C5 nothing lands in unknown for committed data');
  const flat = ['major', 'shoes', 'small'].reduce((t, k) => t + g[k].length, 0);
  eq(flat, Object.keys(counts).length, 'C5 every item appears in exactly one category');
}

// --- C6: within-category ordering is deterministic and count-descending ---
{
  const counts = { '3004': 5, '3105': 5, '3210': 1, '2301': 9, '1001': 3, '2208': 3 };
  const run = () => A.groupItemsByClass(counts);
  const g = run();
  eq(g.major.map(e => e[0]), ['3004', '3105', '3210'],
    'C6 major sorted count-descending, id tie-break');
  eq(g.small.map(e => e[0]), ['1001', '2208'], 'C6 small sorted with id tie-break');
  eq(g.shoes.map(e => e[0]), ['2301'], 'C6 shoes sorted');
  const again = run();
  eq(JSON.stringify(again), JSON.stringify(g), 'C6 ordering is deterministic across runs');
  // A higher count must never demote an item's category.
  const boosted = A.groupItemsByClass({ '1001': 999, '3004': 1 });
  eq(boosted.small.map(e => e[0]), ['1001'], 'C6 most-used component stays small');
  eq(boosted.major.map(e => e[0]), ['3004'], 'C6 least-used completed item stays major');
}

// --- C7: empty categories are omitted, exact labels, groups stay separate ---
{
  const onlyShoes = A.itemGroups({ '2301': 4 });
  eq(onlyShoes.map(g => g.key), ['shoes'], 'C7 empty major/small groups omitted');
  eq(onlyShoes.map(g => g.label), ['Shoes'], 'C7 exact label for the only category');
  const all3 = A.itemGroups({ '3004': 5, '2301': 4, '1001': 3 });
  eq(all3.map(g => g.label), ['Major Items', 'Shoes', 'Small Items'],
    'C7 groups render in the exact required order with exact labels');
  eq(A.itemGroups({}).length, 0, 'C7 no usage renders no item groups');

  // Rendered markup: three separate .userow sections, one per category.
  const html = A.assetRowsHTML({ emb: {}, tal: {}, item: { '3004': 5, '2301': 4, '1001': 3 } }, '');
  for (const label of ['Major Items', 'Shoes', 'Small Items']) {
    ok(html.includes('>' + label + '</div>'), 'C7 markup contains a "' + label + '" section');
  }
  const rows = (html.match(/class="userow"/g) || []).length;
  eq(rows, 5, 'C7 markup renders 5 rows (emblem+talent+3 categories)');
  ok(!html.includes('>Items</div>'), 'C7 old single "Items" row replaced by categories');
  const bladeIdx = html.indexOf('data-item="3004"');
  const shoeIdx = html.indexOf('data-item="2301"');
  const compIdx = html.indexOf('data-item="1001"');
  ok(bladeIdx > -1 && shoeIdx > bladeIdx && compIdx > shoeIdx,
    'C7 markup order is major -> shoes -> small');
}

// --- C8: unknown identifiers never fall into the wrong category ---
{
  eq(A.itemClass('9999'), null, 'C8 unknown numeric id returns null');
  eq(A.itemClass('https://example.invalid/nope.png'), null, 'C8 unknown url id returns null');
  eq(A.itemClass(''), null, 'C8 empty id returns null');
  const g = A.groupItemsByClass({ '3004': 2, '9999': 7 });
  eq(g.major.map(e => e[0]), ['3004'], 'C8 unknown id is not filed as major');
  eq(g.small.length, 0, 'C8 unknown id is not filed as small');
  eq(g.shoes.length, 0, 'C8 unknown id is not filed as shoes');
  eq(g.unknown.map(e => e[0]), ['9999'], 'C8 unknown id is reported separately');
  const groups = A.itemGroups({ '9999': 1 });
  eq(groups.map(x => x.label), ['Unclassified'], 'C8 unknown renders an explicit Unclassified group');
  // A mapping with no map at all must not crash or invent categories.
  const empty = mkNS({});
  eq(empty.itemClass('3004'), null, 'C8 empty map classifies nothing');
  eq(empty.groupItemsByClass({ '3004': 1 }).unknown.length, 1, 'C8 empty map routes to unknown');
}

// --- C9: the obsolete frequency heuristic is gone from the source ---
{
  ok(!/topEntries\(u\.item,\s*\d+\)/.test(appSrc), 'C9 no top-N cap on item usage');
  ok(!appSrc.includes('en[1]>2'), 'C9 count>2 frequency grouping removed');
  ok(!appSrc.includes('rareitem'), 'C9 obsolete rare-item box treatment removed');
  ok(!appSrc.includes('use-sep'), 'C9 obsolete hairline removed');
  ok(appSrc.includes('ITEM_CLS_ORDER'), 'C9 three-category order declared');
}

console.log('\n' + (count - fails) + '/' + count + ' passed, ' + fails + ' failed');
process.exit(fails ? 1 : 0);