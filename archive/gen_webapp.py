"""Generate self-contained Pinterest-style webapp from CSV/DB data."""
import csv, json, html
from pathlib import Path
BASE = Path(__file__).parent
ROOT = BASE.parent

def load_csv(name):
    with open(ROOT/'data'/'csv'/f'{name}.csv', encoding='utf-8') as f:
        return list(csv.DictReader(f))

matches = load_csv('matches')
sched = load_csv('schedule_all')
games = load_csv('games')
bans = load_csv('game_bans')
season = load_csv('player_season_stats')
stand = load_csv('standings')
players_raw = load_csv('game_players')

# Trim heavy URL columns for embedding
players = [{k: r[k] for k in ('match_detail_id','game_no','team','player','lane','hero','kills','deaths','assists','kda','gold','gold_per_min','hero_damage','damage_taken','tower_damage')} for r in players_raw]
# numeric coercion for JS ease (keep strings for ids)
for r in players:
    for k in ('game_no','kills','deaths','assists','gold','hero_damage','damage_taken','tower_damage'):
        try: r[k] = int(float(r[k])) if r[k] not in ('',None) else 0
        except: r[k] = 0
    for k in ('kda','gold_per_min'):
        try: r[k] = float(r[k]) if r[k] not in ('',None) else 0
        except: r[k] = 0

# hero pool per player from game rows
from collections import Counter, defaultdict
pool = defaultdict(Counter)
for r in players:
    pool[r['player']][r['hero']] += 1
hero_pool = {p: sorted(c.items(), key=lambda x:-x[1])[:6] for p,c in pool.items()}

DATA = {"matches": matches, "schedule": sched, "games": games, "players": players,
        "hero_pool": hero_pool, "season": season, "standings": stand}
data_js = json.dumps(DATA, ensure_ascii=False).replace('</script>', '<\\/script>')

TEAMS = ["AE","BTR","DEWA","EVOS","GEEK","NAVI","ONIC","RRQ","TLID"]
TEAM_COLORS = {"AE":"#e11d48","BTR":"#dc2626","DEWA":"#0ea5e9","EVOS":"#3b82f6","GEEK":"#a855f7","NAVI":"#eab308","ONIC":"#f59e0b","RRQ":"#f97316","TLID":"#0d9488"}

