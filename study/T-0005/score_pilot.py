"""Score the T-0005 pilot from its grading records: verified issues, raised issues, user-accepted issues, and key
recall per run.

Usage: python3 score_pilot.py GRADING_DIR   (writes GRADING_DIR/pilot_scores.json and prints it)

Inputs in GRADING_DIR: issues.json (findings grouped into issues), verify.tally.json (the three-skeptic panel),
db/issue_verdicts/ (the user's rulings on disputed issues), db/issue_matches/ (issue -> Key 1 item),
db/issue_ratings/ (the user's acceptance), and mapping.json (run label -> run folder).
An issue is verified when the panel found it real unanimously, or the user ruled it real when the panel didn't
agree unanimously. A run's scores count distinct issues it raised; key recall is distinct key items matched / 7.
"""
import glob
import json
import os
import sys

g = sys.argv[1]


def load(collection):
    out = {}
    for f in glob.glob(os.path.join(g, "db", collection, "*.json")):
        d = json.load(open(f))
        d = d.get("data", d)
        out[d["issue"]] = d
    return out


verdicts, matches, ratings = load("issue_verdicts"), load("issue_matches"), load("issue_ratings")
issues = {i["id"]: i for i in json.load(open(os.path.join(g, "issues.json")))["issues"]}
tally = json.load(open(os.path.join(g, "verify.tally.json")))
mapping_file = os.path.join(g, "mapping.json")
if not os.path.exists(mapping_file):
    mapping_file = os.path.join(g, "mapping.sealed.json")
mapping = json.load(open(mapping_file))

real = set()
for k, v in tally.items():
    if v["status"] == "unanimous":
        if v["majority"] == "real":
            real.add(k)
    elif verdicts[k]["verdict"] == "real":
        real.add(k)

rows = {}
for run in sorted(mapping):
    raised = {k for k, i in issues.items() if any(m.startswith(run + "-") for m in i["members"])}
    keys = {matches[k]["key_item"] for k in raised if matches[k].get("key_item")}
    rows[run] = {
        "cond": "baseline" if "baseline" in mapping[run] else "lsp",
        "run": mapping[run],
        "raised": len(raised),
        "verified": len(raised & real),
        "accepted": sum(1 for k in raised if ratings[k]["verdict"] == "act"),
        "not_verified": len(raised - real),
        "key_recall": round(len(keys) / 7, 2),
    }
result = {"final_verified": sorted(real), "rows": rows}
json.dump(result, open(os.path.join(g, "pilot_scores.json"), "w"), indent=2)
print(json.dumps(result, indent=2))
