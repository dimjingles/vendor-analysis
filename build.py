#!/usr/bin/env python3
"""Build the completed vendor analysis from the source list + classifications.

Inputs
  data/vendors_source.csv     the assessment file, untouched
  data/classifications.psv    one pipe-separated line per vendor, same order

Outputs
  output/vendor_analysis_completed.csv   original 5 columns filled in, plus Rationale,
                                         Confidence, Est. Annual Savings, Top 3 Opportunity
  output/summary.md                      spend by department / recommendation
  output/figures.json                    the numbers every written deliverable is generated from

The script refuses to write anything if the two inputs are misaligned or a
value is outside the allowed sets, so a bad edit cannot silently shift rows.
"""
import csv
import json
import sys
from collections import defaultdict
from pathlib import Path

ROOT = Path(__file__).resolve().parent
SOURCE = ROOT / "data" / "vendors_source.csv"
CLASSIFICATIONS = ROOT / "data" / "classifications.psv"
OUT_DIR = ROOT / "output"

ACTIONS = {"Terminate", "Consolidate", "Optimize"}
# Department list comes from the Config tab of the assessment spreadsheet.
#
# Department rules. A vendor is classified by its PRIMARY FUNCTION (the
# department that normally buys and owns that kind of vendor), never by a
# theory of how this particular company might use it. First rule that fits:
#   1. Deal and ownership costs (advisers, data rooms, owner fees) -> M&A
#   2. A tool or service serving one function goes to that function:
#      CRM, sales intelligence/engagement, sales documents, customer
#      procurement portals -> Sales; marketing automation, ads, PR, SEO,
#      conferences, associations, merchandise, print -> Marketing; cloud,
#      developer tools, monitoring, outsourced development, technical
#      training -> Engineering; product management and design -> Product;
#      accounting, audit, tax, payroll processing, banking, insurance
#      broking, equity administration -> Finance (employer-of-record and
#      staffing are people costs and fall to rule 5); law firms, entity management, IP, escrow,
#      regulatory fees -> Legal; PSA, certification delivery -> Professional
#      Services; helpdesk and remote-support tooling -> Support
#   3. Company-wide business software with no single owner -> SaaS
#   4. Physical workplace (offices, utilities, telecoms, supplies, pantry,
#      couriers, parking) -> Facilities
#   5. Everything else (benefits, recruiting, travel, meals, events, IT
#      hardware, individuals, unidentified payees) -> G&A
DEPARTMENTS = {
    "Engineering", "Facilities", "G&A", "Legal", "M&A", "Marketing", "SaaS",
    "Product", "Professional Services", "Sales", "Support", "Finance",
}
CONFIDENCE = {"": "High", "H": "High", "M": "Medium", "L": "Low"}

# --- Savings model -----------------------------------------------------------
# Estimated annual saving = last-12-month cost x a savings rate. The rate is
# the first match of: vendor override, rationale-template rate, action default.
ACTION_RATE = {"Terminate": 1.00, "Consolidate": 0.30, "Optimize": 0.10}
TEMPLATE_RATE = {
    "statutory": 0.0,   # government / statutory charges cannot be reduced
    "dup": 0.0,         # merging a duplicate record does not remove the spend
    "person": 0.0,      # re-routing a payment is a control fix, not a saving
    "unknown": 0.0,     # unidentified payees: nothing assumed until verified
    "travel": 0.10,     # spend continues, booked through Navan at better rates
    "health": 0.15,     # pooled pricing; cover itself continues
    "audit": 0.20, "legal_uk": 0.20,  # audits and legal work are still required
    "recruit": 0.70,    # some approved hiring will still need an agency
    # one-off discretionary spend: half is assumed to reappear on expenses
    "meal": 0.50, "tail": 0.50, "event": 0.50, "gift": 0.50,
}
VENDOR_RATE = {  # key prefix -> rate, with the reason
    "Salesforce Uk": 0.15,     # licence true-down plus renewal discount (range 10-20%)
    "Gpt Space": 0.70, "Wework Singapore": 0.70,  # net of on-demand desks
    "Big Frontier": 0.0,       # unverified vendor: no saving assumed
    "Sodexo": 0.0, "Pluxee": 0.0,              # pass-through meal benefit
    "Athlete Service": 0.0, "Mercer": 0.0, "Bigshare": 0.0,
    "Jensten": 0.10, "Shoff Darby": 0.10,      # mostly pass-through insurance premiums
    "Care Health": 0.15, "Icici Lombard": 0.15,  # same rate as the other health insurers
    "Hr Solution": 0.10,       # employer of record: mostly pass-through salaries, saving on the fee only
    "Pingo": 0.0, "Mosaic": 0.0, "Nefron": 0.0, "Bijeli": 0.0, "(Blank)": 0.0,  # unverified: no saving assumed
    "Crowe Horwath": 0.20,     # statutory audit continues
    "Tog Uk": 0.50,            # London reduced to a small hub
    "Zagrebtower": 0.40,       # surplus floor space handed back / sublet
    "Innovent": 0.40,          # single India site, renegotiated desk count
    "Weking": 0.0,             # unverified vendor: no saving assumed
    "Sveu": 0.0, "Studentski Centar": 0.0,   # pass-through student labour
    "Telefonica Global": 0.0, "Telef": 0.0,  # customer-mandated fees
    "Green Commute": 0.0, "Inside Edge": 0.0,  # employee-funded salary sacrifice
    "Australian Taxation": 0.0, "Cayman Islands": 0.0,
}

