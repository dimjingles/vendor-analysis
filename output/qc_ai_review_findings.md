# Independent AI review: findings and what was done

Reviewer: a separate Claude Code sub-agent given the output CSV, my business-context assumptions, the department conventions and a review checklist (prompt in `prompts/subagent_1_independent_review.md`). It read all 386 rows, the top 100 by spend closely. 71 of the top 100 had no issue. Savings total before the review: $2,276,944. After: $1,801,526.

| # | Vendor(s) | Finding | Disposition |
|---|---|---|---|
| 1 | Salesforce | Saving used 20% but the rationale text said 5-10%; OEM pricing may not flex with seat counts | Applied: 15% with a stated 10-20% range, confidence Medium |
| 2 | RSM, Houlihan Lokey, Intralinks, Vector Capital | One-off deal costs end anyway; not a negotiated run-rate saving | Kept Terminate; memo and Top 3 state this amount is one-off cost falling away |
| 3 | GPT Space&Co, WeWork Singapore | 100% saving ignores replacement desks | Applied: 70%, confidence Medium |
| 4 | TOG, Zagrebtower, Innovent | High confidence without lease terms | Applied: Medium, "subject to break date" |
| 5 | BDO and other audit firms | 40% saving on statutory audit is implausible | Applied: audit template 20%, BDO Medium |
| 6 | Four recruitment agencies | 100% assumes zero agency hiring | Applied: 70%, Medium |
| 7 | Weking | May be a property company; possible second Zagreb lease | Applied to description and rationale; still Low, $0 |
| 8 | Big Frontier (Cult of Monday) | May be a Salesforce recruiter, not marketing | Applied: moved to G&A, described as unconfirmed, $0 until verified |
| 9 | Tmforum | Consolidate with only its own duplicate; fee is tiered | Applied: Optimize |
| 10 | Sodexo / Pluxee | Pass-through benefit; merge saves nothing | Applied: $0 |
| 11 | Navan Inc, HRsolution AG, Tm Forum | Saving booked for merging duplicate records | Applied: duplicate template $0 |
| 12 | Athlete Service | Cycle-to-work purchase treated unlike Green Commute | Applied: Optimize, $0 |
| 13 | Jensten | Mostly pass-through premiums; 30% too high | Applied: 10%, Medium |
| 14 | UK law firms | 40% aggressive and inconsistent with other countries | Applied: 20% |
| 15 | Six individual payees | Re-routing payment is a control fix, not a saving | Applied: $0 |
| 16 | Unidentified vendors | Inconsistent Optimize vs Terminate | Applied: explicit rule (under $5K Terminate, $5K and over verify first), all $0 |
| 17 | Acclime, Intertrust, Capitol Services | Same function split across Finance and Legal | Applied: all Legal |
| 18 | Caterers | In Facilities while meals are G&A | Applied: moved to G&A |
| 19 | One-off discretionary spend | Rates varied 50% / 100% | Applied: single 50% rate |
| 20 | Crowe Horwath, TP Prime | Conflicting rationales; TEB wrongly listed as an adviser | Applied |
| 21 | Mercer | Saving booked while expanding its role | Applied: $0 |
| 22 | FastSpring | Misdescribed as the company's payment platform | Applied: reseller-billed software, SaaS, Optimize |
| 23 | JLL, CBRE | "Likely" with High confidence | Applied: Medium |
| 24 | Sage, Planful | Depends on acquirer's systems | Applied: Medium |
| 25 | Bigshare | Called a statutory charge but is a private registrar | Applied: reworded |
| 26 | GrantTree | Suggested using the audit firm (independence issue) | Applied: reworded |
| 27 | Google Ireland | "Workspace and/or Ads" is vague | Partly applied: reworded, Medium; needs an invoice to settle |
| 28 | Peakon / PerformancePro | Different functions treated as duplicates | Applied: assumption stated, Medium |
| 29 | Kimble, Workato | Department is defensible either way | No change (judgment call) |

Not changed by this review: one-off event venues stay Terminate. This review also did not question Salesforce being classed as Engineering, because the reviewer had been given that assumption as context; it was corrected later in the blind department re-check (see `department_recheck.md`).
