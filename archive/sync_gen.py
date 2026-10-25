"""One-way sync: templates (css/js/doc) from shipped dark HTML into tools/gen_dark.py."""
import re
from pathlib import Path
BASE = Path(__file__).parent
ROOT = BASE.parent
html = (ROOT / "mpl_id_s18_dark.html").read_text(encoding="utf-8")
p_style = html.index("<style>\n")
p_estyle = html.index("</style>", p_style)
p_assets = html.index("<script>window.ASSETS=")
p_eassets = html.index("</script>", p_assets)
p_mains = html.index("<script>\nconst DATA =", p_eassets)
p_emain = html.index("</script>", p_mains)
pre = html[:p_style + len("<style>\n")]
css = html[p_style + len("<style>\n"):p_estyle]
mid = html[p_estyle:p_assets]
assets_blob = html[p_assets + len("<script>window.ASSETS="):p_eassets]
__import__("json").loads(assets_blob)
js = html[p_mains + len("<script>\n"):p_emain]
tail = html[p_emain:]
dm = re.match(r"const DATA = (\{.*?\});\n", js, re.S)
assert dm, "DATA blob not found"
__import__("json").loads(dm.group(1).replace("<\\/script>", "</script>"))
js_tpl = js[:dm.start(1)] + "__DATA__" + js[dm.end(1):]
gpath = BASE / "gen_dark.py"
g = gpath.read_text(encoding="utf-8")
g = re.sub(r'css = r?""".*?"""\n', lambda m: "css = " + '"""' + css + '"""\n', g, count=1, flags=re.S)
g = re.sub(r'js = r""".*?"""\n', lambda m: 'js = r"""' + js_tpl + '"""\n', g, count=1, flags=re.S)
start = g.index('doc = """<!DOCTYPE html>')
end = g.index('</html>"""', start) + len('</html>"""')
doc_tpl = pre + "__CSS__" + mid + "<script>window.ASSETS=__ASSETS__</script>\n<script>\n__JS__" + tail
g = g[:start] + 'doc = """' + doc_tpl + '"""' + g[end:]
gpath.write_text(g, encoding="utf-8")
print("synced templates into tools/gen_dark.py")
