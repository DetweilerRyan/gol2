"""Build the blind issue-rating page: findings grouped into distinct issues, each rated once.

Usage: python3 make_issues_page.py GRADING_DIR OUT_HTML [--stage2]
Reads GRADING_DIR/issues.json (the grouping, made blind to condition and checked by a second agent) and the
R*.findings.json files it refers to. Ratings are saved to the artifact's db at issue_ratings/<issue>; with
--stage2 (only after every issue is rated) the page adds Key 1 and GRADING_DIR/issue_proposals.json, locks the
ratings, and saves matches to issue_matches/<issue>. The page reuses rating_page.html's styles.
"""
import glob
import json
import os
import re
import sys

grading_dir, out, *flags = sys.argv[1:]
here = os.path.dirname(os.path.abspath(__file__))
findings = {}
for f in glob.glob(os.path.join(grading_dir, "R*.findings.json")):
    d = json.load(open(f))
    for x in d["findings"]:
        findings[f"{d['run']}-{x['id']}"] = x
issues = json.load(open(os.path.join(grading_dir, "issues.json")))["issues"]
data = [{"id": i["id"], "title": i["title"], "statement": i["statement"], "variants": i.get("variants", ""),
         "members": [{"id": m, "title": findings[m]["title"], "text": findings[m]["text"]} for m in i["members"]]}
        for i in issues]


def js(v):
    return json.dumps(v).replace("</", "<\\/")


style = re.search(r"<style>.*?</style>", open(os.path.join(here, "rating_page.html")).read(), re.S).group(0)
html = open(os.path.join(here, "issues_page.html")).read().replace("<!--__STYLE__-->", style, 1)
html = re.sub(r"/\*__ISSUES__\*/\s*\[\]", lambda _: js(data), html, count=1)
if "--stage2" in flags:
    key = [re.split(r"\s*\|\s*", ln.strip("| "))[1] for ln in open(os.path.join(grading_dir, "key1.md"))
           if re.match(r"^\|\s*\d+\s*\|", ln)]
    proposals = json.load(open(os.path.join(grading_dir, "issue_proposals.json")))
    html = re.sub(r"/\*__STAGE2__\*/\s*null", lambda _: js({"key": key, "proposals": proposals}), html, count=1)
open(out, "w").write(html)
print(f"{len(data)} issues from {sum(len(i['members']) for i in data)} findings -> {out}")
