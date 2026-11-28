#!/usr/bin/env python3
"""Write the submission tabs from the build outputs.

Reads output/vendor_analysis_completed.csv and output/figures.json and writes
  output/top3_opportunities.md
  output/executive_memo.md
  output/methodology.md
  output/Vendor Analysis Assessment - Vincent Chan.xlsx   (all tabs, for Google Sheets import)

Every number in the text is taken from figures.json, so the memo cannot drift
from the vendor-level data. Requires openpyxl for the .xlsx only.
"""
import csv
import json
from pathlib import Path

ROOT = Path(__file__).resolve().parent
OUT = ROOT / "output"
F = json.loads((OUT / "figures.json").read_text())
QC = (OUT / "qc_report.md").read_text() if (OUT / "qc_report.md").exists() else ""

CONFIG_DEPARTMENTS = ["Engineering", "Facilities", "G&A", "Legal", "M&A", "Marketing", "SaaS",
                      "Product", "Professional Services", "Sales", "Support", "Finance"]


def usd(x):
    return f"${x:,.0f}"


def k(x):
    return f"${x / 1000:,.0f}K"


def m(x):
    return f"${x / 1e6:,.2f}M"


total, saving, top3 = F["total_spend"], F["total_saving"], F["top3_saving"]
o1, o2, o3 = (F["opportunities"][n] for n in ("1", "2", "3"))
tc = F["template_counts"]
act = F["by_action"]
rest = saving - top3

# Opportunity 2 sub-totals
def sub(pred):
    ms = [x for x in o2["members"] if pred(x)]
    return len(ms), sum(x["cost"] for x in ms), sum(x["saving"] for x in ms)

PAYROLL = ("Hr Solution", "Hrsolution", "Integrated Personnel", "Australian Payroll")
is_pay = lambda x: x["name_clean"].startswith(PAYROLL)
ma = sub(lambda x: x["dept"] == "M&A")
fin = sub(lambda x: x["dept"] == "Finance" and not is_pay(x))
leg = sub(lambda x: x["dept"] == "Legal")
rec = sub(lambda x: x["template"] == "recruit")
pay = sub(is_pay)
assert ma[0] + fin[0] + leg[0] + rec[0] + pay[0] == o2["vendors"]
sf = o1["members"][0]
weking = max(float(r[2].replace("$", "").replace(",", "")) for r in csv.reader(
    (OUT / "vendor_analysis_completed.csv").open(encoding="utf-8", newline="")) if r[0].strip().startswith("Weking"))
sf_rate = sf["saving"] / sf["cost"]
costs = sorted(F["all_costs"], reverse=True)
n_next, run = 0, 0.0
for c in costs[1:]:
    if run + c >= costs[0]:
        break
    run += c
    n_next += 1
terminated_offices = [x for x in o3["members"] if x["action"] == "Terminate"]
kept_offices = [x for x in o3["members"] if x["action"] != "Terminate"]

