You are an independent grader reviewing a candidate's submission for a hiring assessment. Be critical and specific. Do NOT edit any files; only report.

## The assignment ("Vendor Spend Strategy Memo", 2 hours)
The candidate acts as VP of Operations for an acquired company, doing acquisition due diligence on ~400 vendors to find major cost savings and present to senior leadership. The work must be done in the Claude Code CLI, with a project folder and README explaining everything.
- Part 1: for each vendor assign a Department (from a fixed list: Engineering, Facilities, G&A, Legal, M&A, Marketing, SaaS, Product, Professional Services, Sales, Support, Finance), a one-line Description of what the vendor does, and one of Terminate / Consolidate / Optimize.
- Part 2: "Top 3 Opportunities" tab: title, explanation, estimated annual savings.
- Part 3: "Methodology" tab: approach, tools, prompts used, and how quality was validated, with evidence.
- Part 4: 1-page executive memo to CEO and CFO (findings, recommendations, timeline, implementation, risks). Busy readers; don't overemphasise the obvious. Delivered as a Google Doc linked from the sheet.
Grading criteria: accurate departments; specific descriptions (not "business services provider"); realistic recommendations with risks considered; Top 3 financially justified; documented QC; clean memo with no math errors; savings "significant enough to move the needle for a $1 billion business"; well-organised project folder.

## What to review
Project folder: [path]. Start with README.md. Deliverables are in output/: vendor_analysis_completed.csv (Part 1, 386 rows; source is data/vendors_source.csv), top3_opportunities.md (Part 2), methodology.md (Part 3), executive_memo.md and executive_memo.pdf (Part 4), and the .xlsx workbook that gets imported into Google Sheets (inspect with openpyxl). Scripts: build.py, qc.py, make_workbook.py. Prompts log: prompts/.
Vendor names in the source were deliberately altered by the assessment and some have encoding damage; that is not a candidate error.

## What to check
1. Part 1: sample at least the top 60 vendors by spend plus 60 others spread through the file. Wrong departments, factually wrong or vague descriptions, unrealistic or inconsistent actions (same kind of vendor treated differently), rationale contradicting the action.
2. Numbers: recompute independently from the CSV: total spend, total savings, each Top 3 figure, counts quoted anywhere. Check every number in the memo, Top 3, methodology, README and workbook agrees with every other and with the CSV. Report any mismatch with both values and locations.
3. Top 3: is each financially justified and realistic? Are assumptions stated? Anything a CFO would challenge?
4. Memo: one page? Clear ask, timeline, implementation, risks? Anything unclear, unsupported, missing, or inconsistent with other deliverables?
5. Methodology and README: complete, accurate, consistent with what the scripts actually do? Stale statements? Claims not backed by a file in the repo?
6. Workbook: do all tabs carry the content; anything blank, truncated, misformatted, or inconsistent with the md files?
7. Project folder: organisation, stray or missing files, does the documented pipeline exist. Do not run anything that writes files; read only.
8. How it stacks against each grading criterion, including where it is weakest.

## Report format
A prioritised list of concrete findings, most important first: location | what is wrong | suggested fix | severity (error / should-fix / judgment call). Cap at 35. Then a short verdict per grading criterion. State what you checked and what you did not. Label anything you could not verify.