# --- Top 3 opportunities -----------------------------------------------------
LEASES = ("Tog Uk", "Zagrebtower", "Innovent", "Gpt Space", "Wework Singapore",
          "Work Easy", "Common Desk")
PAYROLL = ("Hr Solution", "Hrsolution", "Integrated Personnel", "Australian Payroll")


def opportunity(key, dept, template):
    if key.startswith("Salesforce Uk"):
        return 1
    if key.startswith("Ncc Services"):
        return 0  # escrow is a customer-contract requirement, not back-office consolidation
    if template == "statutory":
        return 0  # government charges are not part of any consolidation
    if dept in ("Finance", "Legal", "M&A") or template == "recruit" or key.startswith(PAYROLL):
        return 2
    if key.startswith(LEASES):
        return 3
    return 0


def savings_rate(key, action, template):
    for prefix, rate in VENDOR_RATE.items():
        if key.startswith(prefix):
            return rate
    if template in TEMPLATE_RATE:
        return TEMPLATE_RATE[template]
    return ACTION_RATE[action]

# Reusable rationales for vendor groups that share one recommendation.
TEMPLATES = {
    "audit": "Ten-plus audit, accounting and tax firms are used across entities. Consolidate to one global network firm (ideally the parent company's auditor) plus the minimum local statutory filers.",
    "legal_uk": "Several UK law firms are used ad hoc for similar employment/commercial work. Consolidate to a single panel firm on fixed fees.",
    "recruit": "Contingent recruitment agency fees. Stop agency hiring after the acquisition and run any approved roles through the parent company's talent team and LinkedIn.",
    "health": "Health cover is bought from a different insurer in each country. Consolidate under one global benefits broker/programme (e.g. via Mercer) for pooled pricing.",
    "telecom": "Several UK telephony/connectivity providers (NSN, BT, Inet Telecoms, Avoxi). Consolidate to one provider.",
    "hardware": "IT equipment is bought from many retailers and resellers. Consolidate to one reseller per region with standard device bundles.",
    "apple": "Apple hardware is bought through four separate Apple entities/stores. Consolidate under one Apple Business account or a single reseller.",
    "pmtools": "Overlapping work-management tools (Atlassian direct, Veniture, Trello, Smartsheet, Aha!). Standardise on the Atlassian suite under one contract.",
    "salesintel": "Three overlapping sales-intelligence tools (Cognism, Lusha, 6sense). Keep one.",
    "monitoring": "Overlapping monitoring/logging tools (SolarWinds, Papertrail, Uptime Robot). Consolidate, ideally onto AWS-native monitoring.",
    "domains": "Domains and DNS are split across registrars (GoDaddy, DNSimple). Consolidate into one registrar or AWS Route 53.",
    "cosec": "Corporate secretarial/entity compliance is split across providers (Acclime, Acclime USA, Intertrust, Capitol Services). Consolidate to one global entity-management provider.",
    "courier": "Many courier and postal providers for small volumes. Consolidate to one courier account.",
    "merch": "Several promotional-merchandise suppliers. Consolidate to one supplier and one annual order.",
    "print": "Several ad hoc print shops. Consolidate to one online print supplier.",
    "catering": "Multiple caterers and meal-delivery services. Consolidate to one preferred caterer per office.",
    "pantry": "Office pantry and drinks are bought from several shops and distributors. Consolidate to one scheduled delivery per office.",
    "supplies": "Office supplies are bought through several retail accounts. Consolidate into one Amazon Business (or equivalent) account with approval rules.",
    "occmed": "Four occupational-medicine clinics are used for the same mandatory employee medical exams. Consolidate to one provider with an agreed price list.",
    "travel": "Travel booked directly with the supplier, outside the corporate travel tool. Consolidate into Navan for negotiated rates and policy control.",
    "dup": "Duplicate vendor record for a supplier that is already on the list. Merge the records and contract under one entity.",
    "statutory": "Statutory or government charge; cannot be terminated or consolidated. Verify the assessed amount and pay on time to avoid penalties.",
    "event": "One-off team event / offsite spend. Discretionary: no ongoing vendor needed, close the record and govern future events through a per-head events budget.",
    "meal": "One-off meal or food purchase. Should not be an AP vendor: close the record and route through the expense policy / corporate card.",
    "gift": "One-off gift purchase. Discretionary: close the vendor record and route any future gifting through the expense policy.",
    "tail": "Low-value one-off purchase with no ongoing relationship. Close the vendor record and route any future spend through the corporate card.",
    "unknown": "Payee could not be identified and the spend is under $5K. Verify it with a budget owner within 30 days and stop payments only if nobody claims it. No saving is assumed until verified.",
    "person": "Individual, not a company. Pay contractors through a contract with a PO and reimbursements through the expense system (Navan), then close the AP vendor record.",
}