OPPS = [
    ("Salesforce CRM contract reset",
     f"Salesforce is {usd(sf['cost'])} a year, {sf['cost'] / total:.0%} of all vendor spend and more than the next "
     f"{n_next} vendors combined, so it is the single biggest lever. It is the company's CRM and core "
     f"sales system, so the aim is to pay less for it, not to remove it. First step: confirm the contract type, because "
     f"the amount is large for internal CRM seats alone and several other vendors on the list are Salesforce-related. "
     f"(a) If it is seat licensing: audit licences, editions and add-on clouds against active users, remove unused "
     f"seats, and renegotiate at renewal with a multi-year commitment or under the parent company's agreement. "
     f"(b) If it is a platform or reseller agreement tied to the company's own product: the lever is the fee rate and "
     f"minimum commitment, negotiated with the parent company's scale. Estimate assumes a {sf_rate:.0%} reduction under "
     f"either route (range 10-20% until the contract is reviewed). Each 5 points is worth {usd(sf['cost'] * 0.05)}.",
     o1["saving"]),
    ("Move back-office finance, legal and hiring vendors to the parent company",
     f"{o2['vendors']} vendors and {usd(o2['spend'])} go on finance, legal, deal and hiring support that a parent company "
     f"normally has in-house or under its own contracts (to be confirmed). Breakdown of the saving: (1) deal advisers "
     f"and prior-owner fees that end with the transaction ({ma[0]} vendors, {usd(ma[2])}; this is cost falling away, not a "
     f"negotiated saving, and excluding it this opportunity is worth {usd(o2['saving'] - ma[2])}); (2) {fin[0]} finance vendors "
     f"(audit, tax and accounting firms, finance software, insurance broking, equity administration) moved to the parent "
     f"company's auditor and systems, one firm per function ({usd(fin[2])}); (3) {rec[0]} recruitment agencies stopped in "
     f"favour of the parent company's talent team ({usd(rec[2])}; assumes 70% of last year's agency fees are avoided); "
     f"(4) {leg[0]} law firms and entity-management vendors reduced to one panel firm plus local counsel ({usd(leg[2])}); "
     f"(5) payroll and employer-of-record providers merged into one contract ({usd(pay[2])}, on the service fee only). "
     f"Statutory filings and local counsel are kept in every country.",
     o2["saving"]),
    ("Shrink the office footprint from seven sites to three",
     f"{o3['vendors']} identified leases and coworking contracts cost {usd(o3['spend'])} a year across six countries. Close the "
     f"{len(terminated_offices)} small satellite sites ("
     + ", ".join(f"{x['name_clean']} {usd(x['cost'])}" for x in terminated_offices)
     + ") and move those teams to remote working (net of an allowance for on-demand desks), and resize the three sites that stay to actual hybrid attendance: "
     + ", ".join(f"{x['name_clean']} {usd(x['cost'])}" for x in kept_offices)
     + ". Assumes 50% less space in London and 40% less in Zagreb and India; these are assumptions, not measured "
     f"attendance, and each 10 points across the three sites is worth {usd(sum(x['cost'] for x in kept_offices) * 0.10)}. "
     f"Timing depends on lease break dates, which were not in the data. Not included: Weking d.o.o. ({usd(weking)}), an "
     "unverified payee that may be an eighth site; if it is a lease it should be added to this review.",
     o3["saving"]),
]

top3_md = ["# Top 3 opportunities", "", "| # | Opportunity | Explanation | Estimated annual savings (USD) |", "|---|---|---|---:|"]
for i, (title, text, s) in enumerate(OPPS, 1):
    top3_md.append(f"| {i} | {title} | {text} | {usd(s)} |")
TOP3_TOTAL = (f"{top3 / total:.0%} of total vendor spend ({usd(total)}); {top3 / saving:.0%} of all savings identified "
              f"({usd(saving)}). Excluding the {usd(ma[2])} of deal and prior-owner fees that end anyway, the Top 3 is "
              f"{usd(top3 - ma[2])} and total savings are {usd(saving - ma[2])} ({(saving - ma[2]) / total:.0%} of spend).")
top3_md += [f"| | **Total** | {TOP3_TOTAL} | **{usd(top3)}** |", ""]
for n, o in F["opportunities"].items():
    top3_md += [f"## Opportunity {n}: vendors included", "", "| Vendor | Department | Spend | Action | Est. saving |", "|---|---|---:|---|---:|"]
    top3_md += [f"| {x['name_clean']} | {x['dept']} | {usd(x['cost'])} | {x['action']} | {usd(x['saving'])} |" for x in o["members"]]
    top3_md.append("")
(OUT / "top3_opportunities.md").write_text("\n".join(top3_md), encoding="utf-8")

# ---- Executive memo ---------------------------------------------------------
# Block types: title, meta (header lines), h (heading), p, ol, ul, table.
_vendor_rows = list(csv.reader((OUT / "vendor_analysis_completed.csv").open(encoding="utf-8", newline="")))[1:]
_low = [float(r[2].replace("$", "").replace(",", "")) for r in _vendor_rows if r[6] == "Low"]
other_vendors = F["vendors"] - sum(o["vendors"] for o in F["opportunities"].values())
n_closed = {1: "one", 2: "two", 3: "three", 4: "four", 5: "five"}[len(terminated_offices)]
n_kept = {1: "one", 2: "two", 3: "three", 4: "four"}[len(kept_offices)]
n_sites = {5: "five", 6: "six", 7: "seven", 8: "eight"}[o3["vendors"]]

