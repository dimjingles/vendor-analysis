# Final independent review: findings and dispositions

Reviewer: a separate Claude Code sub-agent given the assignment brief and grading criteria, and none of my reasoning or earlier review logs (prompt in `prompts/subagent_3_final_review.md`). It read every deliverable, script and prompt file, all 386 vendor rows and every workbook tab, and recomputed the totals, Top 3 figures and counts from the CSV. It did not check vendor identities against the web.

Its numbers check found every figure consistent with the CSV. It returned 35 findings: 26 applied, 3 partly applied, 5 left unchanged with a reason, 1 open (re-import of the final workbook into the live sheet).

Effect on the numbers: total savings $1,801,526 to $1,764,587; Opportunity 2 $549,086 to $530,901 and 62 to 60 vendors; Low-confidence vendors 52 to 53.

| # | Finding | Disposition |
|---|---|---|
| 1 | Live Google Sheet still shows the older Methodology tab | Open: needs the final workbook re-imported into the sheet (a manual step) |
| 2 | Salesforce saving assumes seat licensing; evidence suggests it may be a platform or reseller agreement | Applied: Top 3, vendor rationale, memo risk 3 and README now make confirming the contract type the first step and describe both routes; 15% kept as the estimate, range 10-20% |
| 3 | Opportunity 2 is mostly spend that ends anyway | Applied: Top 3 total row, memo total row and README show savings excluding the deal and prior-owner fees; recruiter assumption stated |
| 4 | Opportunity 2 membership is 'all Finance/Legal/M&A', including statutory rows and finance software | Applied: statutory rows removed from the opportunity (62 to 60 vendors); title and breakdown reworded to name finance software, broking and equity administration. Software was not split into a separate line |
| 5 | 'Seven sites' ignores a possible eighth (Weking) | Applied: Top 3 names it; memo risk 5 flags the $144K vendor for verification |
| 6 | Office reduction rates have no basis; people risk omitted | Applied: stated as assumptions with the value of each 10 points; retention added to memo risk 4 |
| 7 | Employer of record given 30% saving on pass-through salaries | Applied: 10%, on the service fee only |
| 8 | Brokers and health insurers carry different rates | Applied: brokers 10%, all health insurers 15% |
| 9 | Veniture: 30% under 'standardise on Atlassian' although it is the Atlassian channel | Applied: Optimize at 10% with its own rationale |
| 10 | 'No public record matched' on vendors that were never searched | Applied: reworded to 'could not be identified from the name; not researched (spend under $5K)' on 34 rows; kept on Mosaic Concept, which was searched |
| 11 | About 12% of descriptions are generic or non-descriptions | Partly applied: three descriptions that contradicted their rationale were fixed. Generic one-liners for small law firms, accountants and food outlets were left: nothing more is known from the name and I did not invent detail |
| 12 | '52 vendors unidentified' overstates; 37 are | Applied: memo says low-confidence; README gives both counts |
| 13 | Unverified vendors carrying a 10% saving; '(Blank)' High confidence at 100% | Applied: Pingo, Mosaic, Nefron, Bijeli Pijesak and (Blank) set to $0; (Blank) set to Low |
| 14 | README says the first reviewer saw only the CSV and a checklist | Applied: corrected |
| 15 | Stale pointer to the reviewer prompt | Applied |
| 16 | Department re-check counts do not visibly reconcile | Applied: reconciliation section added to department_recheck.md |
| 17 | Raw sub-agent evidence not in the repo | Partly applied: blind classifier input and output added under output/evidence/. The first reviewer's raw reply and the web search result pages were not retained; only the findings log and the queries exist |
| 18 | Manual QC item never recorded as done | Applied: all 27 rows read; list in data/manual_review.txt; qc.py now fails if an unread one appears |
| 19 | No cost to achieve or year-one figure | Partly applied: memo states year-one savings will be lower than the run rate and that exit costs are not netted off. No figure given: the data has no contract terms to base one on |
| 20 | Nothing frames the saving against a $1 billion business | Left, with a note in README Limitations: the list totals $7.9M and the saving is not inflated to fit |
| 21 | Timeline says 'exit or resize' London and Zagreb; India missing | Applied |
| 22 | 'Acquirer' and 'parent company' both used | Applied: 'parent company' throughout |
| 23 | 'Deal fees' includes owner monitoring fees | Applied: 'deal and prior-owner fees'; README notes the inference |
| 24 | 'Figures cannot disagree' overstated; brittle assert | Applied: claim narrowed to dollar figures and counts; assert removed |
| 25 | Memo PDF not produced by the pipeline | Applied: make_workbook.py renders it and stops if it is not one page |
| 26 | Workbook cost column sums to $7,887,360 against $7,887,359 quoted | Left: the template stores unrounded cents; the quoted figure is the sum of the whole-dollar source values. Costs are passed through untouched |
| 27 | Top 3 total row worded differently in sheet and markdown | Applied: one string |
| 28 | Opportunity members not traceable in the sheet | Applied: 'Top 3 Opportunity' column added to the vendor tab and CSV |
| 29 | Three descriptions contradict their rationale | Applied |
| 30 | Discretionary training treated differently (Calm Achiever vs coaching) | Left: Calm Achiever is a one-off course; the others are ongoing engagements whose scope is unknown |
| 31 | GoTo may be Support tooling | Left: product not identifiable from the name; department kept as SaaS |
| 32 | 6sense rationale says sales intelligence, department Marketing | Applied: rationale reworded |
| 33 | build.py docstring incomplete; stray qc_ai_review.md | Applied: docstring updated, fragment removed |
| 34 | BDO may itself be the group auditor; 20% unsupported | Left: stated in the rationale as depending on the parent company's auditor; flagged in memo risk 2 |
| 35 | Unknown payees under $5K: 'stop payments' wording is riskier than the memo's | Applied: rationale now says verify first, stop only if nobody claims it |
