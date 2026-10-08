const DATA = __DATA__;
const TEAMS = ["AE", "BTR", "DEWA", "EVOS", "GEEK", "NAVI", "ONIC", "RRQ", "TLID"];
const TEAM_LOGOS = {ae:"assets/teams/ae.png",btr:"assets/teams/btr.png",dewa:"assets/teams/dewa.png",evos:"assets/teams/evos.png",geek:"assets/teams/geek.png",navi:"assets/teams/navi.png",onic:"assets/teams/onic.png",rrq:"assets/teams/rrq.png",tlid:"assets/teams/tlid.png"};
const logoOf = t => TEAM_LOGOS[String(t||'').toLowerCase()] || '';
const IMG_HIDE = 'onerror="this.style.visibility=\'hidden\'"';
function eqId(u){const m=/(?:equipment|equip)\/(\d+)\.png/.exec(u||'');return m?m[1]:'';}
function itemRef(u){const id=eqId(u);if(id)return id;if(u&&u.indexOf('scoregg.com')>-1)return String(u).split('?')[0];return null;}
function srt(arr,fn,str){const d=(S.tsort&&S.tsort.d)||1;return [...arr].sort((a,b)=>str?String(fn(a)).localeCompare(String(fn(b)))*d:(fn(a)-fn(b))*d);}
function th(t,k,label){const a=S.tsort.t===t&&S.tsort.k===k;return `<th data-ts="${t}:${k}">${label}${a?` <span class="sarr">${S.tsort.d===1?'▲':'▼'}</span>`:''}</th>`;}
function imgSlot(el){const s=document.createElement('span');s.className='slot-miss';s.title=el.alt||'item';s.textContent=el.dataset.eq||'?';el.replaceWith(s);}
const S = {view:'overview',q:'',team:'',sort:'kda',lane:'',compact:false,layout:'grid',ov:null,mlimit:24,plimit:24,phase:'reg',stat:'mvp',tsort:{t:'heroes',k:'pick',d:-1}};
const PICON_RAW = ((window.ASSETS||{}).players||{});
const PICON_CI = Object.fromEntries(Object.entries(PICON_RAW).map(([k,v])=>[k.toLowerCase(),v]));
const PICON_ALIAS = {arfy:'dingarai',yazukee:'affan',hijumee:'dalvin',alekk:'alexander',joshuaa:'joshuaa',kevinn:'kevin',maykidss:'maykids',shanee:'shanee',sanz:'s a n z'};
const PICON = n => {const k=String(n||'');const l=k.toLowerCase();return PICON_RAW[k]||PICON_CI[l]||PICON_CI[PICON_ALIAS[l]||'']||'';};
function ppic(n){const u=PICON(n);const init=esc(String(n||'?').split(/[\s_]+/).map(w=>w[0]).join('').slice(0,2).toUpperCase());
return (u?`<img class="ppic" src="${esc(u)}" alt="" loading="lazy" onerror="this.nextElementSibling.style.display='inline-flex';this.remove()">`:'')+`<span class="ppic-fb"${u?' style="display:none"':''}>${init}</span>`;}
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
function agg(){const m={};DATA.players.forEach(r=>{(m[r.player]=m[r.player]||{player:r.player,team:r.team,gp:0,k:0,d:0,a:0,gpm:0,hs:new Set()});
const o=m[r.player];o.gp++;o.k+=r.kills;o.d+=r.deaths;o.a+=r.assists;o.gpm+=r.gold_per_min;o.hs.add(r.hero);});
const seas=Object.fromEntries(DATA.season.map(s=>[String(s.player||'').toLowerCase(),s]));
const SALIAS={hijumee:'dalvin',arfy:'dingarai',yazukee:'affan',alekk:'alexander',kevinn:'kevin',maykids:'maykidss',kennzyskie:'kennzyyskie'};
const seasOf=n=>{const l=String(n||'').toLowerCase();return seas[l]||seas[SALIAS[l]||'']||null;};
const ultra=s=>String(s||'').toLowerCase().replace(/[^a-z0-9]/g,'');
const LIQLANES={nino:'EXP',affan:'JUNGLE',dalvin:'MID',dingarai:'GOLD',alexander:'ROAM',reyy:'JUNGLE',halim:'MID',ivann:'ROAM',shogun:'EXP',nnael:'JUNGLE',morenoo:'MID',emann:'GOLD',finn:'ROAM',miguel:'FLEX',rendyy:'EXP',alberttt:'JUNGLE',ryzaa:'MID',erlan:'GOLD',muezza:'ROAM',vell:'EXP',egatzy:'ROAM',drianw:'MID',qinn:'EXP',hazle:'JUNGLE',octa:'MID',maybeee:'GOLD',shane:'ROAM',itoshikesu:'ROAM',rulgood:'FLEX',kayn:'JUNGLE',marcel:'EXP',maykids:'JUNGLE',aboy:'MID',kennzyyskie:'GOLD',frenzyy:'ROAM',febriii:'EXP',nazara:'JUNGLE',audytzy:'ROAM',karss:'EXP',joshua:'EXP',jiizee:'MID',zeonn:'GOLD',aprho:'ROAM',febbb:'EXP',andoryuuu:'JUNGLE',lutpiii:'EXP',kairi:'JUNGLE',sanz:'MID',kelra:'GOLD',kiboy:'ROAM',killuaa:'MID',samuel:'ROAM',demonkite:'JUNGLE',hajirin:'MID',arthur:'GOLD',said:'ROAM',habil:'GOLD',clayyy:'MID',excellent99:'ROAM',faviannn:'JUNGLE',aran:'EXP',kevin:'JUNGLE',drichel:'MID',keven:'GOLD',lyoni:'ROAM',anaver:'MID'};
const liqLane=n=>LIQLANES[ultra(n)]||'';
return Object.values(m).map(o=>{const s=seasOf(o.player);const avgg=o.gpm/Math.max(1,o.gp);
const gp=s?+s.total_games||0:o.gp,k=s?+s.total_kills||0:o.k,d=s?+s.total_deaths||0:o.d,a=s?+s.total_assists||0:o.a;
const avgkda=(s&&s.avg_kda!=null&&s.avg_kda!=='')?+s.avg_kda:(k+a)/Math.max(1,d);
return {...o,gp,k,d,a,avgkda,nh:o.hs.size,avgg,lane:((s||{}).lane||liqLane(o.player)||'')}});}
function rows(id,gn){return DATA.players.filter(r=>r.match_detail_id===id&&String(r.game_no)===String(gn));}
const io=new IntersectionObserver(es=>es.forEach(e=>{if(e.isIntersecting){e.target.classList.add('in');io.unobserve(e.target);}}),{rootMargin:'80px'});
function syncControls(){const v=S.view;
const show=(id,on)=>{const el=document.getElementById(id);if(el)el.hidden=!on;};
show('searchBox',v==='players'||v==='matches');
show('chips',v==='players'||v==='matches');
show('sortBox',v==='players');
show('laneBox',v==='players');
show('layoutSeg',v==='players'||v==='matches');}
function render(){const out=[];
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
return `<div class="pin mpin"><div class="body"><div class="kicker">${esc(m.date||'')} · ${esc(m.status||'')}</div><div class="mteams"><div class="mt"><img src="${TICON(m.team_a)}" alt="" loading="lazy" ${IMG_HIDE}><span>${esc(m.team_a)}</span></div><div class="score">${m.score_a??'–'} : ${m.score_b??'–'}</div><div class="mt"><img src="${TICON(m.team_b)}" alt="" loading="lazy" ${IMG_HIDE}><span>${esc(m.team_b)}</span></div></div>${gmvp?`<div class="mmvp-grid">MVP · <b>${esc(gmvp)}</b></div>`:''}<div class="mmeta"><span class="tag">${done?('Detail #'+esc(m.match_detail_id)):esc(m.status||'upcoming')}</span></div></div><div class="actions">${done?`<button class="primary" data-m="${esc(m.match_detail_id)}">Scoreboard</button>`:`<button class="ghost" disabled>Soon</button>`}</div></div>`;}).join('');
const regAll=ms.filter(m=>!isPO(m)),poAll=ms.filter(isPO);
const reg=regAll.slice(0,S.mlimit),po=poAll.slice(0,S.plimit);
const pbtn=(k,label,n)=>`<button data-phase="${k}" aria-pressed="${S.phase===k?'true':'false'}">${label} (${n})</button>`;
const phaseCtl=`<div class="seg" role="group" aria-label="Phase">${pbtn('reg','Regular Season',regAll.length)}${pbtn('po','Playoffs',poAll.length)}</div>`;
const mvpById=Object.fromEntries((DATA.matches||[]).map(m=>[String(m.match_detail_id),m.liq_mvp||'']));
const mrow=m=>{const done=m.match_detail_id&&m.status==='completed';
const aWins=(+m.score_a)>(+m.score_b),bWins=(+m.score_b)>(+m.score_a);
return `<div class="mrow"${done?' data-m="'+esc(m.match_detail_id)+'"':''}><span class="mdate hide-m">${esc(m.iso_date||m.date||'')}</span>`
+`<span class="mfix"><img src="${TICON(m.team_a)}" alt="" loading="lazy" ${IMG_HIDE}><span class="mt ${done?(aWins?'mwin':'mlose'):''}">${esc(m.team_a)}</span><span class="msc">${m.score_a??'–'} : ${m.score_b??'–'}</span><span class="mt ${done?(bWins?'mwin':'mlose'):''}">${esc(m.team_b)}</span><img src="${TICON(m.team_b)}" alt="" loading="lazy" ${IMG_HIDE}></span>`
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
else{out.push(secHead('Regular Season',reg.length)+standBoard()+secCards(reg));
if(regAll.length>S.mlimit)out.push(`<div class="pin" style="grid-column:1/-1"><div class="body" style="text-align:center"><p>Showing ${S.mlimit} of ${regAll.length} regular-season matches</p><div class="actions"><button class="primary" data-more="24">Show more</button></div></div></div>`);}}}
if(S.view==='stats'){
const sbtn=(k,label)=>`<button data-stat="${k}" aria-pressed="${S.stat===k?'true':'false'}">${label}</button>`;
out.push(`<div class="pin" style="grid-column:1/-1"><div class="body phasebar"><div><div class="kicker">Statistics</div><h3 style="margin:.25em 0">${S.stat==='heroes'?'Heroes':'Series MVP'}</h3></div><div class="seg" role="group" aria-label="Stats">${sbtn('mvp','Series MVP')}${sbtn('heroes','Heroes')}</div></div></div>`);
if(S.stat==='heroes'){
const hs=(DATA.heroes||[]).map(h=>({hero:h.hero,img:h.hero_image,pick:+h.pick||0,ban:+h.ban||0,win:+h.win||0,wr:h.win_rate||'–'}));
const pb=h=>h.pick+h.ban;
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
out.push(`<div class="pin" style="grid-column:1/-1"><div class="body"><div class="kicker">Every contested hero · pick / ban / win</div><div class="lscroll"><table style="min-width:700px"><tr>${th('heroes','hero','Hero')}${th('heroes','pick','Pick')}${th('heroes','ban','Ban')}${th('heroes','pb','P+B')}${th('heroes','win','Win')}${th('heroes','wr','WR')}${th('heroes','share','Share')}</tr>${hrows.map(h=>`<tr><td data-ovhero="${esc(h.hero)}" data-scope="global" tabindex="0" title="Open ${esc(h.hero)} stats"><span class="hcell">${h.img?`<img src="${esc(h.img)}" alt="" loading="lazy" onerror="this.remove()">`:''}${esc(h.hero)}</span></td><td>${h.pick}</td><td>${h.ban}</td><td>${pb(h)}</td><td>${h.win}</td><td>${esc(h.wr)}</td><td style="min-width:110px"><span class="bar"><span style="width:${Math.round(pb(h)/maxPB*100)}%"></span></span></td></tr>`).join('')}</table></div></div></div>`);}
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
out.push(`<div class="pin"><div class="body"><div class="kicker">History</div><h3 style="margin:.25em 0">Series MVPs</h3><div class="lscroll"><table style="min-width:520px"><tr>${th('hist','date','Date')}${th('hist','match','Match')}${th('hist','mvp','MVP')}</tr>${hist.map(m=>{const c=canonicalPlayer(m.liq_mvp);return `<tr><td>${esc(m.iso_date||m.date||'')}</td><td>${esc(m.team_a)} ${m.score_a??''}:${m.score_b??''} ${esc(m.team_b)}</td><td>${esc(c)}${c!==m.liq_mvp?` <span style="font-family:var(--font-mono);font-size:10.5px;color:var(--muted)">(as ${esc(m.liq_mvp)})</span>`:''}</td></tr>`;}).join('')}</table></div></div></div>`);}}
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
board.querySelectorAll('[data-ts]').forEach(b=>b.onclick=()=>{const [t,k]=b.dataset.ts.split(':');const str=k==='hero'||k==='player'||k==='team'||k==='match'||k==='mvp'||k==='date';if(S.tsort.t===t&&S.tsort.k===k)S.tsort.d*=-1;else S.tsort={t,k,d:str?1:-1};render();});
wireCharts();wireBracket();}
function normId(s){return String(s||'').toLowerCase().replace(/[^a-z0-9]/g,'');}
function offOf(n){const m={};DATA.season.forEach(s=>{m[String(s.player||'').toLowerCase()]=s;});
const GALIAS={hijumee:'dalvin',arfy:'dingarai',yazukee:'affan',alekk:'alexander',kevinn:'kevin',maykids:'maykidss',kennzyskie:'kennzyyskie'};
const l=String(n||'').toLowerCase();return m[l]||m[GALIAS[l]||'']||null;}
/* PLAYER IDENTITY — one real player = one canonical roster identity.
   Series MVP names come from Liquipedia match pages while game rows use live-API
   IGNs, so the same person can appear under different spellings. Verified (public):
   Coolfire->Joshuaa (reddit r/mobilelegendsesports 2026-08-30 "joshua(coolfire)";
   both MVP rows are NAVI matches; Joshuaa is the NAVI jungler per navi.gg + MLDB),
   JOOOOO->Kevinn (bo3.gg lists both "JOOOOO (Yonathan Chin)" and
   "Kevinn (Yonathan Chin)" for TLID; teamliquid.com TLID roster lists JOOOOO;
   Keven Julio Keven is a different person — TLID gold laner),
   Sutsujin->Arthur (Liquipedia "Arthur 'Sutsujin' Sunarkho", MLDB, RRQ Hoshi).
   Mechanical (MVP-row teams intersect the roster team; re-verify if contested):
   A B O Y->Aboyy, Jizeezeze->Jiizee, Maykids->Maykidss, Moreno->Morenooo,
   Rendyy->Rendyyy. Roster spelling duplicate from the live API: MAYKIDSS->Maykidss.
   Deliberately NOT merged: Joshua (RRQ) vs Joshuaa (NAVI) — different people.
   To add a future alias: add one normalized->canonical entry to PLAYER_ALIAS.
   Every aggregation/display path goes through canonicalPlayer(), so no second
   identity can arise from a new spelling. */