MEMO = [
    ("title", "Vendor Spend Review"),
    ("meta", ["To: CEO, CFO", "From: VP of Operations", "Date: 27 November 2026",
              f"Re: {m(saving)} of annual vendor savings; three decisions needed"]),
    ("h", "Summary and decisions needed"),
    ("p", f"I reviewed all {F['vendors']} vendors ({m(total)} over the last 12 months) and identified about {m(saving)} of "
          f"annual savings ({saving / total:.0%}). {m(top3)} depends on the three decisions in rows 1 to 3 below, which I ask "
          "you to approve. Decisions take 90 days; savings arrive over 12 months as contracts renew, so year one "
          f"will be lower. Salesforce alone is "
          f"{m(sf['cost'])} ({sf['cost'] / total:.0%}) of spend."),
    ("h", "Recommendations"),
    ("table", [
        ["", "Action", "Annual saving"],
        ["1", "Reset the Salesforce contract. Confirm the contract type, remove unused licences and renegotiate. "
              f"Assumes {sf_rate:.0%} (range 10-20%).", k(o1["saving"])],
        ["2", "Move back-office services to the parent company. One auditor, legal panel and payroll "
              f"provider; no agency recruiting. Includes {k(ma[2])} of deal fees ending anyway.", k(o2["saving"])],
        ["3", f"Reduce offices from {n_sites} sites to {n_kept}. Close {n_closed} satellite sites and resize London, Zagreb "
              "and India.", k(o3["saving"])],
        ["4", "Other vendors. Overlapping software, benefits, travel and one-off purchases.", k(rest)],
        ["", f"Total ({m(saving - ma[2])} excluding those fees)", m(saving)],
    ]),
    ("h", "Timeline"),
    ("ul", ["Days 1-30: Freeze new commitments and auto-renewals. Stop agency recruiting. Collect the top 25 contracts.",
            "Days 31-90: Audit Salesforce licences and open the negotiation. Appoint the auditor, legal panel and "
            "payroll provider. Give notice on the satellite offices.",
            "Months 4-12: Resize London, Zagreb and India at break dates. Consolidate the rest at renewal. Report monthly."]),
    ("h", "Risks and mitigations"),
    ("ol", ["These are estimates from vendor names and spend; no contracts seen, exit costs not netted off. "
            "Mitigation: confirm against the top 25 contracts within 30 days.",
            "Row 2 assumes the parent has providers we can join. Mitigation: confirm before giving notice.",
            "Salesforce may be a platform deal, not seat licences. Mitigation: confirm the type in week one.",
            "Office closures affect retention; break dates may delay savings. Mitigation: confirm dates.",
            f"{F['by_confidence']['Low']['vendors']} low-confidence vendors ({k(F['by_confidence']['Low']['spend'])}), "
            f"one at {k(max(_low))}. Mitigation: verify each before stopping payment."]),
]


def _memo_text(b):
    kind, v = b
    if kind == "meta":
        return " ".join(v)
    if kind in ("ol", "ul"):
        return " ".join(v)
    if kind == "table":
        return " ".join(" ".join(r) for r in v)
    return v


memo_words = sum(len(_memo_text(b).split()) for b in MEMO)

md = []
for kind, v in MEMO:
    if kind == "title":
        md.append(f"# {v}")
    elif kind == "meta":
        md.append("  \n".join(v))
    elif kind == "h":
        md.append(f"## {v}")
    elif kind == "p":
        md.append(v)
    elif kind == "ol":
        md.append("\n".join(f"{n}. {x}" for n, x in enumerate(v, 1)))
    elif kind == "ul":
        md.append("\n".join(f"- {x}" for x in v))
    elif kind == "table":
        md.append("\n".join(["| # | Action | Annual saving |", "|---|---|---:|"] + [f"| {a} | {b} | {c} |" for a, b, c in v[1:]]))
