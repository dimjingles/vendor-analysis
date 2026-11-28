Classify 386 vendors into departments. Input: blind_input.csv with columns row, vendor, description (a one-line description of what each vendor does; some vendor names have character-encoding damage, ignore that).

Assign each vendor exactly one department from this fixed list: Engineering, Facilities, G&A, Legal, M&A, Marketing, SaaS, Product, Professional Services, Sales, Support, Finance.

Classify by the vendor's PRIMARY FUNCTION, i.e. the department that normally buys and owns that kind of vendor in a B2B software company. Do not speculate about how this particular company might use it. Apply these rules in order and use the first that fits:
1. Deal and ownership costs (M&A advisers, investment banks, deal data rooms, private-equity owner fees) -> M&A.
2. A tool or service that serves one function goes to that function:
   - CRM, sales intelligence, sales engagement, quoting/document generation for sales, customer procurement-portal fees -> Sales
   - marketing automation, advertising, PR, SEO, events and conferences, industry association memberships, promotional merchandise, print, creative/stock assets -> Marketing
   - cloud infrastructure, developer tools, code libraries, monitoring/logging, outsourced software development, technical training -> Engineering
   - product management, UX/design tools and training -> Product
   - accounting, audit, tax, payroll, banking, insurance broking, equity administration, credit data, finance software -> Finance
   - law firms, corporate secretarial/entity management, IP, notary, regulatory registrations, software escrow -> Legal
   - professional services delivery tooling (PSA), customer certification/exam delivery, project-management certification -> Professional Services
   - customer support / helpdesk / remote-support tooling -> Support
3. Business software used across the whole company with no single functional owner (productivity suites, messaging, e-signature, password managers, automation/integration, domains/DNS, HR/people software, learning management, general work-management tools) -> SaaS.
4. Physical workplace: office leases and coworking, utilities, telecoms and internet, parking, office supplies and pantry, couriers and post, cleaning, furniture, safety inspections, municipal property charges -> Facilities.
5. Everything else -> G&A: employee benefits and health insurance, recruitment and staffing, immigration, training and coaching not specific to one function, travel and hotels, meals and catering, team events and gifts, IT hardware purchases, individuals, and payees that cannot be identified.

Write the result to blind_output.csv with header `row,department,rule` and exactly 386 data rows, where rule is the rule number (and sub-function where relevant, e.g. "2-Sales") you applied. Use only the 12 department names exactly as spelled above. Verify the file has 386 rows and only valid department names before finishing. In your reply, list any rows where you felt two departments were genuinely defensible, with the row number, vendor and the two options.
