"""Build the blind rating page for one batch of sanitized review findings.

Usage: python3 make_rating_page.py GRADING_DIR OUT_HTML [--stage2]
Reads GRADING_DIR/R*.findings.json (written by the sanitizer agents; condition-hidden) and embeds them in a page
where the user rates each finding on its merits. The answer key is deliberately not in this page. Ratings are saved
to the artifact's db at ratings/<run>-<finding id> with a timestamp, and read back with the ArtifactData tool.
"""
import glob
import json
import os
import re
import sys

grading_dir, out, *flags = sys.argv[1:]
runs = []
for f in sorted(glob.glob(os.path.join(grading_dir, "R*.findings.json"))):
    d = json.load(open(f))
    runs.append({
        "run": d["run"],
        "preamble": d.get("preamble", ""),
        "findings": [{"id": x["id"], "title": x["title"], "text": x["text"], "citations": x.get("citations", [])}
                     for x in d["findings"]],
    })
data = json.dumps(runs).replace("</", "<\\/")
html = open(os.path.join(os.path.dirname(os.path.abspath(__file__)), "rating_page.html")).read()
html = re.sub(r"/\*__DATA__\*/\s*\[\]", lambda _: data, html, count=1)
if "--stage2" in flags:
    # Stage 2, only after the user has rated every finding blind: Key 1 and the grader's proposals.
    key = [re.split(r"\s*\|\s*", ln.strip("| "))[1] for ln in open(os.path.join(grading_dir, "key1.md"))
           if re.match(r"^\|\s*\d+\s*\|", ln)]
    proposals = {r["run"]: json.load(open(os.path.join(grading_dir, f"{r['run']}.proposals.json"))) for r in runs}
    stage2 = json.dumps({"key": key, "proposals": proposals}).replace("</", "<\\/")
    html = re.sub(r"/\*__STAGE2__\*/\s*null", lambda _: stage2, html, count=1)
open(out, "w").write(html)
print(f"{sum(len(r['findings']) for r in runs)} findings in {len(runs)} runs -> {out}")