(OUT / "executive_memo.md").write_text("\n\n".join(md) + "\n", encoding="utf-8")

# HTML version, formatted for pasting into the Google Doc.
import html as _html
E = _html.escape
BLUE = "#073763"  # the template's header colour
P = "margin:0 0 5pt 0;line-height:1.2"
h = ["<html><head><meta charset='utf-8'></head><body style='font-family:Arial;font-size:10pt;color:#000'>"]
for kind, v in MEMO:
    if kind == "title":
        h.append(f"<p style='margin:0 0 6pt 0;font-size:16pt;font-weight:bold;color:{BLUE}'>{E(v)}</p>")
    elif kind == "meta":
        fmt = lambda line: "<b>{}:</b> {}".format(*map(E, line.split(": ", 1)))
        h.append("<p style='margin:0;line-height:1.3'>" + " &nbsp;&nbsp;|&nbsp;&nbsp; ".join(fmt(x) for x in v[:3]) + "</p>")
        h.append(f"<p style='margin:0;line-height:1.3'>{fmt(v[3])}</p>")
        h.append(f"<hr style='border:0;border-top:1.5pt solid {BLUE};margin:6pt 0'>")
    elif kind == "h":
        h.append(f"<p style='margin:8pt 0 3pt 0;font-size:11pt;font-weight:bold;color:{BLUE}'>{E(v)}</p>")
    elif kind == "p":
        h.append(f"<p style='{P}'>{E(v)}</p>")
    elif kind in ("ol", "ul"):
        h.append(f"<{kind} style='margin:0 0 5pt 0;padding-left:18pt'>")
        for x in v:
            head, sep, body = x.partition(": ")
            if kind == "ul" and sep:
                x_html = f"<b>{E(head)}:</b> {E(body)}"
            else:
                x_html = E(x).replace("Mitigation:", "<b>Mitigation:</b>")
            h.append(f"<li style='margin:0 0 3pt 0;line-height:1.2'>{x_html}</li>")
        h.append(f"</{kind}>")
    elif kind == "table":
        cell = "border:0.75pt solid #999;padding:3pt 5pt;vertical-align:top;font-size:10pt;font-weight:normal"
        h.append("<table style='border-collapse:collapse;width:100%;margin:0 0 5pt 0'>")
        for n, (a, b, c) in enumerate(v):
            if n == 0:
                st = f"{cell.replace('font-weight:normal', 'font-weight:bold')};background:{BLUE};color:#fff"
            elif n == len(v) - 1:
                st = cell.replace("font-weight:normal", "font-weight:bold")
            else:
                st = cell
                first, _, more = b.partition(". ")
                b_html = f"<b>{E(first)}.</b> <span style='font-weight:normal'>{E(more)}</span>"
            b_cell = E(b) if n in (0, len(v) - 1) else b_html
            h.append(f"<tr><td style='{st};width:4%'>{E(a)}</td><td style='{st}'>{b_cell}</td>"
                     f"<td style='{st};width:16%;text-align:right;white-space:nowrap'>{E(c)}</td></tr>")
        h.append("</table>")
h.append("</body></html>")
(OUT / "executive_memo.html").write_text("\n".join(h), encoding="utf-8")

# One-page check: render the memo to PDF (Letter, one-inch margins) with headless Chrome when it is installed.
import subprocess, tempfile
CHROME = "/Applications/Google Chrome.app/Contents/MacOS/Google Chrome"
if Path(CHROME).exists():
    with tempfile.TemporaryDirectory() as tmp:
        src = Path(tmp) / "memo.html"
        src.write_text("\n".join(h).replace("<head>", "<head><style>@page{size:letter;margin:1in}</style>"), encoding="utf-8")
        subprocess.run([CHROME, "--headless", "--disable-gpu", "--no-pdf-header-footer",
                        f"--print-to-pdf={OUT / 'executive_memo.pdf'}", src.as_uri()], capture_output=True, timeout=120)
    import re as _re
    memo_pages = len(_re.findall(rb"/Type\s*/Page[^s]", (OUT / "executive_memo.pdf").read_bytes()))
    assert memo_pages == 1, f"memo is {memo_pages} pages"


