"""Write docs/cv-stats.json for the website's CV card.

Counts come from the totcount values LaTeX writes to main.aux, so they always
match the compiled PDF. Citations are read from the number typed in main.tex.
"""
import datetime
import json
import re
from pathlib import Path

tex = Path("main.tex").read_text()
aux = Path("main.aux").read_text() if Path("main.aux").exists() else ""

counters = {k: int(v) for k, v in re.findall(r"\\setcounter\{(\w+)@totc\}\{(\d+)\}", aux)}


def count_items(env):
    """Fallback if main.aux is missing: count \\item in every `env` block."""
    body = re.sub(r"(?<!\\)%.*", "", tex)
    blocks = re.findall(rf"\\begin\{{{env}\}}(.*?)\\end\{{{env}\}}", body, re.S)
    return sum(len(re.findall(r"\\item\b", b)) for b in blocks)


citations = re.search(r"\\textbf\{(\d+)\}\s*citations", tex)

stats = {
    "publications": counters.get("pubcount", count_items("primarylist") + count_items("nthauthorlist")),
    "citations": int(citations.group(1)) if citations else None,
    "invited_talks": counters.get("invitedcount", count_items("invitedlist")),
    "talks": counters.get("talkcount", count_items("invitedlist") + count_items("contriblist")),
    "updated": datetime.date.today().isoformat(),
}

Path("docs").mkdir(exist_ok=True)
Path("docs/cv-stats.json").write_text(json.dumps(stats, indent=2) + "\n")
print(json.dumps(stats))
