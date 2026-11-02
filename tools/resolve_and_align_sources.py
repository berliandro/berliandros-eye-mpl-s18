#!/usr/bin/env python3
"""Resumable verification of schedule-derived VOD candidates and transcript-caption alignment."""
from __future__ import annotations
import argparse,csv,json,re,subprocess,sys
from datetime import datetime,timezone
from pathlib import Path
TOOLS=Path(__file__).resolve().parent; REPO=TOOLS.parent
sys.path.insert(0,str(TOOLS))
from link_video_source import ytdlp_metadata,video_id_from  # noqa: E402
from transcript_evidence import align_captions,fetch_timed,sha256_file  # noqa: E402
MANIFEST=REPO/"analysis/sources/source-manifest.json"; SCHEDULE=REPO/"data/csv/schedule_all.csv"
SUMMARY=REPO/"analysis/evidence/timed-alignment.json"; CACHE=REPO/"analysis/cache"; ALIGN=CACHE/"timed"; REPORT=CACHE/"video-resolution-report.json"
def now():return datetime.now(timezone.utc).isoformat(timespec="seconds")
def atomic_json(path,data):
 path.parent.mkdir(parents=True,exist_ok=True);tmp=path.with_suffix(path.suffix+".tmp");tmp.write_text(json.dumps(data,indent=2,ensure_ascii=False)+"\n",encoding="utf-8");tmp.replace(path)
def read_json(path,default):return json.loads(path.read_text(encoding="utf-8")) if path.exists() else default
def regular_schedule_rows(path=SCHEDULE):
 with path.open("r",encoding="utf-8-sig",newline="") as f:rows=list(csv.DictReader(f))
 return [r for r in rows if (r.get("status") or "").lower()=="completed" and "playoff" not in (r.get("schedule_id") or "").lower()]
def build_schedule_candidates(manifest,schedule_path=SCHEDULE):
 rows=regular_schedule_rows(schedule_path);dates=sorted({(r.get("iso_date") or "").strip() for r in rows}-{""})
 sources=sorted(manifest.get("sources",[]),key=lambda s:(int(s.get("week") or 0),int(s.get("day") or 0)))
 if len(sources)!=27:raise ValueError(f"expected 27 transcript sources, found {len(sources)}")
 if len(dates)!=len(sources):raise ValueError(f"source/date mismatch: {len(sources)} sources vs {len(dates)} dates")
 grouped={}
 for r in rows:grouped.setdefault((r.get("iso_date") or "").strip(),[]).append(r)
 sh=sha256_file(Path(schedule_path));result={};failures=[]
 for source,date in zip(sources,dates):
  day=sorted(grouped[date],key=lambda r:r.get("iso_datetime") or "");ids=set();issues=[]
  for r in day:
   url=(r.get("vod_url") or "").strip();mid=(r.get("match_detail_id") or "").strip()
   if not url:issues.append(f"series {mid or r.get('schedule_id')}: missing VOD URL");continue
   try:ids.add(video_id_from(url))
   except (ValueError,SystemExit) as e:issues.append(f"series {mid}: invalid URL ({e})")
  if len(ids)!=1:issues.append(f"expected one distinct VOD ID on {date}; found {len(ids)}")
  failures.extend(f"{source['source_id']}: {e}" for e in issues);candidate=next(iter(ids)) if len(ids)==1 and not issues else None
  old={str(m.get("match_detail_id")):m for m in source.get("series_mapping",[])};mappings=[]
  for r in day:
   mid=str(r.get("match_detail_id") or "")
   if mid in old:
    m=dict(old[mid]);m.update(schedule_date=date,scheduled_start=r.get("iso_datetime"),scheduled_team_a=r.get("team_a"),scheduled_team_b=r.get("team_b"),schedule_vod_candidate_id=candidate)
   else:m={"match_detail_id":mid,"confidence":"medium","method":"canonical_schedule_date_and_vod_url","schedule_date":date,"scheduled_start":r.get("iso_datetime"),"scheduled_team_a":r.get("team_a"),"scheduled_team_b":r.get("team_b"),"schedule_vod_candidate_id":candidate,"rationale":f"Schedule associates series {mid} ({r.get('team_a')} vs {r.get('team_b')}) on {date} with candidate VOD {candidate or 'unresolved'}. Exact in-video start offsets remain unverified."}
   mappings.append(m)
  result[source["source_id"]]={"broadcast_date":date,"candidate_video_id":candidate,"candidate_video_url":f"https://www.youtube.com/watch?v={candidate}" if candidate else None,"candidate_provenance":{"source":"data/csv/schedule_all.csv","sha256":sh,"method":"unique VOD ID across completed regular fixtures on this date","schedule_match_ids":[str(r.get("match_detail_id")) for r in day],"resolution_errors":issues},"schedule_match_ids":[str(r.get("match_detail_id")) for r in day],"series_mapping":mappings}
 return result,failures