const PLAYER_ALIAS={coolfire:'Joshuaa',jooooo:'Kevinn',sutsujin:'Arthur',jizeezeze:'Jiizee',maykids:'Maykidss',maykidss:'Maykidss',moreno:'Morenooo',morenooo:'Morenooo',rendyy:'Rendyyy',rendyyy:'Rendyyy',aboy:'Aboyy',aboyy:'Aboyy'};
const ROSTER_SPELLING={maykidss:'Maykidss'};
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
return `<tr><td data-ovhero="${esc(h)}" tabindex="0" title="View ${esc(h)} games"><span class="hcell">${hi?`<img src="${esc(hi)}" alt="" loading="lazy" onerror="this.remove()">`:''}${esc(h)}</span></td><td>${o.n}</td><td><div style="display:flex;gap:6px;align-items:center"><span class="wrbar"><i style="width:${o.n?Math.round(o.w/o.n*100):0}%"></i></span>${o.n?Math.round(o.w/o.n*100):0}%</div></td><td>${(o.k/Math.max(1,o.n)).toFixed(1)}/${(o.d/Math.max(1,o.n)).toFixed(1)}/${(o.a/Math.max(1,o.n)).toFixed(1)}</td><td>${Math.round(o.gpm/Math.max(1,o.n))}</td></tr>`;}).join('');
const sides={};rows.forEach(x=>{const sd=(x.info.side||'').toLowerCase()||'unknown';(sides[sd]=sides[sd]||{w:0,n:0}).n++;if(x.info.won===true)sides[sd].w++;});
const sideTbl=Object.entries(sides).map(([sd,o])=>`<tr><td style="text-transform:capitalize">${esc(sd)} side</td><td>${o.n}</td><td>${o.n?Math.round(o.w/o.n*100):0}%</td></tr>`).join('');
const opps={};rows.forEach(x=>{const o=x.info.opp||'?';(opps[o]=opps[o]||{w:0,n:0}).n++;if(x.info.won===true)opps[o].w++;});
const oppTbl=Object.entries(opps).sort((a,b)=>b[1].n-a[1].n).map(([o,v])=>`<tr><td data-ovopp="${esc(o)}" tabindex="0" title="View games vs ${esc(o)}"><img src="${TICON(o)}" alt="" loading="lazy" style="width:20px;height:20px;object-fit:contain;vertical-align:-5px" onerror="this.remove()"> ${esc(o)}</td><td>${v.n}</td><td>${v.w}-${v.n-v.w}</td></tr>`).join('');
const useCounts=heroUseCounts(rows);
const itemGrid=topEntries(useCounts.item,12).map(([id,c])=>itemCell(id,c)).join('')||'<p>No item data</p>';
const embHtml=topEntries(useCounts.emb,7).map(([id,c])=>embBadge(id,c)).join('')||'<p>No emblem data</p>';
const talHtml=topEntries(useCounts.tal,8).map(([id,c])=>talBadge(id,c)).join('')||'<p>No talent data</p>';
const mvps=(DATA.matches||[]).filter(m=>m.liq_mvp&&samePlayer(m.liq_mvp,name));
const mvpHtml=mvps.length?mvps.map(m=>{const sc=(DATA.schedule||[]).find(s=>String(s.match_detail_id)===String(m.match_detail_id))||{};return `<tr><td>${esc(sc.date||sc.iso_date||'')}</td><td>${esc(m.team_a)} vs ${esc(m.team_b)}</td></tr>`;}).join(''):'<tr><td colspan="2">No recorded MVPs</td></tr>';
const log=rows.map(x=>`<tr><td class="mono">${esc(x.info.date||'')}</td><td>G${x.r.game_no}</td><td>vs ${esc(x.info.opp||'')}</td><td>${esc(x.r.hero||'')}</td><td>${x.r.kills??x.r.kill}/${x.r.deaths??x.r.death}/${x.r.assists??x.r.assist}</td><td>${x.info.won===null?'–':(x.info.won?'W':'L')}</td></tr>`).join('');
const kp=s.kill_participation||'—';
return `<div class="pin ov"><div class="body"><div class="phead">${u?`<img class="ppic" src="${esc(u)}" alt="" onerror="this.remove()">`:''}<div><div class="kicker">${esc(g.team||'')} · ${esc(g.lane||'—')}</div><h3 style="margin:0">${esc(name)}</h3></div><img class="tlogo" src="${TICON(g.team)}" alt="" loading="lazy" onerror="this.remove()"><button class="ghost" id="ovPick" style="margin-left:auto;border:1px solid var(--line);background:transparent;color:var(--ink);border-radius:8px;padding:8px 14px;cursor:pointer;font-weight:600">Player ▾</button></div>`
+`<div class="tiles"><div class="tile"><b>${g.gp||0}</b><span>Games</span></div><div class="tile"><b>${(g.avgkda||0).toFixed(2)}</b><span>Avg KDA</span></div><div class="tile"><b>${wins}-${scored.length-wins}</b><span>Game W-L</span></div><div class="tile"><b>${wr}%</b><span>Game WR</span></div><div class="tile"><b>${mw}-${ml}</b><span>Match W-L</span></div><div class="tile"><b>${mwr}%</b><span>Match WR</span></div><div class="tile"><b>${fmtDur(avgD)}</b><span>Avg game</span></div><div class="tile"><b>${esc(String(kp))}</b><span>Kill part.</span></div></div>`
+`<div class="ovgrid"><div class="ovsec"><h4>KDA trend per game</h4>${trendChart(rows.map(x=>{const k=x.r.kills??x.r.kill??0,d=x.r.deaths??x.r.death??0,a=x.r.assists??x.r.assist??0;return {v:(k+a)/Math.max(1,d),date:x.info.date||'',opp:x.info.opp||'',hero:x.r.hero||'',kda:((k+a)/Math.max(1,d)).toFixed(2),won:x.info.won};}))}<p>${rows.length} scored games · total gold ${(totG/1000).toFixed(0)}k · hero dmg ${(totD/1000).toFixed(0)}k · taken ${(totT/1000).toFixed(0)}k · tower ${(totTw/1000).toFixed(0)}k</p></div>`
+`<div class="ovsec"><h4>Hero pool (${heroRows.length} heroes)</h4><table><tr><th>Hero</th><th>GP</th><th>Win%</th><th>Avg K/D/A</th><th>GPM</th></tr>${heroTbl}</table></div></div>`
+`<div class="ovgrid"><div class="ovsec"><h4>Hero win rate</h4><table>${heroRows.map(o=>`<tr><td data-ovhero="${esc(o.h)}" tabindex="0" title="View ${esc(o.h)} games">${esc(o.h)}</td><td><div style="display:flex;gap:6px;align-items:center"><span class="wrbar"><i style="width:${o.wr}%"></i></span>${o.wr}%</div></td></tr>`).join('')}</table></div>`
+`<div class="ovsec"><h4>Sides</h4><table><tr><th>Side</th><th>GP</th><th>Win%</th></tr>${sideTbl}</table></div></div>`
+`<div class="ovgrid"><div class="ovsec"><h4>Top items</h4><div class="itemgrid">${itemGrid}</div></div>`
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
function assetRowsHTML(u,scope){const e=topEntries(u.emb,3),t=topEntries(u.tal,4),it=topEntries(u.item,6);
const row=(label,cells)=>`<div class="userow"><div class="ulabel">${label}</div><div class="ubadges">${cells}</div></div>`;
const dash='<span style="color:var(--muted)">–</span>';
return `<div class="usegrid">`
+row('Emblems',e.map(([id,c])=>embBadge(id,c,scope)).join('')||dash)
+row('Talents',t.map(([id,c])=>talBadge(id,c,scope)).join('')||dash)
+row('Items',it.map(([id,c])=>scope==='global'?itemBtn(id,c,scope):itemCell(id,c)).join('')||dash)+`</div>`;}
function usageSummaryHTML(list,scope){return `<div class="msec">Usage summary · ${list.length} game${list.length===1?'':'s'}</div>`+assetRowsHTML(heroUseCounts(list),scope);}
function heroBreakdownRows(byH,scope){const A=window.ASSETS||{heroes:{}};return Object.entries(byH).sort((a,b)=>b[1]-a[1]).map(([h,n])=>{const hi=A.heroes&&A.heroes[h];
return `<tr><td data-ovhero="${esc(h)}"${scope==='global'?' data-scope="global"':''} tabindex="0" title="View ${esc(h)} games"><span class="hcell">${hi?`<img src="${esc(hi)}" alt="" loading="lazy" onerror="this.remove()">`:''}${esc(h)}</span></td><td>×${n}</td></tr>`;}).join('');}
function gameRowHTML(x){const r=x.r,k=r.kills??r.kill??0,d=r.deaths??r.death??0,a=r.assists??r.assist??0;
const kda=((k+a)/Math.max(1,d)).toFixed(1);
const A=window.ASSETS||{};
const hi=r.hero&&A.heroes&&A.heroes[r.hero]?A.heroes[r.hero]:null;
const dt=(x.info.iso||'').slice(0,10)||x.info.date||'';
return `<div class="mrow" data-ovg="${esc(String(r.match_detail_id))}:${esc(String(r.game_no))}" tabindex="0" role="button" aria-label="Open game ${esc(String(r.game_no))} vs ${esc(x.info.opp||'')}"><span class="mdate">${esc(dt)}</span>`
+`<span class="mfix">${hi?`<img src="${esc(hi)}" alt="" loading="lazy" onerror="this.remove()">`:''}<span class="msc">G${esc(String(r.game_no))}</span><span class="mt">vs ${esc(x.info.opp||'?')} · ${esc(r.hero||'')} · ${k}/${d}/${a}</span></span>`
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
dSet(hero,'Stats · Heroes · '+picks.length+' picks · '+bans.length+' bans',
`${hi?`<p><img src="${esc(hi)}" alt="${esc(hero)}" loading="lazy" style="width:40px;height:40px;border-radius:10px;border:1px solid var(--line);object-fit:cover" onerror="this.remove()"></p>`:''}`
+sumHtml+gamesHtml);}
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
const A=window.ASSETS||{heroes:{}};
const bh={};r.forEach(x=>{(bh[x.hero]=bh[x.hero]||[]).push(x);});
const t=Object.entries(bh).map(([h,rs])=>{const hg=rs.reduce((s,x)=>s+(x.gold_per_min||0),0)/rs.length;
const ak=rs.reduce((s,x)=>s+x.kills,0)/rs.length,ad=rs.reduce((s,x)=>s+x.deaths,0)/rs.length,aa=rs.reduce((s,x)=>s+x.assists,0)/rs.length;
const akda=rs.reduce((s,x)=>s+(+x.kda||0),0)/rs.length;
const hi=(A.heroes&&A.heroes[h])||'';return `<tr><td><span class="hcell">${hi?`<img src="${esc(hi)}" alt="" loading="lazy" onerror="this.remove()">`:''}${esc(h)}</span></td><td>${rs.length}</td><td>${akda.toFixed(2)}</td><td>${ak.toFixed(1)}</td><td>${ad.toFixed(1)}</td><td>${aa.toFixed(1)}</td><td>–</td><td>–</td><td>${hg.toFixed(0)}</td></tr>`;}).join('');
const u=PICON(disp);
openD(disp,(g.team||'')+' · '+(g.lane||''),`<div class="pdhead">${u?`<img src="${esc(u)}" alt="" onerror="this.remove()">`:''}<div><div class="kicker">${esc(g.team||'')} · ${esc(g.lane||'—')}</div><div style="font-family:var(--font-display);font-size:19px;font-weight:700">${esc(disp)}</div></div></div><div class="tiles"><div class="tile"><b>${g.gp||r.length}</b><span>Games</span></div><div class="tile"><b>${(g.avgkda||0).toFixed(2)}</b><span>Avg KDA</span></div><div class="tile"><b>${(g.avgg||0).toFixed(0)}</b><span>Avg gold/min</span></div><div class="tile"><b>${g.k||0}/${g.d||0}/${g.a||0}</b><span>Total K / D / A</span></div></div><div class="lscroll"><table style="min-width:560px"><tr><th>Hero</th><th>GP</th><th>AVG KDA</th><th>AVG K</th><th>AVG D</th><th>AVG A</th><th title="Under development — no official ID source publishes this yet">MANIAC *</th><th title="Under development — no official ID source publishes this yet">SAVAGE *</th><th>GPM</th></tr>${t}</table></div><div class="mono" style="font-family:var(--font-mono);font-size:10.5px;color:var(--muted);margin-top:6px">* MANIAC / SAVAGE tracking is under development — no official MPL ID source publishes these counts yet.</div>`);}
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
const items=itemObjs.map(o=>{const src=(o.eq&&A.items&&A.items[o.eq])||(o.url&&A.items&&A.items[o.url])||o.url;if(!src)return '';return `<img src="${esc(src)}" alt="item ${o.eq||''}" data-eq="${o.eq||''}" loading="lazy" onerror="imgSlot(this)">`;}).join('');
return `<div class="sb-p">${heroImg}<div class="sb-id"><b>${esc(r.player)}</b><span>${esc(r.hero||'')} · ${r.kills}/${r.deaths}/${r.assists} · KDA ${r.kda}</span></div>`
+`<div class="sb-side">G ${r.gold}${r.gpm!=null?' ('+r.gpm+'/m)':''}<br>DMG ${r.hero_damage??'–'} · TAKEN ${r.damage_taken??'–'}</div>`
+`<div class="sb-gear"><span class="sb-tal">${embSm}${tals}</span>${items?`<span class="sb-items">${items}</span>`:''}</div></div>`;}).join('');
return `<div class="sb-team${flip?' flip':''}${pk?' '+pk:''}"><div class="sb-thead"><img src="${logoOf(code)}" alt="" ${IMG_HIDE}><b class="${won===true?'tw':won===false?'tl':''}">${esc(code)}</b><span class="k">${kills} kills</span></div>${prow}</div>`;}
function winName(g){return g.winner==='team_a'?g.team_a:(g.winner==='team_b'?g.team_b:(g.winner||''));}
/* Playoff chances (1 series win = 1 point; every team plays exactly 16 series).
   Top 6 → playoffs ("% Playoff Chance"), top 2 → upper bracket ("% Upper
   Bracket"). Hard limits use max-possible = current + (16 - played):
   PC 100 iff pts > max max-possible of 7th/8th/9th; PC 0 iff max-possible <
   pts of 6th. UB 100 iff pts > max max-possible of 3rd..9th; UB 0 iff
   max-possible < pts of 2nd. Undecided teams: seeded Monte-Carlo (500 trials)
   over the actual remaining fixtures, each sampled with P(A wins) =
   wra/(wra+wrb) from series win rates, cuts on (pts, net game diff).
   Fixed seed → stable across renders. */
