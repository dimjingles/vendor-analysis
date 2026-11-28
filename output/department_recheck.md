# Department re-check

## What went wrong

Salesforce was first classified as Engineering. I had inferred, from its size (40% of spend) and the Salesforce-related vendors around it (a Salesforce-native PSA tool, a Salesforce document generator, a Salesforce recruiter), that the company's product was built on Salesforce, and classified it by that inferred role. That put a theory about the company ahead of what the vendor is: a CRM, which is a Sales tool. The brief also says names and costs were modified, so reasoning from spend size was unsafe. The first independent review did not catch it because the reviewer was given my theory as context.

## Process change

1. Department is decided by the vendor's primary function, using five ordered rules (in `build.py`). Company-specific inference may break a tie but never override the function.
2. Reviewers are no longer given my assumptions. A blind classifier sees only vendor names, neutral descriptions and the rules.
3. Every disagreement between the two passes is adjudicated and logged below.

## Result of the re-run on all 386 vendors

The blind classifier agreed with the existing department on 370 of 386 vendors (95.9%).

| Vendor | Spend | Was | Blind pass | Decision | Reason |
|---|---:|---|---|---|---|
| Salesforce Uk Ltd-Uk | $3,117,226 | Engineering | Sales | **Changed to Sales** | CRM is a sales tool (fixed before the blind pass) |
| Cloudcrossing Bvba (PDF Butler) | $208,675 | Engineering | Sales | **Changed to Sales** | Sales document generation; same root cause as Salesforce |
| Ncc Services Limited | $3,036 | Engineering | Legal | **Changed to Legal** | Software escrow is a contract obligation managed by Legal |
| Epignosis Llc (TalentLMS) | $833 | Professional Services | SaaS | **Changed to SaaS** | Learning management is company-wide software |
| Lider Media D.O.O. | $80 | Marketing | G&A | **Changed to G&A** | A magazine subscription is not marketing spend |
| 6Sense Insights Inc | $76 | Sales | Marketing | **Changed to Marketing** | Account-based marketing platform |
| Hr Solution International Gmbh, Hrsolution International Ag | $87,810 | G&A | Finance | Kept G&A | Employer-of-record employs staff on the company's behalf, which is a people cost (rule 5), like the staffing vendors. Briefly moved to Finance on the "payroll" keyword, then reverted on review |
| Acclime Usa, Inc | $4,995 | Legal | Finance | Kept Legal | Kept with the other three entity-management vendors it consolidates with |
| Adobe Systems Software | $3,929 | Marketing | SaaS | Kept Marketing | Creative Cloud is primarily a marketing/design tool |
| Urbani Eventi, Blink Events, Event Ors, Entrio | $2,131 | G&A | Marketing | Kept G&A | Treated as team events, consistent with the other event vendors |
| Smashing Media Ag | $850 | Engineering | Product | Kept Engineering | Front-end development conference and training |
| Tau On-Line D.O.O. | $534 | SaaS | Engineering | Kept SaaS | Service unconfirmed; general IT/web services |
| NSDL, Bigshare Services | $469 | Finance | Legal | Kept Finance | Share registry sits with equity administration (as Computershare) |

No savings figures changed: departments moved, actions and rates did not.

## How the counts reconcile

Six departments changed in total: Salesforce and Cloudcrossing (PDF Butler) were corrected by me before the blind pass, as the root-cause fix, and 4 more were accepted from the blind classifier. The blind classifier then disagreed with the corrected list on 16 vendors: those 4 accepted changes plus 12 kept with a recorded reason. 386 - 16 = 370 agreed (95.9%). Raw classifier input and output: `output/evidence/blind_input.csv` and `output/evidence/blind_output.csv`.
