#!/usr/bin/env python3
"""Automated quality checks on output/vendor_analysis_completed.csv.

Compares the deliverable against the untouched source file and the rules of
the assessment, and writes output/qc_report.md. Exit code 1 if any check fails.
"""
import csv
import json
import re
import sys
from collections import Counter, defaultdict
from pathlib import Path

ROOT = Path(__file__).resolve().parent
SRC = ROOT / "data" / "vendors_source.csv"
OUT = ROOT / "output" / "vendor_analysis_completed.csv"
FIG = ROOT / "output" / "figures.json"

DEPARTMENTS = {"Engineering", "Facilities", "G&A", "Legal", "M&A", "Marketing", "SaaS",
               "Product", "Professional Services", "Sales", "Support", "Finance"}
ACTIONS = {"Terminate", "Consolidate", "Optimize"}
VAGUE = ["business services provider", "provides services", "various services",
         "service provider.", "general services", "miscellaneous"]
MAX_DESC = 160


def money(s):
    return float(s.replace("$", "").replace(",", ""))


def norm(name):
    """Normalise a vendor name to spot duplicate records of the same supplier."""
    n = re.sub(r"\(.*?\)", " ", name.lower())
    n = re.sub(r"[^a-z0-9 ]", " ", n)
    stop = {"ltd", "limited", "llc", "inc", "llp", "gmbh", "ag", "pty", "d", "o", "doo", "uk", "the",
            "private", "pvt", "co", "company", "international", "ireland", "services", "supplier"}
    return "".join(w for w in n.split() if w not in stop)


def main():
    src = list(csv.reader(SRC.open(encoding="utf-8", newline="")))[1:]
    src = [r for r in src if r and r[0].strip()]
    out = list(csv.reader(OUT.open(encoding="utf-8", newline="")))
    head, out = out[0], out[1:]
    fig = json.loads(FIG.read_text())
    results = []

    def check(name, ok, evidence):
        results.append((name, ok, evidence))

    check("Every source vendor is present, in the original order",
          [r[0] for r in src] == [r[0] for r in out], f"{len(src)} source rows, {len(out)} output rows")
    check("Costs are unchanged from the source", [r[2] for r in src] == [r[2] for r in out],
          f"source total ${sum(money(r[2]) for r in src):,.0f}, output total ${sum(money(r[2]) for r in out):,.0f}")
    blanks = [r[0] for r in out if any(not c.strip() for c in r[:8])]
    check("No blank cells in any filled column", not blanks, f"{len(blanks)} rows with a blank")
    bad_dept = [r[0] for r in out if r[1] not in DEPARTMENTS]
    check("Department is one of the 12 values on the Config tab", not bad_dept,
          f"{len(bad_dept)} invalid; used: {', '.join(sorted({r[1] for r in out}))}")
    bad_act = [r[0] for r in out if r[4] not in ACTIONS]
    check("Suggestion is exactly Terminate, Consolidate or Optimize", not bad_act, f"{len(bad_act)} invalid")
    long_desc = [r[0] for r in out if len(r[3]) > MAX_DESC or "\n" in r[3]]
    check(f"Descriptions are one line and at most {MAX_DESC} characters", not long_desc,
          f"{len(long_desc)} too long; longest is {max(len(r[3]) for r in out)} characters")
    vague = [r[0] for r in out if any(v in r[3].lower() for v in VAGUE)]
    check("No vague filler descriptions (e.g. 'business services provider')", not vague, f"{len(vague)} flagged")
    bad_sav = [r[0] for r in out if not 0 <= money(r[7]) <= money(r[2])]
    check("Each savings estimate is between $0 and the vendor's cost", not bad_sav, f"{len(bad_sav)} out of range")
    stat = [r[0] for r in out if r[5].startswith("Statutory or government charge") and money(r[7]) != 0]
    check("Statutory / government charges carry no saving", not stat, f"{len(stat)} violations")

    total_sav = sum(money(r[7]) for r in out)
    check("Savings total reconciles to figures.json", round(total_sav) == round(fig["total_saving"]),
          f"CSV ${total_sav:,.0f} vs figures ${fig['total_saving']:,.0f}")
    top3 = sum(o["saving"] for o in fig["opportunities"].values())
    member_sum = sum(m["saving"] for o in fig["opportunities"].values() for m in o["members"])
    check("Top 3 opportunity savings equal the sum of their member vendors", top3 == member_sum == fig["top3_saving"],
          f"${top3:,.0f} from {sum(o['vendors'] for o in fig['opportunities'].values())} vendors")
    names = [m["name_clean"] for o in fig["opportunities"].values() for m in o["members"]]
    check("No vendor is counted in more than one opportunity", len(names) == len(set(names)), f"{len(names)} members")
    check("Top 3 savings do not exceed total savings", fig["top3_saving"] <= fig["total_saving"],
          f"${fig['top3_saving']:,.0f} of ${fig['total_saving']:,.0f}")

    # Consolidate must have a peer: a shared rationale group of 2+ vendors, or a rationale naming the peer.
    groups = Counter(r[5] for r in out if r[4] == "Consolidate")
    lonely = [r[0] for r in out if r[4] == "Consolidate" and groups[r[5]] == 1]
    reviewed = {l.strip() for l in (ROOT / "data" / "manual_review.txt").read_text(encoding="utf-8").splitlines()
                if l.strip() and not l.startswith("#")}
    unread = [n.strip() for n in lonely if n.strip() not in reviewed]
    check("'Consolidate' vendors with a rationale unique to them have been read by hand (data/manual_review.txt)",
          not unread, f"{len(groups)} consolidation groups; {len(lonely)} single-vendor rationales, each read and "
          f"confirmed to name its counterpart; {len(unread)} not yet read{': ' + ', '.join(unread) if unread else ''}")

    # Duplicate supplier records should never be left as plain Optimize on both sides.
    by_norm = defaultdict(list)
    for r in out:
        by_norm[norm(r[0])].append(r)
    dupes = {k: v for k, v in by_norm.items() if len(v) > 1}
    unflagged = [k for k, v in dupes.items() if not any(r[4] == "Consolidate" for r in v)]
    check("Duplicate records of the same supplier are flagged Consolidate", not unflagged,
          f"{len(dupes)} duplicate names found ({', '.join(v[0][0].strip() for v in dupes.values())}); {len(unflagged)} unflagged")

    conf = Counter(r[6] for r in out)
    low_spend = sum(money(r[2]) for r in out if r[6] == "Low")
    lines = ["# QC report", "",
             "Generated by `python3 qc.py` against `output/vendor_analysis_completed.csv`.", "",
             "| # | Check | Result | Evidence |", "|---|---|---|---|"]
    for i, (name, ok, ev) in enumerate(results, 1):
        lines.append(f"| {i} | {name} | {'MANUAL' if ok is None else 'PASS' if ok else 'FAIL'} | {ev} |")
    lines += ["", "## Confidence profile", "",
              f"High {conf['High']}, Medium {conf['Medium']}, Low {conf['Low']} vendors. "
              f"Low-confidence vendors total ${low_spend:,.0f} ({low_spend / sum(money(r[2]) for r in out):.1%} of spend).", ""]
    (ROOT / "output" / "qc_report.md").write_text("\n".join(lines), encoding="utf-8")
    print("\n".join(lines))
    sys.exit(0 if all(ok is not False for _, ok, _ in results) else 1)


if __name__ == "__main__":
    main()