/* Dynamic season config (no hardcoded team/slot counts below). MPL ID regular
   season: 9 teams, double round-robin → each team plays 16 series. */
const TOTAL_TEAMS=9,ROUND_ROBIN_ROUNDS=2,PLAYOFF_SLOTS=6,UPPER_BRACKET_SLOTS=2;
const TOTAL_SERIES=ROUND_ROBIN_ROUNDS*(TOTAL_TEAMS-1),TRIALS=500;
function poRow(m){return String(m.schedule_id||m.match_id||'').indexOf('playoffs')>-1||(m.team_a==='TBD'&&m.team_b==='TBD');}
function playoffChance(){
const rows=[...DATA.standings].sort((a,b)=>a.rank-b.rank);
const key=r=>String(r.team_slug||r.team_name||'').toLowerCase();
const code=t=>String(t||'').toLowerCase();
const pts=r=>+r.match_point||0;
const played=r=>(+r.match_win||0)+(+r.match_lose||0);
const maxP=r=>pts(r)+Math.max(0,TOTAL_SERIES-played(r));
const wr=r=>{const p=played(r);return p?((+r.match_win||0)/p):0.5;};
const rem=(DATA.schedule||[]).filter(m=>m.status!=='completed'&&!poRow(m));
const p6=pts(rows[PLAYOFF_SLOTS-1]||{match_point:0}),max789=Math.max.apply(null,rows.slice(PLAYOFF_SLOTS).map(maxP).concat([-1]));
const p2=pts(rows[UPPER_BRACKET_SLOTS-1]||{match_point:0}),max39=Math.max.apply(null,rows.slice(UPPER_BRACKET_SLOTS).map(maxP).concat([-1]));
const out={};
let seed=0x51ab;const rnd=()=>{seed|=0;seed=seed+0x6D2B79F5|0;
let t=Math.imul(seed^seed>>>15,1|seed);t=t+Math.imul(t^t>>>7,61|t)^t;return((t^t>>>14)>>>0)/4294967296;};
const cut6={},cut2={};
rows.forEach(r=>{const k=key(r);
const pc=pts(r)>max789?{v:100,why:'Clinched'}:(maxP(r)<p6?{v:0,why:'Eliminated'}:null);
const ub=pts(r)>max39?{v:100,why:'Clinched'}:(maxP(r)<p2?{v:0,why:'Eliminated'}:null);
if(pc&&ub){out[k]={pc:pc,ub:ub};return;}
out[k]={pc:pc,ub:ub};if(!pc)cut6[k]=0;if(!ub)cut2[k]=0;});
if(Object.keys(cut6).length||Object.keys(cut2).length){
const rate={};rows.forEach(r=>{rate[key(r)]=wr(r);});
for(let t=0;t<TRIALS;t++){const p={};rows.forEach(r=>{p[key(r)]=pts(r);});
rem.forEach(m=>{const a=code(m.team_a),b=code(m.team_b);if(!(a in p)||!(b in p))return;
const pa=rate[a],pb=rate[b],q=(pa+pb)?pa/(pa+pb):0.5;p[rnd()<q?a:b]++;});
const rank=[...rows].sort((x,y)=>{const kx=key(x),ky=key(y);
return (p[ky]-p[kx])||((+y.net_game_win||0)-(+x.net_game_win||0))||String(kx).localeCompare(String(ky));});
rank.slice(0,PLAYOFF_SLOTS).forEach(r=>{const k=key(r);if(k in cut6)cut6[k]++;});
rank.slice(0,UPPER_BRACKET_SLOTS).forEach(r=>{const k=key(r);if(k in cut2)cut2[k]++;});}
rows.forEach(r=>{const k=key(r);
if(!out[k].pc)out[k].pc={v:Math.round(cut6[k]/TRIALS*100),why:'Simulated over '+rem.length+' remaining series'};
if(!out[k].ub)out[k].ub={v:Math.round(cut2[k]/TRIALS*100),why:'Simulated over '+rem.length+' remaining series'};});}
const res={};rows.forEach(r=>{res[key(r)]=out[key(r)]||{pc:{v:0,why:'Eliminated'},ub:{v:0,why:'Eliminated'}};});return res;}
function standBoard(){
const stBase=[...DATA.standings].sort((a,b)=>a.rank-b.rank);
const pcMap=playoffChance();
stBase.forEach(s=>{const k=String(s.team_slug||s.team_name||'').toLowerCase();const e=pcMap[k]||{pc:{v:0},ub:{v:0}};s._pc=e.pc.v;s._pcWhy=e.pc.why||'';s._ub=e.ub.v;s._ubWhy=e.ub.why||'';});
const sval=(s,k)=>k==='team'?s.team_name:k==='pts'?+s.match_point:k==='pc'?+s._pc:k==='ub'?+s._ub:k==='mw'?+s.match_win:k==='gw'?+s.game_win:k==='df'?+s.net_game_win:+s.rank;
const st=S.tsort.t==='stand'?srt(stBase,s=>sval(s,S.tsort.k),S.tsort.k==='team'):stBase;
return `<div class="pin" style="grid-column:1/-1"><div class="body"><div class="phasebar"><div><div class="kicker">Regular season</div><h3 style="margin:.25em 0">Standings</h3></div></div><div class="lscroll"><table style="min-width:700px"><tr>${th('stand','rank','#')}${th('stand','team','Team')}${th('stand','pts','Pts')}${th('stand','mw','Match W-L')}${th('stand','gw','Game W-L')}${th('stand','df','+/-')}${th('stand','pc','% Playoff Chance')}${th('stand','ub','% Upper Bracket')}</tr>${st.map(s=>{const slug=(s.team_slug||s.team_name||'').toLowerCase();const ng=+s.net_game_win||0;return `<tr><td>${s.rank}</td><td><img src="${TICON(slug)}" alt="" loading="lazy" style="width:20px;height:20px;object-fit:contain;vertical-align:-5px" ${IMG_HIDE}> ${esc(s.team_name)}</td><td>${s.match_point}</td><td>${s.match_win}-${s.match_lose}</td><td>${s.game_win}-${s.game_lose}</td><td>${ng>0?'+'+ng:ng}</td><td title="${esc(s._pcWhy||'Playoff chance')}"><b>${s._pc}%</b></td><td title="${esc(s._ubWhy||'Upper bracket chance')}"><b>${s._ub}%</b></td></tr>`;}).join('')}</table></div></div></div>`;}
function finalBoard(){
const places=['Champion','Runner-up','3rd place','4th place','5th place','6th place','7th place','8th place'];
return `<div class="pin" style="grid-column:1/-1"><div class="body"><div class="phasebar"><div><div class="kicker">Playoffs · decided at finals</div><h3 style="margin:.25em 0">Final positions</h3></div></div><div class="lscroll"><table style="min-width:420px"><tr><th>Pos</th><th>Place</th><th>Team</th></tr>${places.map((p,i)=>`<tr><td>#${i+1}</td><td>${p}</td><td>TBD</td></tr>`).join('')}</table></div></div></div>`;}
function bracketHTML(){
const ms=((DATA.playoffs||{}).matches||[]);
if(!ms.length)return '';
const byRound={};ms.forEach(m=>{byRound[m.round]=m;});
return `<div class="pin" style="grid-column:1/-1"><div class="body"><div class="phasebar"><div><div class="kicker">Playoffs</div><h3 style="margin:.25em 0">Bracket preview</h3></div></div>${bracketGrid(byRound)}</div></div>`;}
const teamRow=(n,logo,sc,w)=>`<div class="brk-team${w?' w':''}"${n?` data-brkt="${esc(n)}"`:''}>${logo?`<img src="${esc(logo)}" alt="" loading="lazy" onerror="this.remove()">`:''}<span>${esc(n||'TBD')}</span><b>${sc??''}</b></div>`;
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
const seedTooltip=n=>`<div class="brk-team seed" data-seed="${n}" tabindex="0"><span>Seed ${n}</span><span class="seedtip" role="tooltip"><span class="sdisc">${n}</span><span class="stext"><b>${ORD[n-1]} position</b><i>Regular season</i></span></span></div>`;
const tbdRow=()=>`<div class="brk-team tbd"><span>TBD</span></div>`;
const rowFor=(m,ab,seed)=>{const t=m?(ab==='a'?m.team_a:m.team_b):null;
if(t&&t!=='TBD')return teamRow(t,m?(ab==='a'?m.team_a_logo:m.team_b_logo):null,m?(ab==='a'?m.score_a:m.score_b):null,m?(ab==='a'?m.winner==='team_a':m.winner==='team_b'):false);
if(seed)return seedTooltip(seed);return tbdRow();};
const matchCard=(slot,m)=>{const inner=!m?`<div class="brk-match brk-tbd"><span>TBD</span></div>`:`<div class="brk-match"><div class="brk-round">${esc(slot.label)}</div>${rowFor(m,'a',slot.seeds[0])}${rowFor(m,'b',slot.seeds[1])}<div class="brk-date">${esc(m.date||'')}</div></div>`;
return inner.replace('brk-match','brk-match" data-brk="'+esc(slot.rk));};
const colHTML=(c,byRound)=>`<div class="brk-col${c.bottom?' split':(c.mid?' center':'')}"><div class="brk-title">${c.h}</div>${(c.top||c.mid||[]).map(s=>matchCard(s,byRound[s.rk])).join('')}${c.bottom?'<div class="brk-gap"></div>'+c.bottom.map(s=>matchCard(s,byRound[s.rk])).join(''):''}</div>`;
function bracketGrid(byRound){return `<div class="brk">${BRK_COLS.map(c=>colHTML(c,byRound)).join('')}</div>`;}
/* Standard double-elim feeds: winners move right (solid), R2 losers drop to
   the lower semi (dashed). R1 losers have no outgoing path in this format.
   The UBF winner drops into the Grand Final from above ('top' entry) so its
   line never crosses the Lower Final card. */
const BRK_FEEDS=[['Round 1 Match 1','Round 2 Match 1',0],['Round 1 Match 2','Round 2 Match 2',0],['Round 2 Match 1','Upper Bracket Finals',0],['Round 2 Match 2','Upper Bracket Finals',0],['Round 2 Match 1','Lower Bracket Semi Finals',1],['Round 2 Match 2','Lower Bracket Semi Finals',1],['Upper Bracket Finals','Grand Finals',0,'top'],['Upper Bracket Finals','Lower Bracket Finals',1],['Lower Bracket Semi Finals','Lower Bracket Finals',0],['Lower Bracket Finals','Grand Finals',0]];
/* Grand Final slot routing: Upper winner → TOP row, Lower winner → BOTTOM row. */
const BRK_GF_SLOT={'Upper Bracket Finals':0,'Lower Bracket Finals':1};
function svgOverlay(el){el.querySelectorAll('svg.brk-lines,svg.brk-hover').forEach(s=>s.remove());
const q=rk=>el.querySelector('[data-brk="'+rk+'"]');
const ST='rgba(255,255,255,.22)',DT='rgba(255,255,255,.16)';
const bez=(x1,y1,x2,y2)=>{const mx=(x1+x2)/2;return `M${x1},${y1} C${mx},${y1} ${mx},${y2} ${x2},${y2}`;};
const box=rk=>{const c=q(rk);if(!c)return null;const g=brkRect(el,c);
return {l:g.left,r:g.right,t:g.top,cy:g.cy};};
const rowY=(rk,slot)=>{const c=q(rk);if(!c||slot==null)return null;
const rows=c.querySelectorAll('.brk-team');if(!rows.length||slot>=rows.length)return null;
const g=brkRect(el,rows[slot]);return g.cy;};
let paths='';
BRK_FEEDS.forEach(([a,b,drop,entry])=>{const A=box(a),T=box(b);if(!A||!T)return;
const st=drop?DT:ST,w=drop?1.5:2;
if(b==='Grand Finals'){const y=rowY(b,BRK_GF_SLOT[a]);if(y==null)return;
paths+=`<path d="${bez(A.r,A.cy,T.l,y)}" fill="none" stroke="${st}" stroke-width="${w}"/>`;}
else{paths+=`<path d="${bez(A.r,A.cy,T.l,T.cy)}" fill="none" stroke="${st}" stroke-width="${w}"/>`;}});
if(!paths)return;
const svg=document.createElementNS('http://www.w3.org/2000/svg','svg');
svg.setAttribute('class','brk-lines');svg.setAttribute('width',el.scrollWidth);svg.setAttribute('height',el.scrollHeight);
svg.innerHTML=paths;el.appendChild(svg);}
/* Hover team pathing: hovering a team row draws glowing bezier inbound paths
   from its previous match position(s) plus outbound branches (advance solid,
   loss dashed; elimination fades down off the container). Exact team-row
   matching by name; TBD/unknown names fall back to card centers. */
const BRK_LOSS={'Round 1 Match 1':null,'Round 1 Match 2':null,'Round 2 Match 1':'Lower Bracket Semi Finals','Round 2 Match 2':'Lower Bracket Semi Finals','Upper Bracket Finals':'Lower Bracket Finals','Lower Bracket Semi Finals':null,'Lower Bracket Finals':null,'Grand Finals':null};
const BRK_NEXT={};BRK_FEEDS.forEach(([a,b,drop])=>{if(!drop){(BRK_NEXT[a]=BRK_NEXT[a]||[]).push(b);}});
const BRK_PREV={};BRK_FEEDS.forEach(([a,b,drop])=>{if(!drop){(BRK_PREV[b]=BRK_PREV[b]||[]).push(a);}});
/* Viewport-anchored geometry: rects are viewport-relative so page scroll
   cancels out; the container's own scroll offset maps into content space. */
function brkRect(brk,node){const b=brk.getBoundingClientRect(),r=node.getBoundingClientRect();
const x=r.left-b.left+brk.scrollLeft,y=r.top-b.top+brk.scrollTop;
return {left:x,top:y,right:x+r.width,cy:y+r.height/2,cx:x+r.width/2,bottom:y+r.height};}
function brkCurve(x1,y1,x2,y2){const mx=(x1+x2)/2;return `M${x1},${y1} C${mx},${y1} ${mx},${y2} ${x2},${y2}`;}
/* Parent hover state: one explicit store instead of scattered DOM flags. */
const BrkHover={activeTeamId:null,activeSeedId:null,el:null,row:null};
function setBrkHover(el,row){BrkHover.el=el;BrkHover.row=row;
BrkHover.activeTeamId=row&&row.dataset.brkt?row.dataset.brkt:null;
BrkHover.activeSeedId=row&&row.dataset.seed?row.dataset.seed:null;}
function clearBrkHover(){BrkHover.activeTeamId=null;BrkHover.activeSeedId=null;BrkHover.el=null;BrkHover.row=null;}
/* Phased draw: previous-position line first, win/loss branches second. */
function playBrk(svg){const prev=[...svg.querySelectorAll('path.prev')],next=[...svg.querySelectorAll('path.win,path.loss')];
const reduced=window.matchMedia&&window.matchMedia('(prefers-reduced-motion: reduce)').matches;
requestAnimationFrame(()=>requestAnimationFrame(()=>{prev.forEach(p=>p.classList.add('go'));
if(reduced||!next.length){next.forEach(p=>p.classList.add('go'));svg.classList.add('done');return;}
setTimeout(()=>next.forEach(p=>p.classList.add('go')),350);
setTimeout(()=>svg.classList.add('done'),850);}));}
function gfSlotY(brk,q,fromRk){const t=q('Grand Finals');if(!t)return null;
const rows=t.querySelectorAll('.brk-team');const i=BRK_GF_SLOT[fromRk];
if(i==null||!rows.length||i>=rows.length)return null;
return {x:brkRect(brk,t).left,y:brkRect(brk,rows[i]).cy};}
function showTeamPaths(brk,row){clearTeamPaths(brk);
const card=row.closest('[data-brk]');if(!card)return;
const round=card.dataset.brk,name=row.dataset.brkt;
const q=rk=>brk.querySelector('[data-brk="'+rk+'"]');
const matchRow=(rk)=>{const c=q(rk);if(!c)return null;
if(name&&name!=='TBD'){const hit=[...c.querySelectorAll('.brk-team')].find(r=>r.dataset.brkt===name);if(hit)return hit;}
return null;};
const P=brkRect(brk,row);
const svg=document.createElementNS('http://www.w3.org/2000/svg','svg');
svg.setAttribute('class','brk-hover');svg.setAttribute('width',brk.scrollWidth);svg.setAttribute('height',brk.scrollHeight);
let paths='';
const add=(d,stroke,w,cls)=>{paths+=`<path d="${d}" pathLength="1" stroke="${stroke}" stroke-width="${w}" class="${cls}"/>`;};
const INK='rgba(242,241,236,.85)',MUT='rgba(166,163,155,.6)';
const gfY=(fromRk)=>gfSlotY(brk,q,fromRk);
(BRK_PREV[round]||[]).forEach(rk=>{const c=q(rk);if(!c)return;
const src=matchRow(rk),S=src?brkRect(brk,src):brkRect(brk,c);
add(brkCurve(S.right,S.cy,P.left,P.cy),INK,2.5,'prev');});
(BRK_NEXT[round]||[]).forEach(rk=>{const t=q(rk);if(!t)return;
if(rk==='Grand Finals'){const G=gfY(round);if(!G)return;
add(brkCurve(P.right,P.cy,brkRect(brk,t).left,G.y),INK,2,'win');return;}
const T=brkRect(brk,t);
add(brkCurve(P.right,P.cy,T.left,T.cy),INK,2,'win');});
const lossTo=BRK_LOSS[round];
if(lossTo){const t=q(lossTo);if(t){const T=brkRect(brk,t);
add(brkCurve(P.right,P.cy,T.left,T.cy),MUT,2,'loss');}}
else if(round!=='Grand Finals'){const yB=brk.scrollHeight;
const elim=`<path d="M${P.cx},${P.cy} C${P.cx},${P.cy+46} ${P.cx},${yB-70} ${P.cx},${yB}" pathLength="1" stroke="${MUT}" stroke-width="2" class="loss" mask="url(#brkfadem)"/>`;
svg.innerHTML=`<defs><linearGradient id="brkfade" x1="0" y1="0" x2="0" y2="1"><stop offset="0" stop-color="#fff" stop-opacity=".7"/><stop offset="1" stop-color="#fff" stop-opacity="0"/></linearGradient><mask id="brkfadem" maskUnits="userSpaceOnUse" x="0" y="0" width="${brk.scrollWidth}" height="${brk.scrollHeight}"><rect x="0" y="0" width="${brk.scrollWidth}" height="${brk.scrollHeight}" fill="url(#brkfade)"/></mask></defs>`+paths+elim;
brk.appendChild(svg);
playBrk(svg);return;}
svg.innerHTML=paths;brk.appendChild(svg);
playBrk(svg);}
/* Seed hover pathing: a pending seed has no previous team, so the primary
   glowing line traces the incoming feed (QF winners converging on its match)
   into the hovered slot; win/loss branches follow the host match's routes. */
const BRK_SEED_MATCH={1:'Round 2 Match 1',2:'Round 2 Match 2',3:'Round 1 Match 1',6:'Round 1 Match 1',4:'Round 1 Match 2',5:'Round 1 Match 2'};
function showSeedPaths(brk,seedRow){clearTeamPaths(brk);
const card=seedRow.closest('[data-brk]');if(!card)return;
const round=card.dataset.brk,q=rk=>brk.querySelector('[data-brk="'+rk+'"]');
const P=brkRect(brk,seedRow);
const svg=document.createElementNS('http://www.w3.org/2000/svg','svg');
svg.setAttribute('class','brk-hover');svg.setAttribute('width',brk.scrollWidth);svg.setAttribute('height',brk.scrollHeight);
let paths='';
const add=(d,stroke,w,cls)=>{paths+=`<path d="${d}" pathLength="1" stroke="${stroke}" stroke-width="${w}" class="${cls}"/>`;};
const INK='rgba(242,241,236,.85)',MUT='rgba(166,163,155,.6)';
(BRK_PREV[round]||[]).forEach(rk=>{const c=q(rk);if(!c)return;
const S=brkRect(brk,c);
add(brkCurve(S.right,S.cy,P.left,P.cy),INK,2.5,'prev');});
(BRK_NEXT[round]||[]).forEach(rk=>{const t=q(rk);if(!t)return;
if(rk==='Grand Finals'){const G=gfSlotY(brk,q,round);if(!G)return;
add(brkCurve(P.right,P.cy,brkRect(brk,t).left,G.y),INK,2,'win');return;}
const T=brkRect(brk,t);
add(brkCurve(P.right,P.cy,T.left,T.cy),INK,2,'win');});
const lossTo=BRK_LOSS[round];
if(lossTo){const t=q(lossTo);if(t){const T=brkRect(brk,t);
add(brkCurve(P.right,P.cy,T.left,T.cy),MUT,2,'loss');}}
else if(round!=='Grand Finals'){const yB=brk.scrollHeight;
const elim=`<path d="M${P.cx},${P.cy} C${P.cx},${P.cy+46} ${P.cx},${yB-70} ${P.cx},${yB}" pathLength="1" stroke="${MUT}" stroke-width="2" class="loss" mask="url(#brkfadem)"/>`;
svg.innerHTML=`<defs><linearGradient id="brkfade" x1="0" y1="0" x2="0" y2="1"><stop offset="0" stop-color="#fff" stop-opacity=".7"/><stop offset="1" stop-color="#fff" stop-opacity="0"/></linearGradient><mask id="brkfadem" maskUnits="userSpaceOnUse" x="0" y="0" width="${brk.scrollWidth}" height="${brk.scrollHeight}"><rect x="0" y="0" width="${brk.scrollWidth}" height="${brk.scrollHeight}" fill="url(#brkfade)"/></mask></defs>`+paths+elim;
brk.appendChild(svg);
playBrk(svg);return;}
svg.innerHTML=paths;brk.appendChild(svg);
playBrk(svg);}
function clearTeamPaths(scope){(scope||document).querySelectorAll('svg.brk-hover').forEach(s=>s.remove());}
document.addEventListener('pointerover',e=>{
const brk=e.target.closest?e.target.closest('.brk'):null;if(!brk)return;
const row=e.target.closest?e.target.closest('.brk-team[data-brkt]'):null;
const seed=e.target.closest?e.target.closest('.brk-team[data-seed]'):null;
if(row){if(BrkHover.row===row&&BrkHover.el===brk)return;setBrkHover(brk,row);showTeamPaths(brk,row);}
else if(seed){if(BrkHover.row===seed&&BrkHover.el===brk)return;setBrkHover(brk,seed);showSeedPaths(brk,seed);}});
document.addEventListener('pointerout',e=>{if(e.pointerType&&e.pointerType!=='mouse')return;
const brk=e.target.closest?e.target.closest('.brk'):null;if(!brk)return;
const to=e.relatedTarget&&e.relatedTarget.closest?e.relatedTarget.closest('.brk-team[data-brkt],.brk-team[data-seed]'):null;
if(!to||to!==BrkHover.row){clearBrkHover();clearTeamPaths(brk);}});
document.addEventListener('pointerdown',e=>{if(e.target.closest&&(e.target.closest('.brk-team[data-brkt]')||e.target.closest('.brk-team[data-seed]')))return;
clearBrkHover();clearTeamPaths(document);});
let brkResizeWired=false;
function wireBracket(){document.querySelectorAll('.brk').forEach(svgOverlay);
const board=document.getElementById('board');
if(board&&window.ResizeObserver&&!wireBracket._ro){wireBracket._ro=new ResizeObserver(()=>{document.querySelectorAll('.brk').forEach(svgOverlay);});wireBracket._ro.observe(board);}
if(!brkResizeWired){brkResizeWired=true;let t=null;
window.addEventListener('resize',()=>{clearTimeout(t);t=setTimeout(()=>document.querySelectorAll('.brk').forEach(svgOverlay),150);});}}
function gameMvp(pa,pb,wcode){const pl=[...(pa||[]),...(pb||[])];const pool=wcode?pl.filter(r=>r.team===wcode):pl;const cands=pool.length?pool:pl;let best=null,bk=null;
cands.forEach(r=>{const k=r.kda??(((r.kills??r.kill??0)+(r.assists??r.assist??0))/Math.max(1,(r.deaths??r.death??0)));const key=[k,(r.kills??r.kill??0),(r.gold??0)];
if(!best||key[0]>bk[0]||(key[0]===bk[0]&&(key[1]>bk[1]||(key[1]===bk[1]&&key[2]>bk[2])))){best=r;bk=key;}});return best;}
function gameSection(g,plistA,plistB,bansA,bansB,live,active){
const sec=durSec(g.duration_str||g.duration);const dur=g.duration_str||g.duration||'';
const wn=winName(g);const gm=gameMvp(plistA,plistB,wn);
const wonA=wn?wn===g.team_a:null,wonB=wn?wn===g.team_b:null;
const bans=(bansA.length||bansB.length)?`<div class="sb-bans"><span>BAN ${esc(g.team_a)}: ${bansA.map(esc).join(', ')||'–'}</span><span>BAN ${esc(g.team_b)}: ${bansB.map(esc).join(', ')||'–'}</span></div>`:'';
return `<div class="sb-game" data-g="${g.game_no}"${active?'':' hidden'}>`
+`<div class="sb-ghead"><h4>Game ${g.game_no}</h4><span>${esc(g.team_a)} ${g.team_a_kills} : ${g.team_b_kills} ${esc(g.team_b)} · ${esc(dur)}${wn?` · <b class="sb-win">${esc(wn)} won</b>`:''}${gm?` · <span class="gmvp">MVP ${esc(gm.player)}</span>`:''}</span></div>`
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
const tabs=gs.map((g,i)=>`<button data-gtab="${g.game_no}"${wtab(g)} aria-pressed="${isActive(g,i)?'true':'false'}">Game ${g.game_no}</button>`).join('');
const body=`<div class="sb-tabs" role="group" aria-label="Games">${tabs}</div>`+gs.map((g,i)=>{
const pa=rows(id,g.game_no).filter(r=>r.team===g.team_a),pb=rows(id,g.game_no).filter(r=>r.team===g.team_b);
return gameSection(g,pa,pb,[],[],false,isActive(g,i));}).join('');
const initG=wantGame!=null?(gs.find(g=>String(g.game_no)===wantGame)||{}):(gs[0]||{});
const initW=winName(initG)||'';
dSet(m.team_a+' vs '+m.team_b,'#'+id+' · '+(m.date||''),body,
initW&&markSrc(initW)?{src:markSrc(initW),side:initW===m.team_a?'l':(initW===m.team_b?'r':'l')}:null);
try{
const ctl=new AbortController();const tmr=setTimeout(()=>ctl.abort(),15000);
const r=await fetch('https://mpl.mlbbhub.com/api/v1/id/match/'+encodeURIComponent(id),{signal:ctl.signal});
clearTimeout(tmr);
if(!r.ok)return;const d=await r.json();if(!d.games||!d.games.length)return;
const firstGame=wantGame!=null?wantGame:String(d.games[0].game);
const t2=d.games.map((g,i)=>`<button data-gtab="${g.game}" data-wtab="${esc(winName(g)||'')}" data-wside="${(winName(g)||'')===g.team_a?'l':'r'}" aria-pressed="${String(g.game)===String(firstGame)?'true':'false'}">Game ${g.game}</button>`).join('');
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
const HUB='https://mpl.mlbbhub.com/api/v1/id';
function normLive(d){const games=[],pros=[],bans=[];
(d.games||[]).forEach(g=>{const sec=durSec(g.duration);
games.push({match_detail_id:String(d.match_id),game_no:g.game,team_a:g.team_a,team_b:g.team_b,team_a_kills:g.team_a_kills,team_b_kills:g.team_b_kills,winner:g.winner,duration_str:g.duration,duration_sec:sec,team_a_side:g.team_a_side,team_b_side:g.team_b_side,vod_url:g.vod_url});
(g.bans_a||[]).forEach(h=>{if(h)bans.push({match_detail_id:String(d.match_id),game_no:g.game,side:'A',hero:h});});
(g.bans_b||[]).forEach(h=>{if(h)bans.push({match_detail_id:String(d.match_id),game_no:g.game,side:'B',hero:h});});
(g.players||[]).forEach(p=>{const eq=u=>itemRef(u);
pros.push({match_detail_id:String(d.match_id),game_no:g.game,team:p.team,player:p.player,lane:p.lane||null,hero:p.hero,hero_image:p.hero_image||null,
kills:p.kill??0,deaths:p.death??0,assists:p.assist??0,kda:p.kda??0,gold:p.gold??0,
gold_per_min:(sec&&p.gold!=null)?Math.round(p.gold/(sec/60)):0,
hero_damage:p.hero_damage??0,damage_taken:p.damage_taken??0,tower_damage:p.tower_damage??0,
e:((/emblem\/(\d+)\.png/.exec(p.emblem||''))||[])[1]||null,
t:(p.talents||[]).map(u=>((/rune\/(\d+)\.png/.exec(u||''))||[])[1]).filter(Boolean),
i:(p.items||[]).map(eq).filter(Boolean)});});});
return {games,pros,bans};}
function buildPool(pros){const m={};pros.forEach(r=>{(m[r.player]=m[r.player]||[]).push(r.hero);});
const o={};Object.entries(m).forEach(([p,hs])=>{const c={};hs.forEach(h=>{c[h]=(c[h]||0)+1;});o[p]=Object.entries(c).sort((a,b)=>b[1]-a[1]).slice(0,6);});return o;}
const TEAMCANON={'rrq hoshi':'rrq','geek fam id':'geek','geek fam':'geek','bigetron by vitality':'btr','team liquid id':'tlid','natus vincere':'navi','alter ego':'ae','dewa united esports':'dewa','onic':'onic','evos':'evos','rrq':'rrq','geek':'geek','btr':'btr','tlid':'tlid','navi':'navi','ae':'ae','dewa':'dewa'};
const canonT=t=>{const n=String(t||'').toLowerCase().replace(/\s+/g,' ').trim();return TEAMCANON[n]||TEAMCANON[n.replace(/esports/g,'').trim()]||n;};
function parseMvps(wt){const out=[];const blocks=wt.split(/\|M\d+=\{\{Match/);
for(let i=1;i<blocks.length;i++){const b=blocks[i];
const t1=(/opponent1=\{\{TeamOpponent\|([^\}\|\n]+)/.exec(b)||[])[1]||'';
const t2=(/opponent2=\{\{TeamOpponent\|([^\}\|\n]+)/.exec(b)||[])[1]||'';
const date=((/\|date=([^\n]+)/.exec(b)||[])[1]||'').replace('{{abbr/ICT}}','ICT').slice(0,60);
const mvp=((/\|mvp=([^\n\|]*)/.exec(b)||[])[1]||'').trim();
out.push({t1:t1.trim(),t2:t2.trim(),date:date,mvp:mvp});}
return out;}
async function fetchMvps(){const q='action=parse&page='+encodeURIComponent('MPL/Indonesia/Season_18/Regular_Season')+'&prop=wikitext&format=json&origin=*';
const timeout=new Promise((_,rej)=>setTimeout(()=>rej(new Error('mvp-timeout')),25000));
const req=fetch('https://liquipedia.net/mobilelegends/api.php?'+q).then(r=>{if(!r.ok)throw new Error('liquipedia');return r.json();});
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
const ids=[...new Set(DATA.matches.map(m=>m.match_detail_id))];
const allGames=[],allPros=[],allBans=[];let done=0,fails=0;const q=[...ids];const okIds=new Set();
upd.textContent='games 0/'+ids.length+'…';
await Promise.all(Array.from({length:6},()=> (async()=>{while(q.length){const id=q.pop();
try{const d=await fetch(HUB+'/match/'+encodeURIComponent(id)).then(r=>{if(!r.ok)throw new Error(id);return r.json();});
const n=normLive(d);allGames.push(...n.games);allPros.push(...n.pros);allBans.push(...n.bans);okIds.add(String(id));}catch(e){fails++;}
done++;upd.textContent='games '+done+'/'+ids.length+'…';}})()));
DATA.games=allGames;DATA.players=allPros;DATA.hero_pool=buildPool(allPros);
DATA.bans=[...allBans,...(DATA.bans||[]).filter(b=>!okIds.has(String(b.match_detail_id)+':'+String(b.game_no)))];
const AH2=(window.ASSETS||{}).heroes||{},AI2=(window.ASSETS||{}).items||{};
const newH=[...new Set(allPros.map(p=>p.hero).filter(h=>h&&!Object.prototype.hasOwnProperty.call(AH2,h)))];
const newI=[...new Set(allPros.flatMap(p=>p.i||[]).filter(x=>x&&!Object.prototype.hasOwnProperty.call(AI2,x)))];
const newMsg=(newH.length||newI.length)?` · ${newH.length+newI.length} new art via live CDN (persist: python tools/fetch_assets.py)`:'';
try{localStorage.setItem('s18db',JSON.stringify({t:Date.now(),schedule:ms,standings:st,season:ps,players:allPros,games:allGames,bans:DATA.bans,heroPool:DATA.hero_pool,matches:DATA.matches,heroes:DATA.heroes,playoffs:DATA.playoffs}));}catch(e){upd.textContent='updated '+new Date().toLocaleTimeString()+' (not cached: storage full)';render();btn.disabled=false;btn.textContent=old;return;}
upd.textContent='updated '+new Date().toLocaleTimeString()+' · '+allGames.length+' games · '+mvpN+' MVPs'+(fails?' · '+fails+' failed':'')+newMsg;setNet();render();
}catch(e){upd.textContent='refresh failed — offline? showing last snapshot';setNet();}
btn.disabled=false;btn.textContent=old;}
document.getElementById('refresh').onclick=refreshDB;
try{const c=JSON.parse(localStorage.getItem('s18db')||'null');
if(c&&c.schedule&&c.schedule.length){DATA.schedule=c.schedule;if(c.standings)DATA.standings=c.standings;if(c.season)DATA.season=c.season;
if(c.players&&c.players.length){DATA.players=c.players;}if(c.games&&c.games.length){DATA.games=c.games;}
if(c.bans&&c.bans.length){DATA.bans=c.bans;}
if(c.heroPool)DATA.hero_pool=c.heroPool;if(c.matches&&c.matches.length){DATA.matches=c.matches;}
if(c.heroes&&c.heroes.length){DATA.heroes=c.heroes;}if(c.playoffs){DATA.playoffs=c.playoffs;}
document.getElementById('upd').textContent='snapshot '+new Date(c.t).toLocaleString();}}catch(e){}
render();
