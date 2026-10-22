const DATA = __DATA__;
const SEASON = __SEASON__;
/* CFG-START */
/* Season configuration guard: the build (tools/gen_dark.py) strictly
   validates data/season.json and aborts on any problem, so an invalid
   SEASON here means a hand-edited bundle. Log clearly and keep rendering
   with the embedded values rather than inventing replacements. */
function validSeasonCfg(c){
if(!c||typeof c!=='object')return false;
if(!Array.isArray(c.teams)||!c.teams.length||c.teams.length!==c.totalTeams)return false;
if(!(c.roundRobinRounds>=1))return false;
if(c.seriesPerTeam!==c.roundRobinRounds*(c.teams.length-1))return false;
if(!(c.playoffSlots>=1&&c.playoffSlots<c.teams.length))return false;
if(!(c.upperBracketSlots>=0&&c.upperBracketSlots<=c.playoffSlots))return false;
if(!c.aliases||typeof c.aliases!=='object'||!Object.keys(c.aliases).length)return false;
if(!c.endpoints||!c.endpoints.hub||!c.endpoints.liquipediaSeasonPage)return false;
if(!c.seasonId||!(c.cacheSchema>=1)||!c.cacheNamespace)return false;
if(!c.model||!(c.model.trials>=1))return false;
return true;}
/* CFG-END */
if(!validSeasonCfg(SEASON))console.error('invalid season configuration in bundle');
const TEAMS = SEASON.teams;
const TEAM_LOGOS = {ae:"assets/teams/ae.png",btr:"assets/teams/btr.png",dewa:"assets/teams/dewa.png",evos:"assets/teams/evos.png",geek:"assets/teams/geek.png",navi:"assets/teams/navi.png",onic:"assets/teams/onic.png",rrq:"assets/teams/rrq.png",tlid:"assets/teams/tlid.png"};
const logoOf = t => TEAM_LOGOS[String(t||'').toLowerCase()] || '';
const IMG_HIDE = 'onerror="this.style.visibility=\'hidden\'"';
function eqId(u){const m=/(?:equipment|equip)\/(\d+)\.png/.exec(u||'');return m?m[1]:'';}
function itemRef(u){const id=eqId(u);if(id)return id;if(u&&u.indexOf('scoregg.com')>-1)return String(u).split('?')[0];return null;}
function srt(arr,fn,str){const d=(S.tsort&&S.tsort.d)||1;return [...arr].sort((a,b)=>str?String(fn(a)).localeCompare(String(fn(b)))*d:(fn(a)-fn(b))*d);}
function th(t,k,label){const a=S.tsort.t===t&&S.tsort.k===k;return `<th data-ts="${t}:${k}">${label}${a?` <span class="sarr">${S.tsort.d===1?'▲':'▼'}</span>`:''}</th>`;}
function imgSlot(el){const s=document.createElement('span');s.className='slot-miss';s.title=el.alt||'item';s.textContent=el.dataset.eq||'?';el.replaceWith(s);}
const S = {view:'overview',q:'',team:'',sort:'kda',lane:'',compact:false,layout:'grid',ov:null,mlimit:24,plimit:24,phase:'reg',stat:'mvp',tsort:{t:'heroes',k:'pick',d:-1},anLane:'',anTab:'players',prepOpp:'',prepTeam:''};
const ANA={};
let PREP=null;
function anPart(k){
  if(ANA[k])return ANA[k];
  const dm={};(DATA.schedule||[]).forEach(m=>{dm[String(m.match_detail_id)]=m.iso_date||m.date||'';});
  const dateOf=m=>dm[String(m)]||'';
  if(k==='AN'){
    const twr={};(DATA.team_games||[]).forEach(r=>{const x=twr[r.team]=twr[r.team]||{n:0,w:0};x.n++;if(r.win===1)x.w++;});
    Object.keys(twr).forEach(t=>{twr[t]=twr[t].n?twr[t].w/twr[t].n:0;});
    ANA[k]=buildPlayerMetrics(DATA.players,DATA.games,DATA.team_games,window.HERO_CLASSES||{},{canon:canonicalPlayer,dateOf,teamWinRate:twr});
  }
  if(k==='TM')ANA[k]=buildTeamMetrics(DATA.team_games||[],DATA.team_season||[],DATA.games||[],{dateOf,bootstraps:100,seed:7});
  if(k==='DM')ANA[k]=buildDraftMetrics(DATA.picks||[],DATA.bans||[],DATA.games||[],window.HERO_CLASSES||{},{minPair:3,dateOf});
  return ANA[k];
}
(function initHash(){
  try{
    const p=new URLSearchParams((location.hash||'').replace(/^#/,''));
    const v=p.get('view');
    if(v&&['overview','players','matches','stats','analytics','prep'].includes(v))S.view=v;
    if(p.get('opp'))S.prepOpp=p.get('opp');
    if(p.get('team'))S.prepTeam=p.get('team');
    if(p.get('tab'))S.anTab=p.get('tab');
    if(p.get('lane'))S.anLane=p.get('lane');
    if(p.get('q'))S.q=p.get('q');
    if(p.get('filterTeam'))S.team=p.get('filterTeam');
  }catch(e){}
})();
const PICON_RAW = ((window.ASSETS||{}).players||{});
const PICON_CI = Object.fromEntries(Object.entries(PICON_RAW).map(([k,v])=>[k.toLowerCase(),v]));
const PICON_ALIAS = {arfy:'dingarai',yazukee:'affan',hijumee:'dalvin',alekk:'alexander',joshuaa:'joshuaa',kevinn:'kevin',maykidss:'maykids',shanee:'shanee',sanz:'s a n z'};
const PICON = n => {const k=String(n||'');const l=k.toLowerCase();return PICON_RAW[k]||PICON_CI[l]||PICON_CI[PICON_ALIAS[l]||'']||'';};
function ppic(n){const u=PICON(n);const init=esc(String(n||'?').split(/[\s_]+/).map(w=>w[0]).join('').slice(0,2).toUpperCase());
return (u?`<img class="ppic" src="${esc(u)}" alt="" loading="lazy" onerror="this.nextElementSibling.style.display='inline-flex';this.remove()">`:'')+`<span class="ppic-fb"${u?' style="display:none"':''}>${esc(init)}</span>`;}
const TICON = t => (((window.ASSETS||{}).teams||{})[String(t||'').toUpperCase()]) || logoOf(t);
const board=document.getElementById('board'),emptyEl=document.getElementById('empty'),q=document.getElementById('q'),
sortEl=document.getElementById('sort'),laneEl=document.getElementById('lane'),countEl=document.getElementById('count'),
chips=document.getElementById('chips'),dlg=document.getElementById('dlg');
let lastFocus=null;
const esc=s=>String(s??'').replace(/[&<>"]/g,c=>({'&':'&amp;','<':'&lt;','>':'&gt;','"':'&quot;'}[c]));
TEAMS.forEach(t=>{const b=document.createElement('button');b.textContent=t;b.setAttribute('aria-pressed','false');
b.onclick=()=>{S.team=S.team===t?'':t;[...chips.children].forEach(x=>x.setAttribute('aria-pressed',x.textContent===S.team?'true':'false'));render();};chips.appendChild(b);});
document.querySelectorAll('.tabs button').forEach(b=>b.onclick=()=>{S.view=b.dataset.view;
if(b.dataset.view==='matches'){S.mlimit=24;S.plimit=24;}
document.querySelectorAll('.tabs button').forEach(x=>x.setAttribute('aria-selected',x===b?'true':'false'));render();});
q.oninput=()=>{S.q=q.value.trim().toLowerCase();render();};
sortEl.onchange=()=>{S.sort=sortEl.value;render();};laneEl.onchange=()=>{S.lane=laneEl.value;render();};
document.getElementById('density').onclick=e=>{S.compact=!S.compact;document.body.classList.toggle('compact',S.compact);
e.target.textContent=S.compact?'Comfort':'Compact';};
function setLayout(l){S.layout=l;document.getElementById('layGrid').setAttribute('aria-pressed',l==='grid'?'true':'false');
document.getElementById('layList').setAttribute('aria-pressed',l==='list'?'true':'false');
document.getElementById('board').classList.toggle('list',l==='list'&&S.view==='players');render();}
document.getElementById('layGrid').onclick=()=>setLayout('grid');
document.getElementById('layList').onclick=()=>setLayout('list');
document.getElementById('dx').onclick=()=>dlg.close();
document.getElementById('dx2').onclick=()=>document.getElementById('dlg2').close();
document.getElementById('db').addEventListener('click',e=>{
const g=e.target.closest('[data-ovg]');if(g){const parts=g.dataset.ovg.split(':');showM(parts[0],{game:parts[1]});return;}
const h=e.target.closest('[data-ovhero]');if(h){(h.dataset.scope==='global'?stHeroDrill:ovHeroDrill)(h.dataset.ovhero);return;}
const m=e.target.closest('[data-ovemb]');if(m){(m.dataset.scope==='global'?stEmbDrill:ovEmbDrill)(m.dataset.ovemb);return;}
const t=e.target.closest('[data-ovtal]');if(t){(t.dataset.scope==='global'?stTalDrill:ovTalDrill)(t.dataset.ovtal);return;}
const it=e.target.closest('[data-ovitem]');if(it){stItemDrill(it.dataset.ovitem);return;}
const p=e.target.closest('[data-p]');if(p){showP(p.dataset.p);return;}
const o=e.target.closest('[data-ovopp]');if(o){ovOppDrill(o.dataset.ovopp);return;}});
document.addEventListener('keydown',e=>{if(e.key!=='Enter'&&e.key!==' ')return;const t=e.target&&e.target.closest?e.target.closest('[data-ovg],[data-ovhero],[data-ovemb],[data-ovtal],[data-ovitem],[data-ovopp],[data-p]'):null;if(!t)return;if(t.tagName==='BUTTON'&&e.key===' ')return;e.preventDefault();t.click();});
document.getElementById('selQ').oninput=renderOvSel;
document.getElementById('selT').onchange=renderOvSel;
document.getElementById('selL').onchange=renderOvSel;
let lastY=0,scrollTick=false;
window.addEventListener('scroll',()=>{if(scrollTick)return;scrollTick=true;requestAnimationFrame(()=>{scrollTick=false;
const y=window.scrollY,hdr=document.querySelector('header');
if(window.innerWidth>640||!hdr){if(hdr)hdr.classList.remove('navhide');}
else if(y>lastY&&y>160){hdr.classList.add('navhide');}else if(y<lastY){hdr.classList.remove('navhide');}
lastY=y;});},{passive:true});
dlg.addEventListener('close',()=>{dnav=[];if(lastFocus)lastFocus.focus();});
function agg(){const m={};const num=v=>{const n=+v;return isFinite(n)?n:0;};DATA.players.forEach(r=>{(m[r.player]=m[r.player]||{player:r.player,team:r.team,gp:0,k:0,d:0,a:0,gpm:0,hs:new Set()});
const o=m[r.player];o.gp++;o.k+=num(r.kills);o.d+=num(r.deaths);o.a+=num(r.assists);o.gpm+=num(r.gold_per_min);o.hs.add(r.hero);});
const seas=Object.fromEntries(DATA.season.map(s=>[String(s.player||'').toLowerCase(),s]));
const SALIAS=(typeof window!=='undefined'&&window.ALIASES&&window.ALIASES.seasonAlias)||{};
const seasOf=n=>{const l=String(n||'').toLowerCase();return seas[l]||seas[SALIAS[l]||'']||null;};
const ultra=s=>String(s||'').toLowerCase().replace(/[^a-z0-9]/g,'');
const LIQLANES=(typeof window!=='undefined'&&window.ALIASES&&window.ALIASES.lanes)||{};
const liqLane=n=>LIQLANES[ultra(n)]||'';
return Object.values(m).map(o=>{const s=seasOf(o.player);const avgg=o.gpm/Math.max(1,o.gp);
const gp=s?+s.total_games||0:o.gp,k=s?+s.total_kills||0:o.k,d=s?+s.total_deaths||0:o.d,a=s?+s.total_assists||0:o.a;
const avgkda=(s&&s.avg_kda!=null&&s.avg_kda!=='')?+s.avg_kda:(k+a)/Math.max(1,d);
return {...o,gp,k,d,a,avgkda,nh:o.hs.size,avgg,lane:((s||{}).lane||liqLane(o.player)||'')}});}
function rows(id,gn){return DATA.players.filter(r=>r.match_detail_id===id&&String(r.game_no)===String(gn));}
function bansFor(mid,gn,side){return (DATA.bans||[]).filter(b=>String(b.match_detail_id)===String(mid)&&String(b.game_no)===String(gn)&&b.side===side).sort((a,b)=>(a.ban_order??99)-(b.ban_order??99)).map(b=>b.hero);}
function pickSlot(mid,gn,team,player){const p=(DATA.picks||[]).find(x=>String(x.match_detail_id)===String(mid)&&String(x.game_no)===String(gn)&&x.team===team&&x.player===player);return p?+p.slot:99;}
const io=new IntersectionObserver(es=>es.forEach(e=>{if(e.isIntersecting){e.target.classList.add('in');io.unobserve(e.target);}}),{rootMargin:'80px'});
function syncControls(){const v=S.view;
const show=(id,on)=>{const el=document.getElementById(id);if(el)el.hidden=!on;};
show('searchBox',v==='players'||v==='matches');
show('chips',v==='players'||v==='matches');
show('sortBox',v==='players');
show('laneBox',v==='players');
show('layoutSeg',v==='players'||v==='matches');}
function render(){const out=[];
document.querySelectorAll('.tabs button').forEach(b=>b.setAttribute('aria-selected',b.dataset.view===S.view?'true':'false'));
syncControls();
board.classList.toggle('list',S.layout==='list');
board.classList.toggle('wide',S.view==='stats');
document.querySelector('main.wrap').classList.toggle('full',S.view==='matches'&&S.layout==='list');
if(S.view==='overview'){out.push(ovHTML());}
if(S.view==='players'){let r=agg();
if(S.team)r=r.filter(x=>x.team===S.team);if(S.lane)r=r.filter(x=>x.lane===S.lane);
if(S.q)r=r.filter(x=>(x.player+' '+x.team+' '+(DATA.hero_pool[x.player]||[]).map(h=>h[0]).join(' ')).toLowerCase().includes(S.q));
const k={kda:'avgkda',kills:'k',goldmin:'avgg',games:'gp'}[S.sort];r.sort((a,b)=>b[k]-a[k]);
if(S.view==='players'&&S.layout==='list'){
out.push(`<div class="pin"><div class="lscroll"><div class="lhead"><span></span><span>Player</span><span>Team</span><span>Lane</span><span>GP</span><span>KDA</span><span>K / D / A</span><span>Gold/min</span><span>Heroes</span></div>`
+r.map(o=>{const pl=(DATA.hero_pool[o.player]||[]).slice(0,3).map(h=>esc(h[0])).join(', ');
return `<div class="lrow">${ppic(o.player)}<span><b>${esc(o.player)}</b></span><span><img class="tlogo" src="${TICON(o.team)}" alt="" loading="lazy" ${IMG_HIDE}> <span class="mono">${esc(o.team)}</span></span><span class="mono">${esc(o.lane||'—')}</span><span class="mono">${o.gp}</span><span class="mono">${o.avgkda.toFixed(2)}</span><span class="mono">${o.k}/${o.d}/${o.a}</span><span class="mono">${o.avgg.toFixed(0)}</span><span class="mono hide-m">${pl}</span></div>`;}).join('')+`</div></div>`);}
else{r.forEach((o,i)=>{const pl=(DATA.hero_pool[o.player]||[]).map(h=>esc(h[0])+' '+h[1]).join(' · ');
out.push(`<div class="pin" style="--index:${i}"><div class="body"><div class="phead">${ppic(o.player)}<div><div class="kicker">${esc(o.team)} · ${esc(o.lane||'—')}</div><h3 style="margin:0">${esc(o.player)}</h3></div><img class="tlogo" src="${TICON(o.team)}" alt="${esc(o.team)}" loading="lazy" ${IMG_HIDE}></div><p>${o.gp} games · KDA ${o.avgkda.toFixed(2)} · GPM ${o.avgg.toFixed(0)} · ${o.nh} heroes</p><p>${pl}</p></div><div class="actions"><button class="ghost" data-p="${esc(o.player)}">Open</button></div></div>`);});}}
if(S.view==='matches'){let ms=DATA.schedule.slice().sort((a,b)=>(a.iso_datetime||'').localeCompare(b.iso_datetime||''));
if(S.team)ms=ms.filter(m=>m.team_a===S.team||m.team_b===S.team);
if(S.q)ms=ms.filter(m=>(m.team_a+' '+m.team_b+' '+m.date).toLowerCase().includes(S.q));
const isPO=m=>String(m.schedule_id||m.match_id||'').indexOf('playoffs')>-1||(m.team_a==='TBD'&&m.team_b==='TBD');
const secHead=(title,n)=>`<div class="pin" style="grid-column:1/-1"><div class="body"><div class="phasebar"><div><div class="kicker">Bracket</div><h3 style="margin:.25em 0">${title} (${n})</h3></div>${phaseCtl}</div></div></div>`;
const secCards=list=>list.map(m=>{const done=m.match_detail_id&&m.status==='completed';
const gmvp=mvpById[String(m.match_detail_id)]||'';
return `<div class="pin mpin"><div class="body"><div class="kicker">${esc(m.date||'')} · ${esc(m.status||'')}</div><div class="mteams"><div class="mt"><img src="${TICON(m.team_a)}" alt="" loading="lazy" ${IMG_HIDE}><span>${esc(m.team_a)}</span></div><div class="score">${esc(m.score_a??'–')} : ${esc(m.score_b??'–')}</div><div class="mt"><img src="${TICON(m.team_b)}" alt="" loading="lazy" ${IMG_HIDE}><span>${esc(m.team_b)}</span></div></div>${gmvp?`<div class="mmvp-grid">MVP · <b>${esc(gmvp)}</b></div>`:''}<div class="mmeta"><span class="tag">${done?('Detail #'+esc(m.match_detail_id)):esc(m.status||'upcoming')}</span></div></div><div class="actions">${done?`<button class="primary" data-m="${esc(m.match_detail_id)}">Scoreboard</button>`:`<button class="ghost" disabled>Soon</button>`}</div></div>`;}).join('');
const regAll=ms.filter(m=>!isPO(m)),poAll=ms.filter(isPO);
const reg=regAll.slice(0,S.mlimit),po=poAll.slice(0,S.plimit);
const pbtn=(k,label,n)=>`<button data-phase="${k}" aria-pressed="${S.phase===k?'true':'false'}">${label} (${n})</button>`;
const phaseCtl=`<div class="seg" role="group" aria-label="Phase">${pbtn('reg','Regular Season',regAll.length)}${pbtn('po','Playoffs',poAll.length)}</div>`;
const mvpById=Object.fromEntries((DATA.matches||[]).map(m=>[String(m.match_detail_id),m.liq_mvp||'']));
const mrow=m=>{const done=m.match_detail_id&&m.status==='completed';
const aWins=(+m.score_a)>(+m.score_b),bWins=(+m.score_b)>(+m.score_a);
return `<div class="mrow"${done?' data-m="'+esc(m.match_detail_id)+'"':''}><span class="mdate hide-m">${esc(m.iso_date||m.date||'')}</span>`
+`<span class="mfix"><img src="${TICON(m.team_a)}" alt="" loading="lazy" ${IMG_HIDE}><span class="mt ${done?(aWins?'mwin':'mlose'):''}">${esc(m.team_a)}</span><span class="msc">${esc(m.score_a??'–')} : ${esc(m.score_b??'–')}</span><span class="mt ${done?(bWins?'mwin':'mlose'):''}">${esc(m.team_b)}</span><img src="${TICON(m.team_b)}" alt="" loading="lazy" ${IMG_HIDE}></span>`
+`<span class="hide-m"><span class="tag">${esc(m.status||'')}</span></span>`
+`<span class="mmvp hide-m">${esc(mvpById[String(m.match_detail_id)]||'—')}</span>`
+`<span class="mgo">${done?'›':''}</span></div>`;};
if(S.layout==='list'){
const mfoot=(secKey,shown,total)=>shown<total?`<button class="mfoot" data-more="24" data-sec="${secKey}"><span>Show more</span><span class="mono">showing ${shown} of ${total}</span></button>`:'';
const ptitle=S.phase==='po'?'Playoffs':'Regular Season';
out.push(`<div class="pin"><div class="body phasebar"><div><div class="kicker">Matches</div><h3 style="margin:.25em 0">${ptitle}</h3></div>${phaseCtl}</div></div>`);
out.push(S.phase==='po'?finalBoard():standBoard());
let mh=`<div class="pin"><div class="lscroll"><div class="mhead"><span>Date</span><span>Match</span><span>Status</span><span>MVP</span><span></span></div>`;
if(S.phase==='po'){if(poAll.length)mh+=po.map(mrow).join('')+mfoot('po',po.length,poAll.length);}
else{if(regAll.length)mh+=reg.map(mrow).join('')+mfoot('reg',reg.length,regAll.length);}
mh+=`</div></div>`;
out.push(mh);
if(S.phase==='po')out.push(bracketHTML());}
else{
if(S.phase==='po'){out.push(secHead('Playoffs — TBD',po.length)+finalBoard()+secCards(po));
if(poAll.length>S.plimit)out.push(`<div class="pin" style="grid-column:1/-1"><div class="body" style="text-align:center"><p>Showing ${S.plimit} of ${poAll.length} playoff matches</p><div class="actions"><button class="primary" data-more="24" data-sec="po">Show more</button></div></div></div>`);
out.push(bracketHTML());}
else{out.push(secHead('Regular Season',reg.length)+standBoard()+teamBoard()+secCards(reg));
if(regAll.length>S.mlimit)out.push(`<div class="pin" style="grid-column:1/-1"><div class="body" style="text-align:center"><p>Showing ${S.mlimit} of ${regAll.length} regular-season matches</p><div class="actions"><button class="primary" data-more="24">Show more</button></div></div></div>`);}}}
if(S.view==='stats'){
const sbtn=(k,label)=>`<button data-stat="${k}" aria-pressed="${S.stat===k?'true':'false'}">${label}</button>`;
out.push(`<div class="pin" style="grid-column:1/-1"><div class="body phasebar"><div><div class="kicker">Statistics</div><h3 style="margin:.25em 0">${S.stat==='heroes'?'Heroes':'Series MVP'}</h3></div><div class="seg" role="group" aria-label="Stats">${sbtn('mvp','Series MVP')}${sbtn('heroes','Heroes')}</div></div></div>`);
if(S.stat==='heroes'){
const HC=window.HERO_CLASSES||{};
const hs=(DATA.heroes||[]).map(h=>{const c=HC[h.hero]||{};return {hero:h.hero,img:h.hero_image,pick:+h.pick||0,ban:+h.ban||0,win:+h.win||0,wr:h.win_rate||'–',role:c.primary_role||'–',lane:c.primary_lane||'–',dmg:c.damage_type||'–'};});
const pb=h=>(+h.pick||0)+(+h.ban||0);
const played=hs.filter(h=>pb(h)>0).sort((a,b)=>b.pick-a.pick||pb(b)-pb(a));
const maxPB=Math.max(1,...played.map(pb));
const hval=(h,k)=>k==='hero'?h.hero:k==='ban'?h.ban:k==='win'?h.win:k==='wr'?(parseFloat(h.wr)||-1):k==='pb'||k==='share'?pb(h):h.pick;
const hrows=S.tsort.t==='heroes'?srt(played,h=>hval(h,S.tsort.k),S.tsort.k==='hero'):played;
if(!played.length)out.push(`<div class="pin" style="grid-column:1/-1"><div class="body"><div class="empty">No hero data yet — hit Refresh.</div></div></div>`);
else{
const mostP=played[0],mostB=[...played].sort((a,b)=>b.ban-a.ban)[0],mostC=[...played].sort((a,b)=>pb(b)-pb(a))[0];
const elig=played.filter(h=>h.pick>=5).sort((a,b)=>(b.win/Math.max(1,b.pick))-(a.win/Math.max(1,a.pick)));
const bestWR=elig[0];
out.push(`<div class="pin" style="grid-column:1/-1"><div class="body"><div class="kicker">Highlights · ${played.length} heroes contested</div><div class="tiles">`
+`<div class="tile"><b data-ovhero="${esc(mostP.hero)}" data-scope="global" tabindex="0" title="Open ${esc(mostP.hero)} stats">${esc(mostP.hero)}</b><span>Most picked · ${mostP.pick}</span></div>`
+`<div class="tile"><b data-ovhero="${esc(mostB.hero)}" data-scope="global" tabindex="0" title="Open ${esc(mostB.hero)} stats">${esc(mostB.hero)}</b><span>Most banned · ${mostB.ban}</span></div>`
+(bestWR?`<div class="tile"><b data-ovhero="${esc(bestWR.hero)}" data-scope="global" tabindex="0" title="Open ${esc(bestWR.hero)} stats">${esc(bestWR.hero)}</b><span>Best win rate (5+ picks) · ${esc(bestWR.wr)}</span></div>`:'')
+`<div class="tile"><b data-ovhero="${esc(mostC.hero)}" data-scope="global" tabindex="0" title="Open ${esc(mostC.hero)} stats">${esc(mostC.hero)}</b><span>Most contested · ${pb(mostC)} pick+ban</span></div>`
+`</div></div></div>`);
out.push(`<div class="pin" style="grid-column:1/-1"><div class="body"><div class="kicker">Every contested hero · pick / ban / win</div><div class="lscroll"><table style="min-width:980px"><tr>${th('heroes','hero','Hero')}<th>Role</th><th>Lane</th><th>DMG</th>${th('heroes','pick','Pick')}${th('heroes','ban','Ban')}${th('heroes','pb','P+B')}${th('heroes','win','Win')}${th('heroes','wr','WR')}${th('heroes','share','Share')}</tr>${hrows.map(h=>`<tr><td data-ovhero="${esc(h.hero)}" data-scope="global" tabindex="0" title="Open ${esc(h.hero)} stats"><span class="hcell">${h.img?`<img src="${esc(h.img)}" alt="" loading="lazy" onerror="this.remove()">`:''}${esc(h.hero)}</span></td><td>${esc(h.role)}</td><td>${esc(h.lane)}</td><td title="Damage type is derived from ability text, not an official field">${esc(h.dmg)}</td><td>${esc(h.pick)}</td><td>${esc(h.ban)}</td><td>${pb(h)}</td><td>${esc(h.win)}</td><td>${esc(h.wr)}</td><td style="min-width:110px"><span class="bar"><span style="width:${Math.round(pb(h)/maxPB*100)}%"></span></span></td></tr>`).join('')}</table></div></div></div>`);}
}else{
const mvps=(DATA.matches||[]).filter(m=>m.liq_mvp);
const srcByCanon=mvpSources();
const cnt={};mvps.forEach(m=>{const c=canonicalPlayer(m.liq_mvp);cnt[c]=(cnt[c]||0)+1;});
const race=Object.entries(cnt).sort((a,b)=>b[1]-a[1]);
const mx=race.length?race[0][1]:1;
const rrows=S.tsort.t==='race'?srt(race,r=>S.tsort.k==='player'?r[0]:r[1],S.tsort.k==='player'):race;
const srcNote=p=>[...(srcByCanon[p]||[])].filter(s=>s!==p);
out.push(`<div class="pin"><div class="body"><div class="kicker">MVP race · ${mvps.length} series decided</div><h3 style="margin:.25em 0">Leaderboard</h3><table><tr>${th('race','rank','#')}${th('race','player','Player')}${th('race','mvps','MVPs')}<th></th></tr>${rrows.map(([p,n],i)=>{const alts=srcNote(p);return `<tr><td>#${i+1}</td><td><span data-p="${esc(p)}" tabindex="0" style="cursor:pointer;font-weight:600"${alts.length?` title="Source name${alts.length>1?'s':''}: ${esc(alts.join(', '))}"`:''}>${esc(p)}</span>${alts.length?` <span style="font-family:var(--font-mono);font-size:10.5px;color:var(--muted)">(as ${esc(alts.join(', '))})</span>`:''}</td><td>${n}</td><td style="min-width:90px"><span class="bar"><span style="width:${Math.round(n/mx*100)}%"></span></span></td></tr>`;}).join('')||'<tr><td colspan="4">No MVPs yet.</td></tr>'}</table></div></div>`);
const histBase=[...mvps].sort((a,b)=>String(a.iso_datetime||'').localeCompare(String(b.iso_datetime||'')));
const hist=S.tsort.t==='hist'?srt(histBase,m=>S.tsort.k==='match'?(m.team_a+' '+m.team_b):S.tsort.k==='mvp'?canonicalPlayer(m.liq_mvp):(m.iso_datetime||''),true):histBase;
out.push(`<div class="pin"><div class="body"><div class="kicker">History</div><h3 style="margin:.25em 0">Series MVPs</h3><div class="lscroll"><table style="min-width:520px"><tr>${th('hist','date','Date')}${th('hist','match','Match')}${th('hist','mvp','MVP')}</tr>${hist.map(m=>{const c=canonicalPlayer(m.liq_mvp);return `<tr><td>${esc(m.iso_date||m.date||'')}</td><td>${esc(m.team_a)} ${esc(m.score_a??'')}:${esc(m.score_b??'')} ${esc(m.team_b)}</td><td>${esc(c)}${c!==m.liq_mvp?` <span style="font-family:var(--font-mono);font-size:10.5px;color:var(--muted)">(as ${esc(m.liq_mvp)})</span>`:''}</td></tr>`;}).join('')}</table></div></div></div>`);}}
if(S.view==='prep'){
const TM=anPart('TM'),AN=anPart('AN'),DM=anPart('DM');
const codes=TM.teams.map(t=>t.team).sort();
const oppCode=codes.includes(S.prepOpp)?S.prepOpp:(codes[0]||'');
S.prepOpp=oppCode;
const opp=TM.teams.find(t=>t.team===oppCode);
const myCode=(S.prepTeam&&S.prepTeam!==oppCode&&codes.includes(S.prepTeam))?S.prepTeam:'';
const my=myCode?TM.teams.find(t=>t.team===myCode):null;
if(opp){
const pc=v=>Math.round(v*100);
const mins=v=>v?Math.round(v/6)/10+'m':'—';
const signed=v=>`${v>0?'+':''}${Math.round(v)}`;
const noMap=(DATA.games||[]).filter(g=>!g.map_mode).length;
const oppD=DM.teams.find(t=>t.team===opp.team)||{topPicks:[],topBans:[],firstBanBlue:[],firstBanRed:[],heroStats:{},picks:0};
const oppPlayers=AN.players.filter(p=>p.team===opp.team).sort((a,b)=>b.impact-a.impact);
const myPlayers=my?AN.players.filter(p=>p.team===my.team):[];
const oppBans=buildBanRanking(opp.team,DM,3).slice(0,10);
const heroWr=h=>{const s=(oppD.heroStats||{})[h];return s&&s.n?pc(s.w/s.n)+'%':'—';};
const opt=(v,l,sel)=>`<option value="${esc(v)}"${sel?' selected':''}>${esc(l)}</option>`;
const teamOpts=codes.map(c=>{const t=TM.teams.find(x=>x.team===c);return opt(c,t.team_name+' ('+c+')',c===oppCode);}).join('');
const myOpts=`<option value="">Neutral</option>`+codes.filter(c=>c!==oppCode).map(c=>{const t=TM.teams.find(x=>x.team===c);return opt(c,t.team_name+' ('+c+')',c===myCode);}).join('');
PREP={opp:opp,my:my,oppBans:oppBans,oppPlayers:oppPlayers};
out.push(`<div class="pin" style="grid-column:1/-1"><div class="body phasebar prep-controls"><div><div class="kicker">Coach prep · opponent</div><h3 style="margin:.2em 0">${esc(opp.team_name)}</h3><div class="an-pct">${opp.games} games · ${opp.wins}–${opp.losses} · ${esc(opp.team)}</div></div><div class="prep-actions"><label>Opponent<select id="prepOpp" aria-label="Opponent">${teamOpts}</select></label><label>Our team<select id="prepTeam" aria-label="Our team">${myOpts}</select></label><button id="prepPrint" class="ghost" type="button">Print / PDF</button><button id="prepCsv" class="ghost" type="button">CSV</button><button id="prepLink" class="primary" type="button">Copy link</button></div></div></div>`);
const tiles=[['Rating',`${Math.round(opp.rating)} <span class="an-pct">(${Math.round(opp.ratingCI[0])}–${Math.round(opp.ratingCI[1])})</span>`],['Record',`${opp.wins}–${opp.losses}`],['Win%',`${pc(opp.winRate)}% <span class="an-pct">(${pc(opp.winCI.lo)}–${pc(opp.winCI.hi)})</span>`],['Form5',`${pc(opp.form5)}% · series ${pc(opp.form5Series)}%`],['SOS',`${Math.round(opp.sos)||'—'}`],['Blue / Red',`${opp.side.blue.w}–${opp.side.blue.n-opp.side.blue.w} / ${opp.side.red.w}–${opp.side.red.n-opp.side.red.w}`],['Win / loss dur',`${mins(opp.tempo.winSec)} / ${mins(opp.tempo.lossSec)}`],['Gold diff',`${signed(opp.dominance.goldDiff)}`],['Blowout',`${pc(opp.dominance.blowout)}%`]];
out.push(`<div class="pin" style="grid-column:1/-1"><div class="body"><div class="tiles">${tiles.map(([k,v])=>`<div class="tile"><b>${v}</b><span>${k}</span></div>`).join('')}</div><p class="an-pct" style="margin:.8em 0 0">Every rate is from completed games and carries n. No objective, timeline or pick-order data exists. Map mode is missing for ${noMap} games. Ban score is a proxy and ignores our draft.</p></div></div>`);
out.push(`<div class="pin" style="grid-column:1/-1"><div class="body"><div class="kicker">Draft tendencies</div><div class="prep-two"><div><div class="kicker">Likely picks</div><table style="min-width:280px"><tr><th>Hero</th><th>Picks</th><th>Pick rate</th><th>WR</th></tr>${(oppD.topPicks||[]).map(p=>`<tr><td><b>${esc(p.hero)}</b></td><td>${p.n}</td><td>${pc(p.share)}%</td><td>${heroWr(p.hero)}</td></tr>`).join('')||'<tr><td colspan="4">—</td></tr>'}</table></div><div><div class="kicker">Ban targets</div><table style="min-width:280px"><tr><th>Hero</th><th>Bans</th></tr>${(oppD.topBans||[]).map(p=>`<tr><td><b>${esc(p.hero)}</b></td><td>${p.n}</td></tr>`).join('')||'<tr><td colspan="2">—</td></tr>'}</table><div class="an-pct" style="margin-top:6px">First ban — blue: ${(oppD.firstBanBlue||[]).map(x=>esc(x.hero)+'×'+x.n).join(', ')||'—'}<br>First ban — red: ${(oppD.firstBanRed||[]).map(x=>esc(x.hero)+'×'+x.n).join(', ')||'—'}</div></div></div><div class="an-pct" style="margin-top:6px">Pick rate = picks ÷ ${opp.games} games.</div></div></div>`);
out.push(`<div class="pin" style="grid-column:1/-1"><div class="body"><div class="kicker">Ban threat ranking · proxy</div><div class="lscroll"><table style="min-width:820px"><tr><th>Hero</th><th>Pick presence</th><th>Contest rate</th><th>Opp WR</th><th>Score</th><th>Picks / bans</th><th>Pick n</th></tr>${oppBans.map(b=>`<tr><td><b>${esc(b.hero)}</b></td><td>${pc(b.presence)}%</td><td>${pc(b.contestRate)}%</td><td>${pc(b.wr)}%</td><td>${b.score.toFixed(2)}</td><td>${b.picks} / ${b.bans}</td><td>${b.n}</td></tr>`).join('')||'<tr><td colspan="7">No picked hero with n≥3.</td></tr>'}</table></div><p class="an-pct" style="margin:.6em 0 0">Score = opponent pick presence × opponent win rate on that hero. Pick presence = picks ÷ games; contest rate = (picks + bans) ÷ games and is shown only for context. The score does not use their bans, ignores our draft and pick order, and is not evidence of their draft intent.</p></div></div>`);
const ML={kda:'KDA',gpm:'GPM',damageShare:'Damage',kp:'KP',towerShare:'Tower'};
const keys=Object.keys(ML);
out.push(`<div class="pin" style="grid-column:1/-1"><div class="body"><div class="kicker">Player form · weaknesses and strengths</div><div class="lscroll"><table style="min-width:1080px"><tr><th>Player</th><th>Lane</th><th>GP</th><th>Impact</th><th>KDA</th><th>Dmg%</th><th>KP</th><th>Weakest</th><th>Strongest</th><th>Close WR</th><th>Pool</th><th>Top hero</th></tr>${oppPlayers.map(p=>{const best=keys.reduce((a,k)=>p.pct[k]>p.pct[a]?k:a,keys[0]);const worst=keys.reduce((a,k)=>p.pct[k]<p.pct[a]?k:a,keys[0]);const top=p.pool[0];return `<tr${p.small?' class="an-small"':''}><td><b>${esc(p.player)}</b></td><td>${esc(p.lane||'—')}</td><td>${p.games}</td><td>${p.impact.toFixed(0)}</td><td>${p.kda.toFixed(2)} <span class="an-pct">P${pc(p.pct.kda)}</span></td><td>${pc(p.damageShare)}% <span class="an-pct">P${pc(p.pct.damageShare)}</span></td><td>${pc(p.kp)}% <span class="an-pct">P${pc(p.pct.kp)}</span></td><td>${ML[worst]} P${pc(p.pct[worst])}</td><td>${ML[best]} P${pc(p.pct[best])}</td><td>${p.close.n?pc(p.close.winRate)+'% ('+p.close.wins+'/'+p.close.n+')':'—'}</td><td>${p.effectivePool}/${p.heroes}</td><td>${top?esc(top.hero)+' ('+top.games+' GP, '+pc(top.wr)+'%)':'—'}</td></tr>`;}).join('')||'<tr><td colspan="12">—</td></tr>'}</table></div><p class="an-pct" style="margin:.6em 0 0">Percentiles are within lane with a ${AN.priorWeight}-game prior; n&lt;${AN.minGames} is muted and indicative. Close = final kill diff ≤5 (proxy; no timeline exists).</p></div></div>`);
const weakMaps=(opp.maps||[]).filter(m=>m.n>=5&&anKnownMap(m.map)).slice().sort((a,b)=>a.wr-b.wr).slice(0,3);
const strongMaps=(opp.maps||[]).filter(m=>m.n>=5&&anKnownMap(m.map)).slice().sort((a,b)=>b.wr-a.wr).slice(0,3);
out.push(`<div class="pin" style="grid-column:1/-1"><div class="body"><div class="kicker">Team tendencies</div><div class="prep-two"><div><div class="kicker">Weak maps</div><table style="min-width:240px"><tr><th>Map</th><th>n</th><th>WR</th></tr>${weakMaps.map(m=>`<tr><td>${esc(m.map)}</td><td>${m.n}</td><td>${pc(m.wr)}%</td></tr>`).join('')||'<tr><td colspan="3">No map at n≥5.</td></tr>'}</table></div><div><div class="kicker">Strong maps</div><table style="min-width:240px"><tr><th>Map</th><th>n</th><th>WR</th></tr>${strongMaps.map(m=>`<tr><td>${esc(m.map)}</td><td>${m.n}</td><td>${pc(m.wr)}%</td></tr>`).join('')||'<tr><td colspan="3">No map at n≥5.</td></tr>'}</table></div></div><p class="an-pct" style="margin:.6em 0 0">Series close: ${opp.clutch.decider.w}–${opp.clutch.decider.n-opp.clutch.decider.w}; game 3: ${opp.clutch.game3.w}–${opp.clutch.game3.n-opp.clutch.game3.w}. Maps require n≥5.</p></div></div>`);
if(my){
const lanes=['EXP','JUNGLE','MID','GOLD','ROAM'];
const pickLane=(list,lane)=>list.filter(p=>p.lane===lane).slice().sort((a,b)=>b.games-a.games)[0];
const hrec=my.h2h[opp.team]||{n:0,w:0};
const mtiles=[['H2H (games)',`${hrec.w}–${hrec.n-hrec.w}`],['Rating',`${Math.round(my.rating)} vs ${Math.round(opp.rating)}`],['Form5',`${pc(my.form5)}% vs ${pc(opp.form5)}%`],['SOS',`${Math.round(my.sos)} vs ${Math.round(opp.sos)}`]];
out.push(`<div class="pin" style="grid-column:1/-1"><div class="body"><div class="kicker">Matchup explorer · ${esc(my.team_name)} vs ${esc(opp.team_name)}</div><div class="tiles">${mtiles.map(([k,v])=>`<div class="tile"><b>${v}</b><span>${k}</span></div>`).join('')}</div><div class="lscroll"><table style="min-width:940px"><tr><th>Lane</th><th>Us</th><th>Opp</th><th>KDA</th><th>Dmg%</th><th>Impact</th><th>Close WR</th></tr>${lanes.map(lane=>{const a=pickLane(myPlayers,lane),b=pickLane(oppPlayers,lane);return `<tr><td>${lane}</td><td>${a?esc(a.player):'—'}</td><td>${b?esc(b.player):'—'}</td><td>${a?a.kda.toFixed(2):'—'} / ${b?b.kda.toFixed(2):'—'}</td><td>${a?pc(a.damageShare)+'%':'—'} / ${b?pc(b.damageShare)+'%':'—'}</td><td>${a?a.impact.toFixed(0):'—'} / ${b?b.impact.toFixed(0):'—'}</td><td>${a&&a.close.n?pc(a.close.winRate)+'%':'—'} / ${b&&b.close.n?pc(b.close.winRate)+'%':'—'}</td></tr>`;}).join('')}</table></div><p class="an-pct" style="margin:.6em 0 0">Modal lane per player; no player-vs-player head-to-head exists in the source. H2H is game results, not series.</p></div></div>`);
}else{
out.push(`<div class="pin" style="grid-column:1/-1"><div class="body"><div class="kicker">Matchup explorer</div><p style="margin:.4em 0 0">Pick “Our team” above to unlock the head-to-head and lane-by-lane comparison.</p></div></div>`);
}
}else{
out.push(`<div class="pin" style="grid-column:1/-1"><div class="body"><div class="kicker">Coach prep</div><p>No completed games.</p></div></div>`);
}
}
if(S.view==='analytics'){
const dateByMid={};(DATA.schedule||[]).forEach(m=>{dateByMid[String(m.match_detail_id)]=m.iso_date||m.date||'';});
const dateOf=m=>dateByMid[String(m)]||'';
const part=k=>{if(ANA[k])return ANA[k];if(k==='AN'){const twr={};(DATA.team_games||[]).forEach(r=>{const x=twr[r.team]=twr[r.team]||{n:0,w:0};x.n++;if(r.win===1)x.w++;});Object.keys(twr).forEach(t=>{twr[t]=twr[t].n?twr[t].w/twr[t].n:0;});ANA[k]=buildPlayerMetrics(DATA.players,DATA.games,DATA.team_games,window.HERO_CLASSES||{},{canon:canonicalPlayer,dateOf,teamWinRate:twr});}if(k==='TM')ANA[k]=buildTeamMetrics(DATA.team_games||[],DATA.team_season||[],DATA.games||[],{dateOf,bootstraps:100,seed:7});if(k==='DM')ANA[k]=buildDraftMetrics(DATA.picks||[],DATA.bans||[],DATA.games||[],window.HERO_CLASSES||{},{minPair:3,dateOf});return ANA[k];};
const mins=v=>v?Math.round(v/6)/10+'m':'—';
const signed=v=>`${v>0?'+':''}${Math.round(v)}`;
const pp=v=>`${v>0?'+':''}${Math.round(v*100)}pp`;
const pc=v=>Math.round(v*100);
const tabs=[['players','Players'],['teams','Teams'],['draft','Draft']].map(([k,l])=>`<button data-antab="${k}" aria-pressed="${S.anTab===k?'true':'false'}">${l}</button>`).join('');
out.push(`<div class="pin" style="grid-column:1/-1"><div class="body phasebar"><div><div class="kicker">Analytics</div><h3 style="margin:.25em 0">${S.anTab==='teams'?'Team strength':S.anTab==='draft'?'Draft intelligence':'Player impact'}</h3></div><div class="seg" role="group" aria-label="Analytics view">${tabs}</div></div></div>`);
if(S.anTab==='players'){
const AN=part('AN');
const lanes=['',...AN.lanes];
const rows=AN.players.filter(p=>!S.anLane||p.lane===S.anLane);
const maxImpact=Math.max(1,...rows.map(p=>Math.abs(p.impact)));
const laneBtn=l=>`<button data-anlane="${esc(l)}" aria-pressed="${S.anLane===l?'true':'false'}">${l||'All lanes'}</button>`;
const w=AN.weights;
out.push(`<div class="pin" style="grid-column:1/-1"><div class="body"><div class="phasebar"><div class="kicker">Lane filter</div><div class="seg" role="group" aria-label="Lane filter">${lanes.map(laneBtn).join('')}</div></div></div></div>`);
out.push(`<div class="pin" style="grid-column:1/-1"><div class="body"><div class="kicker">Method · every number shows its sample</div><p style="max-width:900px;margin:.4em 0 0">Impact = ${Math.round(w.damageShare*100)}% damage share + ${Math.round(w.kp*100)}% kill participation + ${Math.round(w.goldShare*100)}% gold share + ${Math.round(w.towerShare*100)}% tower share − ${Math.round(-w.deathShare*100)}% death share. Each component is a percentile within lane, shrunk toward the lane mean with a ${AN.priorWeight}-game prior. Win rates use a 95% Wilson interval. Rows with fewer than ${AN.minGames} games are muted and indicative only.</p></div></div>`);
out.push(`<div class="pin" style="grid-column:1/-1"><div class="body"><div class="kicker">${rows.length} players · ${AN.lanes.length} lanes</div><div class="lscroll"><table style="min-width:1040px"><tr><th>#</th><th>Player</th><th>Team</th><th>Lane</th><th>GP</th><th>Impact</th><th>KDA</th><th>GPM</th><th>Dmg%</th><th>KP</th><th>Win% (95% CI)</th><th>Form</th></tr>${rows.map((p,i)=>`<tr${p.small?` class="an-small" title="Small sample (n<${AN.minGames}) — indicative only"`:''}><td>${i+1}</td><td><span data-p="${esc(p.player)}" tabindex="0" style="cursor:pointer;font-weight:600">${esc(p.player)}</span></td><td>${esc(p.team)}</td><td>${esc(p.lane||'—')}</td><td>${p.games}</td><td style="min-width:120px"><div style="display:flex;gap:6px;align-items:center"><span class="bar"><span style="width:${Math.max(0,Math.round(p.impact/maxImpact*100))}%"></span></span><b>${p.impact.toFixed(0)}</b></div></td><td>${p.kda.toFixed(2)}<span class="an-pct">P${pc(p.pct.kda)}</span></td><td>${Math.round(p.gpm)}<span class="an-pct">P${pc(p.pct.gpm)}</span></td><td>${pc(p.damageShare)}%<span class="an-pct">P${pc(p.pct.damageShare)}</span></td><td>${pc(p.kp)}%<span class="an-pct">P${pc(p.pct.kp)}</span></td><td>${pc(p.winRate)}% <span class="an-pct">(${pc(p.winCI.lo)}–${pc(p.winCI.hi)})</span></td><td>${p.formDelta>=0?'+':''}${p.formDelta.toFixed(2)}</td></tr>`).join('')||'<tr><td colspan="12">No games.</td></tr>'}</table></div></div></div>`);
}else if(S.anTab==='teams'){
const TM=part('TM');
out.push(`<div class="pin" style="grid-column:1/-1"><div class="body"><div class="kicker">Method · relative strength with uncertainty</div><p style="max-width:980px;margin:.4em 0 0">Bradley-Terry on one paired observation per game with a 1-1 prior against an average team and ${TM.method.bootstraps} bootstrap resamples. Each bootstrap resamples whole games so opponents stay paired. Rating = 1500 + 400·log10(strength), relative to this season only. SOS is the mean fitted opponent rating. Form5 is the last five games by date; Blue/Red use the recorded sides; tempo and clutch use completed games; Series close is the last game of a series (including 2-0 closeouts), while G3 is game 3 only. Intervals are wide at roughly 40 games per team. Game W–L and Series W–L are separate contracts; both use completed regular-season rows.</p></div></div>`);
out.push(`<div class="pin" style="grid-column:1/-1"><div class="body"><div class="kicker">${TM.teams.length} teams · ${TM.teams.reduce((s,t)=>s+t.games,0)} team-games</div><div class="lscroll"><table style="min-width:1320px"><tr><th>Team</th><th>Games GP</th><th>Game W-L</th><th>Series W-L</th><th>Win% (95% CI)</th><th>Rating (95% CI)</th><th>SOS</th><th>Form5 games</th><th>Form5 series</th><th>Blue</th><th>Red</th><th>Win dur</th><th>Loss dur</th><th>Gold diff</th><th>Blowout</th><th>G3</th><th>Series close</th></tr>${TM.teams.map(t=>`<tr><td><b>${esc(t.team_name)}</b> <span class="an-pct">${esc(t.team)}</span></td><td>${t.games}</td><td>${t.wins}-${t.losses}</td><td>${t.seriesWins}-${t.seriesLosses}</td><td>${pc(t.winRate)}% <span class="an-pct">(${pc(t.winCI.lo)}–${pc(t.winCI.hi)})</span></td><td>${Math.round(t.rating)} <span class="an-pct">(${Math.round(t.ratingCI[0])}–${Math.round(t.ratingCI[1])})</span></td><td>${Math.round(t.sos)||'—'}</td><td>${pc(t.form5)}%</td><td>${pc(t.form5Series)}%</td><td>${t.side.blue.w}–${t.side.blue.n-t.side.blue.w}</td><td>${t.side.red.w}–${t.side.red.n-t.side.red.w}</td><td>${mins(t.tempo.winSec)}</td><td>${mins(t.tempo.lossSec)}</td><td>${signed(t.dominance.goldDiff)}</td><td>${pc(t.dominance.blowout)}%</td><td>${t.clutch.game3.w}–${t.clutch.game3.n-t.clutch.game3.w}</td><td>${t.clutch.decider.w}–${t.clutch.decider.n-t.clutch.decider.w}</td></tr>`).join('')}</table></div></div></div>`);
const sorted=[...TM.teams].sort((a,b)=>b.rating-a.rating);
out.push(`<div class="pin" style="grid-column:1/-1"><div class="body"><div class="kicker">Head-to-head · row wins–losses vs column</div><div class="lscroll"><table style="min-width:860px"><tr><th>Team</th>${sorted.map(x=>`<th>${esc(x.team)}</th>`).join('')}</tr>${sorted.map(a=>`<tr><td><b>${esc(a.team)}</b></td>${sorted.map(b=>{if(a.team===b.team)return '<td>—</td>';const h=a.h2h[b.team]||{n:0,w:0};return `<td>${h.w}–${h.n-h.w}</td>`;}).join('')}</tr>`).join('')}</table></div><p class="an-pct" style="margin:.6em 0 0">Game results, not series. A blank cell means the teams have not met.</p></div></div>`);
}else{
const DM=part('DM');
const noMap=(DATA.games||[]).filter(g=>!g.map_mode).length;
const heroRows=[...DM.heroes].sort((a,b)=>(b.picks+b.bans)-(a.picks+a.bans)||a.hero.localeCompare(b.hero));
const topLane=h=>Object.keys(h.lanes).sort((a,b)=>h.lanes[b]-h.lanes[a]||a.localeCompare(b))[0]||'—';
const pairRows=DM.pairs.slice(0,20),ctrRows=DM.counters.slice(0,20);
const mvRows=[...DM.movement.slice(0,8),...DM.movement.slice(-8).reverse()].filter((x,i,a)=>a.findIndex(y=>y.hero===x.hero)===i);
out.push(`<div class="pin" style="grid-column:1/-1"><div class="body"><div class="stats" style="display:flex;gap:30px;flex-wrap:wrap"><div><div class="kicker">Heroes seen</div><b style="font-family:var(--font-mono);font-size:22px">${DM.heroes.length}</b></div><div><div class="kicker">Pairs n≥3</div><b style="font-family:var(--font-mono);font-size:22px">${DM.pairs.length}</b></div><div><div class="kicker">Counters n≥3</div><b style="font-family:var(--font-mono);font-size:22px">${DM.counters.length}</b></div><div><div class="kicker">Maps</div><b style="font-family:var(--font-mono);font-size:22px">${DM.maps.length}</b></div><div><div class="kicker">Archetypes</div><b style="font-family:var(--font-mono);font-size:22px">${DM.compositions.length}</b></div></div><p style="max-width:1000px;margin:1em 0 0">Pairs and counters are descriptive, not causal: synergy compares a pair's win rate with the average of the two heroes' individual win rates; counters compare hero A against B with the average of A's win rate and B's loss rate. Compositions use hero classes (frontline = Tank/Fighter; damage = 3+ physical or 3+ magic; CC = specialties mentioning Crowd Control, Initiator or Engage). Map mode is missing for ${noMap} games, shown as Unknown.</p></div></div>`);
out.push(`<div class="pin" style="grid-column:1/-1"><div class="body"><div class="kicker">Meta movement · last two non-empty 7-day date windows</div><div class="lscroll"><table style="min-width:680px"><tr><th>Hero</th><th>Recent presence/game</th><th>Previous</th><th>Delta</th><th>Games (recent)</th></tr>${mvRows.map(m=>`<tr><td>${esc(m.hero)}</td><td>${Math.round(m.recent*100)}%</td><td>${Math.round(m.previous*100)}%</td><td>${m.delta>0?'+':''}${Math.round(m.delta*100)}pp</td><td>${m.games}</td></tr>`).join('')||'<tr><td colspan="5">Not enough date windows.</td></tr>'}</table></div><p class="an-pct" style="margin:.6em 0 0">Presence = (picks + bans) ÷ games in that date window. Windows start at the first game date and are not official competition weeks; this comparison is ${DM.movementInfo&&DM.movementInfo.adjacent?'adjacent':'non-adjacent'}. The final window is a small sample; treat it as a signal, not proof.</p></div></div>`);
out.push(`<div class="pin" style="grid-column:1/-1"><div class="body"><div class="kicker">Heroes · picks + bans · sorted by presence</div><div class="lscroll" style="max-height:520px"><table style="min-width:820px"><tr><th>Hero</th><th>Role</th><th>Damage</th><th>Picks</th><th>Bans</th><th>P+B</th><th>WR (95% CI)</th><th>Flex</th><th>Top lane</th></tr>${heroRows.map(h=>`<tr><td><b>${esc(h.hero)}</b></td><td>${esc(h.role||'—')}</td><td>${esc(h.damage||'—')}</td><td>${h.picks}</td><td>${h.bans}</td><td>${h.picks+h.bans}</td><td>${pc(h.winRate)}% <span class="an-pct">(${pc(h.winCI.lo)}–${pc(h.winCI.hi)})</span></td><td>${h.flex}</td><td>${esc(topLane(h))}</td></tr>`).join('')}</table></div></div></div>`);
out.push(`<div class="pin" style="grid-column:1/-1"><div class="body"><div class="kicker">Same-team pairs · n≥3 · ${pairRows.length} most observed</div><div class="lscroll"><table style="min-width:560px"><tr><th>Pair</th><th>n</th><th>WR</th><th>vs baseline</th></tr>${pairRows.map(p=>`<tr><td>${esc(p.a)} + ${esc(p.b)}</td><td>${p.n}</td><td>${pc(p.wr)}%</td><td>${pp(p.delta)}</td></tr>`).join('')||'<tr><td colspan="4">No pairs at n≥3.</td></tr>'}</table></div></div></div>`);
out.push(`<div class="pin" style="grid-column:1/-1"><div class="body"><div class="kicker">Opposing pairs · n≥3 · ${ctrRows.length} most observed</div><div class="lscroll"><table style="min-width:640px"><tr><th>Matchup</th><th>n</th><th>First hero WR</th><th>vs baseline</th></tr>${ctrRows.map(p=>`<tr><td>${esc(p.a)} vs ${esc(p.b)}</td><td>${p.n}</td><td>${pc(p.wr)}%</td><td>${pp(p.delta)}</td></tr>`).join('')||'<tr><td colspan="4">No counters at n≥3.</td></tr>'}</table></div></div></div>`);
out.push(`<div class="pin" style="grid-column:1/-1"><div class="body"><div class="kicker">Composition archetypes · derived from hero classes</div><div class="lscroll"><table style="min-width:620px"><tr><th>Archetype</th><th>n</th><th>WR (95% CI)</th><th>Avg CC</th></tr>${DM.compositions.map(c=>`<tr><td>${esc(c.damage)} · ${c.frontline} front</td><td>${c.n}</td><td>${pc(c.wr)}% <span class="an-pct">(${pc(c.winCI.lo)}–${pc(c.winCI.hi)})</span></td><td>${c.avgCC.toFixed(1)}</td></tr>`).join('')||'<tr><td colspan="4">No complete drafts.</td></tr>'}</table></div></div></div>`);
out.push(`<div class="pin" style="grid-column:1/-1"><div class="body"><div class="kicker">Map meta · completed games</div><div class="lscroll"><table style="min-width:720px"><tr><th>Map</th><th>Games</th><th>Blue WR</th><th>Avg duration</th><th>Top picks</th></tr>${DM.maps.map(m=>`<tr><td>${esc(m.map)}</td><td>${m.games}</td><td>${pc(m.blueWR)}%</td><td>${mins(m.avgSec)}</td><td>${m.topHeroes.map(h=>`${esc(h.hero)}×${h.n}`).join(', ')}</td></tr>`).join('')}</table></div></div></div>`);
out.push(`<div class="pin" style="grid-column:1/-1"><div class="body"><div class="kicker">Team draft fingerprints · HHI = pick concentration</div><div class="lscroll"><table style="min-width:1120px"><tr><th>Team</th><th>Picks</th><th>Unique</th><th>HHI</th><th>Top picks</th><th>Top bans</th><th>First ban (blue)</th><th>First ban (red)</th><th>Pocket picks</th></tr>${DM.teams.map(t=>`<tr><td><b>${esc(t.team)}</b></td><td>${t.picks}</td><td>${Object.keys(t.heroes).length}</td><td>${t.hhi.toFixed(2)}</td><td>${t.topPicks.map(p=>`${esc(p.hero)}×${p.n}`).join(', ')}</td><td>${t.topBans.map(p=>`${esc(p.hero)}×${p.n}`).join(', ')}</td><td>${t.firstBanBlue.map(p=>`${esc(p.hero)}×${p.n}`).join(', ')||'—'}</td><td>${t.firstBanRed.map(p=>`${esc(p.hero)}×${p.n}`).join(', ')||'—'}</td><td>${t.pocketPicks.length?t.pocketPicks.map(p=>`${esc(p.hero)}×${p.n}`).join(', '):'—'}</td></tr>`).join('')}</table></div><p class="an-pct" style="margin:.6em 0 0">HHI is the sum of squared pick shares; higher means a more concentrated pool. Pocket picks require n≥3 and a team share at least twice the league share.</p></div></div>`);
}
}
board.innerHTML=out.join('')||'';emptyEl.hidden=out.length>0;countEl.textContent=out.length+' pins';
board.querySelectorAll('.pin').forEach(p=>io.observe(p));
board.querySelectorAll('[data-p]').forEach(b=>b.onclick=()=>showP(b.dataset.p));
const ovb=document.getElementById('ovPick');if(ovb)ovb.onclick=openOvSel;
board.querySelectorAll('.lrow').forEach(r=>{r.style.cursor='pointer';r.onclick=()=>showP(r.querySelector('b').textContent);});
board.querySelectorAll('[data-m]').forEach(b=>b.onclick=()=>showM(b.dataset.m));
board.querySelectorAll('[data-ovhero]').forEach(b=>b.onclick=()=>(b.dataset.scope==='global'?stHeroDrill:ovHeroDrill)(b.dataset.ovhero));
board.querySelectorAll('[data-ovemb]').forEach(b=>b.onclick=()=>(b.dataset.scope==='global'?stEmbDrill:ovEmbDrill)(b.dataset.ovemb));
board.querySelectorAll('[data-ovtal]').forEach(b=>b.onclick=()=>(b.dataset.scope==='global'?stTalDrill:ovTalDrill)(b.dataset.ovtal));
board.querySelectorAll('[data-ovitem]').forEach(b=>b.onclick=()=>stItemDrill(b.dataset.ovitem));
board.querySelectorAll('[data-ovopp]').forEach(b=>b.onclick=()=>ovOppDrill(b.dataset.ovopp));
board.querySelectorAll('[data-more]').forEach(b=>b.onclick=()=>{const n=+b.dataset.more||24;if(b.dataset.sec==='po')S.plimit+=n;else S.mlimit+=n;render();});
board.querySelectorAll('[data-phase]').forEach(b=>b.onclick=()=>{S.phase=b.dataset.phase;render();});
board.querySelectorAll('[data-stat]').forEach(b=>b.onclick=()=>{S.stat=b.dataset.stat;render();});
board.querySelectorAll('[data-anlane]').forEach(b=>b.onclick=()=>{S.anLane=b.dataset.anlane;render();});
board.querySelectorAll('[data-antab]').forEach(b=>b.onclick=()=>{S.anTab=b.dataset.antab;render();});
const prepOppEl=document.getElementById('prepOpp');if(prepOppEl)prepOppEl.onchange=()=>{S.prepOpp=prepOppEl.value;render();};
const prepTeamEl=document.getElementById('prepTeam');if(prepTeamEl)prepTeamEl.onchange=()=>{S.prepTeam=prepTeamEl.value;render();};
const prepPrintEl=document.getElementById('prepPrint');if(prepPrintEl)prepPrintEl.onclick=()=>window.print();
const prepCsvEl=document.getElementById('prepCsv');if(prepCsvEl)prepCsvEl.onclick=()=>{if(!PREP)return;const rows=[['section','name','games','value1','value2','value3']],o=PREP.opp;rows.push(['team',o.team,o.games,(o.winRate*100).toFixed(1),Math.round(o.rating),Math.round(o.sos)]);PREP.oppBans.forEach(b=>rows.push(['ban',b.hero,b.n,(b.presence*100).toFixed(1),(b.wr*100).toFixed(1),b.score.toFixed(3)]));PREP.oppPlayers.forEach(p=>rows.push(['player',p.player,p.games,p.kda.toFixed(2),p.impact.toFixed(1),p.close.n?(p.close.winRate*100).toFixed(1):'']));const csv='\ufeff'+rows.map(r=>r.map(x=>'"'+String(x).replace(/"/g,'""')+'"').join(',')).join('\n');const blob=new Blob([csv],{type:'text/csv;charset=utf-8'}),a=document.createElement('a');a.href=URL.createObjectURL(blob);a.download='prep_'+o.team+'.csv';a.click();setTimeout(()=>URL.revokeObjectURL(a.href),1000);};
const prepLinkEl=document.getElementById('prepLink');if(prepLinkEl)prepLinkEl.onclick=()=>{if(!PREP)return;const url=location.href.split('#')[0]+'#view=prep&opp='+encodeURIComponent(PREP.opp.team)+(PREP.my?'&team='+encodeURIComponent(PREP.my.team):'');if(navigator.clipboard&&navigator.clipboard.writeText)navigator.clipboard.writeText(url).then(()=>{prepLinkEl.textContent='Copied';setTimeout(()=>{prepLinkEl.textContent='Copy link';},1200);}).catch(()=>prompt('Copy this link',url));else prompt('Copy this link',url);};
try{const hp=new URLSearchParams();hp.set('view',S.view);if(S.view==='prep'){hp.set('opp',S.prepOpp||'');if(S.prepTeam)hp.set('team',S.prepTeam);}if(S.view==='analytics'){hp.set('tab',S.anTab);if(S.anLane)hp.set('lane',S.anLane);}if(S.view==='players'&&S.q)hp.set('q',S.q);if(S.view==='matches'&&S.team)hp.set('filterTeam',S.team);history.replaceState(null,'','#'+hp.toString());}catch(e){}
board.querySelectorAll('[data-ts]').forEach(b=>b.onclick=()=>{const [t,k]=b.dataset.ts.split(':');const str=k==='hero'||k==='player'||k==='team'||k==='match'||k==='mvp'||k==='date';if(S.tsort.t===t&&S.tsort.k===k)S.tsort.d*=-1;else S.tsort={t,k,d:str?1:-1};render();});
wireCharts();wireBracket();}
function normId(s){return String(s||'').toLowerCase().replace(/[^a-z0-9]/g,'');}
function offOf(n){const m={};DATA.season.forEach(s=>{m[String(s.player||'').toLowerCase()]=s;});
const GALIAS=(typeof window!=='undefined'&&window.ALIASES&&window.ALIASES.globalAlias)||{};
const l=String(n||'').toLowerCase();return m[l]||m[GALIAS[l]||'']||null;}
/* PLAYER IDENTITY — one real player = one canonical roster identity.
   Series MVP names come from Liquipedia match pages while game rows use live-API
   IGNs, so the same person can appear under different spellings. Verified (public):
   Coolfire->Joshuaa (reddit r/mobilelegendsesports 2026-08-30 "joshua(coolfire)";
   both MVP rows are NAVI matches; Joshuaa is the NAVI jungler per navi.gg + MLDB),
   JOOOOO->Kevinn (bo3.gg lists both "JOOOOO (Yonathan Chin)" and
   "Kevinn (Yonathan Chin)" for TLID; teamliquid.com TLID roster lists JOOOOO;
   Keven Julio Keven is a different person — TLID gold laner),
   Sutsujin->Arthur (Liquipedia "Arthur 'Sutsujin' Sunarkho", MLDB, RRQ Hoshi),
    Lynchh->Joshua (Liquipedia: Joshua "Lynchh" Nicholas, EXP Laner, RRQ Hoshi
    active roster; id-mpl.com RRQ roster lists JOSHUA as EXP Lane and live-API
    game rows for the MVP series use IGN Joshua; single Joshua on RRQ).
   Mechanical (MVP-row teams intersect the roster team; re-verify if contested):
   A B O Y->Aboyy, Jizeezeze->Jiizee, Maykids->Maykidss, Moreno->Morenooo,
   Rendyy->Rendyyy. Roster spelling duplicate from the live API: MAYKIDSS->Maykidss.
   Deliberately NOT merged: Joshua (RRQ) vs Joshuaa (NAVI) — different people.
   To add a future alias: add one normalized->canonical entry to PLAYER_ALIAS.
   Every aggregation/display path goes through canonicalPlayer(), so no second
   identity can arise from a new spelling. */
const PLAYER_ALIAS=(typeof window!=='undefined'&&window.ALIASES&&window.ALIASES.playerAlias)||{};
const ROSTER_SPELLING=(typeof window!=='undefined'&&window.ALIASES&&window.ALIASES.rosterSpelling)||{};
function rosterCanon(n){const u=normId(n);
const gp=[...new Set((DATA.players||[]).map(r=>r.player))].filter(p=>normId(p)===u);
if(gp.length===1)return gp[0];
if(gp.length>1){const pref=ROSTER_SPELLING[u];if(pref&&gp.includes(pref))return pref;return gp[0];}
const ss=[...new Set((DATA.season||[]).map(s=>s.player))].filter(p=>normId(p)===u);
if(ss.length)return ss[0];
return null;}
function canonicalPlayer(n){const hit=rosterCanon(n);if(hit)return hit;return PLAYER_ALIAS[normId(n)]||n;}
function mvpSources(){const m={};(DATA.matches||[]).forEach(x=>{if(!x.liq_mvp)return;const c=canonicalPlayer(x.liq_mvp);(m[c]=m[c]||new Set()).add(x.liq_mvp);});return m;}
function defaultOv(){const t=[...DATA.season].filter(s=>+s.total_games>0).sort((a,b)=>+b.avg_kda-+a.avg_kda)[0];
if(!t)return 'Joshuaa';const l=String(t.player).toLowerCase();
const hit=agg().find(o=>o.player.toLowerCase()===l||normId(o.player)===normId(t.player));return hit?hit.player:'Joshuaa';}
function gameInfo(r){const gm=(DATA.games||[]).find(g=>String(g.match_detail_id)===String(r.match_detail_id)&&String(g.game_no)===String(r.game_no))||{};
const sc=(DATA.schedule||[]).find(s=>String(s.match_detail_id)===String(r.match_detail_id))||{};
const pa=gm.team_a?gm.team_a===r.team:sc.team_a===r.team;
const won=gm.winner?(gm.winner==='team_a'?!!pa:!pa):null;
const opp=gm.team_a?(pa?gm.team_b:gm.team_a):(sc.team_a?(sc.team_a===r.team?sc.team_b:sc.team_a):'');
return {gm:gm,opp:opp,won:won,side:pa?(gm.team_a_side||''): (gm.team_b_side||''),date:sc.date||sc.iso_date||'',iso:sc.iso_datetime||''};}
let chartSeq=0;
function trendChart(games){if(!games.length)return '<p>No scored games</p>';
const W=560,H=150,PL=36,PR=10,PT=10,PB=22,id='tc'+(++chartSeq);
const vs=games.map(g=>g.v),max=Math.max.apply(null,vs.concat([1])),min=Math.min.apply(null,vs.concat([0]));
const X=i=>PL+i/Math.max(1,vs.length-1)*(W-PL-PR),Y=v=>PT+(1-(v-min)/Math.max(1e-9,max-min))*(H-PT-PB);
const pts=vs.map((v,i)=>X(i).toFixed(1)+','+Y(v).toFixed(1)).join(' ');
const avg=vs.reduce((a,b)=>a+b,0)/vs.length;
let grid='';for(let g=0;g<=3;g++){const v=min+(max-min)*g/3,y=Y(v).toFixed(1);
grid+='<line x1="'+PL+'" x2="'+(W-PR)+'" y1="'+y+'" y2="'+y+'" stroke="currentColor" opacity=".12"/><text x="'+(PL-5)+'" y="'+(+y+3)+'" text-anchor="end" font-size="9" fill="currentColor" opacity=".55">'+v.toFixed(1)+'</text>';}
const dots=vs.map((v,i)=>'<circle cx="'+X(i).toFixed(1)+'" cy="'+Y(v).toFixed(1)+'" r="3.5" data-i="'+i+'"/>').join('');
const gid=id+'g';
const data=esc(JSON.stringify(games.map(g=>({d:g.date,o:g.opp,h:g.hero,k:g.kda,w:g.won}))));
return '<div class="tchart" id="'+id+'" style="position:relative" data-games="'+data+'">'
+'<svg viewBox="0 0 '+W+' '+H+'" style="width:100%;height:auto;display:block" role="img" aria-label="KDA per game trend"><defs><linearGradient id="'+gid+'" x1="0" y1="0" x2="0" y2="1"><stop offset="0" stop-color="currentColor" stop-opacity=".22"/><stop offset="1" stop-color="currentColor" stop-opacity="0"/></linearGradient></defs>'+grid
+'<polygon points="'+PL+','+(H-PB)+' '+pts+' '+(W-PR)+','+(H-PB)+'" fill="url(#'+gid+')"/>'
+'<polyline points="'+pts+'" fill="none" stroke="currentColor" stroke-width="2" stroke-linejoin="round" stroke-linecap="round"/>'
+'<line x1="'+PL+'" x2="'+(W-PR)+'" y1="'+Y(avg).toFixed(1)+'" y2="'+Y(avg).toFixed(1)+'" stroke="currentColor" stroke-dasharray="4 3" opacity=".4"/>'
+'<g fill="var(--bg)" stroke="currentColor" stroke-width="2">'+dots+'</g>'
+'<line class="xhair" y1="'+PT+'" y2="'+(H-PB)+'" stroke="currentColor" opacity=".35" style="display:none"/>'
+'<rect class="hoverzone" x="'+PL+'" y="'+PT+'" width="'+(W-PL-PR)+'" height="'+(H-PT-PB)+'" fill="transparent"/></svg>'
+'<div class="ttip" style="display:none;position:absolute;pointer-events:none;background:rgba(20,20,18,.95);border:1px solid var(--line);border-radius:8px;padding:8px 10px;font-size:11.5px;line-height:1.5;white-space:nowrap;z-index:5"></div></div>';}
function wireCharts(){document.querySelectorAll('.tchart').forEach(el=>{
const svg=el.querySelector('svg'),tip=el.querySelector('.ttip'),hair=el.querySelector('.xhair');
let games=[];try{games=JSON.parse(el.dataset.games||'[]');}catch(e){}
const dots=[...svg.querySelectorAll('circle')];
function show(i){const g=games[i];if(!g)return;const c=dots[i];if(!c)return;
const cx=+c.getAttribute('cx'),r=el.getBoundingClientRect(),sx=r.width/560;
hair.setAttribute('x1',cx);hair.setAttribute('x2',cx);hair.style.display='';
tip.style.display='';tip.innerHTML='<b>G'+(i+1)+' · '+esc(g.h)+'</b><br>'+esc(g.d)+' vs '+esc(g.o)+' · '+(g.w===null?'–':(g.w?'W':'L'))+' · KDA '+g.k;
const tw=tip.offsetWidth;let lx=cx*sx+10;if(lx+tw>r.width-4)lx=cx*sx-tw-10;
tip.style.left=lx+'px';tip.style.top='8px';}
function hide(){tip.style.display='none';hair.style.display='none';}
svg.querySelector('.hoverzone').addEventListener('mousemove',e=>{const r=svg.getBoundingClientRect();
const mx=(e.clientX-r.left)/r.width*560;let best=0,bd=1e9;dots.forEach((c,i)=>{const d=Math.abs(+c.getAttribute('cx')-mx);if(d<bd){bd=d;best=i;}});show(best);});
svg.querySelector('.hoverzone').addEventListener('mouseleave',hide);
dots.forEach((c,i)=>{c.setAttribute('tabindex','0');c.setAttribute('role','img');
c.addEventListener('focus',()=>show(i));c.addEventListener('blur',hide);});});}

function fmtDur(s){s=Math.round(+s||0);if(!isFinite(s)||s<0)s=0;if(s>3*3600)return '—';const t=Math.floor(s/60)+':'+String(s%60).padStart(2,'0');return t.length>6?'—':t;}
function ovHTML(){const all=agg();if(!S.ov||!all.find(o=>o.player===S.ov))S.ov=defaultOv();
const name=S.ov,g=all.find(o=>o.player===name)||{},s=offOf(name)||{};
const A=window.ASSETS||{heroes:{},items:{},emblems:{},runes:{}};
const u=PICON(name);
const rows=ovRows(name);
const scored=rows.filter(x=>x.info.won!==null);
const wins=scored.filter(x=>x.info.won).length;
const wr=scored.length?Math.round(wins/scored.length*100):0;
const durS=rows.map(x=>+x.info.gm.duration_sec||0).filter(v=>v>0&&v<=3*3600);
const avgD=durS.length?durS.reduce((a,b)=>a+b,0)/durS.length:0;
const mids=[...new Set(rows.map(x=>String(x.r.match_detail_id)))];let mw=0,ml=0;
mids.forEach(id=>{const sc=(DATA.schedule||[]).find(s=>String(s.match_detail_id)===id);
if(!sc||sc.status!=='completed')return;const sa=+sc.score_a,sb=+sc.score_b;
if(!isFinite(sa)||!isFinite(sb)||sa===sb)return;
if((sa>sb?sc.team_a:sc.team_b)===g.team)mw++;else ml++;});
const mwr=(mw+ml)?Math.round(mw/(mw+ml)*100):0;
const kdas=rows.map(x=>{const k=x.r.kills??x.r.kill??0,d=x.r.deaths??x.r.death??0,a=x.r.assists??x.r.assist??0;return (k+a)/Math.max(1,d);});
const totG=rows.reduce((a,x)=>a+(x.r.gold||0),0),totD=rows.reduce((a,x)=>a+(x.r.hero_damage||0),0),
totT=rows.reduce((a,x)=>a+(x.r.damage_taken||0),0),totTw=rows.reduce((a,x)=>a+(x.r.tower_damage||0),0);
const byHero={};rows.forEach(x=>{const h=x.r.hero||'?';(byHero[h]=byHero[h]||{n:0,w:0,k:0,d:0,a:0,gpm:0}).n++;
if(x.info.won===true)byHero[h].w++;byHero[h].k+=x.r.kills??x.r.kill??0;byHero[h].d+=x.r.deaths??x.r.death??0;byHero[h].a+=x.r.assists??x.r.assist??0;byHero[h].gpm+=x.r.gold_per_min||0;});
const heroRows=Object.entries(byHero).map(([h,o])=>({h:h,wr:o.n?Math.round(o.w/o.n*100):0}))
.sort((a,b)=>b.wr-a.wr);
const heroTbl=Object.entries(byHero).map(([h,o])=>{const hi=A.heroes&&A.heroes[h];
return `<tr><td data-ovhero="${esc(h)}" tabindex="0" title="View ${esc(h)} games"><span class="hcell">${hi?`<img src="${esc(hi)}" alt="" loading="lazy" onerror="this.remove()">`:''}${esc(h)}</span></td><td>${esc(o.n)}</td><td><div style="display:flex;gap:6px;align-items:center"><span class="wrbar"><i style="width:${o.n?Math.round(o.w/o.n*100):0}%"></i></span>${o.n?Math.round(o.w/o.n*100):0}%</div></td><td>${(o.k/Math.max(1,o.n)).toFixed(1)}/${(o.d/Math.max(1,o.n)).toFixed(1)}/${(o.a/Math.max(1,o.n)).toFixed(1)}</td><td>${Math.round(o.gpm/Math.max(1,o.n))}</td></tr>`;}).join('');
const sides={};rows.forEach(x=>{const sd=(x.info.side||'').toLowerCase()||'unknown';(sides[sd]=sides[sd]||{w:0,n:0}).n++;if(x.info.won===true)sides[sd].w++;});
const sideTbl=Object.entries(sides).map(([sd,o])=>`<tr><td style="text-transform:capitalize">${esc(sd)} side</td><td>${o.n}</td><td>${o.n?Math.round(o.w/o.n*100):0}%</td></tr>`).join('');
const opps={};rows.forEach(x=>{const o=x.info.opp||'?';(opps[o]=opps[o]||{w:0,n:0}).n++;if(x.info.won===true)opps[o].w++;});
const oppTbl=Object.entries(opps).sort((a,b)=>b[1].n-a[1].n).map(([o,v])=>`<tr><td data-ovopp="${esc(o)}" tabindex="0" title="View games vs ${esc(o)}"><img src="${TICON(o)}" alt="" loading="lazy" style="width:20px;height:20px;object-fit:contain;vertical-align:-5px" onerror="this.remove()"> ${esc(o)}</td><td>${v.n}</td><td>${v.w}-${v.n-v.w}</td></tr>`).join('');
const useCounts=heroUseCounts(rows);
const itemGrid=itemGroups(useCounts.item).map(gr=>`<div class="et-label">${esc(gr.label)}</div><div class="itemgrid">${gr.entries.map(([id,c])=>itemCell(id,c)).join('')}</div>`).join('')||'<p>No item data</p>';
const embHtml=topEntries(useCounts.emb,7).map(([id,c])=>embBadge(id,c)).join('')||'<p>No emblem data</p>';
const talHtml=topEntries(useCounts.tal,8).map(([id,c])=>talBadge(id,c)).join('')||'<p>No talent data</p>';
const mvps=(DATA.matches||[]).filter(m=>m.liq_mvp&&samePlayer(m.liq_mvp,name));
const mvpHtml=mvps.length?mvps.map(m=>{const sc=(DATA.schedule||[]).find(s=>String(s.match_detail_id)===String(m.match_detail_id))||{};return `<tr><td>${esc(sc.date||sc.iso_date||'')}</td><td>${esc(m.team_a)} vs ${esc(m.team_b)}</td></tr>`;}).join(''):'<tr><td colspan="2">No recorded MVPs</td></tr>';
const log=rows.map(x=>`<tr><td class="mono">${esc(x.info.date||'')}</td><td>G${esc(String(x.r.game_no))}</td><td>vs ${esc(x.info.opp||'')}</td><td>${esc(x.r.hero||'')}</td><td>${esc(x.r.kills??x.r.kill??0)}/${esc(x.r.deaths??x.r.death??0)}/${esc(x.r.assists??x.r.assist??0)}</td><td>${x.info.won===null?'–':(x.info.won?'W':'L')}</td></tr>`).join('');
const kp=s.kill_participation||'—';
return `<div class="pin ov"><div class="body"><div class="phead">${u?`<img class="ppic" src="${esc(u)}" alt="" onerror="this.remove()">`:''}<div><div class="kicker">${esc(g.team||'')} · ${esc(g.lane||'—')}</div><h3 style="margin:0">${esc(name)}</h3></div><img class="tlogo" src="${TICON(g.team)}" alt="" loading="lazy" onerror="this.remove()"><button class="ghost" id="ovPick" style="margin-left:auto;border:1px solid var(--line);background:transparent;color:var(--ink);border-radius:8px;padding:8px 14px;cursor:pointer;font-weight:600">Player ▾</button></div>`
+`<div class="tiles"><div class="tile"><b>${g.gp||0}</b><span>Games</span></div><div class="tile"><b>${(g.avgkda||0).toFixed(2)}</b><span>Avg KDA</span></div><div class="tile"><b>${wins}-${scored.length-wins}</b><span>Game W-L</span></div><div class="tile"><b>${wr}%</b><span>Game WR</span></div><div class="tile"><b>${mw}-${ml}</b><span>Match W-L</span></div><div class="tile"><b>${mwr}%</b><span>Match WR</span></div><div class="tile"><b>${fmtDur(avgD)}</b><span>Avg game</span></div><div class="tile"><b>${esc(String(kp))}</b><span>Kill part.</span></div></div>`
+`<div class="ovgrid"><div class="ovsec"><h4>KDA trend per game</h4>${trendChart(rows.map(x=>{const k=x.r.kills??x.r.kill??0,d=x.r.deaths??x.r.death??0,a=x.r.assists??x.r.assist??0;return {v:(k+a)/Math.max(1,d),date:x.info.date||'',opp:x.info.opp||'',hero:x.r.hero||'',kda:((k+a)/Math.max(1,d)).toFixed(2),won:x.info.won};}))}<p>${rows.length} scored games · total gold ${(totG/1000).toFixed(0)}k · hero dmg ${(totD/1000).toFixed(0)}k · taken ${(totT/1000).toFixed(0)}k · tower ${(totTw/1000).toFixed(0)}k</p></div>`
+`<div class="ovsec"><h4>Hero pool (${heroRows.length} heroes)</h4><table><tr><th>Hero</th><th>GP</th><th>Win%</th><th>Avg K/D/A</th><th>GPM</th></tr>${heroTbl}</table></div></div>`
+`<div class="ovgrid"><div class="ovsec"><h4>Hero win rate</h4><table>${heroRows.map(o=>`<tr><td data-ovhero="${esc(o.h)}" tabindex="0" title="View ${esc(o.h)} games">${esc(o.h)}</td><td><div style="display:flex;gap:6px;align-items:center"><span class="wrbar"><i style="width:${o.wr}%"></i></span>${o.wr}%</div></td></tr>`).join('')}</table></div>`
+`<div class="ovsec"><h4>Sides</h4><table><tr><th>Side</th><th>GP</th><th>Win%</th></tr>${sideTbl}</table></div></div>`
+`<div class="ovgrid"><div class="ovsec"><h4>Items</h4>${itemGrid}</div>`
+`<div class="ovsec"><h4>Emblems &amp; talents</h4><div class="et-label">Emblems</div><div class="itemgrid">${embHtml}</div><div class="et-div"></div><div class="et-label">Talents</div><div class="itemgrid">${talHtml}</div></div></div>`
+`<div class="ovgrid"><div class="ovsec"><h4>Record by opponent</h4><table><tr><th>Opponent</th><th>GP</th><th>W-L</th></tr>${oppTbl}</table></div>`
+`<div class="ovsec"><h4>Series MVPs (${mvps.length})</h4><table><tr><th>Date</th><th>Match</th></tr>${mvpHtml}</table></div></div>`
+`<div class="ovsec" style="margin-top:14px"><h4>Game log</h4><div class="lscroll"><table style="min-width:640px"><tr><th>Date</th><th>Game</th><th>Match</th><th>Hero</th><th>K/D/A</th><th>R</th></tr>${log}</table></div></div>`
+`</div></div>`;}
function renderOvSel(){const q2=(document.getElementById('selQ').value||'').toLowerCase();
const t2=document.getElementById('selT').value,l2=document.getElementById('selL').value;
let r=agg();if(t2)r=r.filter(o=>o.team===t2);if(l2)r=r.filter(o=>o.lane===l2);
if(q2)r=r.filter(o=>(o.player+' '+o.team).toLowerCase().includes(q2));
r.sort((a,b)=>b.avgkda-a.avgkda);
document.getElementById('selList').innerHTML=r.map(o=>{const u=PICON(o.player);
return `<div class="selrow2">${u?`<img src="${esc(u)}" alt="" loading="lazy" onerror="this.remove()">`:`<span class="ppic-fb" style="width:34px;height:34px;font-size:13px">${esc(o.player.slice(0,2))}</span>`}<span style="flex:1"><b>${esc(o.player)}</b><br><span class="mono" style="font-family:var(--font-mono);font-size:11px;color:var(--muted)">${esc(o.team)} · ${esc(o.lane||'—')} · ${o.gp} GP</span></span><button class="primary" data-sel="${esc(o.player)}" style="border:0;border-radius:6px;padding:8px 14px;cursor:pointer;font-weight:700;background:#f2f1ec;color:#131311">Select</button></div>`;}).join('')||'<div class="empty">No players match.</div>';
document.querySelectorAll('#selList [data-sel]').forEach(b=>b.onclick=()=>{S.ov=b.dataset.sel;document.getElementById('dlg2').close();render();});}
function openOvSel(){const d=document.getElementById('dlg2');lastFocus=document.activeElement;
const ts=[...new Set(agg().map(o=>o.team))].sort(),ls=[...new Set(agg().map(o=>o.lane).filter(Boolean))].sort();
const st=document.getElementById('selT'),sl=document.getElementById('selL');
st.innerHTML='<option value="">All teams</option>'+ts.map(t=>`<option>${esc(t)}</option>`).join('');
sl.innerHTML='<option value="">All lanes</option>'+ls.map(t=>`<option>${esc(t)}</option>`).join('');
document.getElementById('selQ').value='';renderOvSel();d.showModal();}
function samePlayer(a,b){return normId(canonicalPlayer(a))===normId(canonicalPlayer(b));}
function ovRows(name){return DATA.players.filter(r=>r.player===name).map(r=>({r:r,info:gameInfo(r)}))
.sort((a,b)=>String(a.info.iso).localeCompare(String(b.info.iso)));}
function embIdOf(x){return x.r.e||(/emblem\/(\d+)\.png/.exec(x.r.emblem||'')||[])[1]||null;}
function talIdsOf(x){return (x.r.t&&x.r.t.length?x.r.t:(x.r.talents||[]).map(u=>/rune\/(\d+)\.png/.exec(u||'')?.[1])).filter(Boolean);}
function itemIdsOf(x){return (x.r.i&&x.r.i.length?x.r.i:((x.r.items||[]).map(u=>eqId(u)).filter(Boolean)));}
function embBadge(id,c,scope){const A=window.ASSETS||{emblems:{}};const src=A.emblems&&A.emblems[id];return `<button class="embtn" data-ovemb="${esc(String(id))}"${scope==='global'?' data-scope="global"':''} title="View heroes used with emblem ${esc(String(id))}">${src?`<img src="${esc(src)}" alt="Emblem ${esc(String(id))}" loading="lazy" onerror="this.remove()">`:`<span>E${esc(String(id))}</span>`}<span>×${c}</span></button>`;}
function talBadge(id,c,scope){const A=window.ASSETS||{runes:{}};const src=A.runes&&A.runes[id];return `<button class="embtn" data-ovtal="${esc(String(id))}"${scope==='global'?' data-scope="global"':''} title="View heroes used with talent ${esc(String(id))}">${src?`<img src="${esc(src)}" alt="Talent ${esc(String(id))}" loading="lazy" onerror="this.remove()">`:`<span>T${esc(String(id))}</span>`}<span>×${c}</span></button>`;}
function itemCell(id,c){const A=window.ASSETS||{items:{}};const src=A.items&&A.items[id];return `<span class="itemcell">${src?`<img src="${esc(src)}" alt="" loading="lazy" onerror="this.remove()">`:`<span class="slot-miss">${esc(String(id)).slice(0,8)}</span>`}<span>×${c}</span></span>`;}
function itemBtn(id,c,scope){const A=window.ASSETS||{items:{}};const src=A.items&&A.items[id];const label=String(id).length>14?String(id).slice(0,14)+'…':String(id);return `<button class="embtn" data-ovitem="${esc(String(id))}"${scope==='global'?' data-scope="global"':''} title="View heroes using item ${esc(label)}">${src?`<img class="sq" src="${esc(src)}" alt="Item ${esc(label)}" loading="lazy" onerror="this.remove()">`:`<span>${esc(label)}</span>`}<span>×${c}</span></button>`;}
function heroUseCounts(list){const emb={},tal={},item={};list.forEach(x=>{const e=embIdOf(x);if(e)emb[e]=(emb[e]||0)+1;talIdsOf(x).forEach(id=>{tal[id]=(tal[id]||0)+1;});itemIdsOf(x).forEach(id=>{item[id]=(item[id]||0)+1;});});return {emb:emb,tal:tal,item:item};}
function topEntries(obj,n){return Object.entries(obj).sort((a,b)=>b[1]-a[1]).slice(0,n);}
/* Equipment identity -> category, from the committed data/item_classes.json map
   (embedded as window.ITEM_CLASSES by tools/gen_dark.py). A category is a
   property of what the item IS - a completed Tier-3 item, footwear, or a
   component - never of how often it was built. An id the map does not know
   returns null, so it can never be silently filed under Major or Small. */
const ITEM_CLASSES=window.ITEM_CLASSES||{};
const ITEM_CLS_ORDER=[['major','Major Items'],['shoes','Shoes'],['small','Small Items']];
function itemClass(id){const e=ITEM_CLASSES[String(id)];return e?e.cls:null;}
function itemName(id){const e=ITEM_CLASSES[String(id)];return e&&e.name?e.name:'';}
/* Partition usage counts into the three categories. Count-descending with a
   deterministic id tie-break so repeated renders cannot reorder. */
function groupItemsByClass(counts){const g={major:[],shoes:[],small:[],unknown:[]};
Object.entries(counts).forEach(en=>{const c=itemClass(en[0]);(c&&g[c]?g[c]:g.unknown).push(en);});
[].concat(g.major,g.shoes,g.small,g.unknown).forEach(a=>a.sort((x,y)=>y[1]-x[1]||(x[0]<y[0]?-1:x[0]>y[0]?1:0)));
return g;}
/* Grouped item sections, shared by the hero stats drill-down and the player
   overview so both classify identically. Empty categories are omitted. */
function itemGroups(counts){const g=groupItemsByClass(counts||{}),out=[];
ITEM_CLS_ORDER.forEach(([k,label])=>{if(g[k].length)out.push({key:k,label:label,entries:g[k]});});
if(g.unknown.length)out.push({key:'unknown',label:'Unclassified',entries:g.unknown});
return out;}
/* Items are listed in full: usage counts are exact facts from the data, so an
   arbitrary top-N cap makes this view answer "what did they build on this
   hero?" incorrectly. Each cell is a drill-down, so nothing is hidden. Items
   are split into the three equipment categories; a category with no items is
   omitted rather than rendered as an empty row. */
function assetRowsHTML(u,scope){
const row=(label,cells)=>`<div class="userow"><div class="ulabel">${label}</div><div class="ubadges">${cells}</div></div>`;
const dash='<span style="color:var(--muted)">–</span>';
const e=topEntries(u.emb,3),t=topEntries(u.tal,4);
const cell=([id,c])=>scope==='global'?itemBtn(id,c,scope):itemCell(id,c);
const sections=itemGroups(u.item).map(gr=>row(gr.label,gr.entries.map(cell).join('')));
return `<div class="usegrid">`
+row('Emblems',e.map(([id,c])=>embBadge(id,c,scope)).join('')||dash)
+row('Talents',t.map(([id,c])=>talBadge(id,c,scope)).join('')||dash)
+sections.join('')+`</div>`;}
function usageSummaryHTML(list,scope){return `<div class="msec">Usage summary · ${list.length} game${list.length===1?'':'s'}</div>`+assetRowsHTML(heroUseCounts(list),scope);}
function heroBreakdownRows(byH,scope){const A=window.ASSETS||{heroes:{}};return Object.entries(byH).sort((a,b)=>b[1]-a[1]).map(([h,n])=>{const hi=A.heroes&&A.heroes[h];
return `<tr><td data-ovhero="${esc(h)}"${scope==='global'?' data-scope="global"':''} tabindex="0" title="View ${esc(h)} games"><span class="hcell">${hi?`<img src="${esc(hi)}" alt="" loading="lazy" onerror="this.remove()">`:''}${esc(h)}</span></td><td>×${n}</td></tr>`;}).join('');}
function gameRowHTML(x){const r=x.r,k=r.kills??r.kill??0,d=r.deaths??r.death??0,a=r.assists??r.assist??0;
const kda=((k+a)/Math.max(1,d)).toFixed(1);
const A=window.ASSETS||{};
const hi=r.hero&&A.heroes&&A.heroes[r.hero]?A.heroes[r.hero]:null;
const dt=(x.info.iso||'').slice(0,10)||x.info.date||'';
return `<div class="mrow" data-ovg="${esc(String(r.match_detail_id))}:${esc(String(r.game_no))}" tabindex="0" role="button" aria-label="Open game ${esc(String(r.game_no))} vs ${esc(x.info.opp||'')}"><span class="mdate">${esc(dt)}</span>`
+`<span class="mfix">${hi?`<img src="${esc(hi)}" alt="" loading="lazy" onerror="this.remove()">`:''}<span class="msc">G${esc(String(r.game_no))}</span><span class="mt">vs ${esc(x.info.opp||'?')} · ${esc(r.hero||'')} · ${esc(k)}/${esc(d)}/${esc(a)}</span></span>`
+`<span><span class="tag">${x.info.won===null?'–':(x.info.won?'W':'L')}</span></span>`
+`<span class="mmvp hide-m">KDA ${kda}</span>`
+`<span class="mgo">›</span></div>`;}
function gameListView(title,sub,list,extra){dSet(title,sub,(extra||'')+`<div class="msec">Games · ${list.length}</div><div class="mhead"><span>Date</span><span>Game</span><span>Result</span><span>KDA</span><span></span></div>`+(list.map(gameRowHTML).join('')||'<div class="empty">No games found.</div>'));}
function ovHeroDrill(hero){const list=ovRows(S.ov).filter(x=>(x.r.hero||'')===hero);
gameListView(hero+' — '+list.length+' game'+(list.length===1?'':'s'),S.ov+' · hero pool',list,usageSummaryHTML(list));}
function ovOppDrill(opp){const list=ovRows(S.ov).filter(x=>(x.info.opp||'')===opp);
gameListView('vs '+opp+' — '+list.length+' game'+(list.length===1?'':'s'),S.ov+' · record by opponent',list);}
function ovEmbDrill(id){const A=window.ASSETS||{emblems:{}};
const list=ovRows(S.ov).filter(x=>String(embIdOf(x)||'')===String(id));
const byH={};list.forEach(x=>{const h=x.r.hero||'?';byH[h]=(byH[h]||0)+1;});
const src=(A.emblems&&A.emblems[id])||'';
const rowsHtml=heroBreakdownRows(byH);
dSet('Emblem '+id,S.ov+' · '+list.length+' games',`${src?`<p><img src="${esc(src)}" alt="Emblem ${esc(String(id))}" loading="lazy" style="width:40px;height:40px;border-radius:50%;border:1px solid var(--line)" onerror="this.remove()"></p>`:''}<table><tr><th>Hero</th><th>Used</th></tr>${rowsHtml||'<tr><td colspan="2">No games found.</td></tr>'}</table>`);}
function ovTalDrill(id){const A=window.ASSETS||{runes:{}};
const list=ovRows(S.ov).filter(x=>talIdsOf(x).map(String).includes(String(id)));
const byH={};list.forEach(x=>{const h=x.r.hero||'?';byH[h]=(byH[h]||0)+1;});
const src=(A.runes&&A.runes[id])||'';
const rowsHtml=heroBreakdownRows(byH);
dSet('Talent '+id,S.ov+' · '+list.length+' games',`${src?`<p><img src="${esc(src)}" alt="Talent ${esc(String(id))}" loading="lazy" style="width:34px;height:34px;border-radius:50%;border:1px solid var(--line)" onerror="this.remove()"></p>`:''}<table><tr><th>Hero</th><th>Used</th></tr>${rowsHtml||'<tr><td colspan="2">No games found.</td></tr>'}</table>`);}
/* Stats hero drill-down (global scope): hero statistics across the whole dataset
   plus every associated game. Ban rows come from game_bans (match, game, side,
   hero) — that source carries NO order/phase columns, and game_players carries
   NO pick-order column, so no order numbers are shown rather than invented.
   Side A/B maps to team_a/team_b (see build_s18_db.py ingest: bans_a->A). */
function stGameMeta(mid,gno){const gm=(DATA.games||[]).find(g=>String(g.match_detail_id)===String(mid)&&String(g.game_no)===String(gno))||{};
const sc=(DATA.schedule||[]).find(s=>String(s.match_detail_id)===String(mid))||{};return {gm:gm,sc:sc};}
function sideCls(s){s=String(s||'').toLowerCase();return s==='blue'?'b':(s==='red'?'r':'');}
const MON=['Jan','Feb','Mar','Apr','May','Jun','Jul','Aug','Sep','Oct','Nov','Dec'];
function fmtD(iso,date){const m=/(\d{4})-(\d{2})-(\d{2})/.exec(iso||'');
if(m)return MON[+m[2]-1]+' '+(+m[3]);
const m2=/(\d{1,2}) ([A-Za-z]+)/.exec(date||'');if(m2)return m2[2].slice(0,3)+' '+(+m2[1]);
return '–';}
function stGameRowHTML(e){
const tag=e.kind==='ban'?'<span class="tag ban">BAN</span>':'<span class="tag pick">PICK</span>';
const sA=e.clsA==='b'?'sa':(e.clsA==='r'?'sb':''),sB=e.clsB==='b'?'sa':(e.clsB==='r'?'sb':'');
const wA=e.win?(e.win===e.teamA?'tw':'tl'):'',wB=e.win?(e.win===e.teamB?'tw':'tl'):'';
const res=e.res==='win'?'<span class="res win">Win</span>':(e.res==='loss'?'<span class="res loss">Loss</span>':'<span class="res na">–</span>');
return `<div class="mrow sg" data-ovg="${esc(String(e.mid))}:${esc(String(e.gno))}" tabindex="0" role="button" aria-label="Open game ${esc(String(e.gno))} ${esc(e.teamA||'')} vs ${esc(e.teamB||'')}"><span class="mdate">${esc(fmtD(e.iso,e.date))}</span>`
+`<span class="mfix"><span class="mt ${sA} ${wA}">${esc(e.teamA||'?')}</span><span class="msep" aria-hidden="true">·</span><span class="mt ${sB} ${wB}">${esc(e.teamB||'?')}</span></span>`
+`<span class="mgame">${esc(String(e.gno))}</span>`
+`<span class="sgtype">${tag}</span>`
+`<span class="sgres">${res}</span>`
+`<span class="sgmeta">${esc(fmtD(e.iso,e.date))} · Game ${esc(String(e.gno))}</span>`
+`<span class="mgo">›</span></div>`;}
function stHeroDrill(hero){const A=window.ASSETS||{heroes:{}};
const hc=(window.HERO_CLASSES||{})[hero]||{};
const picks=DATA.players.filter(r=>(r.hero||'')===hero).map(r=>({r:r,info:gameInfo(r)}))
.sort((a,b)=>String(a.info.iso).localeCompare(String(b.info.iso)));
const bans=(DATA.bans||[]).filter(b=>(b.hero||'')===hero);
const hi=A.heroes&&A.heroes[hero];
const scored=picks.filter(x=>x.info.won!==null),wins=scored.filter(x=>x.info.won).length;
const wr=scored.length?Math.round(wins/scored.length*100):0;
const byP={};picks.forEach(x=>{const p=canonicalPlayer(x.r.player);byP[p]=(byP[p]||0)+1;});
const nPlayers=Object.keys(byP).length;
const playersHtml=Object.entries(byP).sort((a,b)=>b[1]-a[1]).map(([p,n])=>`<tr><td><span data-p="${esc(p)}" tabindex="0" style="cursor:pointer;font-weight:600">${esc(p)}</span></td><td>×${n}</td></tr>`).join('');
const sumHtml=`<div class="msec">Hero statistics · ${picks.length} pick${picks.length===1?'':'s'} · ${bans.length} ban${bans.length===1?'':'s'}</div>`
+`<div class="tiles"><div class="tile"><b>${picks.length}</b><span>Picks</span></div><div class="tile"><b>${bans.length}</b><span>Bans</span></div><div class="tile"><b>${wr}%</b><span>Pick WR</span></div><div class="tile"><b>${nPlayers}</b><span>Players</span></div></div>`
+assetRowsHTML(heroUseCounts(picks),'global')
+`<div class="msec">Players · ${nPlayers}</div><div class="lscroll"><table style="min-width:320px"><tr><th>Player</th><th>Uses</th></tr>${playersHtml||'<tr><td colspan="2">No picks recorded.</td></tr>'}</table></div>`;
const entries=[];
picks.forEach(x=>{const gm=x.info.gm||{};const w=winName(gm);
entries.push({kind:'pick',mid:x.r.match_detail_id,gno:x.r.game_no,iso:x.info.iso,date:x.info.date,win:w||'',
res:w?(w===x.r.team?'win':'loss'):null,
teamA:gm.team_a||x.r.team,teamB:gm.team_b||x.info.opp,clsA:sideCls(gm.team_a_side),clsB:sideCls(gm.team_b_side)});});
bans.forEach(b=>{const m=stGameMeta(b.match_detail_id,b.game_no),gm=m.gm;const w=winName(gm);
const teamA=gm.team_a||m.sc.team_a,teamB=gm.team_b||m.sc.team_b;
entries.push({kind:'ban',mid:b.match_detail_id,gno:b.game_no,iso:m.sc.iso_datetime||'',date:m.sc.date||m.sc.iso_date||'',win:w||'',
res:null,
teamA:teamA,teamB:teamB,clsA:sideCls(gm.team_a_side),clsB:sideCls(gm.team_b_side)});});
entries.sort((a,b)=>String(a.iso).localeCompare(String(b.iso))||(+a.gno-+b.gno)||(a.kind==='pick'?-1:1));
const gamesHtml=`<div class="msec">Games · ${picks.length} pick${picks.length===1?'':'s'} · ${bans.length} ban${bans.length===1?'':'s'}</div><div class="mhead sg"><span>Date</span><span>Match</span><span>GAME</span><span>Type</span><span>Result</span><span></span></div>`
+(entries.map(stGameRowHTML).join('')||'<div class="empty">No games found.</div>');
const meta=(hc.primary_role||hc.primary_lane||hc.damage_type)?`<div class="kicker">${esc(hc.primary_role||'—')} · ${esc(hc.primary_lane||'—')} lane · <span title="Damage type is derived from ability text, not an official field">${esc(hc.damage_type||'—')} damage</span></div>`:'';
dSet(hero,'Stats · Heroes · '+picks.length+' picks · '+bans.length+' bans',
`${hi?`<p><img src="${esc(hi)}" alt="${esc(hero)}" loading="lazy" style="width:40px;height:40px;border-radius:10px;border:1px solid var(--line);object-fit:cover" onerror="this.remove()"></p>`:''}`
+meta+sumHtml+gamesHtml);}
/* Global asset drill-downs: usage across ALL players (not one overview player).
   Same table component as the overview asset views; hero clicks carry
   data-scope="global" so they reopen global hero modals. */
function stAssetView(kind,id,iconHtml,list){const A=window.ASSETS||{heroes:{}};
const byH={};list.forEach(r=>{const h=r.hero||'?';byH[h]=(byH[h]||0)+1;});
const rowsHtml=heroBreakdownRows(byH,'global');
dSet(kind+' '+id+' · global','Across all players · '+list.length+' games',
`${iconHtml||''}<table><tr><th>Hero</th><th>Used</th></tr>${rowsHtml||'<tr><td colspan="2">No games found.</td></tr>'}</table>`);}
function stEmbDrill(id){const A=window.ASSETS||{emblems:{}};
const list=(DATA.players||[]).filter(r=>String(embIdOf({r:r})||'')===String(id));
const src=(A.emblems&&A.emblems[id])||'';
stAssetView('Emblem',id,src?`<p><img src="${esc(src)}" alt="Emblem ${esc(String(id))}" loading="lazy" style="width:40px;height:40px;border-radius:50%;border:1px solid var(--line)" onerror="this.remove()"></p>`:'',list);}
function stTalDrill(id){const A=window.ASSETS||{runes:{}};
const list=(DATA.players||[]).filter(r=>talIdsOf({r:r}).map(String).includes(String(id)));
const src=(A.runes&&A.runes[id])||'';
stAssetView('Talent',id,src?`<p><img src="${esc(src)}" alt="Talent ${esc(String(id))}" loading="lazy" style="width:34px;height:34px;border-radius:50%;border:1px solid var(--line)" onerror="this.remove()"></p>`:'',list);}
function stItemDrill(id){const A=window.ASSETS||{items:{}};
const list=(DATA.players||[]).filter(r=>itemIdsOf({r:r}).map(String).includes(String(id)));
const src=(A.items&&A.items[id])||'';
stAssetView('Item usage',/^\d+$/.test(String(id))?'#'+id:'',src?`<p><img src="${esc(src)}" alt="" loading="lazy" style="width:40px;height:40px;border-radius:8px;border:1px solid var(--line);object-fit:cover" onerror="this.remove()"></p>`:'',list);}
function showP(n){const r=DATA.players.filter(x=>samePlayer(x.player,n));const g=agg().find(o=>samePlayer(o.player,n))||{};
const disp=r.length?r[0].player:(g.player||n);
const dm={};(DATA.schedule||[]).forEach(m=>{dm[String(m.match_detail_id)]=m.iso_date||m.date||'';});
const twr={};(DATA.team_games||[]).forEach(x=>{const o=twr[x.team]=twr[x.team]||{n:0,w:0};o.n++;if(x.win===1)o.w++;});Object.keys(twr).forEach(k=>{twr[k]=twr[k].n?twr[k].w/twr[k].n:0;});
const anp=buildPlayerMetrics(DATA.players,DATA.games,DATA.team_games,window.HERO_CLASSES||{},{canon:canonicalPlayer,dateOf:m=>dm[String(m)]||'',teamWinRate:twr}).players.find(x=>samePlayer(x.player,disp))||null;
const A=window.ASSETS||{heroes:{}};
const bh={};r.forEach(x=>{(bh[x.hero]=bh[x.hero]||[]).push(x);});
const t=Object.entries(bh).map(([h,rs])=>{const hg=rs.reduce((s,x)=>s+(x.gold_per_min||0),0)/rs.length;
const ak=rs.reduce((s,x)=>s+x.kills,0)/rs.length,ad=rs.reduce((s,x)=>s+x.deaths,0)/rs.length,aa=rs.reduce((s,x)=>s+x.assists,0)/rs.length;
const akda=rs.reduce((s,x)=>s+(+x.kda||0),0)/rs.length;
const hi=(A.heroes&&A.heroes[h])||'';return `<tr><td><span class="hcell">${hi?`<img src="${esc(hi)}" alt="" loading="lazy" onerror="this.remove()">`:''}${esc(h)}</span></td><td>${rs.length}</td><td>${akda.toFixed(2)}</td><td>${ak.toFixed(1)}</td><td>${ad.toFixed(1)}</td><td>${aa.toFixed(1)}</td><td>–</td><td>–</td><td>${hg.toFixed(0)}</td></tr>`;}).join('');
const u=PICON(disp);
const extra=anp?`<div class="tiles"><div class="tile"><b>${anp.close.n?Math.round(anp.close.winRate*100)+'%':'–'}</b><span>Close-game WR (${anp.close.wins}/${anp.close.n})</span></div><div class="tile"><b>${anp.effectivePool}/${anp.heroes}</b><span>Effective pool</span></div><div class="tile"><b>${anp.comfort.toFixed(2)}</b><span>Comfort index</span></div><div class="tile"><b>${anp.flexHeroes}</b><span>Flex heroes</span></div><div class="tile"><b>${anp.dpg.toFixed(2)}</b><span>Damage / gold</span></div><div class="tile"><b>${Math.round(anp.towerPerGame)}</b><span>Tower dmg / game</span></div></div><div class="lscroll"><table style="min-width:520px"><tr><th>Split</th><th>GP</th><th>KDA</th><th>Dmg%</th></tr><tr><td>vs ≥50% teams</td><td>${anp.oppTier.strong.n}</td><td>${anp.oppTier.strong.kda.toFixed(2)}</td><td>${Math.round(anp.oppTier.strong.damageShare*100)}%</td></tr><tr><td>vs &lt;50% teams</td><td>${anp.oppTier.weak.n}</td><td>${anp.oppTier.weak.kda.toFixed(2)}</td><td>${Math.round(anp.oppTier.weak.damageShare*100)}%</td></tr></table></div><div class="lscroll" style="margin-top:8px"><table style="min-width:560px"><tr><th>Hero fit</th><th>GP</th><th>Player WR</th><th>League WR</th><th>Delta</th><th>Comfort</th></tr>${anp.pool.slice(0,8).map(h=>`<tr><td>${esc(h.hero)}</td><td>${h.games}</td><td>${Math.round(h.wr*100)}%</td><td>${Math.round(h.leagueWr*100)}%</td><td>${h.delta>0?'+':''}${Math.round(h.delta*100)}pp</td><td>${h.comfort.toFixed(2)}</td></tr>`).join('')}</table></div><div class="an-pct" style="margin-top:6px">Close = final kill diff ≤5 (proxy for composure; no timeline exists). Opponent split uses team win rate; n is shown. Hero fit compares the player's WR on the hero with the league WR; effective pool = heroes with ≥2 games and ≥50% WR.</div>`:'';
openD(disp,(g.team||'')+' · '+(g.lane||''),`<div class="pdhead">${u?`<img src="${esc(u)}" alt="" onerror="this.remove()">`:''}<div><div class="kicker">${esc(g.team||'')} · ${esc(g.lane||'—')}</div><div style="font-family:var(--font-display);font-size:19px;font-weight:700">${esc(disp)}</div></div></div><div class="tiles"><div class="tile"><b>${g.gp||r.length}</b><span>Games</span></div><div class="tile"><b>${(g.avgkda||0).toFixed(2)}</b><span>Avg KDA</span></div><div class="tile"><b>${(g.avgg||0).toFixed(0)}</b><span>Avg gold/min</span></div><div class="tile"><b>${g.k||0}/${g.d||0}/${g.a||0}</b><span>Total K / D / A</span></div></div>${extra}<div class="lscroll"><table style="min-width:560px"><tr><th>Hero</th><th>GP</th><th>AVG KDA</th><th>AVG K</th><th>AVG D</th><th>AVG A</th><th title="Under development — no official ID source publishes this yet">MANIAC *</th><th title="Under development — no official ID source publishes this yet">SAVAGE *</th><th>GPM</th></tr>${t}</table></div><div class="mono" style="font-family:var(--font-mono);font-size:10.5px;color:var(--muted);margin-top:6px">* MANIAC / SAVAGE tracking is under development — no official MPL ID source publishes these counts yet.</div>`);}
function durSec(s){const m=/(\d+):(\d+)/.exec(s||'');return m?(+m[1])*60+(+m[2]):0;}
function normPl(r,sec){const kills=r.kill??r.kills??0,deaths=r.death??r.deaths??0,assists=r.assist??r.assists??0;
const gpm=r.gold_per_min??((sec&&r.gold!=null)?Math.round(r.gold/(sec/60)):null);return Object.assign({},r,{kills,deaths,assists,gpm});}
function aid(u,re){const m=re.exec(u||'');return m?m[1]:'';}
function teamBlock(code,kills,plist,sec,side,flip,won){
const A=window.ASSETS||{items:{},heroes:{},emblems:{},runes:{}};
const pk=String(side||'').toLowerCase()==='blue'?'pk-b':(String(side||'').toLowerCase()==='red'?'pk-r':'');
const prow=plist.map(r0=>{const r=normPl(r0,sec);
const heroLocal=(r.hero&&A.heroes&&Object.prototype.hasOwnProperty.call(A.heroes,r.hero))?A.heroes[r.hero]:null;
const heroRemote=(!heroLocal&&(r.hero_image||r.heroImage))||'';
const heroSrc=heroLocal||heroRemote;
const heroImg=heroSrc?`<img class="sb-hero" src="${esc(heroSrc)}" alt="${esc(r.hero||'')}" loading="lazy" onerror="this.style.visibility='hidden'">`:`<span class="sb-hero" style="display:inline-flex;align-items:center;justify-content:center;font:10px var(--font-mono);font-family:var(--font-mono);color:var(--muted)">${esc((r.hero||'?').slice(0,2))}</span>`;
const embId=r.e||aid(r.emblem,/emblem\/(\d+)\.png/);
const embSrc=(embId&&A.emblems&&A.emblems[embId])||r.emblem||'';
const embSm=embSrc?`<img src="${esc(embSrc)}" alt="emblem" loading="lazy" style="width:20px;height:20px;border-radius:50%;border:1px solid var(--line)" onerror="this.remove()">`:'';
const talObjs=(r.t&&r.t.length)?r.t.map(id=>({id:id,url:null})):(r.talents||[]).map(u=>({id:aid(u,/rune\/(\d+)\.png/),url:u}));
const tals=talObjs.map(o=>{const src=(o.id&&A.runes&&A.runes[o.id])||(o.url&&A.runes&&A.runes[o.url])||o.url;return src?`<img src="${esc(src)}" alt="" loading="lazy" onerror="this.remove()">`:'';}).join('');
const itemObjs=(r.i&&r.i.length)?r.i.map(ref=>String(ref).indexOf('http')===0?{eq:null,url:ref}:{eq:ref,url:null}):(r.items||[]).map(u=>({eq:eqId(u)||null,url:u}));
const items=itemObjs.map(o=>{const src=(o.eq&&A.items&&A.items[o.eq])||(o.url&&A.items&&A.items[o.url])||o.url;if(!src)return '';return `<img src="${esc(src)}" alt="item ${esc(o.eq||'')}" data-eq="${esc(o.eq||'')}" loading="lazy" onerror="imgSlot(this)">`;}).join('');
return `<div class="sb-p">${heroImg}<div class="sb-id"><b>${esc(r.player)}</b><span>${esc(r.lane||'—')} · ${esc(r.hero||'')} · ${esc(r.kills)}/${esc(r.deaths)}/${esc(r.assists)} · KDA ${esc(r.kda)}</span></div>`
+`<div class="sb-side">G ${esc(r.gold)}${r.gpm!=null?' ('+esc(r.gpm)+'/m)':''}<br>DMG ${esc(r.hero_damage??'–')} · TAKEN ${esc(r.damage_taken??'–')}</div>`
+`<div class="sb-gear"><span class="sb-tal">${embSm}${tals}</span>${items?`<span class="sb-items">${items}</span>`:''}</div></div>`;}).join('');
return `<div class="sb-team${flip?' flip':''}${pk?' '+pk:''}"><div class="sb-thead"><img src="${logoOf(code)}" alt="" ${IMG_HIDE}><b class="${won===true?'tw':won===false?'tl':''}">${esc(code)}</b><span class="k">${esc(kills)} kills</span></div>${prow}</div>`;}
function winName(g){return g.winner==='team_a'?g.team_a:(g.winner==='team_b'?g.team_b:(g.winner||''));}
/* Playoff chances (1 series win = 1 point; every team plays exactly 16 series).
   Top 6 → playoffs ("% Playoff Chance"), top 2 → upper bracket ("% Upper
   Bracket"). Method (see calcChances): points-sufficient hard limits
   (clinched/eliminated no matter the tiebreakers), otherwise a seeded
   Monte-Carlo (2000 trials) over the reconciled remaining fixtures with
   P(A wins) = pa/(pa+pb) from Beta(2,2)-smoothed series win rates
   ((won+2)/(played+4)), per-series game
   scores sampled from the Beta(2,2)-smoothed BO3 sweep rate, and cuts on
   (points, simulated game diff, head-to-head mini-league). Official
   tiebreakers: 1. Matches Win, 2. Diff, 3. H2H
   (docs/MPL_ID_S18_Regular_Season.md). Fixed seed → stable across renders. */
/* Season constants derived from the validated bundle configuration
   (data/season.json); see also tools/test_config.js which pins the Season 18
   values and tools/gen_dark.py which refuses to build invalid configs. */
const TOTAL_TEAMS=SEASON.totalTeams,ROUND_ROBIN_ROUNDS=SEASON.roundRobinRounds,PLAYOFF_SLOTS=SEASON.playoffSlots,UPPER_BRACKET_SLOTS=SEASON.upperBracketSlots;
const TOTAL_SERIES=SEASON.seriesPerTeam,TRIALS=SEASON.model.trials;
/* CHANCES-START */
/* Fixture normalization (pure, tested): schedule rows -> calcChances input.
   Drops playoff rows and unknown/TBD sides; marks completed rows decided
   (winner from the winner field, else inferred from a terminal BO3 score);
   treats a NON-completed row with a terminal BO3 scoreline (2-0/2-1) as
   decided — the result is already reflected in the standings feed (observed
   Oct 3: AE 1-2 NAVI still flagged live while NAVI/AE played counts include
   it); re-simulating it would award the point twice. Finally caps
   played + remaining at totalSeries per team by dropping that team's live
   rows first (upcoming rows are never dropped: each is simulated exactly
   once; completed results are never re-simulated). */
/* Canonical team codes from the season configuration. Keys are lowercase
   alphanumeric (no spaces/punctuation); every spelling in tools/test_config.js
   battery resolves through this single map. Unknown sides pass through so
   fixture validation can report them instead of silently dropping them. */
var TEAM_ALIAS=SEASON.aliases||{};
function normTeamCode(t){return String(t||'').toLowerCase().replace(/[^a-z0-9]/g,'');}
function normTeam(t){var u=normTeamCode(t);return String(TEAM_ALIAS[u]||u).toLowerCase();}
function isPORow(m){return String(m.schedule_id||m.match_id||'').indexOf('playoffs')>-1||(m.team_a==='TBD'&&m.team_b==='TBD');}
function isTerminalScore(sa,sb){return (sa===2&&(sb===0||sb===1))||(sb===2&&(sa===0||sa===1));}
function normalizeFixtures(schedule,known,playedMap,totalSeries){
var fixtures=[],decidedLive=0;
(schedule||[]).forEach(function(m){
if(isPORow(m))return;
var a=normTeam(m.team_a),b=normTeam(m.team_b);
if(!a||!b||a===b||!known[a]||!known[b])return;
var sa=+m.score_a,sb=+m.score_b;
var fin=isTerminalScore(sa,sb);
var live=String(m.status||'')!=='completed'&&String(m.status||'')!=='upcoming';
if(String(m.status)==='completed'){
var w=m.winner==='team_a'?'a':(m.winner==='team_b'?'b':(fin?(sa>sb?'a':'b'):null));
fixtures.push({a:a,b:b,decided:true,winner:w,sweep:fin?((sa===2&&sb===0)||(sb===2&&sa===0)):null,live:false,id:String(m.schedule_id||m.match_id||'')});
}else if(fin){
decidedLive++;
fixtures.push({a:a,b:b,decided:true,winner:(sa>sb?'a':'b'),sweep:((sa===2&&sb===0)||(sb===2&&sa===0)),live:true,id:String(m.schedule_id||m.match_id||'')});
}else{
fixtures.push({a:a,b:b,decided:false,winner:null,sweep:null,live:live,id:String(m.schedule_id||m.match_id||'')});
}});
var dropped=[];
var guard=99;
while(guard-->0){
var cnt={};fixtures.forEach(function(f){if(!f.decided){cnt[f.a]=(cnt[f.a]||0)+1;cnt[f.b]=(cnt[f.b]||0)+1;}});
var cut=-1;
for(var i=0;i<fixtures.length;i++){
var f=fixtures[i];
if(f.decided)continue;
var badA=(playedMap[f.a]||0)+(cnt[f.a]||0)>totalSeries;
var badB=(playedMap[f.b]||0)+(cnt[f.b]||0)>totalSeries;
if((badA||badB)&&f.live){cut=i;break;}
}
if(cut<0)break;
dropped.push(fixtures[cut].id);
fixtures.splice(cut,1);
}
return {fixtures:fixtures,decidedLive:decidedLive,dropped:dropped};
}
/* Pure probability engine: P(final top-6) and P(final top-2) per team.
   standings: [{key,pts,won,lost,diff}] in OFFICIAL rank order (ties keep the
   official order; cut values only read points, which the official order
   respects). fixtures: [{a,b,decided,winner,sweep}] with winner 'a'/'b'/null
   and sweep true(2-0)/false(2-1)/null(unknown); decided fixtures are NOT
   re-simulated (their points already sit in `pts`) — they only feed the H2H
   base table and the sweep-rate calibration. opts: {totalSeries,
   playoffSlots, upperSlots, trials, seed, winProb:'bradley-terry'|'even',
   sweepP (override), exact (enumerate, fixtures<=12)}.
   Team strength is never invented: 'bradley-terry' converts smoothed series
   win rates into P(A wins) via the ratio pa/(pa+pb) — a Bradley-Terry-STYLE
   heuristic, not a fitted model. Smoothing applies a symmetric Beta(2,2)
   prior (4 pseudo-series at 2-2): (won+2)/(played+4), so 0-0 estimates sit
   at 0.5 and no finite record yields exactly 0 or 1; 'even' is the
   documented neutral baseline. Game-score sampling uses the sweep share
   among decided BO3s with the same Beta(2,2) prior ((sweeps+2)/(decided+4),
   0.5 with no data). Ranking per outcome: points, then
   simulated game diff, then head-to-head series record inside the tied group
   (mini-league over decided + simulated results); leftover ties fall back to
   key order — deterministic but arbitrary, documented here, never presented
   as an official rule. The shared rankTeams() helper implements this order so
   offline exhaustive provers rank outcomes identically. Hard 100/0 limits are
   points-sufficient conditions
   (below-cutoff teams cannot even tie the mark / above-cutoff teams cannot
   be pushed out: at most 5 rivals can finish ahead), hence true guarantees.
   Fractional (unrounded) shares sum to exactly playoffSlots*100 /
   upperSlots*100 across teams; callers round only for display. Simulated
   entries also carry trial counts (q/n) and a Wilson 95% CI in their tooltip
   text so a rounded 0%/100% is never mistaken for a proven certainty. */
/* Shared ranking used by the engine and by offline provers: points, then
   game diff, then head-to-head series record inside a tied group
   (mini-league over decided h2h + simulated sim results), then key order. */
function rankTeams(keys,P,D,sim,h2h){
var arr=keys.slice().sort(function(x,y){
return (P[y]-P[x])||(D[y]-D[x])||(x<y?-1:(x>y?1:0));});
var i=0;
while(i<arr.length){
var j=i+1;
while(j<arr.length&&P[arr[j]]===P[arr[i]]&&D[arr[j]]===D[arr[i]])j++;
if(j-i>1){
var group=arr.slice(i,j),inG={};
group.forEach(function(k){inG[k]=1;});
var scored=group.map(function(t){
var n=0;
group.forEach(function(k){if(k===t)return;
if(h2h[t]&&h2h[t][k])n+=h2h[t][k];});
if(sim)sim.forEach(function(f){
if(f.w!==t)return;
var o=(f.a===t)?f.b:f.a;
if((f.a===t||f.b===t)&&inG[o])n++;});
return {k:t,m:n};});
scored.sort(function(x,y){return (y.m-x.m)||(x.k<y.k?-1:1);});
for(var k=0;k<scored.length;k++)arr[i+k]=scored[k].k;
}
i=j;}
return arr;
}
/* Wilson 95% score interval for k successes in n trials, in percent. */
function wilson(k,n){
if(!(n>0))return [0,100];
var z=1.96,p=k/n,den=1+z*z/n,ct=p+z*z/(2*n),mg=z*Math.sqrt(p*(1-p)/n+z*z/(4*n*n));
return [Math.max(0,(ct-mg)/den)*100,Math.min(1,(ct+mg)/den)*100];
}
function calcChances(standings, fixtures, opts){
opts=opts||{};
var totalSeries=opts.totalSeries!=null?opts.totalSeries:16;
var playoffSlots=opts.playoffSlots!=null?opts.playoffSlots:6;
var upperSlots=opts.upperSlots!=null?opts.upperSlots:2;
var trials=opts.trials!=null?opts.trials:2000;
var seedInit=opts.seed!=null?opts.seed:0x51ab;
var mode=opts.winProb==='even'?'even':'bradley-terry';
var exact=!!opts.exact;
var diag={teams:0,remaining:0,sweepP:0.5,dropped:[],invalid:[],maxSplitErr:0};
var rows=[];
(standings||[]).forEach(function(s,i){
var k=s&&(s.key!=null?s.key:(s.team_slug||s.team_name));
k=String(k!=null?k:'').toLowerCase();
var rawP=s&&(s.pts!=null?s.pts:s.match_point);
var rawW=s&&(s.won!=null?s.won:s.match_win);
var rawL=s&&(s.lost!=null?s.lost:s.match_lose);
var rawD=s&&(s.diff!=null?s.diff:s.net_game_win);
var pts=+rawP||0,won=+rawW||0,lost=+rawL||0,diff=+rawD||0;
if(!(won>=0))won=0;if(!(lost>=0))lost=0;
if(!k){diag.invalid.push('standing#'+i);return;}
rows.push({key:k,pts:pts,won:won,lost:lost,diff:diff});
if(won+lost>totalSeries)diag.invalid.push(k+':played-over');
});
var byKey={};
rows=rows.filter(function(r){if(byKey[r.key]){diag.invalid.push('dup:'+r.key);return false;}byKey[r.key]=r;return true;});
diag.teams=rows.length;
var remFx=[],baseH2H={},sweepN=0,sweepD=0;
(fixtures||[]).forEach(function(f,i){
var a=String(f&&(f.a!=null?f.a:'')).toLowerCase();
var b=String(f&&(f.b!=null?f.b:'')).toLowerCase();
if(!a||!b||a===b||!byKey[a]||!byKey[b]){diag.invalid.push('fixture#'+i);return;}
if(f&&f.decided){
var w=(f.winner==='a')?a:((f.winner==='b')?b:null);
if(w){baseH2H[a]=baseH2H[a]||{};baseH2H[b]=baseH2H[b]||{};
baseH2H[a][b]=(baseH2H[a][b]||0)+(w===a?1:0);
baseH2H[b][a]=(baseH2H[b][a]||0)+(w===b?1:0);}
if(f.sweep===true){sweepN++;sweepD++;}else if(f.sweep===false){sweepD++;}
return;}
remFx.push({a:a,b:b});
});
diag.remaining=remFx.length;
/* Statistical smoothing (Beta prior: priorW pseudo-wins in priorN
   pseudo-series, S18: Beta(2,2) = 4 pseudo-series at 2-2 via opts/the season
   config; invalid values clamp to 2/4): win-rate
   estimates shrink toward the neutral 50% baseline when samples are small
   and converge to the observed record as results accumulate. Strength 4 is
   ~25% of a 16-series season: enough to prevent exact 0%/100% matchup
   probabilities from finite-sample extremes (0-0 -> 0.5; an undefeated team
   still meets a winless team strictly inside (0,1)), small enough that a
   full season of data dominates the prior. Team strength is never invented:
   the prior is symmetric and team-independent; only actual series wins and
   losses move estimates. Upcoming fixtures are never counted as history.
   Matchup conversion keeps the existing win-rate-ratio form pa/(pa+pb): a
   Bradley-Terry-STYLE heuristic on smoothed rates, NOT a formally fitted
   Bradley-Terry model (no iterative fitting is performed). 'even' mode is
   the documented neutral baseline (0.5 for every fixture). */
var PRIOR_W=opts.priorW!=null?+opts.priorW:2,PRIOR_N=opts.priorN!=null?+opts.priorN:4;
if(!(PRIOR_N>0)||!(PRIOR_W>=0)||!(PRIOR_W<=PRIOR_N)){PRIOR_W=2;PRIOR_N=4;}
var sweepP=opts.sweepP!=null?+opts.sweepP:(sweepN+PRIOR_W)/(sweepD+PRIOR_N);
if(!(sweepP>=0&&sweepP<=1))sweepP=0.5;
diag.sweepP=sweepP;
function winRate(r){return (r.won+PRIOR_W)/(r.won+r.lost+PRIOR_N);}
function qWin(a,b){
if(mode==='even')return 0.5;
var pa=winRate(byKey[a]),pb=winRate(byKey[b]);
return (pa+pb)>0?pa/(pa+pb):0.5;
}
function maxP(r){return r.pts+Math.max(0,totalSeries-(r.won+r.lost));}
var p6=rows.length>=playoffSlots&&playoffSlots>0?rows[playoffSlots-1].pts:0;
var p2=rows.length>=upperSlots&&upperSlots>0?rows[upperSlots-1].pts:0;
function maxPoss(list){var m=-1;list.forEach(function(r){var v=maxP(r);if(v>m)m=v;});return m;}
var maxBelow6=playoffSlots>0?maxPoss(rows.slice(playoffSlots)):Infinity;
var maxBelow2=upperSlots>0?maxPoss(rows.slice(upperSlots)):Infinity;
var out={},cut6={},cut2={};
rows.forEach(function(r){
var pc=playoffSlots>0?(r.pts>maxBelow6?{v:100,why:'Clinched on points'}:(maxP(r)<p6?{v:0,why:'Eliminated on points'}:null)):{v:0,why:'No playoff slots'};
var ub=upperSlots>0?(r.pts>maxBelow2?{v:100,why:'Clinched on points'}:(maxP(r)<p2?{v:0,why:'Eliminated on points'}:null)):{v:0,why:'No upper slots'};
out[r.key]={pc:pc,ub:ub};
if(!pc)cut6[r.key]=0;
if(!ub)cut2[r.key]=0;
});
function rankOrder(P,D,sim){
return rankTeams(rows.map(function(r){return r.key;}),P,D,sim,baseH2H);
}
var exactWhy='Exact enumeration over '+remFx.length+' remaining series';
if(exact){
var n=remFx.length;
if(n>12)throw new Error('exact enumeration over '+n+' fixtures infeasible');
var P0={},D0={};
rows.forEach(function(r){P0[r.key]=r.pts;D0[r.key]=r.diff;});
var acc6={},acc2={};
rows.forEach(function(r){acc6[r.key]=0;acc2[r.key]=0;});
var sim=[];
(function rec(i,prob){
if(prob<=0)return;
if(i===n){
var ord=rankOrder(P0,D0,sim);
var s,u;
for(s=0;s<playoffSlots&&s<ord.length;s++)acc6[ord[s]]+=prob;
for(u=0;u<upperSlots&&u<ord.length;u++)acc2[ord[u]]+=prob;
return;}
var f=remFx[i],q=qWin(f.a,f.b);
var branches=[[f.a,q*sweepP,2],[f.a,q*(1-sweepP),1],[f.b,(1-q)*sweepP,2],[f.b,(1-q)*(1-sweepP),1]];
for(var bi=0;bi<4;bi++){
var w=branches[bi][0],bp=branches[bi][1],dg=branches[bi][2];
if(bp<=0)continue;
var l=(w===f.a)?f.b:f.a;
P0[w]++;D0[w]+=dg;D0[l]-=dg;sim.push({a:f.a,b:f.b,w:w});
rec(i+1,prob*bp);
sim.pop();P0[w]--;D0[w]-=dg;D0[l]+=dg;}
})(0,1);
rows.forEach(function(r){
var k=r.key;
if(!out[k].pc)out[k].pc={v:acc6[k]*100,why:exactWhy};
if(!out[k].ub)out[k].ub={v:acc2[k]*100,why:exactWhy};});
}else if(Object.keys(cut6).length||Object.keys(cut2).length){
var seed=seedInit|0;
var rnd=function(){seed=seed+0x6D2B79F5|0;
var t=Math.imul(seed^seed>>>15,1|seed);
t=t+Math.imul(t^t>>>7,61|t)^t;
return ((t^t>>>14)>>>0)/4294967296;};
var B=4,per=Math.max(1,Math.round(trials/B)),done=0;
var P={},D={},sim2=[];
var bkeys6=Object.keys(cut6),bkeys2=Object.keys(cut2);
for(var bIdx=0;bIdx<B;bIdx++){
var l6={},l2={};
bkeys6.forEach(function(k){l6[k]=0;});
bkeys2.forEach(function(k){l2[k]=0;});
for(var t=0;t<per;t++){
rows.forEach(function(r){P[r.key]=r.pts;D[r.key]=r.diff;});
sim2.length=0;
for(var fi=0;fi<remFx.length;fi++){
var f=remFx[fi],qq=qWin(f.a,f.b);
var w=(rnd()<qq)?f.a:f.b;
var dg=(rnd()<sweepP)?2:1;
P[w]++;
D[w]+=dg;
var ll=(w===f.a)?f.b:f.a;
D[ll]-=dg;
sim2.push({a:f.a,b:f.b,w:w});}
var ord=rankOrder(P,D,sim2);
var s2,u2;
for(s2=0;s2<playoffSlots&&s2<ord.length;s2++){var k6=ord[s2];if(k6 in cut6){cut6[k6]++;l6[k6]++;}}
for(u2=0;u2<upperSlots&&u2<ord.length;u2++){var k2=ord[u2];if(k2 in cut2){cut2[k2]++;l2[k2]++;}}
done++;}
bkeys6.forEach(function(k){
var e=Math.abs(l6[k]/per-cut6[k]/done);
if(e>diag.maxSplitErr)diag.maxSplitErr=e;});
bkeys2.forEach(function(k){
var e2=Math.abs(l2[k]/per-cut2[k]/done);
if(e2>diag.maxSplitErr)diag.maxSplitErr=e2;});}
diag.maxSplitErr=diag.maxSplitErr*100;
rows.forEach(function(r){
var k=r.key;
if(!out[k].pc){var c6=cut6[k],f6=c6/done*100,ci6=wilson(c6,done);
out[k].pc={v:f6,q:c6,n:done,why:'Seeded simulation over '+remFx.length+' remaining series: '+c6+'/'+done+' trials ~'+f6.toFixed(1)+'% (95% CI '+ci6[0].toFixed(1)+'-'+ci6[1].toFixed(1)+')'};}
if(!out[k].ub){var c2=cut2[k],f2=c2/done*100,ci2=wilson(c2,done);
out[k].ub={v:f2,q:c2,n:done,why:'Seeded simulation over '+remFx.length+' remaining series: '+c2+'/'+done+' trials ~'+f2.toFixed(1)+'% (95% CI '+ci2[0].toFixed(1)+'-'+ci2[1].toFixed(1)+')'};}});
}
var res={};rows.forEach(function(r){res[r.key]=out[r.key];});
return {chances:res,diag:diag};
}
/* CHANCES-END */
/* ANALYTICS-START */
/* C1/C2: statistical primitives + player metrics.
   Every rate carries n; lane percentiles shrink toward the lane mean so a
   3-game sample cannot rank first. Pure functions: no DOM, no DATA globals. */
const IMPACT_WEIGHTS={damageShare:0.35,kp:0.25,goldShare:0.20,towerShare:0.10,deathShare:-0.10};
function anMean(a){return a.length?a.reduce((s,x)=>s+(+x||0),0)/a.length:0;}
function anQuantile(a,q){const v=a.filter(x=>isFinite(x)).slice().sort((x,y)=>x-y);if(!v.length)return 0;const p=(v.length-1)*q,i=Math.floor(p),f=p-i;return v[i]+(v[Math.min(i+1,v.length-1)]-v[i])*f;}
function anWilson(k,n,z){z=z||1.96;if(!n)return{p:0,lo:0,hi:0,n:0};const p=k/n,den=1+z*z/n,centre=p+z*z/(2*n),m=z*Math.sqrt(p*(1-p)/n+z*z/(4*n*n));return{p:p,lo:Math.max(0,(centre-m)/den),hi:Math.min(1,(centre+m)/den),n:n};}
function anShrink(value,n,prior,weight){weight=weight==null?5:weight;if(!n)return prior;return (value*n+prior*weight)/(n+weight);}
function anPct(values,x){const v=values.filter(y=>isFinite(y)).slice().sort((a,b)=>a-b);if(!v.length)return 0;if(v.length===1)return 0.5;if(v[0]===v[v.length-1])return 0.5;if(x<=v[0])return 0;if(x>=v[v.length-1])return 1;let below=0,equal=0;v.forEach(y=>{if(y<x)below++;else if(y===x)equal++;});return (below+(equal-1)/2)/(v.length-1);}
function anMode(values){const c={};values.forEach(v=>{if(v)c[v]=(c[v]||0)+1;});return Object.entries(c).sort((a,b)=>b[1]-a[1]||a[0].localeCompare(b[0]))[0]?.[0]||'';}
function anLane(rows){return anMode(rows.map(r=>r.lane));}
/* Missing/unresolved map labels are data-quality facts, never real maps.
   Rankings called "weak maps" / "strong maps" must filter through this. */
function anKnownMap(m){const s=String(m==null?'':m).trim().toLowerCase();return !!s&&s!=='unknown'&&s!=='unresolved'&&s!=='n/a'&&s!=='null';}

function buildPlayerMetrics(players,games,teamGames,classes,opts){
  opts=opts||{};
  const priorWeight=opts.priorWeight==null?5:opts.priorWeight;
  const minGames=opts.minGames==null?5:opts.minGames;
  const canon=opts.canon||(x=>x);
  const dateOf=opts.dateOf||(()=> '');
  const teamWinRate=opts.teamWinRate||{};
  const gk=(mid,gn)=>String(mid)+':'+String(gn);
  const gameBy={};
  (games||[]).forEach(g=>{gameBy[gk(g.match_detail_id,g.game_no)]=g;});
  const tgBy={};
  (teamGames||[]).forEach(t=>{tgBy[gk(t.match_detail_id,t.game_no)+':'+t.team]=t;});

  const rows=[];
  (players||[]).forEach(r=>{
    const g=gameBy[gk(r.match_detail_id,r.game_no)]||{};
    const tg=tgBy[gk(r.match_detail_id,r.game_no)+':'+r.team]||{};
    const kills=+r.kills||0,deaths=+r.deaths||0,assists=+r.assists||0;
    const teamKills=+tg.kills||0,teamDeaths=+tg.deaths||0,teamGold=+tg.gold||0,teamDmg=+tg.hero_damage||0,teamTaken=+tg.damage_taken||0,teamTower=+tg.tower_damage||0;
    const won=g.winner==='team_a'?g.team_a===r.team:(g.winner==='team_b'?g.team_b===r.team:null);
    const opponent=r.team===g.team_a?g.team_b:(r.team===g.team_b?g.team_a:'');
    const oppTg=opponent?tgBy[gk(r.match_detail_id,r.game_no)+':'+opponent]:null;
    const close=oppTg?Math.abs(teamKills-(+oppTg.kills||0))<=5:false;
    rows.push({
      player:canon(r.player), rawPlayer:r.player, team:r.team, hero:r.hero, lane:r.lane||'',
      mid:String(r.match_detail_id), gn:+r.game_no, date:dateOf(r.match_detail_id),
      opponent:opponent, oppWr:(opponent&&teamWinRate[opponent]!=null)?+teamWinRate[opponent]:null, close:close,
      kills:kills, deaths:deaths, assists:assists, gold:+r.gold||0, gpm:+r.gold_per_min||0,
      dmg:+r.hero_damage||0, taken:+r.damage_taken||0, tower:+r.tower_damage||0,
      kda:(kills+assists)/Math.max(1,deaths),
      win:won===null?null:(won?1:0),
      damageShare:teamDmg?((+r.hero_damage||0)/teamDmg):0,
      goldShare:teamGold?((+r.gold||0)/teamGold):0,
      takenShare:teamTaken?((+r.damage_taken||0)/teamTaken):0,
      towerShare:teamTower?((+r.tower_damage||0)/teamTower):0,
      kp:teamKills?((kills+assists)/teamKills):0,
      deathShare:teamDeaths?deaths/teamDeaths:0,
      heroRole:(classes&&classes[r.hero]&&classes[r.hero].primary_role)||''
    });
  });

  const heroDmg={};
  rows.forEach(r=>{(heroDmg[r.hero]=heroDmg[r.hero]||[]).push(r.damageShare);});
  const heroDmgMean={};
  Object.keys(heroDmg).forEach(h=>{heroDmgMean[h]=anMean(heroDmg[h]);});
  const leagueHero={};
  rows.forEach(r=>{const x=leagueHero[r.hero]=leagueHero[r.hero]||{n:0,w:0};x.n++;if(r.win===1)x.w++;});

  const byP={};
  rows.forEach(r=>{(byP[r.player]=byP[r.player]||[]).push(r);});
  const out=Object.keys(byP).map(player=>{
    const rs=byP[player].slice().sort((a,b)=>String(a.date).localeCompare(String(b.date))||(a.gn-b.gn));
    const n=rs.length,wins=rs.filter(r=>r.win===1).length,decided=rs.filter(r=>r.win!==null).length;
    const kda=anMean(rs.map(r=>r.kda));
    const kdas=rs.map(r=>r.kda);
    const lane=anLane(rs);
    const off=rs.filter(r=>lane&&r.lane&&r.lane!==lane);
    const main=rs.filter(r=>!lane||!r.lane||r.lane===lane);
    const last5=rs.slice(-5);
    const closed=rs.filter(r=>r.close);
    const closeWins=closed.filter(r=>r.win===1).length;
    const tier=arr=>({n:arr.length,wins:arr.filter(r=>r.win===1).length,kda:anMean(arr.map(r=>r.kda)),damageShare:anMean(arr.map(r=>r.damageShare))});
    const strong=tier(rs.filter(r=>r.oppWr!=null&&r.oppWr>=0.5));
    const weak=tier(rs.filter(r=>r.oppWr!=null&&r.oppWr<0.5));
    const byHero={};
    rs.forEach(r=>{(byHero[r.hero]=byHero[r.hero]||[]).push(r);});
    const pool=Object.keys(byHero).map(h=>{
      const hs=byHero[h],w=hs.filter(r=>r.win===1).length,lg=leagueHero[h]||{n:0,w:0};
      const wr=hs.length?w/hs.length:0,leagueWr=lg.n?lg.w/lg.n:0;
      return {hero:h,games:hs.length,wins:w,wr:wr,leagueWr:leagueWr,delta:wr-leagueWr,usage:hs.length/n,comfort:(hs.length/n)*wr,lanes:[...new Set(hs.map(r=>r.lane).filter(Boolean))]};
    }).sort((a,b)=>b.games-a.games||a.hero.localeCompare(b.hero));
    const effectivePool=pool.filter(h=>h.games>=2&&h.wr>=0.5).length;
    const flexHeroes=pool.filter(h=>h.lanes.length>=2).length;
    const comfort=pool.length?Math.max(...pool.map(h=>h.comfort)):0;
    return {
      player:player, team:anMode(rs.map(r=>r.team)), lane:lane, role:lane,
      games:n, wins:wins, decided:decided, winRate:decided?wins/decided:0, winCI:anWilson(wins,decided),
      kda:kda, gpm:anMean(rs.map(r=>r.gpm)),
      damageShare:anMean(rs.map(r=>r.damageShare)),
      goldShare:anMean(rs.map(r=>r.goldShare)),
      takenShare:anMean(rs.map(r=>r.takenShare)),
      towerShare:anMean(rs.map(r=>r.towerShare)),
      kp:anMean(rs.map(r=>r.kp)),
      deathShare:anMean(rs.map(r=>r.deathShare)),
      heroAdjDamage:anMean(rs.map(r=>r.damageShare-(heroDmgMean[r.hero]||0))),
      kdaP10:anQuantile(kdas,0.10),kdaP25:anQuantile(kdas,0.25),kdaP50:anQuantile(kdas,0.50),kdaP75:anQuantile(kdas,0.75),kdaP90:anQuantile(kdas,0.90),
      kdaIQR:anQuantile(kdas,0.75)-anQuantile(kdas,0.25),
      formDelta:(last5.length?anMean(last5.map(r=>r.kda)):0)-kda,
      offLaneGames:off.length,
      offLaneDelta:(off.length&&main.length)?anMean(off.map(r=>r.kda))-anMean(main.map(r=>r.kda)):null,
      heroes:new Set(rs.map(r=>r.hero)).size,
      close:{n:closed.length,wins:closeWins,winRate:closed.length?closeWins/closed.length:0,winCI:anWilson(closeWins,closed.length)},
      oppTier:{strong:strong,weak:weak,kdaDelta:strong.kda-weak.kda,damageDelta:strong.damageShare-weak.damageShare},
      pool:pool,effectivePool:effectivePool,flexHeroes:flexHeroes,comfort:comfort,
      dpg:anMean(rs.map(r=>r.dmg/Math.max(1,r.gold))),
      towerPerGame:anMean(rs.map(r=>r.tower)),
      small:n<minGames,
      raw:rs
    };
  });

  const metrics=['kda','gpm','damageShare','goldShare','towerShare','kp','deathShare'];
  const lanes={};
  out.forEach(p=>{(lanes[p.lane]=lanes[p.lane]||[]).push(p);});
  Object.keys(lanes).forEach(l=>{
    const list=lanes[l];
    metrics.forEach(k=>{
      const prior=anMean(list.map(p=>p[k]));
      list.forEach(p=>{p['_s_'+k]=anShrink(p[k],p.games,prior,priorWeight);});
      const vals=list.map(p=>p['_s_'+k]);
      list.forEach(p=>{p['pct_'+k]=anPct(vals,p['_s_'+k]);});
    });
  });
  out.forEach(p=>{
    p.pct={kda:p.pct_kda,gpm:p.pct_gpm,damageShare:p.pct_damageShare,goldShare:p.pct_goldShare,towerShare:p.pct_towerShare,kp:p.pct_kp,deathShare:p.pct_deathShare};
    p.shrunk={kda:p._s_kda,gpm:p._s_gpm,damageShare:p._s_damageShare,goldShare:p._s_goldShare,towerShare:p._s_towerShare,kp:p._s_kp,deathShare:p._s_deathShare};
    p.impact=100*(IMPACT_WEIGHTS.damageShare*p.pct.damageShare+IMPACT_WEIGHTS.kp*p.pct.kp+IMPACT_WEIGHTS.goldShare*p.pct.goldShare+IMPACT_WEIGHTS.towerShare*p.pct.towerShare+IMPACT_WEIGHTS.deathShare*p.pct.deathShare);
    metrics.forEach(k=>{delete p['_s_'+k];delete p['pct_'+k];});
  });
  out.sort((a,b)=>b.impact-a.impact||a.player.localeCompare(b.player));
  return {players:out,lanes:Object.keys(lanes).sort(),weights:IMPACT_WEIGHTS,priorWeight:priorWeight,minGames:minGames};
}
function anMulberry32(a){return function(){a|=0;a=a+0x6D2B79F5|0;let t=Math.imul(a^a>>>15,1|a);t=t+Math.imul(t^t>>>7,61|t)^t;return((t^t>>>14)>>>0)/4294967296;};}
function anBT(rows,teams,prior,dedupe){
  const idx={};teams.forEach((t,i)=>idx[t]=i);
  const p=teams.map(()=>1),wins=teams.map(()=>prior),opp=teams.map(()=>new Map());
  const seen={};
  (rows||[]).forEach(r=>{if(!r)return;
    // A game has two team-perspective rows. The symmetric updater already
    // credits both sides, so discard the second perspective here. This is the
    // one-observation-per-game contract (tested in test_analytics.js). Bootstrap
    // callers pass dedupe=false because sampling with replacement must keep
    // duplicate game draws.
    const key=(r.match_detail_id!=null&&r.game_no!=null)?String(r.match_detail_id)+':'+String(r.game_no):null;
    if(dedupe!==false&&key!==null){if(seen[key])return;seen[key]=1;}
    const i=idx[r.team],j=idx[r.opponent];if(i==null||j==null||i===j)return;if(r.win===1)wins[i]++;else wins[j]++;opp[i].set(j,(opp[i].get(j)||0)+1);opp[j].set(i,(opp[j].get(i)||0)+1);});
  for(let it=0;it<40;it++){
    const next=p.map((pi,i)=>{let den=2*prior/(pi+1);opp[i].forEach((cnt,j)=>{den+=cnt/(pi+p[j]);});return wins[i]/Math.max(1e-9,den);});
    for(let i=0;i<next.length;i++)p[i]=next[i];
  }
  return p;
}
function buildTeamMetrics(teamGames,teams,games,opts){
  opts=opts||{};
  const bootstraps=opts.bootstraps==null?100:opts.bootstraps;
  const prior=opts.prior==null?1:opts.prior;
  const dateOf=opts.dateOf||(()=> '');
  const gk=(mid,gn)=>String(mid)+':'+String(gn);
  const gameBy={};(games||[]).forEach(g=>{gameBy[gk(g.match_detail_id,g.game_no)]=g;});
  const tgBy={};(teamGames||[]).forEach(t=>{tgBy[gk(t.match_detail_id,t.game_no)+':'+t.team]=t;});
  const list=teams||[];
  const codes=list.map(t=>t.team);
  // Fit/bootstrap the paired game result once, not once per perspective row.
  // Resampling the game keeps both opponents together in each bootstrap copy.
  const seenGames={},gameRows=[];
  (teamGames||[]).forEach(r=>{if(!r)return;const k=gk(r.match_detail_id,r.game_no);if(seenGames[k])return;seenGames[k]=1;gameRows.push(r);});
  const rating=anBT(gameRows,codes,prior,false);
  const ratingOf=Object.fromEntries(codes.map((c,i)=>[c,rating[i]]));
  const rand=anMulberry32(opts.seed==null?7:opts.seed);
  const boot=[];
  for(let b=0;b<bootstraps&&gameRows.length;b++){
    const sample=[];
    for(let i=0;i<gameRows.length;i++)sample.push(gameRows[Math.floor(rand()*gameRows.length)]);
    boot.push(anBT(sample,codes,prior,false));
  }
  const ci={};codes.forEach((c,i)=>{const v=boot.map(x=>x[i]).sort((a,b)=>a-b);ci[c]=v.length?[v[Math.floor(v.length*0.025)],v[Math.floor(v.length*0.975)]]:[rating[i],rating[i]];});
  const toElo=p=>1500+400*Math.log10(Math.max(1e-6,p));
  const mean=a=>a.length?a.reduce((s,x)=>s+x,0)/a.length:0;
  return {teams:list.map(t=>{
    const code=t.team;
    const rs=(teamGames||[]).filter(r=>r.team===code).slice().sort((a,b)=>String(dateOf(a.match_detail_id)).localeCompare(String(dateOf(b.match_detail_id)))||(+a.game_no-+b.game_no));
    const n=rs.length,wins=rs.filter(r=>r.win===1).length;
    const last5=rs.slice(-5),form5=last5.length?last5.filter(r=>r.win===1).length/last5.length:0;
    const winD=rs.filter(r=>r.win===1),lossD=rs.filter(r=>r.win===0);
    const diffs=rs.map(r=>{const o=tgBy[gk(r.match_detail_id,r.game_no)+':'+r.opponent]||{};return {k:(+r.kills||0)-(+o.kills||0),g:(+r.gold||0)-(+o.gold||0),d:(+r.hero_damage||0)-(+o.hero_damage||0),tw:(+r.tower_damage||0)-(+o.tower_damage||0)};});
    const sides={blue:{n:0,w:0},red:{n:0,w:0}};
    rs.forEach(r=>{const g=gameBy[gk(r.match_detail_id,r.game_no)]||{};const raw=(r.team===g.team_a?g.team_a_side:g.team_b_side)||'';const side=String(raw).toLowerCase();if(sides[side]){sides[side].n++;if(r.win===1)sides[side].w++;}});
    const byMatch={};rs.forEach(r=>{(byMatch[r.match_detail_id]=byMatch[r.match_detail_id]||[]).push(r);});
    const g3=rs.filter(r=>+r.game_no===3),dec=[];
    Object.keys(byMatch).forEach(mid=>{const arr=byMatch[mid];const mx=Math.max(...arr.map(r=>+r.game_no));dec.push(...arr.filter(r=>+r.game_no===mx));});
    const series=Object.keys(byMatch).map(mid=>{const arr=byMatch[mid];return {win:arr.filter(r=>r.win===1).length>arr.length/2,date:String(dateOf(mid))};}).sort((a,b)=>a.date.localeCompare(b.date));
    const last5s=series.slice(-5),form5Series=last5s.length?last5s.filter(s=>s.win).length/last5s.length:0;
    const h2h={};rs.forEach(r=>{const o=h2h[r.opponent]=h2h[r.opponent]||{n:0,w:0};o.n++;if(r.win===1)o.w++;});
    const sos=mean(rs.map(r=>ratingOf[r.opponent]||1));
    const ciV=ci[code]||[ratingOf[code]||1,ratingOf[code]||1];
    const maps={};rs.forEach(r=>{const m=r.map_mode||'Unknown';const x=maps[m]=maps[m]||{n:0,w:0};x.n++;if(r.win===1)x.w++;});
    return {
      team:code,team_name:t.team_name||code,team_slug:t.team_slug||code,
      games:n,wins:wins,losses:n-wins,winRate:n?wins/n:0,winCI:anWilson(wins,n),
      rating:toElo(ratingOf[code]||1),ratingCI:[toElo(ciV[0]),toElo(ciV[1])],sos:rs.length?toElo(sos):0,
      form5:form5,
      form5Series:form5Series,
      series:series.length,seriesWins:series.filter(s=>s.win).length,seriesLosses:series.filter(s=>!s.win).length,
      h2h:h2h,
      tempo:{winSec:mean(winD.map(r=>+r.duration_sec||0)),lossSec:mean(lossD.map(r=>+r.duration_sec||0)),fastWins:winD.filter(r=>(+r.duration_sec||0)<900).length,lateWins:winD.filter(r=>(+r.duration_sec||0)>1320).length},
      dominance:{killDiff:mean(diffs.map(d=>d.k)),goldDiff:mean(diffs.map(d=>d.g)),damageDiff:mean(diffs.map(d=>d.d)),towerDiff:mean(diffs.map(d=>d.tw)),blowout:n?rs.filter((r,i)=>Math.abs(diffs[i].k)>=10).length/n:0},
      clutch:{game3:{n:g3.length,w:g3.filter(r=>r.win===1).length},decider:{n:dec.length,w:dec.filter(r=>r.win===1).length}},
      side:sides,
      maps:Object.keys(maps).map(m=>({map:m,n:maps[m].n,w:maps[m].w,wr:maps[m].n?maps[m].w/maps[m].n:0})).sort((a,b)=>b.n-a.n||a.map.localeCompare(b.map))
    };
  }),method:{prior:prior,bootstraps:bootstraps,model:'Bradley-Terry on one paired observation per game, 1-1 prior vs an average team; bootstrap resamples whole games (opponents stay paired); rating = 1500 + 400*log10(strength)'}};
}
function buildDraftMetrics(picks,bans,games,classes,opts){
  opts=opts||{};
  const minPair=opts.minPair==null?5:opts.minPair;
  const dateOf=opts.dateOf||(()=> '');
  const dateMs=d=>{const t=Date.parse(d);return isFinite(t)?t:null;};
  const allDates=(games||[]).map(g=>dateOf(g.match_detail_id)).map(dateMs).filter(x=>x!=null);
  const start=allDates.length?Math.min(...allDates):0;
  // Explicit 7-day date windows from the first game date. These are not
  // official competition weeks; the UI labels them as date windows.
  const weekOf=mid=>{const t=dateMs(dateOf(mid));return t==null||!start?-1:Math.floor((t-start)/604800000);};
  const weekGames={},weekRange={};
  (games||[]).forEach(g=>{const w=weekOf(g.match_detail_id);if(w>=0){weekGames[w]=(weekGames[w]||0)+1;
    const d=dateOf(g.match_detail_id),r=weekRange[w]=weekRange[w]||{start:d,end:d};
    if(String(d)<String(r.start))r.start=d;if(String(d)>String(r.end))r.end=d;}});
  const gk=(mid,gn)=>String(mid)+':'+String(gn);
  const gameBy={};(games||[]).forEach(g=>{gameBy[gk(g.match_detail_id,g.game_no)]=g;});
  const wonBy=(g,team)=>g&&(g.winner==='team_a'?g.team_a===team:g.winner==='team_b'?g.team_b===team:null);
  const H={};
  const ensure=h=>H[h]||(H[h]={hero:h,picks:0,bans:0,wins:0,lanes:{},sides:{blue:{n:0,w:0},red:{n:0,w:0}},maps:{},weeks:{},role:(classes&&classes[h]&&classes[h].primary_role)||'',damage:(classes&&classes[h]&&classes[h].damage_type)||''});
  (picks||[]).forEach(p=>{const h=ensure(p.hero);const g=gameBy[gk(p.match_detail_id,p.game_no)]||{};const w=wonBy(g,p.team);h.picks++;if(w)h.wins++;h.lanes[p.lane]=(h.lanes[p.lane]||0)+1;const side=String(p.side||'').toLowerCase();if(h.sides[side]){h.sides[side].n++;if(w)h.sides[side].w++;}const m=g.map_mode||'Unknown';const mm=h.maps[m]=h.maps[m]||{n:0,w:0};mm.n++;if(w)mm.w++;const wk=weekOf(p.match_detail_id);if(wk>=0){const x=h.weeks[wk]=h.weeks[wk]||{picks:0,bans:0};x.picks++;}});
  (bans||[]).forEach(b=>{const h=ensure(b.hero);h.bans++;const wk=weekOf(b.match_detail_id);if(wk>=0){const x=h.weeks[wk]=h.weeks[wk]||{picks:0,bans:0};x.bans++;}});
  Object.keys(H).forEach(h=>{const x=H[h];x.winRate=x.picks?x.wins/x.picks:0;x.winCI=anWilson(x.wins,x.picks);x.flex=Object.keys(x.lanes).filter(l=>x.lanes[l]/Math.max(1,x.picks)>=0.1).length;});
  const heroes=Object.keys(H).map(h=>H[h]).sort((a,b)=>b.picks-a.picks||b.bans-a.bans||a.hero.localeCompare(b.hero));
  const weeks=Object.keys(weekGames).map(Number).sort((a,b)=>a-b);
  const last=weeks.length?weeks[weeks.length-1]:-1,prev=weeks.length>1?weeks[weeks.length-2]:-1;
  const movement=(last>=0&&prev>=0)?Object.keys(H).map(k=>{const h=H[k];const a=h.weeks[last]||{picks:0,bans:0},b=h.weeks[prev]||{picks:0,bans:0};const recent=(a.picks+a.bans)/Math.max(1,weekGames[last]),previous=(b.picks+b.bans)/Math.max(1,weekGames[prev]);return {hero:h.hero,recent:recent,previous:previous,delta:recent-previous,picks:a.picks,bans:a.bans,games:weekGames[last]||0,period:{index:last,start:(weekRange[last]||{}).start||'',end:(weekRange[last]||{}).end||''},previousPeriod:{index:prev,start:(weekRange[prev]||{}).start||'',end:(weekRange[prev]||{}).end||''},adjacent:prev===last-1};}).sort((a,b)=>b.delta-a.delta||a.hero.localeCompare(b.hero)):[];

  const pickBy={};
  (picks||[]).forEach(p=>{const k=gk(p.match_detail_id,p.game_no)+':'+p.team;(pickBy[k]=pickBy[k]||[]).push(p);});
  const pairMap={};
  Object.keys(pickBy).forEach(k=>{
    const parts=k.split(':'),g=gameBy[gk(parts[0],parts[1])]||{},team=parts[2],w=wonBy(g,team);
    const list=pickBy[k].slice().sort((a,b)=>a.hero.localeCompare(b.hero));
    for(let i=0;i<list.length;i++)for(let j=i+1;j<list.length;j++){
      const a=list[i].hero,b=list[j].hero,key=a+'|'+b,e=pairMap[key]=pairMap[key]||{a:a,b:b,n:0,w:0};
      e.n++;if(w)e.w++;
    }
  });
  const pairs=Object.keys(pairMap).map(k=>pairMap[k]).map(e=>{const wr=e.n?e.w/e.n:0;const wa=(H[e.a]&&H[e.a].winRate)||0,wb=(H[e.b]&&H[e.b].winRate)||0;return {...e,wr:wr,expected:(wa+wb)/2,delta:wr-(wa+wb)/2};}).sort((a,b)=>b.n-a.n||a.a.localeCompare(b.a));

  const counterMap={};
  (games||[]).forEach(g=>{
    const A=pickBy[gk(g.match_detail_id,g.game_no)+':'+g.team_a]||[],B=pickBy[gk(g.match_detail_id,g.game_no)+':'+g.team_b]||[];
    const aWon=g.winner==='team_a';
    A.forEach(a=>B.forEach(b=>{
      const swap=a.hero>b.hero,key=swap?b.hero+'|'+a.hero:a.hero+'|'+b.hero;
      const e=counterMap[key]=counterMap[key]||{a:swap?b.hero:a.hero,b:swap?a.hero:b.hero,n:0,w:0};
      e.n++;if((!swap&&aWon)||(swap&&!aWon))e.w++;
    }));
  });
  const counters=Object.keys(counterMap).map(k=>counterMap[k]).map(e=>{const wr=e.n?e.w/e.n:0;const wa=(H[e.a]&&H[e.a].winRate)||0,wb=(H[e.b]&&H[e.b].winRate)||0;const expected=(wa+(1-wb))/2;return {...e,wr:wr,expected:expected,delta:wr-expected};}).sort((a,b)=>b.n-a.n||a.a.localeCompare(b.a));

  const T={};
  const ensureT=team=>T[team]||(T[team]={team:team,picks:0,heroes:{},bans:{},firstBans:{blue:{},red:{}},heroStats:{}});
  (picks||[]).forEach(p=>{const t=ensureT(p.team);t.picks++;t.heroes[p.hero]=(t.heroes[p.hero]||0)+1;const g=gameBy[gk(p.match_detail_id,p.game_no)]||{},w=wonBy(g,p.team),x=t.heroStats[p.hero]=t.heroStats[p.hero]||{n:0,w:0};x.n++;if(w)x.w++;});
  (bans||[]).forEach(b=>{const g=gameBy[gk(b.match_detail_id,b.game_no)]||{};const team=b.side==='A'?g.team_a:g.team_b;if(!team)return;const t=ensureT(team);t.bans[b.hero]=(t.bans[b.hero]||0)+1;if(+b.ban_order===1){const raw=(b.side==='A'?g.team_a_side:g.team_b_side)||'';const side=String(raw).toLowerCase();if(t.firstBans[side])t.firstBans[side][b.hero]=(t.firstBans[side][b.hero]||0)+1;}});
  const totalPicks=Object.keys(T).reduce((s,k)=>s+T[k].picks,0)||1;
  const leagueHero={};Object.keys(T).forEach(k=>{Object.keys(T[k].heroes).forEach(h=>{leagueHero[h]=(leagueHero[h]||0)+T[k].heroes[h];});});
  Object.keys(leagueHero).forEach(h=>{leagueHero[h]/=totalPicks;});
  const top=(o,n)=>Object.keys(o).sort((a,b)=>o[b]-o[a]||a.localeCompare(b)).slice(0,n);
  const teams=Object.keys(T).map(k=>T[k]).map(t=>{
    const hhi=Object.keys(t.heroes).reduce((s,h)=>s+Math.pow(t.heroes[h]/Math.max(1,t.picks),2),0);
    const games=Math.max(1,Math.round(t.picks/5));
    const pockets=Object.keys(t.heroes).filter(h=>t.heroes[h]>=3&&(t.heroes[h]/Math.max(1,t.picks))>=(leagueHero[h]||0)*2).map(h=>({hero:h,n:t.heroes[h],share:t.heroes[h]/t.picks,leagueShare:leagueHero[h]})).sort((a,b)=>b.n-a.n);
    return {...t,topPicks:top(t.heroes,5).map(h=>({hero:h,n:t.heroes[h],share:t.heroes[h]/games})),topBans:top(t.bans,5).map(h=>({hero:h,n:t.bans[h]})),firstBanBlue:top(t.firstBans.blue,3).map(h=>({hero:h,n:t.firstBans.blue[h]})),firstBanRed:top(t.firstBans.red,3).map(h=>({hero:h,n:t.firstBans.red[h]})),hhi:hhi,pocketPicks:pockets};
  }).sort((a,b)=>b.picks-a.picks||a.team.localeCompare(b.team));

  const maps={};
  (games||[]).forEach(g=>{const m=g.map_mode||'Unknown';const e=maps[m]=maps[m]||{map:m,games:0,blueWins:0,totalSec:0,heroes:{}};e.games++;e.totalSec+=+g.duration_sec||0;const blue=g.team_a_side==='blue'?g.team_a:g.team_b;const blueWon=(g.winner==='team_a'&&blue===g.team_a)||(g.winner==='team_b'&&blue===g.team_b);if(blueWon)e.blueWins++;const A=pickBy[gk(g.match_detail_id,g.game_no)+':'+g.team_a]||[],B=pickBy[gk(g.match_detail_id,g.game_no)+':'+g.team_b]||[];[...A,...B].forEach(p=>{e.heroes[p.hero]=(e.heroes[p.hero]||0)+1;});});
  const mapMeta=Object.keys(maps).map(m=>maps[m]).map(m=>({...m,blueWR:m.games?m.blueWins/m.games:0,avgSec:m.games?m.totalSec/m.games:0,topHeroes:Object.keys(m.heroes).sort((a,b)=>m.heroes[b]-m.heroes[a]||a.localeCompare(b)).slice(0,5).map(h=>({hero:h,n:m.heroes[h]}))})).sort((a,b)=>b.games-a.games||a.map.localeCompare(b.map));

  const comps={};
  Object.keys(pickBy).forEach(k=>{
    const parts=k.split(':'),g=gameBy[gk(parts[0],parts[1])]||{},team=parts[2],list=pickBy[k];
    if(list.length<5)return;
    const w=wonBy(g,team),cls=list.map(p=>(classes&&classes[p.hero])||{});
    const frontline=cls.filter(c=>c.primary_role==='Tank'||c.primary_role==='Fighter').length;
    const phys=cls.filter(c=>c.damage_type==='physical').length,mag=cls.filter(c=>c.damage_type==='magic').length;
    const dmg=phys>=3&&mag<=1?'physical':(mag>=3&&phys<=1?'magic':'mixed');
    const cc=cls.filter(c=>(c.specialties||[]).some(s=>/crowd control|initiator|engage|cc/i.test(String(s)))).length;
    const key=dmg+'|'+frontline,e=comps[key]=comps[key]||{damage:dmg,frontline:frontline,n:0,w:0,ccTotal:0};
    e.n++;if(w)e.w++;e.ccTotal+=cc;
  });
  const compositions=Object.keys(comps).map(k=>comps[k]).map(e=>({...e,wr:e.n?e.w/e.n:0,winCI:anWilson(e.w,e.n),avgCC:e.n?e.ccTotal/e.n:0})).sort((a,b)=>b.n-a.n||a.damage.localeCompare(b.damage)||a.frontline-b.frontline);

  const movementInfo=movement.length?{period:movement[0].period,previousPeriod:movement[0].previousPeriod,adjacent:movement[0].adjacent}:{period:null,previousPeriod:null,adjacent:false};
  return {heroes:heroes,pairs:pairs.filter(e=>e.n>=minPair),counters:counters.filter(e=>e.n>=minPair),teams:teams,maps:mapMeta,compositions:compositions,movement:movement,movementInfo:movementInfo,method:{minPair:minPair,pairBaseline:'average of the two heroes overall win rates',counterBaseline:'average of hero A win rate and hero B loss rate',compositionBaseline:'frontline = Tank/Fighter count; damage = 3+ physical or magic picks; CC = specialties mentioning Crowd Control/Initiator/Engage',movement:'presence per game in the last two non-empty 7-day date windows; windows are not official competition weeks'}};
}
function buildBanRanking(team,dm,minN){
  const t=(dm&&dm.teams||[]).find(x=>x.team===team);
  if(!t)return [];
  const games=Math.max(1,Math.round(t.picks/5)),floor=minN==null?1:minN;
  // This is a pick-threat ranking against the opponent, not a claim about the
  // opponent's ban intent. Presence is their observed pick rate; their own bans
  // are reported separately as context and never enter the score.
  return Object.keys(t.heroStats||{}).map(h=>{
    const s=t.heroStats[h],bans=(t.bans&&t.bans[h])||0;
    const presence=s.n/games,contestRate=(s.n+bans)/games,wr=s.n?s.w/s.n:0;
    return {hero:h,picks:s.n,wins:s.w,bans:bans,wr:wr,presence:presence,contestRate:contestRate,score:presence*wr,n:s.n};
  }).filter(x=>x.n>=floor).sort((a,b)=>b.score-a.score||a.hero.localeCompare(b.hero));
}
/* ANALYTICS-END */
function poRow(m){return String(m.schedule_id||m.match_id||'').indexOf('playoffs')>-1||(m.team_a==='TBD'&&m.team_b==='TBD');}
function playoffChance(){
const rows=[...DATA.standings].sort((a,b)=>a.rank-b.rank);
const key=r=>String(r.team_slug||r.team_name||'').toLowerCase();
const known={};rows.forEach(r=>{known[key(r)]=1;});
const playedMap={};rows.forEach(r=>{playedMap[key(r)]=(+r.match_win||0)+(+r.match_lose||0);});
const nf=normalizeFixtures(DATA.schedule||[],known,playedMap,TOTAL_SERIES);
const standingsN=rows.map(r=>({key:key(r),pts:+r.match_point||0,won:+r.match_win||0,lost:+r.match_lose||0,diff:+r.net_game_win||0}));
const res=calcChances(standingsN,nf.fixtures,{totalSeries:TOTAL_SERIES,playoffSlots:PLAYOFF_SLOTS,upperSlots:UPPER_BRACKET_SLOTS,trials:TRIALS,seed:SEASON.model.seed,priorW:SEASON.model.priorWins,priorN:SEASON.model.priorGames});
const out={};
rows.forEach(r=>{const k=key(r);const e=(res.chances||{})[k]||{pc:{v:0,why:'Eliminated'},ub:{v:0,why:'Eliminated'}};
out[k]={pc:{v:Math.round(e.pc.v),why:e.pc.why||''},ub:{v:Math.round(e.ub.v),why:e.ub.why||''}};});
return out;}
function standBoard(){
const stBase=[...DATA.standings].sort((a,b)=>a.rank-b.rank);
const pcMap=playoffChance();
stBase.forEach(s=>{const k=String(s.team_slug||s.team_name||'').toLowerCase();const e=pcMap[k]||{pc:{v:0},ub:{v:0}};s._pc=e.pc.v;s._pcWhy=e.pc.why||'';s._ub=e.ub.v;s._ubWhy=e.ub.why||'';});
const sval=(s,k)=>k==='team'?s.team_name:k==='pts'?+s.match_point:k==='pc'?+s._pc:k==='ub'?+s._ub:k==='mw'?+s.match_win:k==='gw'?+s.game_win:k==='df'?+s.net_game_win:+s.rank;
const st=S.tsort.t==='stand'?srt(stBase,s=>sval(s,S.tsort.k),S.tsort.k==='team'):stBase;
return `<div class="pin" style="grid-column:1/-1"><div class="body"><div class="phasebar"><div><div class="kicker">Regular season</div><h3 style="margin:.25em 0">Standings</h3></div></div><div class="lscroll"><table style="min-width:700px"><tr>${th('stand','rank','#')}${th('stand','team','Team')}${th('stand','pts','Pts')}${th('stand','mw','Match W-L')}${th('stand','gw','Game W-L')}${th('stand','df','+/-')}${th('stand','pc','% Playoff Chance')}${th('stand','ub','% Upper Bracket')}</tr>${st.map(s=>{const slug=(s.team_slug||s.team_name||'').toLowerCase();const ng=+s.net_game_win||0;return `<tr><td>${esc(s.rank)}</td><td><img src="${TICON(slug)}" alt="" loading="lazy" style="width:20px;height:20px;object-fit:contain;vertical-align:-5px" ${IMG_HIDE}> ${esc(s.team_name)}</td><td>${esc(s.match_point)}</td><td>${esc(s.match_win)}-${esc(s.match_lose)}</td><td>${esc(s.game_win)}-${esc(s.game_lose)}</td><td>${ng>0?'+'+ng:ng}</td><td title="${esc(s._pcWhy||'Playoff chance')}"><b>${s._pc}%</b></td><td title="${esc(s._ubWhy||'Upper bracket chance')}"><b>${s._ub}%</b></td></tr>`;}).join('')}</table></div></div></div>`;}
function teamBoard(){
const ts=[...(DATA.team_season||[])].sort((a,b)=>(+b.win_rate||0)-(+a.win_rate||0)||(+b.kda||0)-(+a.kda||0));
if(!ts.length)return '';
const games=ts.reduce((n,t)=>n+(+t.games||0),0);
return `<div class="pin" style="grid-column:1/-1"><div class="body"><div class="phasebar"><div><div class="kicker">Derived from ${games} team-games</div><h3 style="margin:.25em 0">Team profiles</h3></div></div><div class="lscroll"><table style="min-width:800px"><tr><th>Team</th><th>Games GP</th><th>Game W-L</th><th>Win%</th><th>KDA</th><th>Avg gold</th><th>Avg game</th></tr>${ts.map(t=>`<tr><td><img src="${TICON(t.team_slug||t.team)}" alt="" loading="lazy" style="width:20px;height:20px;object-fit:contain;vertical-align:-5px" ${IMG_HIDE}> ${esc(t.team_name||t.team)}</td><td>${esc(t.games)}</td><td>${esc(t.wins)}-${esc(t.losses)}</td><td>${Math.round((+t.win_rate||0)*100)}%</td><td>${(+t.kda||0).toFixed(2)}</td><td>${Math.round(+t.avg_gold||0).toLocaleString()}</td><td>${fmtDur(+t.avg_duration_sec||0)}</td></tr>`).join('')}</table></div><p class="an-pct" style="margin:.6em 0 0">Games GP and Game W-L are game appearances from completed regular-season game rows. The Standings table above preserves the official Match W-L and Game W-L separately.</p></div></div>`;}
function finalBoard(){
const places=['Champion','Runner-up','3rd place','4th place','5th place','6th place','7th place','8th place'];
return `<div class="pin" style="grid-column:1/-1"><div class="body"><div class="phasebar"><div><div class="kicker">Playoffs · decided at finals</div><h3 style="margin:.25em 0">Final positions</h3></div></div><div class="lscroll"><table style="min-width:420px"><tr><th>Pos</th><th>Place</th><th>Team</th></tr>${places.map((p,i)=>`<tr><td>#${i+1}</td><td>${p}</td><td>TBD</td></tr>`).join('')}</table></div></div></div>`;}
function bracketHTML(){
const ms=((DATA.playoffs||{}).matches||[]);
if(!ms.length)return '';
const byRound={};ms.forEach(m=>{byRound[m.round]=m;});
return `<div class="pin" style="grid-column:1/-1"><div class="body"><div class="phasebar"><div><div class="kicker">Playoffs</div><h3 style="margin:.25em 0">Bracket preview</h3></div></div>${bracketGrid(byRound)}</div></div>`;}
const teamRow=(n,logo,sc,w)=>`<div class="brk-team${w?' w':''}"${n?` data-brkt="${esc(n)}"`:''}>${logo?`<img src="${esc(logo)}" alt="" loading="lazy" onerror="this.remove()">`:''}<span>${esc(n||'TBD')}</span><b>${esc(sc??'')}</b></div>`;
const ORD=['1st','2nd','3rd','4th','5th','6th'];
/* Strict 2-3-2-1 bracket: QF seeds 3v6/4v5, SF seeds 1/2 await QF winners,
   lower slots stay TBD until results decide them. Seeds are pending (season
   still live) — never presented as locked teams. */
const BRK_COLS=[
 {h:'Quarterfinals',top:[
  {rk:'Round 1 Match 1',label:'Upper Bracket QF · Match 1',seeds:[3,6]},
  {rk:'Round 1 Match 2',label:'Upper Bracket QF · Match 2',seeds:[4,5]}]},
 {h:'Semifinals',top:[
  {rk:'Round 2 Match 1',label:'Upper Bracket SF · Match 1',seeds:[1,null]},
  {rk:'Round 2 Match 2',label:'Upper Bracket SF · Match 2',seeds:[2,null]}],
  bottom:[{rk:'Lower Bracket Semi Finals',label:'Lower Bracket SF',seeds:[null,null]}]},
 {h:'Finals',top:[{rk:'Upper Bracket Finals',label:'Upper Bracket Final',seeds:[null,null]}],
  bottom:[{rk:'Lower Bracket Finals',label:'Lower Bracket Final',seeds:[null,null]}]},
 {h:'Grand Final',mid:[{rk:'Grand Finals',label:'Grand Final',seeds:[null,null]}]}];
const seedTooltip=n=>`<div class="brk-team seed" data-seed="${n}" tabindex="0"><span>TBD <span class="sn-sub">(${n})</span></span><span class="seedtip" role="tooltip"><span class="sdisc">${n}</span><span class="stext"><b>${ORD[n-1]} position</b><i>Regular season</i></span></span></div>`;
const tbdRow=()=>`<div class="brk-team tbd"><span>TBD</span></div>`;
const rowFor=(m,ab,seed)=>{const t=m?(ab==='a'?m.team_a:m.team_b):null;
if(t&&t!=='TBD')return teamRow(t,m?(ab==='a'?m.team_a_logo:m.team_b_logo):null,m?(ab==='a'?m.score_a:m.score_b):null,m?(ab==='a'?m.winner==='team_a':m.winner==='team_b'):false);
if(seed)return seedTooltip(seed);return tbdRow();};
const matchCard=(slot,m)=>{const inner=!m?`<div class="brk-match brk-tbd"><span>TBD</span></div>`:`<div class="brk-match"><div class="brk-round">${esc(slot.label)}</div>${rowFor(m,'a',slot.seeds[0])}${rowFor(m,'b',slot.seeds[1])}<div class="brk-date">${esc(m.date||'')}</div></div>`;
return inner.replace('brk-match','brk-match" data-brk="'+esc(slot.rk));};
const colHTML=(c,byRound)=>`<div class="brk-col${c.bottom?' split':(c.mid?' center':'')}"><div class="brk-title">${c.h}</div>${(c.top||c.mid||[]).map(s=>matchCard(s,byRound[s.rk])).join('')}${c.bottom?'<div class="brk-gap"></div>'+c.bottom.map(s=>matchCard(s,byRound[s.rk])).join(''):''}</div>`;
function bracketGrid(byRound){return `<div class="brk">${BRK_COLS.map(c=>colHTML(c,byRound)).join('')}</div>`;}
/* STATE A — default winning/advancement routes only. Drop/loss relationships
   (drop=1) stay in the data for hover use but are never drawn by default. */
const BRK_FEEDS=[['Round 1 Match 1','Round 2 Match 1',0],['Round 1 Match 2','Round 2 Match 2',0],['Round 2 Match 1','Upper Bracket Finals',0],['Round 2 Match 2','Upper Bracket Finals',0],['Round 2 Match 1','Lower Bracket Semi Finals',1],['Round 2 Match 2','Lower Bracket Semi Finals',1],['Upper Bracket Finals','Grand Finals',0],['Upper Bracket Finals','Lower Bracket Finals',1],['Lower Bracket Semi Finals','Lower Bracket Finals',0],['Lower Bracket Finals','Grand Finals',0]];
/* Grand Final slot routing: Upper winner → TOP row, Lower winner → BOTTOM row. */
const BRK_GF_SLOT={'Upper Bracket Finals':0,'Lower Bracket Finals':1};
/* Rounded orthogonal polyline: straight H/V segments, quadratic rounding at
   every direction change. Collinear points pass through untouched. */
function brkRound(pts,r){r=r==null?8:r;
let d=`M${pts[0][0]},${pts[0][1]}`;
for(let i=1;i<pts.length-1;i++){
const [x0,y0]=pts[i-1],[x1,y1]=pts[i],[x2,y2]=pts[i+1];
const dx1=x1-x0,dy1=y1-y0,dx2=x2-x1,dy2=y2-y1;
const l1=Math.hypot(dx1,dy1),l2=Math.hypot(dx2,dy2);
const rr=Math.max(0,Math.min(r,l1/2,l2/2));
if(rr<=0||(dx1*dy2===dy1*dx2&&(dx1*dx2+dy1*dy2)>0)){d+=` L${x1},${y1}`;continue;}
const ax=x1-dx1/l1*rr,ay=y1-dy1/l1*rr,bx=x1+dx2/l2*rr,by=y1+dy2/l2*rr;
d+=` L${ax},${ay} Q${x1},${y1} ${bx},${by}`;}
const last=pts[pts.length-1];
return d+` L${last[0]},${last[1]}`;}
/* Shared drop-route geometry: exits the source card's bottom-center edge,
   travels down, routes LEFT into the destination's middle-left edge. Built
   once — hover only ever reveals these paths, never rebuilds them. */
function brkDropD(A,T){const y0=A.bottom+12,lane=T.left-16;
return brkRound([[A.cx,A.bottom],[A.cx,y0],[lane,y0],[lane,T.cy],[T.left,T.cy]],10);}
/* Final elimination route: straight down from the card's bottom-center,
   vertically aligned with its origin. Fixed travel (never shortened to the
   container — the wrapper clips the excess); the fade is calibrated so
   opacity reaches 0% exactly at the wrapper's bottom boundary. */
function brkElimLeft(C){const run=260,y2=C.bottom+run;
return {d:`M${C.cx},${C.bottom} L${C.cx},${y2}`,
x1:C.cx,y1:C.bottom,x2:C.cx,y2:y2};}
function svgOverlay(el){el.querySelectorAll('svg.brk-lines').forEach(s=>s.remove());
const q=rk=>el.querySelector('[data-brk="'+rk+'"]');
const ST='rgba(255,255,255,.22)';
const full=rk=>{const c=q(rk);return c?brkRect(el,c):null;};
const rowY=(rk,slot)=>{const c=q(rk);if(!c||slot==null)return null;
const rows=c.querySelectorAll('.brk-team');if(!rows.length||slot>=rows.length)return null;
const g=brkRect(el,rows[slot]);return g.cy;};
let wins='';
BRK_FEEDS.forEach(([a,b,drop])=>{if(drop)return;
const A=full(a);if(!A)return;
const st=ST,w=2;
let x2,y2;
if(b==='Grand Finals'){const T=full(b);if(!T)return;const y=rowY(b,BRK_GF_SLOT[a]);if(y==null)return;x2=T.left;y2=y;}
else{const T=full(b);if(!T)return;x2=T.left;y2=T.cy;}
let d;
if(A.right>x2-4){const lane=A.right+14;
d=brkRound([[A.right,A.cy],[lane,A.cy],[lane,y2],[x2,y2]],8);}
else{const mx=(A.right+x2)/2;
d=brkRound([[A.right,A.cy],[mx,A.cy],[mx,y2],[x2,y2]],8);}
wins+=`<path d="${d}" fill="none" stroke="${st}" stroke-width="${w}" data-a="${esc(a)}" data-b="${esc(b)}"/>`;});
/* Dormant contextual paths: full drop/elim geometry exists in the DOM from
   the start, invisible, waiting to be revealed by hover. */
let ctx='',defs='';
BRK_FEEDS.forEach(([a,b,drop])=>{if(!drop)return;
const A=full(a),T=full(b);if(!A||!T)return;
ctx+=`<path d="${brkDropD(A,T)}" fill="none" stroke="${BRK_LOSS_INK}" stroke-width="2.5" pathLength="1" class="drop" data-from="${esc(a)}" data-to="${esc(b)}"/>`;});
const rounds={};BRK_FEEDS.forEach(([a,b])=>{rounds[a]=1;rounds[b]=1;});
Object.keys(rounds).forEach(rk=>{if(rk==='Grand Finals'||BRK_LOSS[rk])return;
const C=full(rk);if(!C)return;const e=brkElimLeft(C);
const yEdge=Math.max(el.scrollHeight,C.bottom+4);
e.x2=e.x1;e.y2=yEdge;
const id='brkfade'+rk.replace(/\s+/g,'');
defs+=`<linearGradient id="${id}" gradientUnits="userSpaceOnUse" x1="${e.x1}" y1="${e.y1}" x2="${e.x2}" y2="${e.y2}"><stop offset="0" stop-color="#fff" stop-opacity=".9"/><stop offset=".55" stop-color="#fff" stop-opacity=".3"/><stop offset="1" stop-color="#fff" stop-opacity="0"/></linearGradient><mask id="${id}m" maskUnits="userSpaceOnUse" x="0" y="0" width="${el.scrollWidth}" height="${el.scrollHeight}"><rect x="0" y="0" width="${el.scrollWidth}" height="${el.scrollHeight}" fill="url(#${id})"/></mask>`;
ctx+=`<path d="${e.d}" fill="none" stroke="${BRK_LOSS_INK}" stroke-width="2.5" pathLength="1" class="drop" data-from="${esc(rk)}" data-elim="1" mask="url(#${id}m)"/>`;});
if(!wins&&!ctx)return;
const svg=document.createElementNS('http://www.w3.org/2000/svg','svg');
svg.setAttribute('class','brk-lines');svg.setAttribute('width',el.scrollWidth);svg.setAttribute('height',el.scrollHeight);
svg.innerHTML=(defs?`<defs>${defs}</defs>`:'')+wins+ctx;el.appendChild(svg);}
/* STATE B entry points (thin wrappers; all positions share showContextPaths). */
/* Rounds with a loss destination (used at overlay build to place elims). */
const BRK_LOSS={'Round 1 Match 1':null,'Round 1 Match 2':null,'Round 2 Match 1':'Lower Bracket Semi Finals','Round 2 Match 2':'Lower Bracket Semi Finals','Upper Bracket Finals':'Lower Bracket Finals','Lower Bracket Semi Finals':null,'Lower Bracket Finals':null,'Grand Finals':null};
/* Viewport-anchored geometry: rects are viewport-relative so page scroll
   cancels out; the container's own scroll offset maps into content space. */
function brkRect(brk,node){const b=brk.getBoundingClientRect(),r=node.getBoundingClientRect();
const x=r.left-b.left+brk.scrollLeft,y=r.top-b.top+brk.scrollTop;
return {left:x,top:y,right:x+r.width,cy:y+r.height/2,cx:x+r.width/2,bottom:y+r.height};}
/* Parent hover state: one explicit store instead of scattered DOM flags. */
const BrkHover={activeTeamId:null,activeSeedId:null,el:null,row:null,round:null};
function setBrkHover(el,row){BrkHover.el=el;BrkHover.row=row;
BrkHover.activeTeamId=row&&row.dataset.brkt?row.dataset.brkt:null;
BrkHover.activeSeedId=row&&row.dataset.seed?row.dataset.seed:null;}
function clearBrkHover(){BrkHover.activeTeamId=null;BrkHover.activeSeedId=null;BrkHover.el=null;BrkHover.row=null;BrkHover.round=null;}
/* Hover path geometry (strict): every highlighted path starts/ends exactly
   at a CARD edge, so no glowing segment ever hides under the hovered card.
   WIN leaves the card's middle-right edge horizontally; LOSS leaves the
   card's bottom-center edge, travels down, then routes LEFT into the
   destination's middle-left edge. */
const BRK_LOSS_INK='#c9c9d4';
/* Phased reveal: PREVIOUS (incoming wins yellow + arrivals grey), brief
   pause, WIN (outgoing yellow), then LOSS (own drops/elims grey). Operates
   on pre-existing overlay paths; timers cancel on early pointer-leave. */
function playBrk(brk,ph1,ph2,ph3){
if(brk._brkT)brk._brkT.forEach(clearTimeout);
brk._brkT=[];
const reduced=window.matchMedia&&window.matchMedia('(prefers-reduced-motion: reduce)').matches;
const fire=els=>els.forEach(p=>{
if(p.classList.contains('drop'))p.classList.add('go');
else{p.classList.remove('faded');p.classList.add('lit-win');}});
if(reduced){[ph1,ph2,ph3].forEach(fire);return;}
brk._brkT.push(setTimeout(()=>fire(ph1),150));
brk._brkT.push(setTimeout(()=>fire(ph2),500));
brk._brkT.push(setTimeout(()=>fire(ph3),800));}
/* STATE B — reveal, never generate. Every contextual path already exists in
   the overlay (wins visible, drops/elims dormant); hover only changes
   visual state: fade touching wins, then light the attached relationships
   in sequence. Works for seed, team, and plain TBD rows alike. */
function showContextPaths(brk,row){
const card=row.closest('[data-brk]');if(!card)return;
const round=card.dataset.brk;
if(BrkHover.round===round&&BrkHover.el===brk&&BrkHover.row){BrkHover.row=row;
BrkHover.activeTeamId=row.dataset.brkt||null;BrkHover.activeSeedId=row.dataset.seed||null;return;}
clearTeamPaths(brk);setBrkHover(brk,row);BrkHover.round=round;
const L=brk.querySelector('svg.brk-lines');if(!L)return;
const prevWin=[...L.querySelectorAll(`path[data-b="${round}"]`)];
const ownWin=[...L.querySelectorAll(`path[data-a="${round}"]`)];
const arr=[...L.querySelectorAll(`path.drop[data-to="${round}"]`)];
const lost=[...L.querySelectorAll(`path.drop[data-from="${round}"]`)];
[...prevWin,...ownWin].forEach(p=>p.classList.add('faded'));
playBrk(brk,[...prevWin,...arr],ownWin,lost);}
function showTeamPaths(brk,row){showContextPaths(brk,row);}
function showSeedPaths(brk,row){showContextPaths(brk,row);}
/* HOVER → DEFAULT: cancel pending phases, strip contextual classes; the
   overlay's own transitions fade everything back smoothly. */
function clearTeamPaths(scope){const roots=scope&&scope.classList&&scope.classList.contains('brk')?[scope]:[...(scope||document).querySelectorAll('.brk')];
roots.forEach(b=>{if(b._brkT){b._brkT.forEach(clearTimeout);b._brkT=null;}
b.querySelectorAll('svg.brk-lines path.faded,svg.brk-lines path.lit-win,svg.brk-lines path.drop.go').forEach(p=>p.classList.remove('faded','lit-win','go'));});}
document.addEventListener('pointerover',e=>{
const brk=e.target.closest?e.target.closest('.brk'):null;if(!brk)return;
const row=e.target.closest?e.target.closest('.brk-team'):null;
if(!row)return;
if(BrkHover.row===row&&BrkHover.el===brk)return;
setBrkHover(brk,row);showContextPaths(brk,row);});
document.addEventListener('pointerout',e=>{if(e.pointerType&&e.pointerType!=='mouse')return;
const brk=e.target.closest?e.target.closest('.brk'):null;if(!brk)return;
const to=e.relatedTarget&&e.relatedTarget.closest?e.relatedTarget.closest('.brk-team'):null;
if(!to||to!==BrkHover.row){clearBrkHover();clearTeamPaths(brk);}});
document.addEventListener('pointerdown',e=>{if(e.target.closest&&e.target.closest('.brk-team'))return;
clearBrkHover();clearTeamPaths(document);});
let brkResizeWired=false;
function wireBracket(){document.querySelectorAll('.brk').forEach(svgOverlay);
clearBrkHover();
const board=document.getElementById('board');
if(board&&window.ResizeObserver&&!wireBracket._ro){wireBracket._ro=new ResizeObserver(()=>{wireBracket();});wireBracket._ro.observe(board);}
if(!brkResizeWired){brkResizeWired=true;let t=null;
window.addEventListener('resize',()=>{clearTimeout(t);t=setTimeout(()=>wireBracket(),150);});}}
function gameMvp(pa,pb,wcode){const pl=[...(pa||[]),...(pb||[])];const pool=wcode?pl.filter(r=>r.team===wcode):pl;const cands=pool.length?pool:pl;let best=null,bk=null;
cands.forEach(r=>{const k=r.kda??(((r.kills??r.kill??0)+(r.assists??r.assist??0))/Math.max(1,(r.deaths??r.death??0)));const key=[k,(r.kills??r.kill??0),(r.gold??0)];
if(!best||key[0]>bk[0]||(key[0]===bk[0]&&(key[1]>bk[1]||(key[1]===bk[1]&&key[2]>bk[2])))){best=r;bk=key;}});return best;}
function gameSection(g,plistA,plistB,bansA,bansB,live,active){
const sec=durSec(g.duration_str||g.duration);const dur=g.duration_str||g.duration||'';
const wn=winName(g);const gm=gameMvp(plistA,plistB,wn);
const wonA=wn?wn===g.team_a:null,wonB=wn?wn===g.team_b:null;
const bans=(bansA.length||bansB.length)?`<div class="sb-bans"><span>BAN ${esc(g.team_a)}: ${bansA.map(esc).join(', ')||'–'}</span><span>BAN ${esc(g.team_b)}: ${bansB.map(esc).join(', ')||'–'}</span></div>`:'';
return `<div class="sb-game" data-g="${esc(String(g.game_no))}"${active?'':' hidden'}>`
+`<div class="sb-ghead"><h4>Game ${esc(String(g.game_no))}</h4><span>${esc(g.team_a)} ${esc(g.team_a_kills)} : ${esc(g.team_b_kills)} ${esc(g.team_b)} · ${esc(dur)}${g.map_mode?` · ${esc(g.map_mode)}`:''}${g.vod_url?` · <a href="${esc(g.vod_url)}" target="_blank" rel="noopener noreferrer">VOD</a>`:''}${wn?` · <b class="sb-win">${esc(wn)} won</b>`:''}${gm?` · <span class="gmvp">MVP ${esc(gm.player)}</span>`:''}</span></div>`
+bans+`<div class="sb-duo">`+teamBlock(g.team_a,g.team_a_kills,plistA,sec,g.team_a_side,'',wonA)+teamBlock(g.team_b,g.team_b_kills,plistB,sec,g.team_b_side,'flip',wonB)+`</div></div>`;}
function wireTabs(){const db=document.getElementById('db');
db.querySelectorAll('[data-gtab]').forEach(b=>b.onclick=()=>selGame(b.dataset.gtab));}
function selGame(gno){const db=document.getElementById('db');if(!db||gno==null||gno==='')return;
db.querySelectorAll('[data-gtab]').forEach(x=>x.setAttribute('aria-pressed',x.dataset.gtab===String(gno)?'true':'false'));
db.querySelectorAll('.sb-game').forEach(s=>{s.hidden=s.dataset.g!==String(gno);});
const tab=[...db.querySelectorAll('[data-gtab]')].find(x=>x.dataset.gtab===String(gno));
const w=tab?tab.dataset.wtab:'';setMark(w&&markSrc(w)?{src:markSrc(w),side:tab.dataset.wside||'l'}:null);}
async function showM(id,opts){opts=opts||{};const wantGame=opts.game!=null?String(opts.game):null;
const m=DATA.schedule.find(x=>String(x.match_detail_id)===String(id))||{};
const gs=DATA.games.filter(g=>g.match_detail_id===id);
const isActive=(g,i)=>wantGame!=null?String(g.game_no)===wantGame:i===0;
const wtab=g=>{const w=winName(g)||'';return ` data-wtab="${esc(w)}" data-wside="${w?(w===g.team_a?'l':'r'):'l'}"`;};
const tabs=gs.map((g,i)=>`<button data-gtab="${esc(String(g.game_no))}"${wtab(g)} aria-pressed="${isActive(g,i)?'true':'false'}">Game ${esc(String(g.game_no))}</button>`).join('');
const body=`<div class="sb-tabs" role="group" aria-label="Games">${tabs}</div>`+gs.map((g,i)=>{
const pa=rows(id,g.game_no).filter(r=>r.team===g.team_a).sort((a,b)=>pickSlot(id,g.game_no,g.team_a,a.player)-pickSlot(id,g.game_no,g.team_a,b.player));
const pb=rows(id,g.game_no).filter(r=>r.team===g.team_b).sort((a,b)=>pickSlot(id,g.game_no,g.team_b,a.player)-pickSlot(id,g.game_no,g.team_b,b.player));
return gameSection(g,pa,pb,bansFor(id,g.game_no,'A'),bansFor(id,g.game_no,'B'),false,isActive(g,i));}).join('');
const initG=wantGame!=null?(gs.find(g=>String(g.game_no)===wantGame)||{}):(gs[0]||{});
const initW=winName(initG)||'';
dSet(m.team_a+' vs '+m.team_b,'#'+id+' · '+(m.date||''),body,
initW&&markSrc(initW)?{src:markSrc(initW),side:initW===m.team_a?'l':(initW===m.team_b?'r':'l')}:null);
// Completed series already carry picks, lanes and map mode from the ETL;
// refetching would replace them with the API's lane-less rows.
if(gs.length&&gs.every(g=>g.winner==='team_a'||g.winner==='team_b'))return;
try{
const ctl=new AbortController();const tmr=setTimeout(()=>ctl.abort(),15000);
const r=await fetch(HUB+'/match/'+encodeURIComponent(id),{signal:ctl.signal});
clearTimeout(tmr);
if(!r.ok)return;const d=await r.json();if(!d.games||!d.games.length)return;
const firstGame=wantGame!=null?wantGame:String(d.games[0].game);
const t2=d.games.map((g,i)=>`<button data-gtab="${esc(String(g.game))}" data-wtab="${esc(winName(g)||'')}" data-wside="${(winName(g)||'')===g.team_a?'l':'r'}" aria-pressed="${String(g.game)===String(firstGame)?'true':'false'}">Game ${esc(String(g.game))}</button>`).join('');
const live=`<div class="sb-tabs" role="group" aria-label="Games">${t2}</div>`+d.games.map((g,i)=>{
const gg={game_no:g.game,team_a:g.team_a,team_b:g.team_b,team_a_kills:g.team_a_kills,team_b_kills:g.team_b_kills,winner:g.winner,duration:g.duration,team_a_side:g.team_a_side,team_b_side:g.team_b_side};
const pa=(g.players||[]).filter(p=>p.team===g.team_a),pb=(g.players||[]).filter(p=>p.team===g.team_b);
return gameSection(gg,pa,pb,g.bans_a||[],g.bans_b||[],true,String(g.game)===String(firstGame));}).join('');
document.getElementById('db').innerHTML=live;
if(dnav.length)dnav[dnav.length-1].h=live;
wireTabs();
}catch(e){}}
let dnav=[];
function markSrc(t){return TICON(t)||logoOf(t)||'';}
function setMark(mark){const el=document.getElementById('dmark');if(!el)return;
if(mark&&mark.src){if(el.getAttribute('src')!==mark.src)el.setAttribute('src',mark.src);el.className='dmark '+mark.side;el.hidden=false;}
else{el.hidden=true;el.removeAttribute('src');}}
function dShow(){const top=dnav[dnav.length-1];if(!top)return;
document.getElementById('dt').textContent=top.t;
document.getElementById('ds').textContent=top.s||'';
document.getElementById('db').innerHTML=top.h;
document.getElementById('dback').hidden=dnav.length<2;
setMark(top.mark||null);
wireTabs();}
function dSet(t,s,h,mark){if(!dlg.open){dnav=[];lastFocus=document.activeElement;}
dnav.push({t:t,s:s,h:h,mark:mark||null});dShow();if(!dlg.open)dlg.showModal();}
function dBack(){if(dnav.length>1){dnav.pop();dShow();}}
function openD(t,s,h){dSet(t,s,h);}
document.getElementById('dback').onclick=()=>dBack();
document.addEventListener('keydown',e=>{if(e.key==='Escape'){const d2=document.getElementById('dlg2');if(d2&&d2.open)d2.close();else if(dlg.open)dlg.close();}});
document.addEventListener('keydown',e=>{if(e.key!=='Tab')return;const d=[dlg,document.getElementById('dlg2')].find(x=>x&&x.open);if(!d)return;
const f=[...d.querySelectorAll('button,input,select,[tabindex]')].filter(el=>!el.disabled&&el.offsetParent!==null);if(!f.length)return;
const first=f[0],last=f[f.length-1];
if(e.shiftKey&&document.activeElement===first){e.preventDefault();last.focus();}
else if(!e.shiftKey&&document.activeElement===last){e.preventDefault();first.focus();}});
document.getElementById('dlg2').addEventListener('close',()=>{if(lastFocus)lastFocus.focus();});
function palRows(q){
  const s=String(q||'').toLowerCase().trim();
  if(!s)return [];
  const seen={},res=[];
  const add=(t,label,sub,id)=>{const k=t+'|'+label;if(seen[k])return;seen[k]=1;res.push({t:t,label:label,sub:sub,id:id||''});};
  DATA.players.forEach(r=>{const c=canonicalPlayer(r.player);if(c.toLowerCase().includes(s))add('player',c,(r.team||'')+' · '+(r.lane||'—'));});
  TEAMS.forEach(t=>{if(t.toLowerCase().includes(s))add('team',t,'Team');});
  (DATA.heroes||[]).forEach(h=>{if(String(h.hero).toLowerCase().includes(s))add('hero',h.hero,(h.pick||0)+' picks · '+(h.ban||0)+' bans');});
  DATA.schedule.forEach(m=>{if((m.team_a+' '+m.team_b+' '+m.iso_date).toLowerCase().includes(s))add('match',m.team_a+' vs '+m.team_b,(m.iso_date||'')+' · '+(m.score_a??'-')+':'+(m.score_b??'-'),m.match_detail_id);});
  return res.slice(0,14);
}
function palList(q){
  const rows=palRows(q);
  return rows.map(r=>`<button type="button" class="palrow" data-pal="${r.t}" data-id="${esc(r.id)}" data-q="${esc(r.label)}"><b>${esc(r.label)}</b><span>${esc(r.sub)}</span></button>`).join('')||`<div class="an-pct" style="padding:8px 0">${q?'No matches.':'Type to search players, teams, heroes or matches.'}</div>`;
}
function openPalette(){
  openD('Search','Players · teams · heroes · matches',`<input id="paletteQ" type="search" placeholder="Search everything…" aria-label="Search everything" style="width:100%;background:var(--bg2);color:var(--ink);border:1px solid var(--line);border-radius:6px;padding:10px"><div id="paletteList" style="margin-top:10px">${palList('')}</div>`);
  const q=document.getElementById('paletteQ'),list=document.getElementById('paletteList');
  if(q){q.focus();q.oninput=()=>{list.innerHTML=palList(q.value);};}
  if(list)list.onclick=e=>{const b=e.target.closest('[data-pal]');if(!b)return;const t=b.dataset.pal,id=b.dataset.id,label=b.dataset.q;dlg.close();if(t==='player'){S.view='players';S.q=label.toLowerCase();render();}else if(t==='team'){S.view='matches';S.team=label;render();}else if(t==='hero'){stHeroDrill(label);}else if(t==='match'&&id){showM(id);}};
}
document.addEventListener('keydown',e=>{if((e.ctrlKey||e.metaKey)&&String(e.key).toLowerCase()==='k'){e.preventDefault();openPalette();}});
const palBtn=document.getElementById('paletteBtn');if(palBtn)palBtn.onclick=openPalette;
const HUB=SEASON.endpoints.hub;
function normLive(d){const games=[],pros=[],bans=[];
const num=v=>{const n=+v;return isFinite(n)?n:0;};
(d.games||[]).forEach(g=>{const sec=durSec(g.duration);
games.push({match_detail_id:String(d.match_id),game_no:g.game,team_a:g.team_a,team_b:g.team_b,team_a_kills:num(g.team_a_kills),team_b_kills:num(g.team_b_kills),winner:g.winner,duration_str:g.duration,duration_sec:sec,team_a_side:g.team_a_side,team_b_side:g.team_b_side,vod_url:g.vod_url});
(g.bans_a||[]).forEach(h=>{if(h)bans.push({match_detail_id:String(d.match_id),game_no:g.game,side:'A',hero:h});});
(g.bans_b||[]).forEach(h=>{if(h)bans.push({match_detail_id:String(d.match_id),game_no:g.game,side:'B',hero:h});});
(g.players||[]).forEach(p=>{const eq=u=>itemRef(u);
pros.push({match_detail_id:String(d.match_id),game_no:g.game,team:p.team,player:p.player,lane:p.lane||null,hero:p.hero,hero_image:p.hero_image||null,
kills:num(p.kill??p.kills),deaths:num(p.death??p.deaths),assists:num(p.assist??p.assists),kda:(+p.kda)||0,gold:num(p.gold),
gold_per_min:(sec&&p.gold!=null)?Math.round(num(p.gold)/(sec/60)):0,
hero_damage:num(p.hero_damage),damage_taken:num(p.damage_taken),tower_damage:num(p.tower_damage),
e:((/emblem\/(\d+)\.png/.exec(p.emblem||''))||[])[1]||null,
t:(p.talents||[]).map(u=>((/rune\/(\d+)\.png/.exec(u||''))||[])[1]).filter(Boolean),
i:(p.items||[]).map(eq).filter(Boolean)});});});
return {games,pros,bans};}
function buildPool(pros){const m={};pros.forEach(r=>{(m[r.player]=m[r.player]||[]).push(r.hero);});
const o={};Object.entries(m).forEach(([p,hs])=>{const c={};hs.forEach(h=>{c[h]=(c[h]||0)+1;});o[p]=Object.entries(c).sort((a,b)=>b[1]-a[1]).slice(0,6);});return o;}
/* SNAPSHOT-START */
/* Pure derivation of every analytics input from one raw snapshot. The embedded
   CSV aggregates are generated by tools/aggregate_teams.py; after a live
   refresh these helpers rebuild the same contracts from the refreshed raw
   rows so Analytics, Prep, Team profiles and standings cannot mix versions. */
const SNAP_LANES={EXP:1,JUNGLE:2,MID:3,GOLD:4,ROAM:5};
function snapKey(mid,gn,team){return String(mid)+':'+String(gn)+':'+String(team);}
function preserveFields(rows,oldRows,keyFn,fields){
  const old={};(oldRows||[]).forEach(r=>{if(r)old[keyFn(r)]=r;});
  return (rows||[]).map(r=>{const o=old[keyFn(r)];if(!o)return r;const out=Object.assign({},r);
    (fields||[]).forEach(f=>{if((out[f]===undefined||out[f]===null||out[f]==='')&&o[f]!==undefined&&o[f]!==null)out[f]=o[f];});
    return out;});
}
function derivePicks(pros,games,oldPicks){
  const gameBy={};(games||[]).forEach(g=>{gameBy[snapKey(g.match_detail_id,g.game_no)]=g;});
  const oldBy={};(oldPicks||[]).forEach(p=>{oldBy[snapKey(p.match_detail_id,p.game_no,p.team)+':'+String(p.player)+':'+String(p.hero)]=p;});
  const out=[],seen={};
  (pros||[]).forEach(p=>{
    const g=gameBy[snapKey(p.match_detail_id,p.game_no)]||{};
    const old=oldBy[snapKey(p.match_detail_id,p.game_no,p.team)+':'+String(p.player)+':'+String(p.hero)]||{};
    const side=p.team===g.team_a?g.team_a_side:(p.team===g.team_b?g.team_b_side:'');
    const lane=p.lane||old.lane||'';
    const slot=+old.slot||SNAP_LANES[lane]||0;
    const row={match_detail_id:String(p.match_detail_id),game_no:+p.game_no,team:p.team,side:String(side||'').toLowerCase(),
      slot:slot,lane:lane,hero:p.hero,player:p.player};
    const k=snapKey(row.match_detail_id,row.game_no,row.team)+':'+String(row.player)+':'+String(row.hero);
    if(!seen[k]){seen[k]=1;out.push(row);}
  });
  return out;
}
function deriveTeamGames(pros,games,fallback){
  const gameBy={};(games||[]).forEach(g=>{gameBy[snapKey(g.match_detail_id,g.game_no)]=g;});
  const groups={};
  (pros||[]).forEach(p=>{
    const k=snapKey(p.match_detail_id,p.game_no,p.team),x=groups[k]=groups[k]||{match_detail_id:String(p.match_detail_id),game_no:+p.game_no,team:p.team,players:0,kills:0,deaths:0,assists:0,gold:0,hero_damage:0,damage_taken:0,tower_damage:0};
    x.players++;['kills','deaths','assists','gold','hero_damage','damage_taken','tower_damage'].forEach(f=>{x[f]+=(+p[f]||0);});
  });
  const oldBy={};(fallback||[]).forEach(t=>{oldBy[snapKey(t.match_detail_id,t.game_no,t.team)]=t;});
  const out=Object.keys(groups).map(k=>{
    const x=groups[k],g=gameBy[snapKey(x.match_detail_id,x.game_no)]||{};
    const opponent=x.team===g.team_a?g.team_b:(x.team===g.team_b?g.team_a:'');
    const win=(g.winner==='team_a'&&x.team===g.team_a)||(g.winner==='team_b'&&x.team===g.team_b)?1:0;
    return {...x,opponent:opponent,kda:(x.kills+x.assists)/Math.max(1,x.deaths),win:win,
      map_mode:g.map_mode||'',duration_sec:+g.duration_sec||0};
  });
  Object.keys(oldBy).forEach(k=>{if(!groups[k])out.push(oldBy[k]);});
  return out;
}
function deriveTeamSeason(teamGames,baseSeason,standings){
  const base={};(baseSeason||[]).forEach(t=>{base[t.team]=t;});
  const official={};((standings)||[]).forEach(s=>{official[String(s.team_slug||s.team_name||'').toUpperCase()]=s;});
  const groups={};(teamGames||[]).forEach(r=>{
    const x=groups[r.team]=groups[r.team]||{team:r.team,games:0,wins:0,losses:0,kills:0,deaths:0,assists:0,gold:0,hero_damage:0,damage_taken:0,tower_damage:0,total_sec:0};
    x.games++;if(r.win===1)x.wins++;else x.losses++;
    ['kills','deaths','assists','gold','hero_damage','damage_taken','tower_damage'].forEach(f=>{x[f]+=(+r[f]||0);});
    x.total_sec+=(+r.duration_sec||0);
  });
  return Object.keys(groups).map(k=>{const x=groups[k],b=base[k]||{},o=official[String(b.team_slug||k).toUpperCase()]||{};
    return {team:k,games:x.games,wins:x.wins,losses:x.losses,kills:x.kills,deaths:x.deaths,assists:x.assists,gold:x.gold,
      hero_damage:x.hero_damage,damage_taken:x.damage_taken,tower_damage:x.tower_damage,
      kda:Math.round(((x.kills+x.assists)/Math.max(1,x.deaths))*1000)/1000,
      win_rate:Math.round((x.wins/Math.max(1,x.games))*10000)/10000,
      avg_gold:Math.round((x.gold/Math.max(1,x.games))*10)/10,
      avg_duration_sec:Math.round((x.total_sec/Math.max(1,x.games))*10)/10,
      team_name:o.team_name||b.team_name||k,team_slug:o.team_slug||b.team_slug||String(k).toLowerCase()};
  });
}
function deriveAnalyticsSnapshot(data){
  const picks=derivePicks(data.players,data.games,data.picks);
  const team_games=deriveTeamGames(data.players,data.games,data.team_games);
  const team_season=deriveTeamSeason(team_games,data.team_season,data.standings);
  return {picks:picks,team_games:team_games,team_season:team_season};
}
/* SNAPSHOT-END */
/* REFRESH-START */
/* Pure live-refresh merge/validation helpers (tested, no DOM access).
   Composite keys mirror the ETL primary keys: games (match, game),
   player rows (match, game, team, player, hero), bans (match, game, side,
   hero). mergeRefresh() replaces old rows ONLY for successfully refreshed
   match IDs and keeps previous records for failed IDs; both sides dedupe,
   so repeated refreshes never duplicate rows. validSnapshot() gates what
   may become shared state or cache. refreshStatus() phrases complete vs
   partial outcomes for the existing status element. */
function keyGame(g){return g.match_detail_id+':'+g.game_no;}
function keyPro(p){return p.match_detail_id+':'+p.game_no+':'+p.team+':'+p.player+':'+p.hero;}
function keyBan(b){return b.match_detail_id+':'+b.game_no+':'+b.side+':'+b.hero;}
function mergeRefresh(oldArr,freshById,pick,keyFn){
var out=[],seen={};
function good(f){return f&&f.ok&&Array.isArray(f[pick]);}
Object.keys(freshById).forEach(function(id){var f=freshById[id];if(!good(f))return;
f[pick].forEach(function(r){var k=keyFn(r);if(!seen[k]){seen[k]=1;out.push(r);}});});
(oldArr||[]).forEach(function(r){var id=r&&r.match_detail_id;
if(good(freshById[id]))return;
var k=keyFn(r);if(!seen[k]){seen[k]=1;out.push(r);}});
return out;
}
function validSnapshot(s){
var errors=[];
if(!s||!Array.isArray(s.schedule)||!s.schedule.length)errors.push('schedule');
if(!s||!Array.isArray(s.standings)||!s.standings.length)errors.push('standings');
if(!s||!Array.isArray(s.season))errors.push('season');
if(s&&s.standings&&!s.standings.every(function(r){return r&&(r.team_slug||r.team_name)!=null&&(isFinite(+r.match_point)||r.match_point==null);}))errors.push('standings-shape');
return {ok:!errors.length,errors:errors};
}
function refreshStatus(o){
var t=new Date().toLocaleTimeString();
var base=' · '+o.games+' games · '+o.mvpN+' MVPs'+(o.newMsg||'');
if(o.complete)return 'updated '+t+base;
return 'partially updated '+t+base+' · '+o.fails+' failed (kept previous records)';
}
/* REFRESH-END */
/* CACHE-START */
/* Pure versioned-cache helpers (tested, no DOM access). Entries carry
   seasonId, schema version, a deterministic content fingerprint, decided
   fixture count, completeness, and refresh timestamps under a namespaced
   key `mpl-board:<seasonId>:v<schema>`. Freshness rule (documented):
   higher decided-fixture count wins; equal progress with different content
   resolves to the timestamped side, else the bundle. Completeness never
   overrides progress, but a partial snapshot in use is always labelled.
   Offline-first is preserved: a valid older cache remains usable when the
   bundle is older, and partial snapshots are never presented as fresh. */
function cacheKeyFor(seasonId,schema){return 'mpl-board:'+seasonId+':v'+schema;}
function fingerprintSnapshot(s){
// Fingerprint the complete analytics snapshot, not just standings/schedule:
// raw detail and the derived aggregates must move together for a cache to be
// considered the same version.
var str=JSON.stringify([(s.standings||[]).map(function(r){return [r.team_slug||r.team_name,r.match_point,r.match_win,r.match_lose,r.game_win,r.game_lose,r.net_game_win];}),
(s.schedule||[]).map(function(m){return [m.schedule_id||m.match_id,m.team_a,m.team_b,m.score_a,m.score_b,m.status,m.winner];}),
(s.games||[]).map(function(g){return [g.match_detail_id,g.game_no,g.team_a,g.team_b,g.winner,g.team_a_side,g.team_b_side,g.map_mode,g.duration_sec];}),
(s.players||[]).map(function(p){return [p.match_detail_id,p.game_no,p.team,p.player,p.hero,p.lane,p.kills,p.deaths,p.assists,p.gold,p.hero_damage,p.tower_damage];}),
(s.bans||[]).map(function(b){return [b.match_detail_id,b.game_no,b.side,b.hero,b.ban_order];}),
(s.picks||[]).map(function(p){return [p.match_detail_id,p.game_no,p.team,p.player,p.hero,p.side,p.lane,p.slot];}),
(s.team_games||[]).map(function(t){return [t.match_detail_id,t.game_no,t.team,t.win,t.kills,t.deaths,t.gold];}),
(s.team_season||[]).map(function(t){return [t.team,t.games,t.wins,t.losses];})]);
var h=0x811c9dc5;for(var i=0;i<str.length;i++){h^=str.charCodeAt(i);h=Math.imul(h,0x01000193)>>>0;}
return ('0000000'+h.toString(16)).slice(-8);
}
function countDecidedSet(schedule,poRowFn,isTermFn){
var n=0;(schedule||[]).forEach(function(m){
if(poRowFn(m))return;
var sa=+m.score_a,sb=+m.score_b;
if(String(m.status)==='completed'||isTermFn(sa,sb))n++;});return n;}
function makeCacheEntry(s,meta){
return {v:2,seasonId:meta.seasonId,schema:meta.schema,fp:fingerprintSnapshot(s),
decided:meta.decided!=null?meta.decided:0,complete:!!meta.complete,
failedIds:meta.failedIds||[],refreshedAt:meta.refreshedAt||null,
source:meta.source||'refresh',data:s};
}
function validateCacheEntry(e,opts){
if(!e||typeof e!=='object')return {ok:false,reason:'not-an-entry'};
if(e.seasonId!==opts.seasonId)return {ok:false,reason:'season'};
if(e.schema!==opts.schema)return {ok:false,reason:'schema'};
if(!e.data||typeof e.data!=='object')return {ok:false,reason:'shape'};
if(!Array.isArray(e.data.schedule)||!e.data.schedule.length)return {ok:false,reason:'shape'};
if(!Array.isArray(e.data.standings)||!e.data.standings.length)return {ok:false,reason:'shape'};
if(!Array.isArray(e.data.games)||!Array.isArray(e.data.players)||!Array.isArray(e.data.bans)||!Array.isArray(e.data.picks)||!Array.isArray(e.data.team_games)||!Array.isArray(e.data.team_season))return {ok:false,reason:'analytics-shape'};
if(fingerprintSnapshot(e.data)!==e.fp)return {ok:false,reason:'fingerprint'};
// Derived inputs must be reproducible from this cache's own raw rows. A
// hand-edited or half-migrated cache cannot smuggle stale aggregates into a
// newer standings/raw snapshot.
var derived=deriveAnalyticsSnapshot(e.data);
if(JSON.stringify(derived.picks)!==JSON.stringify(e.data.picks)||
   JSON.stringify(derived.team_games)!==JSON.stringify(e.data.team_games)||
   JSON.stringify(derived.team_season)!==JSON.stringify(e.data.team_season))return {ok:false,reason:'aggregates'};
return {ok:true,reason:'valid'};
}
/* emb/cache: {fp,decided[,complete,refreshedAt]} (cache null when absent or
   invalid). Never throws; exact ties resolve to 'embedded'. Selection rule:
   higher decided-fixture count wins ('newer'); equal progress with different
   content resolves to whichever side carries a refresh timestamp, else the
   bundle. Completeness never overrides progress (a newer partial snapshot
   still carries newer standings/schedule; its gaps stay explicit in
   failedIds), but a partial snapshot in use is always labelled as such. */
function selectSnapshot(emb,cache){
if(!cache)return {use:'embedded',why:'no-cache',partial:false};
if(cache.fp===emb.fp)return {use:'embedded',why:'identical',partial:false};
if(cache.decided!==emb.decided)
return cache.decided>emb.decided?{use:'cache',why:'newer',partial:!cache.complete}
:{use:'embedded',why:'newer',partial:false};
if(cache.refreshedAt&&!emb.refreshedAt)return {use:'cache',why:'tiebreak',partial:!cache.complete};
return {use:'embedded',why:'tie',partial:false};
}
/* CACHE-END */
/* MVP team-name canonicalization reuses the single season alias map and the
   same alphanumeric normalization (covered by the mapping battery in
   tools/test_config.js); unknown spellings pass through. */
const canonT=t=>normTeam(t);
function parseMvps(wt){const out=[];const blocks=wt.split(/\|M\d+=\{\{Match/);
for(let i=1;i<blocks.length;i++){const b=blocks[i];
const t1=(/opponent1=\{\{TeamOpponent\|([^\}\|\n]+)/.exec(b)||[])[1]||'';
const t2=(/opponent2=\{\{TeamOpponent\|([^\}\|\n]+)/.exec(b)||[])[1]||'';
const date=((/\|date=([^\n]+)/.exec(b)||[])[1]||'').replace('{{abbr/ICT}}','ICT').slice(0,60);
const mvp=((/\|mvp=([^\n\|]*)/.exec(b)||[])[1]||'').trim();
out.push({t1:t1.trim(),t2:t2.trim(),date:date,mvp:mvp});}
return out;}
async function fetchMvps(){const q='action=parse&page='+encodeURIComponent(SEASON.endpoints.liquipediaSeasonPage)+'&prop=wikitext&format=json&origin=*';
const timeout=new Promise((_,rej)=>setTimeout(()=>rej(new Error('mvp-timeout')),25000));
const req=fetch(SEASON.endpoints.liquipediaApi+'?'+q).then(r=>{if(!r.ok)throw new Error('liquipedia');return r.json();});
const j=await Promise.race([req,timeout]);
return parseMvps((j.parse&&j.parse.wikitext&&j.parse.wikitext['*'])||'');}
function applyMvps(list){let n=0;
const pool=[...list];
(DATA.matches||[]).forEach(m=>{const ha=canonT(m.team_a),hb=canonT(m.team_b);
const ix=pool.findIndex(l=>{const a=canonT(l.t1),b=canonT(l.t2);return (a===ha&&b===hb)||(a===hb&&b===ha);});
if(ix>-1){const found=pool.splice(ix,1)[0];if(found.mvp){m.liq_mvp=found.mvp;n++;}}});
return n;}
function setNet(){const el=document.getElementById('net');if(!el)return;const on=navigator.onLine!==false;el.textContent=on?'online':'offline';el.style.color=on?'var(--muted)':'#f2b8c1';el.style.borderColor=on?'var(--line)':'#7f2b36';}
window.addEventListener('online',()=>{setNet();render();});
window.addEventListener('offline',setNet);
setNet();
async function fetchJSON(url,ms){ms=ms||15000;let last=null;
for(let a=0;a<2;a++){try{const ctl=new AbortController();const t=setTimeout(()=>ctl.abort(),ms);
const r=await fetch(url,{signal:ctl.signal});clearTimeout(t);if(!r.ok)throw new Error('http '+r.status);return await r.json();}
catch(e){last=e;await new Promise(r=>setTimeout(r,600));}}
throw last||new Error('fetch failed');}
async function refreshDB(){const btn=document.getElementById('refresh'),upd=document.getElementById('upd');
btn.disabled=true;const old=btn.textContent;btn.textContent='…';
try{
const [ms,st,ps,mvpList,hs,po]=await Promise.all([
fetchJSON(HUB+'/matches'),
fetchJSON(HUB+'/standings'),
fetchJSON(HUB+'/stats/players'),
fetchMvps().catch(()=>[]),
fetchJSON(HUB+'/stats/heroes').catch(()=>[]),
fetchJSON(HUB+'/playoffs').catch(()=>null)]);
DATA.schedule=ms;DATA.standings=st;DATA.season=ps;
if(hs&&hs.length)DATA.heroes=hs;
if(po)DATA.playoffs=po;
const mvpMap=Object.fromEntries((DATA.matches||[]).map(m=>[String(m.match_detail_id),m.liq_mvp]));
DATA.matches=ms.filter(m=>/^\d+$/.test(String(m.match_detail_id||''))).map(m=>({match_detail_id:String(m.match_detail_id),schedule_id:m.match_id,team_a:m.team_a,team_b:m.team_b,score_a:m.score_a,score_b:m.score_b,date:m.date,iso_date:m.iso_date,iso_datetime:m.iso_datetime,status:m.status,winner:m.winner,vod_url:m.vod_url,match_detail_url:m.match_detail_url,liq_mvp:mvpMap[String(m.match_detail_id)]||''}));
const mvpN=applyMvps(mvpList||[]);
const topChk=validSnapshot({schedule:ms,standings:st,season:ps});
if(!topChk.ok)throw new Error('bad top-level response: '+topChk.errors.join(','));
const ids=[...new Set(DATA.matches.map(m=>m.match_detail_id))];
const fresh={};ids.forEach(id=>{fresh[id]={ok:false};});
let done=0;const q=[...ids];
upd.textContent='games 0/'+ids.length+'…';
await Promise.all(Array.from({length:6},()=> (async()=>{while(q.length){const id=q.pop();
try{const d=await fetch(HUB+'/match/'+encodeURIComponent(id)).then(r=>{if(!r.ok)throw new Error(id);return r.json();});
if(String(d.match_id)!==String(id))throw new Error('id-mismatch '+id);
const n=normLive(d);fresh[id]={ok:true,games:n.games,pros:n.pros,bans:n.bans};}catch(e){fresh[id]={ok:false};}
done++;upd.textContent='games '+done+'/'+ids.length+'…';}})()));
const failedIds=ids.filter(id=>!fresh[id].ok);
const oldGames=DATA.games||[],oldPlayers=DATA.players||[],oldBans=DATA.bans||[];
DATA.games=preserveFields(mergeRefresh(DATA.games,fresh,'games',keyGame),oldGames,keyGame,['map_mode']);
DATA.players=preserveFields(mergeRefresh(DATA.players,fresh,'pros',keyPro),oldPlayers,keyPro,['lane','lane_source']);
DATA.hero_pool=buildPool(DATA.players);
DATA.bans=preserveFields(mergeRefresh(DATA.bans,fresh,'bans',keyBan),oldBans,keyBan,['ban_order']);
// Rebuild every derived analytics input from the merged raw snapshot, then
// discard cached analytics so the next render cannot show pre-refresh values.
const derived=deriveAnalyticsSnapshot({players:DATA.players,games:DATA.games,bans:DATA.bans,picks:DATA.picks,team_games:DATA.team_games,team_season:DATA.team_season,standings:DATA.standings});
DATA.picks=derived.picks;DATA.team_games=derived.team_games;DATA.team_season=derived.team_season;
Object.keys(ANA).forEach(k=>delete ANA[k]);PREP=null;
const complete=!failedIds.length;
const AH2=(window.ASSETS||{}).heroes||{},AI2=(window.ASSETS||{}).items||{};
const newH=[...new Set(DATA.players.map(p=>p.hero).filter(h=>h&&!Object.prototype.hasOwnProperty.call(AH2,h)))];
const newI=[...new Set(DATA.players.flatMap(p=>p.i||[]).filter(x=>x&&!Object.prototype.hasOwnProperty.call(AI2,x)))];
const newMsg=(newH.length||newI.length)?` · ${newH.length+newI.length} new art via live CDN (persist: python tools/fetch_assets.py)`:'';
var cacheObj=makeCacheEntry({schedule:ms,standings:st,season:ps,players:DATA.players,games:DATA.games,bans:DATA.bans,picks:DATA.picks,team_games:DATA.team_games,team_season:DATA.team_season,heroPool:DATA.hero_pool,matches:DATA.matches,heroes:DATA.heroes,playoffs:DATA.playoffs},{seasonId:SEASON_ID,schema:CACHE_SCHEMA,decided:countDecidedSet(ms,isPORow,isTerminalScore),complete:complete,failedIds:failedIds,refreshedAt:Date.now(),source:'refresh'});
try{localStorage.setItem(CK,JSON.stringify(cacheObj));}catch(e){upd.textContent='updated '+new Date().toLocaleTimeString()+' (not cached: storage full)';render();btn.disabled=false;btn.textContent=old;return;}
upd.textContent=refreshStatus({complete:complete,fails:failedIds.length,games:DATA.games.length,mvpN:mvpN,newMsg:newMsg});setNet();render();
}catch(e){upd.textContent='refresh failed — offline? showing last snapshot';setNet();}
btn.disabled=false;btn.textContent=old;}
document.getElementById('refresh').onclick=refreshDB;
const SEASON_ID=SEASON.seasonId,CACHE_SCHEMA=SEASON.cacheSchema;
const CK=cacheKeyFor(SEASON_ID,CACHE_SCHEMA);
function snapOf(){return {schedule:DATA.schedule,standings:DATA.standings,season:DATA.season,players:DATA.players,games:DATA.games,bans:DATA.bans,picks:DATA.picks,team_games:DATA.team_games,team_season:DATA.team_season,heroPool:DATA.hero_pool,matches:DATA.matches,heroes:DATA.heroes,playoffs:DATA.playoffs};}
try{var embSnap=snapOf();
var embMeta={fp:fingerprintSnapshot(embSnap),decided:countDecidedSet(DATA.schedule,isPORow,isTerminalScore),complete:true};
var cacheEntry=null;
try{
var rawC=localStorage.getItem(CK);
if(rawC){var ent=JSON.parse(rawC);
if(validateCacheEntry(ent,{seasonId:SEASON_ID,schema:CACHE_SCHEMA}).ok)cacheEntry=ent;}
else{var legRaw=localStorage.getItem('s18db');
if(legRaw){var leg=null;try{leg=JSON.parse(legRaw);}catch(le){leg=null;}
if(leg&&validSnapshot(leg).ok){
// Legacy entries predate completeness metadata and may hold partial detail
// collections from wholesale replaces: adopt only the always-complete
// top-level collections and keep the embedded games/players/bans. Detail
// rows for newer matches stay missing until the next successful refresh.
var adopt={schedule:leg.schedule,standings:leg.standings,season:leg.season,matches:leg.matches||[],heroes:leg.heroes||[],playoffs:(leg.playoffs||null),heroPool:(leg.heroPool||null),players:DATA.players,games:DATA.games,bans:DATA.bans,picks:DATA.picks,team_games:DATA.team_games,team_season:DATA.team_season};
cacheEntry=makeCacheEntry(adopt,{seasonId:SEASON_ID,schema:CACHE_SCHEMA,decided:countDecidedSet(leg.schedule,isPORow,isTerminalScore),complete:false,failedIds:[],refreshedAt:(typeof leg.t==='number'?leg.t:null),source:'legacy-migration'});
try{localStorage.setItem(CK,JSON.stringify(cacheEntry));localStorage.removeItem('s18db');}catch(se){}}}}
}catch(ce){cacheEntry=null;}
var pick=cacheEntry?selectSnapshot(embMeta,{fp:cacheEntry.fp,decided:cacheEntry.decided,complete:cacheEntry.complete,refreshedAt:cacheEntry.refreshedAt}):selectSnapshot(embMeta,null);
if(cacheEntry&&pick.use==='cache'){var dd=cacheEntry.data;
DATA.schedule=dd.schedule;DATA.standings=dd.standings;DATA.season=dd.season;
DATA.players=dd.players;DATA.games=dd.games;DATA.bans=dd.bans;
if(dd.picks)DATA.picks=dd.picks;if(dd.team_games)DATA.team_games=dd.team_games;if(dd.team_season)DATA.team_season=dd.team_season;
if(!dd.picks||!dd.team_games||!dd.team_season){var dv=deriveAnalyticsSnapshot(DATA);DATA.picks=dv.picks;DATA.team_games=dv.team_games;DATA.team_season=dv.team_season;}
if(dd.heroPool)DATA.hero_pool=dd.heroPool;if(dd.matches&&dd.matches.length)DATA.matches=dd.matches;
if(dd.heroes&&dd.heroes.length)DATA.heroes=dd.heroes;if(dd.playoffs)DATA.playoffs=dd.playoffs;
document.getElementById('upd').textContent='snapshot '+new Date(cacheEntry.refreshedAt||Date.now()).toLocaleString()+(pick.partial?' (partial)':'');}}catch(e){}
render();