def parse_cost(text):
    return float(text.replace("$", "").replace(",", "").strip())


def load_classifications():
    rows = []
    for n, line in enumerate(CLASSIFICATIONS.read_text(encoding="utf-8").splitlines(), 1):
        if not line.strip() or line.startswith("#"):
            continue
        parts = line.split("|")
        if len(parts) not in (5, 6):
            sys.exit(f"{CLASSIFICATIONS.name}:{n}: expected 5 or 6 fields, got {len(parts)}")
        key, dept, desc, action, rationale = (p.strip() for p in parts[:5])
        conf = parts[5].strip() if len(parts) == 6 else ""
        template = ""
        if rationale.startswith("@"):
            template = rationale[1:]
            if template not in TEMPLATES:
                sys.exit(f"{CLASSIFICATIONS.name}:{n}: unknown template {rationale}")
            rationale = TEMPLATES[template]
        errors = []
        if dept not in DEPARTMENTS:
            errors.append(f"department {dept!r}")
        if action not in ACTIONS:
            errors.append(f"action {action!r}")
        if conf not in CONFIDENCE:
            errors.append(f"confidence {conf!r}")
        if not desc or not rationale:
            errors.append("empty description or rationale")
        if errors:
            sys.exit(f"{CLASSIFICATIONS.name}:{n}: invalid " + ", ".join(errors))
        rows.append((n, key, dept, desc, action, rationale, CONFIDENCE[conf], template))
    return rows


