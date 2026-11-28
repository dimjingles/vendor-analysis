You are an independent quality reviewer for a vendor spend analysis. Do not edit any files; only report.

Read output/vendor_analysis_completed.csv (386 vendor rows). Columns: vendor name, Department, last-12-month cost, one-line description, Suggestion (Terminate / Consolidate / Optimize), Rationale, Confidence, Est. Annual Savings.

Context: the company is an acquired B2B software company (apparently a Salesforce-native product sold to telecoms, offices in London, Zagreb, Split, Chennai, Melbourne, Singapore). The analysis is acquisition due diligence by a VP of Operations looking for cost savings. Vendor names in the source have been lightly modified and some have character-encoding damage; that is expected and not an error.

Allowed departments (fixed list): Engineering, Facilities, G&A, Legal, M&A, Marketing, SaaS, Product, Professional Services, Sales, Support, Finance. Conventions used: product platform and developer tooling = Engineering; company-wide business software = SaaS; benefits, recruiting, team events, travel, meals, IT hardware and unidentified payees = G&A; offices, utilities, telecoms, supplies, couriers = Facilities; deal advisers and prior-owner fees = M&A.

Review every row and look for:
1. Factually wrong descriptions of well-known vendors (you know what Salesforce, Navan, Kimble, Peakon, Intralinks etc. do).
2. Department assignments that contradict the conventions above or are clearly wrong.
3. Recommendations that are unrealistic or inconsistent: e.g. "Consolidate" where no peer vendor exists on the list, "Terminate" for something legally required or business-critical, the same kind of vendor treated differently in different rows, rationale text that contradicts the action.
4. Descriptions that are vague (e.g. "business services provider") where a more specific one is clearly possible from the name.
5. Savings estimates that look implausible for the stated action (e.g. a saving on a statutory fee).

Prioritise rows by spend: scrutinise the top 100 by cost closely, and skim the rest for patterns. You may use your own knowledge; web lookups are optional and should be limited to a handful.

Report back a concise list of concrete findings, most important first, each as: vendor name | what is wrong | suggested fix. Cap at 40 findings. Also state how many rows you checked closely and how many you found no issue with. If something is a judgment call rather than an error, label it as such.
