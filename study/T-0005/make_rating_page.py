"""Build the blind rating page for one batch of sanitized review findings.

Usage: python3 make_rating_page.py GRADING_DIR OUT_HTML
Reads GRADING_DIR/R*.findings.json (written by the sanitizer agents; condition-hidden) and embeds them in a page
where the user rates each finding on its merits. The answer key is deliberately not in this page. Ratings are saved
to the artifact's db at ratings/<run>-<finding id> with a timestamp, and read back with the ArtifactData tool.
"""
import glob
import json
import os
import re
import sys

grading_dir, out = sys.argv[1:]
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
open(out, "w").write(re.sub(r"/\*__DATA__\*/\s*\[\]", lambda _: data, html, count=1))
print(f"{sum(len(r['findings']) for r in runs)} findings in {len(runs)} runs -> {out}")