def main():
    with SOURCE.open(encoding="utf-8", newline="") as f:
        reader = csv.reader(f)
        header = next(reader)
        vendors = [r for r in reader if r and r[0].strip()]
    classified = load_classifications()

    if len(vendors) != len(classified):
        sys.exit(f"Row count mismatch: {len(vendors)} vendors vs {len(classified)} classifications")

    rows = []
    for src, (n, key, dept, desc, action, rationale, conf, template) in zip(vendors, classified):
        name = src[0].strip()
        if not name.lower().startswith(key.lower()):
            sys.exit(f"{CLASSIFICATIONS.name}:{n}: key {key!r} does not match vendor {name!r}")
        cost = parse_cost(src[2])
        saving = round(cost * savings_rate(key, action, template))
        rows.append({
            "name": src[0], "name_clean": name, "dept": dept, "cost_text": src[2], "cost": cost,
            "desc": desc, "action": action, "rationale": rationale, "confidence": conf,
            "saving": saving, "opportunity": opportunity(key, dept, template), "template": template,
        })

    OUT_DIR.mkdir(exist_ok=True)
    out_csv = OUT_DIR / "vendor_analysis_completed.csv"
    with out_csv.open("w", encoding="utf-8", newline="") as f:
        writer = csv.writer(f)
        writer.writerow(header[:5] + ["Rationale", "Confidence", "Est. Annual Savings (USD)", "Top 3 Opportunity"])
        for r in rows:
            writer.writerow([r["name"], r["dept"], r["cost_text"], r["desc"], r["action"],
                             r["rationale"], r["confidence"], f"${r['saving']:,}", r["opportunity"] or ""])

    total = sum(r["cost"] for r in rows)
    total_saving = sum(r["saving"] for r in rows)

    def group(field):
        agg = defaultdict(lambda: [0, 0.0, 0])
        for r in rows:
            a = agg[r[field]]
            a[0] += 1
            a[1] += r["cost"]
            a[2] += r["saving"]
        return dict(sorted(agg.items(), key=lambda kv: kv[1][1], reverse=True))

    def table(title, label, agg):
        lines = [f"## {title}", "", f"| {label} | Vendors | Spend (USD) | % of spend | Est. savings (USD) |",
                 "|---|---:|---:|---:|---:|"]
        for k, (cnt, spend, sav) in agg.items():
            lines.append(f"| {k} | {cnt} | ${spend:,.0f} | {spend / total:.1%} | ${sav:,.0f} |")
        return lines + [""]

    by_dept, by_action, by_conf = group("dept"), group("action"), group("confidence")
    summary = [
        "# Vendor analysis summary", "",
        f"{len(rows)} vendors, ${total:,.0f} total last-12-month spend. "
        f"Estimated annual savings ${total_saving:,.0f} ({total_saving / total:.1%} of spend).", "",
        *table("Spend by department", "Department", by_dept),
        *table("Spend by recommendation", "Recommendation", by_action),
        *table("Spend by classification confidence", "Confidence", by_conf),
    ]
    (OUT_DIR / "summary.md").write_text("\n".join(summary), encoding="utf-8")

    # Top 3 opportunities: every figure is a roll-up of the per-vendor rows.
    opps = {}
    for num in (1, 2, 3):
        members = sorted((r for r in rows if r["opportunity"] == num), key=lambda r: r["cost"], reverse=True)
        opps[num] = {
            "vendors": len(members),
            "spend": sum(r["cost"] for r in members),
            "saving": sum(r["saving"] for r in members),
            "members": [{k: r[k] for k in ("name_clean", "dept", "cost", "action", "saving", "template")} for r in members],
        }
    figures = {
        "vendors": len(rows), "total_spend": total, "total_saving": total_saving,
        "by_action": {k: {"vendors": v[0], "spend": v[1], "saving": v[2]} for k, v in by_action.items()},
        "by_dept": {k: {"vendors": v[0], "spend": v[1], "saving": v[2]} for k, v in by_dept.items()},
        "by_confidence": {k: {"vendors": v[0], "spend": v[1], "saving": v[2]} for k, v in by_conf.items()},
        "opportunities": opps,
        "top3_saving": sum(o["saving"] for o in opps.values()),
        "template_counts": {k: sum(1 for r in rows if r["template"] == k) for k in TEMPLATES},
        "top25_spend": sum(sorted((r["cost"] for r in rows), reverse=True)[:25]),
        "all_costs": [r["cost"] for r in rows],
        "top10_spend": sum(sorted((r["cost"] for r in rows), reverse=True)[:10]),
        "unknown_template_vendors": sum(1 for r in rows if r["template"] == "unknown"),
        "one_off_deal_cost": sum(r["cost"] for r in rows if r["dept"] == "M&A" and not r["name_clean"].startswith("Vector")),
    }
    (OUT_DIR / "figures.json").write_text(json.dumps(figures, indent=1), encoding="utf-8")

    print("\n".join(summary))
    for num, o in opps.items():
        print(f"Opportunity {num}: {o['vendors']} vendors, spend ${o['spend']:,.0f}, saving ${o['saving']:,.0f}")
    print(f"Top 3 saving ${figures['top3_saving']:,.0f}; all vendors ${total_saving:,.0f}")
    print(f"Wrote {out_csv.relative_to(ROOT)}, output/summary.md, output/figures.json")


if __name__ == "__main__":
    main()