qc_rows = [l for l in QC.splitlines() if l.startswith("| ") and not l.startswith("| #") and "---" not in l]
qc_pass = sum("| PASS |" in l for l in qc_rows)
qc_fail = sum("| FAIL |" in l for l in qc_rows)
AI_QC = (OUT / "qc_ai_review.md").read_text(encoding="utf-8") if (OUT / "qc_ai_review.md").exists() else ""

# ---- Methodology ------------------------------------------------------------
# Sections of (title, intro, table). A table is [header_row, *rows], 2 or 3 columns.
PROMPT_DIR = ROOT / "prompts"
SESSION_PROMPTS = json.loads((PROMPT_DIR / "session_prompts.json").read_text(encoding="utf-8"))
SUB1 = (PROMPT_DIR / "subagent_1_independent_review.md").read_text(encoding="utf-8").strip()
SUB2 = (PROMPT_DIR / "subagent_2_blind_department_classifier.md").read_text(encoding="utf-8").strip()
SEARCHES = [l.split(". ", 1)[1] for l in (PROMPT_DIR / "web_searches.md").read_text(encoding="utf-8").splitlines()
            if l[:1].isdigit()]
qc_cells = [[c.strip() for c in l.strip("|").split("|")[1:4]] for l in qc_rows]
low = F["by_confidence"]["Low"]
REPO = "https://github.com/dimjingles/crossover-vendor-analysis"

