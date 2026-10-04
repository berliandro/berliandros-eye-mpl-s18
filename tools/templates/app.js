const DATA = __DATA__;
const TEAMS = ["AE", "BTR", "DEWA", "EVOS", "GEEK", "NAVI", "ONIC", "RRQ", "TLID"];
const TEAM_LOGOS = {ae:"assets/teams/ae.png",btr:"assets/teams/btr.png",dewa:"assets/teams/dewa.png",evos:"assets/teams/evos.png",geek:"assets/teams/geek.png",navi:"assets/teams/navi.png",onic:"assets/teams/onic.png",rrq:"assets/teams/rrq.png",tlid:"assets/teams/tlid.png"};
const logoOf = t => TEAM_LOGOS[String(t||'').toLowerCase()] || '';
const IMG_HIDE = 'onerror="this.style.visibility=\'hidden\'"';
function eqId(u){const m=/(?:equipment|equip)\/(\d+)\.png/.exec(u||'');return m?m[1]:'';}
function itemRef(u){const id=eqId(u);if(id)return id;if(u&&u.indexOf('scoregg.com')>-1)return String(u).split('?')[0];return null;}
function imgSlot(el){const s=document.createElement('span');s.className='slot-miss';s.title=el.alt||'item';s.textContent=el.dataset.eq||'?';el.replaceWith(s);}
const S = {view:'overview',q:'',team:'',sort:'kda',lane:'',compact:false,layout:'grid',ov:null,mlimit:24,plimit:24};
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
document.getElementById('selQ').oninput=renderOvSel;
document.getElementById('selT').onchange=renderOvSel;
document.getElementById('selL').onchange=renderOvSel;
let lastY=0,scrollTick=false;
window.addEventListener('scroll',()=>{if(scrollTick)return;scrollTick=true;requestAnimationFrame(()=>{scrollTick=false;
const y=window.scrollY,hdr=document.querySelector('header');
if(window.innerWidth>640||!hdr){if(hdr)hdr.classList.remove('navhide');}
else if(y>lastY&&y>160){hdr.classList.add('navhide');}else if(y<lastY){hdr.classList.remove('navhide');}
lastY=y;});},{passive:true});
dlg.addEventListener('close',()=>{if(lastFocus)lastFocus.focus();});
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
const sec=(title,list)=>{if(!list.length)return '';return `<div class="pin" style="grid-column:1/-1"><div class="body"><div class="kicker">Bracket</div><h3 style="margin:.25em 0">${title} (${list.length})</h3></div></div>`+list.map(m=>{const done=m.match_detail_id&&m.status==='completed';
const gmvp=mvpById[String(m.match_detail_id)]||'';
return `<div class="pin mpin"><div class="body"><div class="kicker">${esc(m.date||'')} · ${esc(m.status||'')}</div><div class="mteams"><div class="mt"><img src="${TICON(m.team_a)}" alt="" loading="lazy" ${IMG_HIDE}><span>${esc(m.team_a)}</span></div><div class="score">${m.score_a??'–'} : ${m.score_b??'–'}</div><div class="mt"><img src="${TICON(m.team_b)}" alt="" loading="lazy" ${IMG_HIDE}><span>${esc(m.team_b)}</span></div></div>${gmvp?`<div class="mmvp-grid">MVP · <b>${esc(gmvp)}</b></div>`:''}<div class="mmeta"><span class="tag">${done?('Detail #'+esc(m.match_detail_id)):esc(m.status||'upcoming')}</span></div></div><div class="actions">${done?`<button class="primary" data-m="${esc(m.match_detail_id)}">Scoreboard</button>`:`<button class="ghost" disabled>Soon</button>`}</div></div>`;}).join('');};
const regAll=ms.filter(m=>!isPO(m)),poAll=ms.filter(isPO);
const reg=regAll.slice(0,S.mlimit),po=poAll.slice(0,S.plimit);
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
let mh=`<div class="pin"><div class="lscroll"><div class="mhead"><span>Date</span><span>Match</span><span>Status</span><span>MVP</span><span></span></div>`;
if(regAll.length)mh+=`<div class="msec">A · Regular Season · ${reg.length}/${regAll.length}</div>`+reg.map(mrow).join('')+mfoot('reg',reg.length,regAll.length);
if(poAll.length)mh+=`<div class="msec">B · Playoffs · ${po.length}/${poAll.length}</div>`+po.map(mrow).join('')+mfoot('po',po.length,poAll.length);
mh+=`</div></div>`;
out.push(mh);}
else{out.push(sec('Regular Season',reg)+sec('Playoffs — TBD',po));
if(ms.filter(m=>!isPO(m)).length>S.mlimit)out.push(`<div class="pin"><div class="body" style="text-align:center"><p>Showing ${S.mlimit} of ${ms.filter(m=>!isPO(m)).length} regular-season matches</p><div class="actions"><button class="primary" data-more="24">Show more</button></div></div></div>`);}}
if(S.view==='stats'){const st=[...DATA.standings].sort((a,b)=>a.rank-b.rank);
out.push(`<div class="pin"><div class="body"><div class="kicker">Board</div><h3>Standings</h3><table><tr><th>#</th><th>Team</th><th>Pts</th><th>W-L</th></tr>${st.map(s=>{const slug=(s.team_slug||s.team_name||'').toLowerCase();return `<tr><td>${s.rank}</td><td><img src="${TICON(slug)}" alt="" loading="lazy" style="width:20px;height:20px;object-fit:contain;vertical-align:-5px" ${IMG_HIDE}> ${esc(s.team_name)}</td><td>${s.match_point}</td><td>${s.match_win}-${s.match_lose}</td></tr>`;}).join('')}</table></div></div>`);
const top=[...DATA.season].filter(s=>+s.total_games>=5).sort((a,b)=>+b.avg_kda-+a.avg_kda).slice(0,10);
out.push(`<div class="pin"><div class="body"><div class="kicker">Leaders</div><h3>Top KDA</h3><table><tr><th>Player</th><th>KDA</th><th>K/D/A</th></tr>${top.map(s=>{const u=PICON(s.player);const tm=s.team_slug?`<img src="${TICON(s.team_slug)}" alt="" loading="lazy" style="width:18px;height:18px;object-fit:contain;vertical-align:-4px" onerror="this.remove()">`:'';return `<tr><td>${u?`<img src="${esc(u)}" alt="" loading="lazy" style="width:24px;height:24px;border-radius:8px;object-fit:cover;vertical-align:-6px" onerror="this.remove()"> `:''}${esc(s.player)} ${tm}</td><td>${s.avg_kda}</td><td>${s.total_kills}/${s.total_deaths}/${s.total_assists}</td></tr>`;}).join('')}</table></div></div>`);
out.push(`<div class="pin"><div class="body"><div class="kicker">History</div><h3>Series MVPs</h3><table><tr><th>Date</th><th>Match</th><th>MVP</th></tr>${[...(DATA.matches||[])].filter(m=>m.liq_mvp).sort((a,b)=>String(a.iso_datetime||'').localeCompare(String(b.iso_datetime||''))).map(m=>`<tr><td>${esc(m.iso_date||m.date||'')}</td><td>${esc(m.team_a)} ${m.score_a??''}:${m.score_b??''} ${esc(m.team_b)}</td><td>${esc(m.liq_mvp)}</td></tr>`).join('')}</table></div></div>`);}
board.innerHTML=out.join('')||'';emptyEl.hidden=out.length>0;countEl.textContent=out.length+' pins';
board.querySelectorAll('.pin').forEach(p=>io.observe(p));
board.querySelectorAll('[data-p]').forEach(b=>b.onclick=()=>showP(b.dataset.p));
const ovb=document.getElementById('ovPick');if(ovb)ovb.onclick=openOvSel;
board.querySelectorAll('.lrow').forEach(r=>{r.style.cursor='pointer';r.onclick=()=>showP(r.querySelector('b').textContent);});
board.querySelectorAll('[data-m]').forEach(b=>b.onclick=()=>showM(b.dataset.m));
board.querySelectorAll('[data-more]').forEach(b=>b.onclick=()=>{const n=+b.dataset.more||24;if(b.dataset.sec==='po')S.plimit+=n;else S.mlimit+=n;render();});
wireCharts();}
function normId(s){return String(s||'').toLowerCase().replace(/[^a-z0-9]/g,'');}
function offOf(n){const m={};DATA.season.forEach(s=>{m[String(s.player||'').toLowerCase()]=s;});
const GALIAS={hijumee:'dalvin',arfy:'dingarai',yazukee:'affan',alekk:'alexander',kevinn:'kevin',maykids:'maykidss',kennzyskie:'kennzyyskie'};
const l=String(n||'').toLowerCase();return m[l]||m[GALIAS[l]||'']||null;}
const MVPALIAS={jooooo:'Kevin',sutsujin:'Arthur',coolfire:'Joshuaa',jizeezeze:'Jiizee',killuaa:'Killuaa',maykids:'Maykids',egatzy:'EgaTzy',qinn:'Qinn',nnael:'Nnael',moreno:'Morenooo',morenooo:'Morenooo',kelra:'Kelra',kairi:'Kairi',arfy:'Dingarai',hijumee:'Dalvin',hazle:'Hazle',nino:'Nino',shogun:'Shogun',rendyy:'Rendyy',alberttt:'Alberttt',karss:'Karss',sanz:'S A N Z',aboy:'A B O Y'};
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
const rows=DATA.players.filter(r=>r.player===name).map(r=>({r:r,info:gameInfo(r)}))
.sort((a,b)=>String(a.info.iso).localeCompare(String(b.info.iso)));
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
return `<tr><td><span class="hcell">${hi?`<img src="${esc(hi)}" alt="" loading="lazy" onerror="this.remove()">`:''}${esc(h)}</span></td><td>${o.n}</td><td><div style="display:flex;gap:6px;align-items:center"><span class="wrbar"><i style="width:${o.n?Math.round(o.w/o.n*100):0}%"></i></span>${o.n?Math.round(o.w/o.n*100):0}%</div></td><td>${(o.k/Math.max(1,o.n)).toFixed(1)}/${(o.d/Math.max(1,o.n)).toFixed(1)}/${(o.a/Math.max(1,o.n)).toFixed(1)}</td><td>${Math.round(o.gpm/Math.max(1,o.n))}</td></tr>`;}).join('');
const sides={};rows.forEach(x=>{const sd=(x.info.side||'').toLowerCase()||'unknown';(sides[sd]=sides[sd]||{w:0,n:0}).n++;if(x.info.won===true)sides[sd].w++;});
const sideTbl=Object.entries(sides).map(([sd,o])=>`<tr><td style="text-transform:capitalize">${esc(sd)} side</td><td>${o.n}</td><td>${o.n?Math.round(o.w/o.n*100):0}%</td></tr>`).join('');
const opps={};rows.forEach(x=>{const o=x.info.opp||'?';(opps[o]=opps[o]||{w:0,n:0}).n++;if(x.info.won===true)opps[o].w++;});
const oppTbl=Object.entries(opps).sort((a,b)=>b[1].n-a[1].n).map(([o,v])=>`<tr><td><img src="${TICON(o)}" alt="" loading="lazy" style="width:20px;height:20px;object-fit:contain;vertical-align:-5px" onerror="this.remove()"> ${esc(o)}</td><td>${v.n}</td><td>${v.w}-${v.n-v.w}</td></tr>`).join('');
const itemC={};rows.forEach(x=>{const ids=x.r.i&&x.r.i.length?x.r.i:((x.r.items||[]).map(u=>eqId(u)).filter(Boolean));ids.forEach(id=>{itemC[id]=(itemC[id]||0)+1;});});
const itemGrid=Object.entries(itemC).sort((a,b)=>b[1]-a[1]).slice(0,12).map(([id,c])=>{const src=A.items&&A.items[id];
return `<span class="itemcell">${src?`<img src="${esc(src)}" alt="" loading="lazy" onerror="this.remove()">`:`<span class="slot-miss">${esc(id)}</span>`}<span>×${c}</span></span>`;}).join('')||'<p>No item data</p>';
const embC={};rows.forEach(x=>{const id=x.r.e||(/emblem\/(\d+)\.png/.exec(x.r.emblem||'')||[])[1];if(id)embC[id]=(embC[id]||0)+1;});
const talC={};rows.forEach(x=>{const ids=x.r.t&&x.r.t.length?x.r.t:(x.r.talents||[]).map(u=>/rune\/(\d+)\.png/.exec(u||'')?.[1]).filter(Boolean);ids.forEach(id=>{talC[id]=(talC[id]||0)+1;});});
const embHtml=Object.entries(embC).map(([id,c])=>{const src=A.emblems&&A.emblems[id];return src?`<img src="${esc(src)}" alt="" title="×${c}" loading="lazy" style="width:26px;height:26px;border-radius:50%;border:1px solid var(--line)" onerror="this.remove()">`:'';}).join('');
const talHtml=Object.entries(talC).sort((a,b)=>b[1]-a[1]).map(([id,c])=>{const src=A.runes&&A.runes[id];return src?`<img src="${esc(src)}" alt="" title="×${c}" loading="lazy" style="width:22px;height:22px;border-radius:50%;border:1px solid var(--line)" onerror="this.remove()">`:'';}).join('');
const mvps=(DATA.matches||[]).filter(m=>{const v=String(m.liq_mvp||'').toLowerCase();return v&&(v===name.toLowerCase()||normId(v)===normId(name)||(MVPALIAS[v]||'')===name);});
const mvpHtml=mvps.length?mvps.map(m=>{const sc=(DATA.schedule||[]).find(s=>String(s.match_detail_id)===String(m.match_detail_id))||{};return `<tr><td>${esc(sc.date||sc.iso_date||'')}</td><td>${esc(m.team_a)} vs ${esc(m.team_b)}</td></tr>`;}).join(''):'<tr><td colspan="2">No recorded MVPs</td></tr>';
const log=rows.map(x=>`<tr><td class="mono">${esc(x.info.date||'')}</td><td>G${x.r.game_no}</td><td>vs ${esc(x.info.opp||'')}</td><td>${esc(x.r.hero||'')}</td><td>${x.r.kills??x.r.kill}/${x.r.deaths??x.r.death}/${x.r.assists??x.r.assist}</td><td>${x.info.won===null?'–':(x.info.won?'W':'L')}</td></tr>`).join('');
const kp=s.kill_participation||'—';
return `<div class="pin ov"><div class="body"><div class="phead">${u?`<img class="ppic" src="${esc(u)}" alt="" onerror="this.remove()">`:''}<div><div class="kicker">${esc(g.team||'')} · ${esc(g.lane||'—')}</div><h3 style="margin:0">${esc(name)}</h3></div><img class="tlogo" src="${TICON(g.team)}" alt="" loading="lazy" onerror="this.remove()"><button class="ghost" id="ovPick" style="margin-left:auto;border:1px solid var(--line);background:transparent;color:var(--ink);border-radius:8px;padding:8px 14px;cursor:pointer;font-weight:600">Player ▾</button></div>`
+`<div class="tiles"><div class="tile"><b>${g.gp||0}</b><span>Games</span></div><div class="tile"><b>${(g.avgkda||0).toFixed(2)}</b><span>Avg KDA</span></div><div class="tile"><b>${wins}-${scored.length-wins}</b><span>Game W-L</span></div><div class="tile"><b>${wr}%</b><span>Game WR</span></div><div class="tile"><b>${mw}-${ml}</b><span>Match W-L</span></div><div class="tile"><b>${mwr}%</b><span>Match WR</span></div><div class="tile"><b>${fmtDur(avgD)}</b><span>Avg game</span></div><div class="tile"><b>${esc(String(kp))}</b><span>Kill part.</span></div></div>`
+`<div class="ovgrid"><div class="ovsec"><h4>KDA trend per game</h4>${trendChart(rows.map(x=>{const k=x.r.kills??x.r.kill??0,d=x.r.deaths??x.r.death??0,a=x.r.assists??x.r.assist??0;return {v:(k+a)/Math.max(1,d),date:x.info.date||'',opp:x.info.opp||'',hero:x.r.hero||'',kda:((k+a)/Math.max(1,d)).toFixed(2),won:x.info.won};}))}<p>${rows.length} scored games · total gold ${(totG/1000).toFixed(0)}k · hero dmg ${(totD/1000).toFixed(0)}k · taken ${(totT/1000).toFixed(0)}k · tower ${(totTw/1000).toFixed(0)}k</p></div>`
+`<div class="ovsec"><h4>Hero pool (${heroRows.length} heroes)</h4><table><tr><th>Hero</th><th>GP</th><th>Win%</th><th>Avg K/D/A</th><th>GPM</th></tr>${heroTbl}</table></div></div>`
+`<div class="ovgrid"><div class="ovsec"><h4>Hero win rate</h4><table>${heroRows.map(o=>`<tr><td>${esc(o.h)}</td><td><div style="display:flex;gap:6px;align-items:center"><span class="wrbar"><i style="width:${o.wr}%"></i></span>${o.wr}%</div></td></tr>`).join('')}</table></div>`
+`<div class="ovsec"><h4>Sides</h4><table><tr><th>Side</th><th>GP</th><th>Win%</th></tr>${sideTbl}</table></div></div>`
+`<div class="ovgrid"><div class="ovsec"><h4>Top items</h4><div class="itemgrid">${itemGrid}</div></div>`
+`<div class="ovsec"><h4>Emblems &amp; talents</h4><div class="itemgrid">${embHtml}${talHtml}</div></div></div>`
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
function showP(n){const r=DATA.players.filter(x=>x.player===n);const g=agg().find(o=>o.player===n)||{};
const A=window.ASSETS||{heroes:{}};
const bh={};r.forEach(x=>{(bh[x.hero]=bh[x.hero]||[]).push(x);});
const t=Object.entries(bh).map(([h,rs])=>{const hg=rs.reduce((s,x)=>s+(x.gold_per_min||0),0)/rs.length;
const ak=rs.reduce((s,x)=>s+x.kills,0)/rs.length,ad=rs.reduce((s,x)=>s+x.deaths,0)/rs.length,aa=rs.reduce((s,x)=>s+x.assists,0)/rs.length;
const akda=rs.reduce((s,x)=>s+(+x.kda||0),0)/rs.length;
const hi=(A.heroes&&A.heroes[h])||'';return `<tr><td><span class="hcell">${hi?`<img src="${esc(hi)}" alt="" loading="lazy" onerror="this.remove()">`:''}${esc(h)}</span></td><td>${rs.length}</td><td>${akda.toFixed(2)}</td><td>${ak.toFixed(1)}</td><td>${ad.toFixed(1)}</td><td>${aa.toFixed(1)}</td><td>–</td><td>–</td><td>${hg.toFixed(0)}</td></tr>`;}).join('');
const u=PICON(n);
openD(n,(g.team||'')+' · '+(g.lane||''),`<div class="pdhead">${u?`<img src="${esc(u)}" alt="" onerror="this.remove()">`:''}<div><div class="kicker">${esc(g.team||'')} · ${esc(g.lane||'—')}</div><div style="font-family:var(--font-display);font-size:19px;font-weight:700">${esc(n)}</div></div></div><div class="tiles"><div class="tile"><b>${g.gp||r.length}</b><span>Games</span></div><div class="tile"><b>${(g.avgkda||0).toFixed(2)}</b><span>Avg KDA</span></div><div class="tile"><b>${(g.avgg||0).toFixed(0)}</b><span>Avg gold/min</span></div><div class="tile"><b>${g.k||0}/${g.d||0}/${g.a||0}</b><span>Total K / D / A</span></div></div><div class="lscroll"><table style="min-width:560px"><tr><th>Hero</th><th>GP</th><th>AVG KDA</th><th>AVG K</th><th>AVG D</th><th>AVG A</th><th title="Under development — no official ID source publishes this yet">MANIAC *</th><th title="Under development — no official ID source publishes this yet">SAVAGE *</th><th>GPM</th></tr>${t}</table></div><div class="mono" style="font-family:var(--font-mono);font-size:10.5px;color:var(--muted);margin-top:6px">* MANIAC / SAVAGE tracking is under development — no official MPL ID source publishes these counts yet.</div>`);}
function durSec(s){const m=/(\d+):(\d+)/.exec(s||'');return m?(+m[1])*60+(+m[2]):0;}
function normPl(r,sec){const kills=r.kill??r.kills??0,deaths=r.death??r.deaths??0,assists=r.assist??r.assists??0;
const gpm=r.gold_per_min??((sec&&r.gold!=null)?Math.round(r.gold/(sec/60)):null);return Object.assign({},r,{kills,deaths,assists,gpm});}
function aid(u,re){const m=re.exec(u||'');return m?m[1]:'';}
function teamBlock(code,kills,plist,sec,side,flip){
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
return `<div class="sb-team${flip?' flip':''}${pk?' '+pk:''}"><div class="sb-thead"><img src="${logoOf(code)}" alt="" ${IMG_HIDE}><b>${esc(code)}</b><span class="k">${kills} kills</span></div>${prow}</div>`;}
function winName(g){return g.winner==='team_a'?g.team_a:(g.winner==='team_b'?g.team_b:(g.winner||''));}
function gameMvp(pa,pb,wcode){const pl=[...(pa||[]),...(pb||[])];const pool=wcode?pl.filter(r=>r.team===wcode):pl;const cands=pool.length?pool:pl;let best=null,bk=null;
cands.forEach(r=>{const k=r.kda??(((r.kills??r.kill??0)+(r.assists??r.assist??0))/Math.max(1,(r.deaths??r.death??0)));const key=[k,(r.kills??r.kill??0),(r.gold??0)];
if(!best||key[0]>bk[0]||(key[0]===bk[0]&&(key[1]>bk[1]||(key[1]===bk[1]&&key[2]>bk[2])))){best=r;bk=key;}});return best;}
function gameSection(g,plistA,plistB,bansA,bansB,live,active){
const sec=durSec(g.duration_str||g.duration);const dur=g.duration_str||g.duration||'';
const wn=winName(g);const gm=gameMvp(plistA,plistB,wn);
const bans=(bansA.length||bansB.length)?`<div class="sb-bans"><span>BAN ${esc(g.team_a)}: ${bansA.map(esc).join(', ')||'–'}</span><span>BAN ${esc(g.team_b)}: ${bansB.map(esc).join(', ')||'–'}</span></div>`:'';
return `<div class="sb-game" data-g="${g.game_no}"${active?'':' hidden'}>`
+`<div class="sb-ghead"><h4>Game ${g.game_no}</h4><span>${esc(g.team_a)} ${g.team_a_kills} : ${g.team_b_kills} ${esc(g.team_b)} · ${esc(dur)} · ${esc(wn)} won${gm?` · <span class="gmvp">MVP ${esc(gm.player)}</span>`:''}</span></div>`
+bans+`<div class="sb-duo">`+teamBlock(g.team_a,g.team_a_kills,plistA,sec,g.team_a_side,'')+teamBlock(g.team_b,g.team_b_kills,plistB,sec,g.team_b_side,'flip')+`</div></div>`;}
function wireTabs(){const db=document.getElementById('db');
db.querySelectorAll('[data-gtab]').forEach(b=>b.onclick=()=>{
db.querySelectorAll('[data-gtab]').forEach(x=>x.setAttribute('aria-pressed',x===b?'true':'false'));
db.querySelectorAll('.sb-game').forEach(s=>{s.hidden=s.dataset.g!==b.dataset.gtab;});});}
async function showM(id){const m=DATA.schedule.find(x=>String(x.match_detail_id)===String(id))||{};
const gs=DATA.games.filter(g=>g.match_detail_id===id);
const tabs=gs.map((g,i)=>`<button data-gtab="${g.game_no}" aria-pressed="${i===0?'true':'false'}">Game ${g.game_no}</button>`).join('');
openD(m.team_a+' vs '+m.team_b,'#'+id+' · '+(m.date||''),`<div class="sb-tabs" role="group" aria-label="Games">${tabs}</div>`+gs.map((g,i)=>{
const pa=rows(id,g.game_no).filter(r=>r.team===g.team_a),pb=rows(id,g.game_no).filter(r=>r.team===g.team_b);
return gameSection(g,pa,pb,[],[],false,i===0);}).join(''));
wireTabs();
try{
const ctl=new AbortController();const tmr=setTimeout(()=>ctl.abort(),15000);
const r=await fetch('https://mpl.mlbbhub.com/api/v1/id/match/'+encodeURIComponent(id),{signal:ctl.signal});
clearTimeout(tmr);
if(!r.ok)return;const d=await r.json();if(!d.games||!d.games.length)return;
const t2=d.games.map((g,i)=>`<button data-gtab="${g.game}" aria-pressed="${i===0?'true':'false'}">Game ${g.game}</button>`).join('');
document.getElementById('db').innerHTML=`<div class="sb-tabs" role="group" aria-label="Games">${t2}</div>`+d.games.map((g,i)=>{
const gg={game_no:g.game,team_a:g.team_a,team_b:g.team_b,team_a_kills:g.team_a_kills,team_b_kills:g.team_b_kills,winner:g.winner,duration:g.duration,team_a_side:g.team_a_side,team_b_side:g.team_b_side};
const pa=(g.players||[]).filter(p=>p.team===g.team_a),pb=(g.players||[]).filter(p=>p.team===g.team_b);
return gameSection(gg,pa,pb,g.bans_a||[],g.bans_b||[],true,i===0);}).join('');
wireTabs();
}catch(e){}}
function openD(t,s,h){lastFocus=document.activeElement;document.getElementById('dt').textContent=t;
document.getElementById('ds').textContent=s;document.getElementById('db').innerHTML=h;dlg.showModal();}
document.addEventListener('keydown',e=>{if(e.key==='Escape'){const d2=document.getElementById('dlg2');if(d2&&d2.open)d2.close();else if(dlg.open)dlg.close();}});
document.addEventListener('keydown',e=>{if(e.key!=='Tab')return;const d=[dlg,document.getElementById('dlg2')].find(x=>x&&x.open);if(!d)return;
const f=[...d.querySelectorAll('button,input,select,[tabindex]')].filter(el=>!el.disabled&&el.offsetParent!==null);if(!f.length)return;
const first=f[0],last=f[f.length-1];
if(e.shiftKey&&document.activeElement===first){e.preventDefault();last.focus();}
else if(!e.shiftKey&&document.activeElement===last){e.preventDefault();first.focus();}});
document.getElementById('dlg2').addEventListener('close',()=>{if(lastFocus)lastFocus.focus();});
const HUB='https://mpl.mlbbhub.com/api/v1/id';
function normLive(d){const games=[],pros=[];
(d.games||[]).forEach(g=>{const sec=durSec(g.duration);
games.push({match_detail_id:String(d.match_id),game_no:g.game,team_a:g.team_a,team_b:g.team_b,team_a_kills:g.team_a_kills,team_b_kills:g.team_b_kills,winner:g.winner,duration_str:g.duration,duration_sec:sec,team_a_side:g.team_a_side,team_b_side:g.team_b_side,vod_url:g.vod_url});
(g.players||[]).forEach(p=>{const eq=u=>itemRef(u);
pros.push({match_detail_id:String(d.match_id),game_no:g.game,team:p.team,player:p.player,lane:p.lane||null,hero:p.hero,hero_image:p.hero_image||null,
kills:p.kill??0,deaths:p.death??0,assists:p.assist??0,kda:p.kda??0,gold:p.gold??0,
gold_per_min:(sec&&p.gold!=null)?Math.round(p.gold/(sec/60)):0,
hero_damage:p.hero_damage??0,damage_taken:p.damage_taken??0,tower_damage:p.tower_damage??0,
e:((/emblem\/(\d+)\.png/.exec(p.emblem||''))||[])[1]||null,
t:(p.talents||[]).map(u=>((/rune\/(\d+)\.png/.exec(u||''))||[])[1]).filter(Boolean),
i:(p.items||[]).map(eq).filter(Boolean)});});});
return {games,pros};}
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
const [ms,st,ps,mvpList]=await Promise.all([
fetchJSON(HUB+'/matches'),
fetchJSON(HUB+'/standings'),
fetchJSON(HUB+'/stats/players'),
fetchMvps().catch(()=>[])]);
DATA.schedule=ms;DATA.standings=st;DATA.season=ps;
const mvpMap=Object.fromEntries((DATA.matches||[]).map(m=>[String(m.match_detail_id),m.liq_mvp]));
DATA.matches=ms.filter(m=>/^\d+$/.test(String(m.match_detail_id||''))).map(m=>({match_detail_id:String(m.match_detail_id),schedule_id:m.match_id,team_a:m.team_a,team_b:m.team_b,score_a:m.score_a,score_b:m.score_b,date:m.date,iso_date:m.iso_date,iso_datetime:m.iso_datetime,status:m.status,winner:m.winner,vod_url:m.vod_url,match_detail_url:m.match_detail_url,liq_mvp:mvpMap[String(m.match_detail_id)]||''}));
const mvpN=applyMvps(mvpList||[]);
const ids=[...new Set(DATA.matches.map(m=>m.match_detail_id))];
const allGames=[],allPros=[];let done=0,fails=0;const q=[...ids];
upd.textContent='games 0/'+ids.length+'…';
await Promise.all(Array.from({length:6},()=> (async()=>{while(q.length){const id=q.pop();
try{const d=await fetch(HUB+'/match/'+encodeURIComponent(id)).then(r=>{if(!r.ok)throw new Error(id);return r.json();});
const n=normLive(d);allGames.push(...n.games);allPros.push(...n.pros);}catch(e){fails++;}
done++;upd.textContent='games '+done+'/'+ids.length+'…';}})()));
DATA.games=allGames;DATA.players=allPros;DATA.hero_pool=buildPool(allPros);
const AH2=(window.ASSETS||{}).heroes||{},AI2=(window.ASSETS||{}).items||{};
const newH=[...new Set(allPros.map(p=>p.hero).filter(h=>h&&!Object.prototype.hasOwnProperty.call(AH2,h)))];
const newI=[...new Set(allPros.flatMap(p=>p.i||[]).filter(x=>x&&!Object.prototype.hasOwnProperty.call(AI2,x)))];
const newMsg=(newH.length||newI.length)?` · ${newH.length+newI.length} new art via live CDN (persist: python tools/fetch_assets.py)`:'';
try{localStorage.setItem('s18db',JSON.stringify({t:Date.now(),schedule:ms,standings:st,season:ps,players:allPros,games:allGames,heroPool:DATA.hero_pool,matches:DATA.matches}));}catch(e){upd.textContent='updated '+new Date().toLocaleTimeString()+' (not cached: storage full)';render();btn.disabled=false;btn.textContent=old;return;}
upd.textContent='updated '+new Date().toLocaleTimeString()+' · '+allGames.length+' games · '+mvpN+' MVPs'+(fails?' · '+fails+' failed':'')+newMsg;setNet();render();
}catch(e){upd.textContent='refresh failed — offline? showing last snapshot';setNet();}
btn.disabled=false;btn.textContent=old;}
document.getElementById('refresh').onclick=refreshDB;
try{const c=JSON.parse(localStorage.getItem('s18db')||'null');
if(c&&c.schedule&&c.schedule.length){DATA.schedule=c.schedule;if(c.standings)DATA.standings=c.standings;if(c.season)DATA.season=c.season;
if(c.players&&c.players.length){DATA.players=c.players;}if(c.games&&c.games.length){DATA.games=c.games;}
if(c.heroPool)DATA.hero_pool=c.heroPool;if(c.matches&&c.matches.length){DATA.matches=c.matches;}
document.getElementById('upd').textContent='snapshot '+new Date(c.t).toLocaleString();}}catch(e){}
render();