html_doc = """<!DOCTYPE html>
<html lang="en">
<head>
<meta charset="utf-8">
<meta name="viewport" content="width=device-width, initial-scale=1">
<title>MPL ID S18 — Pinboard</title>
<style>
:root{--bg:#fafafa;--card:#fff;--ink:#111;--muted:#6b7280;--line:#e5e7eb;--accent:#e60023;--r:12px;--gap:16px}
*{box-sizing:border-box}body{margin:0;background:var(--bg);color:var(--ink);font:14px/1.45 system-ui,-apple-system,Segoe UI,Roboto,sans-serif;overflow-x:clip}
header{position:sticky;top:0;z-index:20;background:#fff;border-bottom:1px solid var(--line);padding:10px 16px;display:flex;flex-wrap:wrap;gap:10px;align-items:center}
.logo{font-weight:800;font-size:18px}.logo span{color:var(--accent)}
.search{flex:1 1 220px;display:flex}.search input{width:100%;padding:10px 14px;border-radius:24px;border:1px solid var(--line);background:#f1f1f1}
.tabs{display:flex;gap:6px;flex-wrap:wrap}.tabs button{border:0;background:#efefef;border-radius:24px;padding:8px 14px;font-weight:600;cursor:pointer}.tabs button[aria-selected=true]{background:#111;color:#fff}
.chips{display:flex;gap:6px;flex-wrap:wrap;padding:10px 16px}.chips button{border:1px solid var(--line);background:#fff;border-radius:16px;padding:6px 12px;cursor:pointer;font-size:12px}.chips button[aria-pressed=true]{background:#111;color:#fff;border-color:#111}
.toolbar{display:flex;gap:8px;flex-wrap:wrap;padding:0 16px 8px;align-items:center;color:var(--muted)}select{padding:6px 10px;border-radius:8px;border:1px solid var(--line)}
main{padding:8px 16px 60px}.masonry{columns:240px;column-gap:var(--gap)}
.pin{break-inside:avoid;background:var(--card);border:1px solid var(--line);border-radius:var(--r);margin:0 0 var(--gap);overflow:hidden;box-shadow:0 1px 2px rgba(0,0,0,.06)}
.pin .body{padding:12px}.pin h3{margin:.2em 0;font-size:15px}.pin p{margin:.3em 0;color:var(--muted);font-size:12.5px}
.pin .meta{display:flex;gap:6px;flex-wrap:wrap;align-items:center;font-size:12px;color:var(--muted)}
.dot{width:10px;height:10px;border-radius:50%;display:inline-block}
.pin img.top{width:100%;height:8px;display:block}
.actions{display:flex;gap:8px;padding:0 12px 12px}.actions button{flex:1;border:0;border-radius:8px;padding:8px;cursor:pointer;font-weight:700}.save{background:var(--accent);color:#fff}.open{background:#efefef}
table{width:100%;border-collapse:collapse;font-size:12.5px}th,td{text-align:left;padding:6px 8px;border-bottom:1px solid var(--line)}th{color:var(--muted);font-weight:600}
dialog{border:1px solid var(--line);border-radius:16px;max-width:min(860px,94vw);width:860px;padding:0}dialog::backdrop{background:rgba(0,0,0,.5)}
.dhead{padding:16px;border-bottom:1px solid var(--line);display:flex;gap:10px;align-items:center;flex-wrap:wrap}.dbody{padding:16px;max-height:70vh;overflow:auto}
.empty{text-align:center;color:var(--muted);padding:40px 0}.skip{position:absolute;left:-9999px}.skip:focus{left:8px;top:8px;background:#111;color:#fff;padding:8px;border-radius:8px;z-index:99}
@media(max-width:420px){main{padding:8px 10px 50px}}
</style>
</head>
<body>
<a class="skip" href="#board">Skip to board</a>
<header>
<div class="logo" aria-label="MPL ID S18 Pinboard">MPL<span>S18</span> Pinboard</div>
<div class="search"><input id="q" type="search" placeholder="Search players, heroes, teams, matches…" aria-label="Search"></div>
<nav class="tabs" role="tablist" aria-label="Views">
<button role="tab" aria-selected="true" data-view="discover">Discover</button>
<button role="tab" aria-selected="false" data-view="players">Players</button>
<button role="tab" aria-selected="false" data-view="matches">Matches</button>
<button role="tab" aria-selected="false" data-view="stats">Stats</button>
</nav>
</header>
<div class="chips" id="teamChips" aria-label="Filter by team"></div>
<div class="toolbar">
<label>Sort <select id="sort"><option value="kda">Avg KDA</option><option value="kills">Total kills</option><option value="goldmin">Avg gold/min</option><option value="games">Games</option></select></label>
<label>Lane <select id="lane"><option value="">All lanes</option><option>MID</option><option>GOLD</option><option>JUNGLE</option><option>EXP</option><option>ROAM</option></select></label>
<span id="count" role="status"></span>
</div>
<main><div class="masonry" id="board"></div><div class="empty" id="empty" hidden>No pins match. Clear search or filters.</div></main>
<dialog id="dlg" aria-labelledby="dt"><div class="dhead"><strong id="dt"></strong><span id="ds"></span><button id="dx" aria-label="Close dialog" style="margin-left:auto">✕ Close</button></div><div class="dbody" id="db"></div></dialog>
<script>
const DATA = __DATA__;
const TEAM_COLORS = __COLORS__;
const state = {view:'discover', q:'', team:'', sort:'kda', lane:''};
const board = document.getElementById('board'), emptyEl = document.getElementById('empty'),
  q = document.getElementById('q'), sortEl = document.getElementById('sort'), laneEl = document.getElementById('lane'),
  countEl = document.getElementById('count'), chips = document.getElementById('teamChips'),
  dlg = document.getElementById('dlg'), dt = document.getElementById('dt'), ds = document.getElementById('ds'), db = document.getElementById('db');
let lastFocus = null;
const esc = s => String(s??'').replace(/[&<>"]/g, c=>({'&':'&amp;','<':'&lt;','>':'&gt;','"':'&quot;'}[c]));
const teams = __TEAMS__;
teams.forEach(t=>{const b=document.createElement('button');b.textContent=t;b.setAttribute('aria-pressed','false');b.onclick=()=>{state.team = state.team===t?'':t;[...chips.children].forEach(x=>x.setAttribute('aria-pressed', x.textContent===state.team?'true':'false'));render();};chips.appendChild(b);});
document.querySelectorAll('.tabs button').forEach(b=>b.onclick=()=>{state.view=b.dataset.view;document.querySelectorAll('.tabs button').forEach(x=>x.setAttribute('aria-selected', x===b?'true':'false'));render();});
q.oninput=()=>{state.q=q.value.trim().toLowerCase();render();};
sortEl.onchange=()=>{state.sort=sortEl.value;render();};laneEl.onchange=()=>{state.lane=laneEl.value;render();};
document.getElementById('dx').onclick=()=>dlg.close();
dlg.addEventListener('close',()=>{if(lastFocus)lastFocus.focus();});
function openDlg(title, sub, htmlbd){lastFocus=document.activeElement;dt.textContent=title;ds.textContent=sub;db.innerHTML=htmlbd;dlg.showModal();}
function agg(){
  const m={};
  DATA.players.forEach(r=>{const k=r.player; (m[k]=m[k]||{player:k,team:r.team,gp:0,k:0,d:0,a:0,gold:0,gpm:0,heroes:new Set()}); const o=m[k]; o.gp++;o.k+=r.kills;o.d+=r.deaths;o.a+=r.assists;o.gold+=r.gold;o.gpm+=r.gold_per_min;o.heroes.add(r.hero);});
  const seas = Object.fromEntries(DATA.season.map(s=>[s.player,s]));
  return Object.values(m).map(o=>({...o, nhero:o.heroes.size, avgkda:(o.k+o.a)/Math.max(1,o.d), avggpm:o.gpm/o.gp, lane:(seas[o.player]||{}).lane||''}));
}
function matchGames(id){return DATA.games.filter(g=>g.match_detail_id===id);}
function gameRows(id,gn){return DATA.players.filter(r=>r.match_detail_id===id && String(r.game_no)===String(gn));}
function cardShell(color, inner, btn){return `<div class="pin"><div class="top" style="background:${color}"></div><div class="body">${inner}</div><div class="actions"><button class="open">${btn}</button></div></div>`;}
function render(){
  const query = state.q, out=[];
  if(state.view==='players'||state.view==='discover'){
    let rows = agg();
    if(state.team) rows=rows.filter(r=>r.team===state.team);
    if(state.lane) rows=rows.filter(r=>r.lane===state.lane);
    if(query) rows=rows.filter(r=>(r.player+' '+r.team+' '+[...DATA.hero_pool[r.player].map(h=>h[0])].join(' ')).toLowerCase().includes(query));
    const key = {kda:'avgkda',kills:'k',goldmin:'avggpm',games:'gp'}[state.sort];
    rows.sort((a,b)=>b[key]-a[key]);
    const list = state.view==='discover' ? rows.slice(0,24) : rows;
    list.forEach(o=>{
      const pool=(DATA.hero_pool[o.player]||[]).map(h=>`${esc(h[0])} ${h[1]}`).join(' · ');
      out.push(`<div class="pin"><div class="top" style="background:${TEAM_COLORS[o.team]||'#111'}"></div><div class="body"><div class="meta"><span class="dot" style="background:${TEAM_COLORS[o.team]||'#111'}"></span><span>${esc(o.team)} · ${esc(o.lane||'—')}</span></div><h3>${esc(o.player)}</h3><p>${o.gp} games · KDA ${o.avgkda.toFixed(2)} · GPM ${o.avggpm.toFixed(0)} · ${o.nhero} heroes</p><p>${esc(pool)}</p></div><div class="actions"><button class="open" data-p="${esc(o.player)}">Open</button></div></div>`);
    });
  }
  if(state.view==='matches'||state.view==='discover'){
    let ms = DATA.schedule.slice().sort((a,b)=>(a.iso_datetime||'').localeCompare(b.iso_datetime||''));
    if(state.team) ms=ms.filter(m=>m.team_a===state.team||m.team_b===state.team);
    if(query) ms=ms.filter(m=>(m.team_a+' '+m.team_b+' '+m.date).toLowerCase().includes(query));
    const list = state.view==='discover' ? ms.filter(m=>m.status==='completed').slice(-12).reverse() : ms;
    list.forEach(m=>{
      const done = m.match_detail_id && m.status==='completed';
      out.push(`<div class="pin"><div class="top" style="background:linear-gradient(90deg,${TEAM_COLORS[m.team_a]||'#111'},${TEAM_COLORS[m.team_b]||'#111'})"></div><div class="body"><div class="meta"><span>${esc(m.date||'')} · ${esc(m.status||'')}</span></div><h3>${esc(m.team_a)} ${m.score_a??'–'} : ${m.score_b??'–'} ${esc(m.team_b)}</h3><p>${done?('Detail #'+esc(m.match_detail_id)+(m.vod_url?` · <a href="${esc(m.vod_url)}">VOD</a>`:'')):'No per-game detail yet'}</p></div><div class="actions">${done?`<button class="open" data-m="${esc(m.match_detail_id)}">Scoreboard</button>`:`<button class="open" disabled>Soon</button>`}</div></div>`);
    });
  }
  if(state.view==='stats'){
    const st=[...DATA.standings].sort((a,b)=>a.rank-b.rank);
    out.push(`<div class="pin"><div class="body"><h3>Standings</h3><table><tr><th>#</th><th>Team</th><th>Pts</th><th>W-L</th></tr>${st.map(s=>`<tr><td>${s.rank}</td><td>${esc(s.team_name)}</td><td>${s.match_point}</td><td>${s.match_win}-${s.match_lose}</td></tr>`).join('')}</table></div></div>`);
    const top=[...DATA.season].filter(s=>+s.total_games>=5).sort((a,b)=>+b.avg_kda-+a.avg_kda).slice(0,10);
    out.push(`<div class="pin"><div class="body"><h3>Top KDA (min 5 games)</h3><table><tr><th>Player</th><th>KDA</th><th>K/D/A</th></tr>${top.map(s=>`<tr><td>${esc(s.player)}</td><td>${s.avg_kda}</td><td>${s.total_kills}/${s.total_deaths}/${s.total_assists}</td></tr>`).join('')}</table></div></div>`);
  }
  board.innerHTML = out.join('') || '';
  emptyEl.hidden = out.length>0;
  countEl.textContent = out.length + ' pins';
  board.querySelectorAll('[data-p]').forEach(b=>b.onclick=()=>showPlayer(b.dataset.p));
  board.querySelectorAll('[data-m]').forEach(b=>b.onclick=()=>showMatch(b.dataset.m));
}
function showPlayer(name){
  const rows = DATA.players.filter(r=>r.player===name);
  const g = agg().find(o=>o.player===name)||{};
  const byHero = {}; rows.forEach(r=>{(byHero[r.hero]=byHero[r.hero]||[]).push(r);});
  const tbl = Object.entries(byHero).map(([h,rs])=>`<tr><td>${esc(h)}</td><td>${rs.length}</td><td>${(rs.reduce((s,r)=>s+r.kills,0)/rs.length).toFixed(1)}/${(rs.reduce((s,r)=>s+r.deaths,0)/rs.length).toFixed(1)}/${(rs.reduce((s,r)=>s+r.assists,0)/rs.length).toFixed(1)}</td><td>${(rs.reduce((s,r)=>s+r.gold_per_min,0)/rs.length).toFixed(0)}</td></tr>`).join('');
  openDlg(name, `${esc(g.team||'')} · ${esc(g.lane||'')} · ${rows.length} games`, `<p>Avg KDA ${(g.avgkda||0).toFixed(2)} · Avg GPM ${(g.avggpm||0).toFixed(0)} · K ${g.k} / D ${g.d} / A ${g.a}</p><table><tr><th>Hero</th><th>GP</th><th>Avg K/D/A</th><th>GPM</th></tr>${tbl}</table>`);
}
function showMatch(id){
  const m = DATA.schedule.find(x=>String(x.match_detail_id)===String(id))||{};
  const gs = matchGames(id);
  const tabs = gs.map(g=>`<h4>Game ${g.game_no} — ${esc(g.team_a)} ${g.team_a_kills} : ${g.team_b_kills} ${esc(g.team_b)} · ${esc(g.duration_str)} · ${esc(g.winner)}</h4>`+`<table><tr><th>Player</th><th>Hero</th><th>K/D/A</th><th>KDA</th><th>Gold</th><th>GPM</th></tr>`+gameRows(id,g.game_no).map(r=>`<tr><td>${esc(r.player)} (${esc(r.team)})</td><td>${esc(r.hero)}</td><td>${r.kills}/${r.deaths}/${r.assists}</td><td>${r.kda}</td><td>${r.gold}</td><td>${r.gold_per_min}</td></tr>`).join('')+`</table>`).join('');
  openDlg(`${m.team_a} vs ${m.team_b}`, `#${id} · ${m.date}`, tabs||'No games');
}
document.addEventListener('keydown',e=>{if(e.key==='Escape'&&dlg.open)dlg.close();});
render();
</script>
</body>
</html>"""
out = ROOT / "mpl_id_s18_pinboard.html"
html_doc = html_doc.replace("__DATA__", data_js).replace("__COLORS__", json.dumps(TEAM_COLORS)).replace("__TEAMS__", json.dumps(TEAMS))
out.write_text(html_doc, encoding="utf-8")
print("wrote", out, len(html_doc), "chars")