def metadata_errors(source,video_id,meta):
 title=re.sub(r"\s+"," ",str(meta.get("title") or "")).casefold();channel=str(meta.get("channel") or meta.get("uploader") or "");want=f"minggu {source.get('week')} hari {source.get('day')}".casefold();errors=[]
 try:
  if video_id_from(video_id)!=video_id:errors.append("candidate ID changed during parsing")
 except (ValueError,SystemExit):errors.append("malformed video ID")
 if not channel.casefold().startswith("mpl indonesia"):errors.append(f"channel mismatch: {channel!r}")
 if want not in title:errors.append(f"title missing {want!r}: {title!r}")
 if "mpl id s18" not in title and "mpl indonesia season 18" not in title:errors.append(f"title does not identify MPL ID S18: {title!r}")
 return errors
def cache_alignment_is_current(source, candidate_id, alignment):
    """Return True only when a local sidecar is tied to the current source and candidate."""
    if not isinstance(alignment, dict) or not candidate_id:
        return False
    if source.get("video_id") != candidate_id or not source.get("video_metadata_provenance"):
        return False
    if alignment.get("source_id") != source.get("source_id"):
        return False
    if alignment.get("video_id") != candidate_id or alignment.get("raw_sha256") != source.get("sha256"):
        return False
    if alignment.get("alignment_status") != "verified" or alignment.get("mismatch_count") != 0:
        return False
    if alignment.get("unmapped_lines", 0) != 0:
        return False
    # Older v1 sidecars had no explicit unmapped count; they were strict 1:1.
    if "unmapped_lines" not in alignment:
        return alignment.get("raw_line_count") == alignment.get("timed_snippet_count")
    return True


def derive_source_status(source, candidate, alignment):
    """Derive source state from current candidate, metadata provenance, and sidecar integrity."""
    candidate_id = candidate.get("candidate_video_id")
    if not candidate_id:
        return "candidate_resolution_failed"
    if source.get("video_id") != candidate_id or not source.get("video_metadata_provenance"):
        return "schedule_candidate_pending_verification"
    if cache_alignment_is_current(source, candidate_id, alignment):
        return "caption_alignment_verified"
    if source.get("video_resolution_status") == "caption_alignment_partial":
        return "caption_alignment_partial"
    return "metadata_verified"


def summary_from_alignment(source, alignment):
    return {
        "source_id": source["source_id"],
        "video_id": alignment["video_id"],
        "raw_sha256": alignment["raw_sha256"],
        "raw_lines": alignment["raw_line_count"],
        "timed_snippets": alignment["timed_snippet_count"],
        "exact_matches": alignment["exact_matches"],
        "normalized_matches": alignment["normalized_matches"],
        "fuzzy_matches": alignment.get("fuzzy_matches", 0),
        "unmapped_lines": alignment.get("unmapped_lines", 0),
        "alignment_confidence": alignment.get("alignment_confidence")
        or round(
            (alignment["exact_matches"] + alignment["normalized_matches"])
            / max(alignment["raw_line_count"], 1),
            4,
        ),
        "timestamp_provenance": alignment["timestamp_provenance"],
    }


def write_timed_summary(items):
    """Replace the active summary with only cache sidecars verified for current source hashes."""
    atomic_json(SUMMARY, {
        "schema_version": 1,
        "generated_at": now(),
        "sources": sorted(items, key=lambda item: item["source_id"]),
    })