METHOD = [
    ("1. Summary",
     f"All work was done in the Claude Code CLI (model: Claude Fable 5.2). Nothing was typed into this sheet by hand: Claude Code "
     f"classified the vendors, wrote the scripts that build every tab, and ran the quality checks. Result: {F['vendors']} vendors, "
     f"{usd(total)} of spend, {usd(saving)} of estimated annual savings ({saving / total:.1%}). Project folder: {REPO}",
     None),
    ("2. Approach", None, [
        ["Step", "What was done", "Output"],
        ["1. Read the source", "Claude Code read the exported vendor list and kept an untouched copy as the input.", "data/vendors_source.csv"],
        ["2. Set department rules", "Each vendor is classified by its primary function (the department that normally buys that kind "
         "of vendor), using five ordered rules: deal costs to M&A; function-specific tools and services to that function; "
         "company-wide software to SaaS; physical workplace to Facilities; everything else to G&A.", "Rules in build.py and the README"],
        ["3. Classify every vendor", "Department (from the Config tab), one-line description, action and written rationale. "
         "Vendors in the same situation share one rationale template so they are treated consistently.", "data/classifications.psv"],
        ["4. Verify unknowns", f"{len(SEARCHES)} web searches on the larger vendors that could not be identified from the name. "
         "Vendors still unconfirmed are marked Low confidence, not given an invented description.", "prompts/web_searches.md"],
        ["5. Apply the acquisition lens", "Deal advisers and prior-owner fees terminate; back-office vendors consolidate into "
         "the parent company; satellite offices close.", "Suggestions and Rationale columns"],
        ["6. Quantify savings", "Saving = cost x a stated rate (Terminate 100%, Consolidate 30%, Optimize 10%), with documented "
         "exceptions such as 0% for statutory charges and unverified vendors, 20% for audit and legal, 15% for Salesforce.",
         "Est. Annual Savings column"],
        ["7. Roll up and write", "The Top 3 tab and the memo are generated by script; every dollar figure and count is "
         "computed from the vendor rows. Wording such as site counts and assumed rates is written by hand.", "make_workbook.py"],
        ["8. Quality-check", "Automated checks, an independent AI review, and a blind re-classification of every department "
         "(section 5).", "output/qc_report.md and review logs"],
    ]),
    ("3. Tools", None, [
        ["Tool", "Used for"],
        ["Claude Code CLI", "Everything: reading files, reasoning about each vendor, writing and running scripts, web search, git."],
        ["Claude Code sub-agents", "Two independent reviews run in separate contexts (prompts in section 4)."],
        ["Python 3 scripts written by Claude Code", "build.py (join, validate, savings model), qc.py (automated checks), "
         "make_workbook.py (generates the tabs and memo)."],
        ["Web search (inside Claude Code)", "Identifying vendors that could not be recognised from the name."],
        ["git and GitHub", "Project folder with inputs, scripts, outputs, prompts and README."],
        ["Google Sheets and Google Docs", "Submission only: the workbook is imported into this sheet; the memo is a Google Doc."],
    ]),
    ("4. Prompts", "4a. Prompts I typed into Claude Code, verbatim and in order. Long pasted material is summarised in [brackets].", [
        ["#", "Prompt", "What Claude Code did"],
        *[[str(n), q, a] for n, (q, a) in enumerate(SESSION_PROMPTS, 1)],
    ]),
    ("4b. Prompts Claude Code wrote for its sub-agents (verbatim; file paths shortened)", None, [
        ["Sub-agent", "Prompt", "Result"],
        *[["Independent reviewer" if n == 0 else "", l,
           "29 findings; 26 applied. Savings fell from $2,276,944 to $1,801,526 at that point." if n == 0 else ""]
          for n, l in enumerate(x for x in SUB1.splitlines() if x.strip())],
        *[["Blind department classifier" if n == 0 else "", l,
           "Agreed on 370 of 386 departments; 4 changes accepted, 12 kept with reasons." if n == 0 else ""]
          for n, l in enumerate(x for x in SUB2.splitlines() if x.strip())],
    ]),
    (f"4c. Web search queries run by Claude Code ({len(SEARCHES)})", "; ".join(SEARCHES), None),
    ("5. Quality checks and evidence", f"5a. Automated checks (qc.py): {qc_pass} of {qc_pass + qc_fail} pass.", [
        ["Check", "Result", "Evidence"],
        *qc_cells,
    ]),
    ("5b. Other checks", None, [
        ["Check", "What it looked for", "Outcome"],
        ["Alignment guard", "Each classification line carries a vendor-name key; build.py refuses to write output if a key "
         "does not match its source row.", "A description cannot shift onto the wrong vendor."],
        ["Independent AI review", "Wrong descriptions, wrong departments, unrealistic or inconsistent recommendations, vague "
         "descriptions, implausible savings. All 386 rows read; top 100 by spend closely.",
         "29 findings, 26 applied. Main effect: savings rates made more conservative. Log: output/qc_ai_review_findings.md"],
        ["Blind department re-check", "A second sub-agent classified all 386 vendors from names, neutral descriptions and the "
         "rules only, with none of my departments or assumptions.",
         "370 of 386 agreed (95.9%). 16 disagreements adjudicated. Log: output/department_recheck.md"],
        ["Final independent review", "A third sub-agent graded the whole submission against the brief with fresh eyes.",
         "35 findings: 26 applied, 3 partly, 5 left with reasons, 1 is the sheet re-import. Log: output/qc_final_review.md"],
        ["Memo length", "The memo was rendered to PDF at Letter size with one-inch margins.", "One page. Copy: output/executive_memo.pdf"],
    ]),
    ("6. Corrections made after review", None, [
        ["Issue found", "Root cause", "Fix"],
        ["Salesforce classified as Engineering", "I inferred from its size and the Salesforce-related vendors around it that "
         "the product was built on Salesforce, and let that theory override what the vendor is (a CRM, a Sales tool). The first "
         "AI review missed it because the reviewer was given my theory as context.",
         "Department rules written down (function first, no company-specific override); all 386 re-run through a blind "
         "classifier. 6 departments changed, including Salesforce and PDF Butler to Sales."],
        ["Savings rates too optimistic", "First-pass rates assumed full savings on items that only partly go away (audits, "
         "agency hiring, duplicate vendor records).", "Rates lowered and documented; total reduced by $475,418 (from $2,276,944 to $1,801,526)."],
        ["Memo first placed in the sheet", "The memo tab's instruction was truncated when read, hiding the request for a Google Doc.",
         "Memo moved to a Google Doc; the tab holds the link."],
        ["Final independent review of the whole submission", "A fresh sub-agent with the assignment brief and grading "
         "criteria, and none of my reasoning, graded every deliverable and recomputed the numbers (prompt in "
         "prompts/subagent_3_final_review.md).",
         f"35 findings, log in output/qc_final_review.md. All figures reconciled. Fixes: Salesforce contract-type "
         f"caveat, consistent rates for like vendors, statutory rows removed from Opportunity 2, run-rate shown "
         f"excluding fees that end anyway. Total reduced from $1,801,526 to {usd(saving)}."],
        ["HRsolution moved to Finance, then back", "The blind pass keyed on the word payroll; the service is employer of record, "
         "a people cost.", "Kept in G&A; payroll rule tightened."],
    ]),
    ("7. Limitations", None, [
        ["Limit", "Detail"],
        ["No contracts, invoices or usage data", "Everything is inferred from vendor names and 12 months of spend. Savings are "
         "estimates to confirm against contracts; exit costs are not netted off."],
        ["Unidentified vendors", f"{low['vendors']} vendors ({usd(low['spend'])}, {low['spend'] / total:.1%} of spend) are Low "
         "confidence and carry almost no assumed saving."],
        ["One-off costs", f"{usd(ma[2])} of Opportunity 2 is deal and prior-owner cost that ends on its own."],
        ["Assumptions about the parent company", "Back-office savings assume the parent has an auditor, counsel and payroll provider to join."],
    ]),
]

