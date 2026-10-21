"""Write a season provenance record (meta.json) from the committed database.

Records what a build was made from. Does not modify the database, so it is safe
to run against the published artifact.
"""
import json
import sqlite3
import subprocess
from datetime import datetime, timezone
from pathlib import Path
import sys

sys.path.insert(0, str(Path(__file__).resolve().parent))
from season import resolve

season = resolve("s18")
con = sqlite3.connect(season["database"])
tables = [r[0] for r in con.execute(
    "SELECT name FROM sqlite_master WHERE type='table' AND name NOT LIKE 'sqlite_%' ORDER BY name")]
counts = {t: con.execute(f"SELECT COUNT(*) FROM {t}").fetchone()[0] for t in tables}
try:
    commit = subprocess.check_output(["git", "rev-parse", "--short", "HEAD"],
                                     cwd=str(season["database"].parents[1])).decode().strip()
except Exception:
    commit = ""

meta = {
    "schema_version": 1,
    "season_id": season["id"],
    "display_name": season["displayName"],
    "generated_at": datetime.now(timezone.utc).isoformat(timespec="seconds"),
    "layout": season["layout"],
    "sources": {
        "hub": "https://mpl.mlbbhub.com/api/v1/id",
        "liquipedia": "https://liquipedia.net/mobilelegends/api.php",
        "liquipedia_page": "MPL/Indonesia/Season_18/Regular_Season",
    },
    "row_counts": counts,
    "build_commit": commit,
}
out = season["meta"]
out.parent.mkdir(parents=True, exist_ok=True)
out.write_text(json.dumps(meta, indent=2, ensure_ascii=False) + "\n", encoding="utf-8")
print("wrote", out)
print(json.dumps(counts, indent=2))