def save_manifest(path,m):m["generated_at"]=now();atomic_json(path,m)
def resolve_one(source,c,no_align=False):
 vid=c.get("candidate_video_id")
 if not vid:return {"source_id":source["source_id"],"status":"candidate_failed","error":"no unambiguous schedule VOD"}
 try:meta=ytdlp_metadata(vid)
 except (Exception,SystemExit) as e:return {"source_id":source["source_id"],"candidate_video_id":vid,"status":"metadata_failed","error":str(e)[:1200]}
 errors=metadata_errors(source,vid,meta)
 if errors:return {"source_id":source["source_id"],"candidate_video_id":vid,"status":"metadata_mismatch","errors":errors,"observed_title":meta.get("title"),"observed_channel":meta.get("channel") or meta.get("uploader")}
 source.update(video_id=vid,video_url=f"https://www.youtube.com/watch?v={vid}",video_title=meta.get("title") or "",video_channel=meta.get("channel") or meta.get("uploader") or "",video_duration_seconds=meta.get("duration"),video_metadata_provenance="local yt-dlp lookup; official channel, season and exact week/day title matched",mapping_confidence="high_video_metadata",video_resolution_status="metadata_verified",resolved_at=now())
 result={"source_id":source["source_id"],"candidate_video_id":vid,"status":"metadata_verified","observed_title":meta.get("title"),"observed_channel":meta.get("channel") or meta.get("uploader")}
 if no_align:return result
 try:
  captions=fetch_timed(vid,("id",));a=align_captions(source,captions);atomic_json(ALIGN/f"{source['source_id']}.json",a)
  if a.get("alignment_status")!="verified" or a.get("mismatch_count")!=0:
   source.update(video_resolution_status="caption_alignment_partial",caption_alignment_status="partial",caption_alignment_provenance="youtube-transcript-api; monotonic alignment left unmatched raw lines un-timestamped")
   result.update(status="caption_alignment_partial",raw_line_count=a["raw_line_count"],timed_snippet_count=a["timed_snippet_count"],exact_matches=a["exact_matches"],normalized_matches=a["normalized_matches"],fuzzy_matches=a.get("fuzzy_matches",0),unmapped_lines=a.get("unmapped_lines",0),error="alignment left raw lines without verified timestamps")
  else:
   source.update(video_resolution_status="caption_alignment_verified",caption_alignment_status="verified",caption_alignment_provenance="youtube-transcript-api; monotonic alignment verified for every raw line")
   result.update(status="caption_alignment_verified",raw_line_count=a["raw_line_count"],timed_snippet_count=a["timed_snippet_count"],exact_matches=a["exact_matches"],normalized_matches=a["normalized_matches"],fuzzy_matches=a.get("fuzzy_matches",0),unmapped_lines=a.get("unmapped_lines",0),alignment_confidence=a.get("alignment_confidence"))
 except (Exception,SystemExit) as e:result.update(status="caption_alignment_failed",error=str(e)[:1200])
 return result
def update_summary(items):
 old=read_json(SUMMARY,{"schema_version":1,"sources":[]});byid={s["source_id"]:s for s in old.get("sources",[])}
 for x in items:byid[x["source_id"]]=x
 atomic_json(SUMMARY,{"schema_version":1,"generated_at":now(),"sources":[byid[k] for k in sorted(byid)]})