md = ["# Methodology", ""]
for title, intro, table in METHOD:
    md += [f"## {title}", ""]
    if intro:
        md += [intro, ""]
    if table:
        cell = lambda s: s.replace("|", "\\|").replace("\n", "<br>")
        md += ["| " + " | ".join(table[0]) + " |", "|" + "---|" * len(table[0])]
        md += ["| " + " | ".join(cell(c) for c in r) + " |" for r in table[1:]]
        md.append("")
(OUT / "methodology.md").write_text("\n".join(md), encoding="utf-8")

# ---- Workbook ---------------------------------------------------------------
# Fill the original assessment template so its formatting (fonts, colours,
# column widths, dropdowns) is preserved. Only values are written; styles are
# copied from neighbouring template cells for anything the template lacks.
from copy import copy
from openpyxl import load_workbook
from openpyxl.styles import Alignment

TEMPLATE = ROOT / "data" / "template" / "template.xlsx"
MEMO_DOC = "https://docs.google.com/document/d/19NjtPyFmHyLvt-GhcvQYQvNUPDNDbir6Nda--FKz-C4/edit?usp=sharing"
wb = load_workbook(TEMPLATE)


def put(ws, ref, value, like=None, wrap=None):
    c = ws[ref]
    c.value = value
    if like is not None:
        c._style = copy(ws[like]._style)
    if wrap is not None:
        a = copy(c.alignment)
        a.wrap_text, a.vertical = wrap, "top"
        c.alignment = a
    return c


ws = wb["Vendor Analysis Assessment"]
rows = list(csv.reader((OUT / "vendor_analysis_completed.csv").open(encoding="utf-8", newline="")))
for col, head in zip("FGHI", ("Rationale", "Confidence", "Est. Annual Savings (USD)", "Top 3 Opportunity")):
    put(ws, f"{col}1", head, like="E1")
for n, r in enumerate(rows[1:], start=2):
    # Row alignment guard (prefix only: the template escapes some damaged characters differently).
    assert str(ws[f"A{n}"].value).strip()[:4] == r[0].strip()[:4], (n, ws[f"A{n}"].value, r[0])
    put(ws, f"B{n}", r[1], like=f"A{n}")
    put(ws, f"D{n}", r[3], like=f"A{n}", wrap=True)
    put(ws, f"E{n}", r[4], like=f"A{n}")
    put(ws, f"F{n}", r[5], like=f"A{n}", wrap=True)
    put(ws, f"G{n}", r[6], like=f"A{n}")
    put(ws, f"H{n}", float(r[7].replace("$", "").replace(",", "")), like=f"C{n}")
    put(ws, f"I{n}", int(r[8]) if r[8] else None, like=f"A{n}")