def main(argv=None):
 p=argparse.ArgumentParser(description=__doc__);p.add_argument("--manifest",type=Path,default=MANIFEST);p.add_argument("--schedule",type=Path,default=SCHEDULE);p.add_argument("--no-align",action="store_true");p.add_argument("--source-id",action="append",default=[]);p.add_argument("--limit",type=int);p.add_argument("--refresh-metadata",action="store_true");p.add_argument("--no-inventory",action="store_true");args=p.parse_args(argv)
 manifest=read_json(args.manifest,None)
 if not isinstance(manifest,dict):print("ERROR: invalid manifest",file=sys.stderr);return 2
 try:candidates,sched_errors=build_schedule_candidates(manifest,args.schedule)
 except Exception as e:print(f"ERROR: schedule resolution failed: {e}",file=sys.stderr);return 2
 byid={s["source_id"]:s for s in manifest.get("sources",[])}
 for sid,c in candidates.items():
  source=byid[sid]
  source.update(c)
  cached=read_json(ALIGN/f"{sid}.json",None)
  source["video_resolution_status"]=derive_source_status(source,c,cached)
 manifest["schedule_mapping_provenance"]={"source":str(args.schedule),"sha256":sha256_file(args.schedule),"method":"source week/day paired with chronological completed regular-season dates","broadcast_days":len({c["broadcast_date"] for c in candidates.values()}),"completed_series":len(regular_schedule_rows(args.schedule)),"note":"schedule candidate, metadata verification and timed-caption alignment are separate states"}
 save_manifest(args.manifest,manifest);selected=list(manifest.get("sources",[]))
 if args.source_id:
  unknown=set(args.source_id)-set(byid)
  if unknown:print("ERROR: unknown source IDs: "+", ".join(sorted(unknown)),file=sys.stderr);return 2
  selected=[s for s in selected if s["source_id"] in set(args.source_id)]
 if args.limit is not None:selected=selected[:max(0,args.limit)]
 results=[];summaries=[];failures=len(sched_errors)
 for s in selected:
  sid=s["source_id"];c=candidates[sid];cp=ALIGN/f"{sid}.json"
  if not args.refresh_metadata and s.get("video_resolution_status")=="caption_alignment_verified" and cp.exists():
   a=read_json(cp,{})
   if cache_alignment_is_current(s,c.get("candidate_video_id"),a):
    s["video_resolution_status"]="caption_alignment_verified"
    s["caption_alignment_status"]="verified"
    s["caption_alignment_provenance"]="cached sidecar; source hash, candidate and alignment status verified"
    results.append({"source_id":sid,"status":"caption_alignment_verified","skipped":"verified current alignment cache"})
    summaries.append(summary_from_alignment(s,a))
    continue
  result=resolve_one(s,c,args.no_align);results.append(result)
  if result.get("status")=="metadata_mismatch":
   s["video_resolution_status"]="metadata_mismatch"
  elif result.get("status")=="candidate_failed":
   s["video_resolution_status"]="candidate_resolution_failed"
  elif result.get("status")=="caption_alignment_partial":
   s["video_resolution_status"]="caption_alignment_partial"
  elif result.get("status")=="caption_alignment_failed":
   s["video_resolution_status"]="metadata_verified"
  elif result.get("status")=="metadata_verified":
   s["video_resolution_status"]="metadata_verified"
  elif result.get("status")=="caption_alignment_verified":
   s["video_resolution_status"]="caption_alignment_verified"
  s["last_resolution_attempt"]=now()
  s["last_resolution_status"]=result.get("status")
  s["last_resolution_error"]=result.get("error") or result.get("errors") or None
  if result.get("status") in ("metadata_failed","metadata_mismatch","candidate_failed","caption_alignment_failed"):failures+=1
  save_manifest(args.manifest,manifest)
 # Rebuild the active alignment summary from integrity-checked local sidecars.
 # Stale entries are removed rather than making a source look aligned by source_id alone.
 active=[]
 for source in manifest.get("sources",[]):
  candidate=candidates[source["source_id"]]
  cached=read_json(ALIGN/f"{source['source_id']}.json",None)
  status=derive_source_status(source,candidate,cached)
  if source.get("video_resolution_status")=="metadata_mismatch":
   status="metadata_mismatch"
  elif source.get("video_resolution_status")=="candidate_resolution_failed":
   status="candidate_resolution_failed"
  source["video_resolution_status"]=status
  if status=="caption_alignment_verified":
   active.append(summary_from_alignment(source,cached))
 write_timed_summary(active)
 save_manifest(args.manifest,manifest)
 out={"schema_version":1,"generated_at":now(),"selected_count":len(selected),"schedule_failures":sched_errors,"no_align":args.no_align,"results":results,"metadata_verified":sum(r.get("status") in ("metadata_verified","caption_alignment_verified","caption_alignment_partial") for r in results),"caption_alignment_verified":sum(r.get("status")=="caption_alignment_verified" for r in results),"caption_alignment_partial":sum(r.get("status")=="caption_alignment_partial" for r in results),"failed":[r for r in results if r.get("status") not in ("metadata_verified","caption_alignment_verified")]}
 atomic_json(REPORT,out);print(json.dumps(out,ensure_ascii=True,indent=2))
 if not args.no_inventory:
  run=subprocess.run([sys.executable,str(TOOLS/"analysis_inventory.py")],cwd=REPO,capture_output=True,text=True,timeout=120);print(run.stdout)
  if run.returncode:print(run.stderr,file=sys.stderr);return run.returncode
 return 1 if failures else 0
if __name__=="__main__":raise SystemExit(main())