for col, w in zip("FGHI", (70, 12, 16, 14)):
    ws.column_dimensions[col].width = w

ws = wb["Top 3 Opportunities"]
put(ws, "D1", "Estimated Annual Savings (USD)", like="C1")
for n, (title, text, s) in enumerate(OPPS, start=2):
    put(ws, f"B{n}", title, wrap=True)
    put(ws, f"C{n}", text, wrap=True)
    put(ws, f"D{n}", s, wrap=True).number_format = '"$"#,##0'
    ws[f"A{n}"].alignment = Alignment(vertical="top")
put(ws, "A5", "Total", like="A4")
put(ws, "C5", TOP3_TOTAL, wrap=True)
put(ws, "D5", "=SUM(D2:D4)", like="A4").number_format = '"$"#,##0'
ws.column_dimensions["C"].width = 100
ws.column_dimensions["D"].width = 20

ws = wb["Methodology"]
from openpyxl.styles import Font, PatternFill
ws.row_dimensions[2].height = None
head_style = copy(ws["A1"]._style)          # the template's dark blue header
body_font = copy(ws["A2"].font)
bold_font = copy(body_font)
bold_font.bold = True
sub_fill = PatternFill("solid", fgColor="D9E2F3")
top = Alignment(wrap_text=True, vertical="top")
for col in "BC":
    ws[f"{col}1"]._style = copy(head_style)
ws.merge_cells("A1:C1")
ws.row_dimensions[1].height = 32
WIDTHS = (30, 95, 60)
# Wrapped lines a text needs in a column of the given width (Arial 8: about 1.15 characters per width unit).
lines = lambda s, w: sum(max(1, -(-len(x) // int(w * 1.15))) for x in str(s).split("\n")) if s else 1
row = 3
for title, intro, table in METHOD:
    main = title[:1].isdigit() and title[1] == "."
    for col in "ABC":
        c = ws[f"{col}{row}"]
        if main:
            c._style = copy(head_style)
        else:
            c.font, c.fill = bold_font, sub_fill
    ws[f"A{row}"].value = title
    ws[f"A{row}"].alignment = Alignment(vertical="center")
    ws.merge_cells(f"A{row}:C{row}")
    row += 1
    if intro:
        c = ws[f"A{row}"]
        c.value, c.font, c.alignment = intro, body_font, top
        ws.merge_cells(f"A{row}:C{row}")
        ws.row_dimensions[row].height = 11 * lines(intro, sum(WIDTHS)) + 4
        row += 1
    if table:
        ncol = len(table[0])
        for r_i, r in enumerate(table):
            cells = list(r) + [""] * (3 - ncol)
            for col, v in zip("ABC", cells):
                c = ws[f"{col}{row}"]
                c.value, c.alignment = v, top
                c.font = bold_font if r_i == 0 else body_font
                if r_i == 0:
                    c.fill = sub_fill
            if ncol == 2:
                ws.merge_cells(f"B{row}:C{row}")
            ws_w = WIDTHS if ncol == 3 else (WIDTHS[0], WIDTHS[1] + WIDTHS[2], 1)
            ws.row_dimensions[row].height = 11 * max(lines(v, w) for v, w in zip(cells, ws_w)) + 4
            row += 1
    row += 1
for col, w in zip("ABC", WIDTHS):
    ws.column_dimensions[col].width = w

ws = wb[[s for s in wb.sheetnames if "Recommendations" in s][0]]
put(ws, "A2", MEMO_DOC, wrap=True)

xlsx = OUT / "Vendor Analysis Assessment - Vincent Chan.xlsx"
wb.save(xlsx)
print(f"Memo: {memo_words} words. Top 3 {usd(top3)}; total {usd(saving)}; other {usd(rest)}")
print(f"Wrote {xlsx.name}, top3_opportunities.md, executive_memo.md, methodology.md")
