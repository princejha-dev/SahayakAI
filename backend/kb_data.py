"""
SahayakAI Knowledge Base Entries
18 entries: rate cards, product sheets, policy snippets, FAQs
"""

KB_ENTRIES = [

    # ── RATE CARDS ────────────────────────────────────────────────────────────

    {
        "title": "Fixed Deposit Interest Rates — Retail",
        "category": "rate_card",
        "content": (
            "Fixed Deposit (FD) interest rates for retail customers (below Rs 2 crore) effective August 2026:\n"
            "- 7 days to 14 days: 3.50% per annum\n"
            "- 15 days to 29 days: 3.75% per annum\n"
            "- 30 days to 45 days: 4.00% per annum\n"
            "- 46 days to 90 days: 4.50% per annum\n"
            "- 91 days to 180 days: 5.50% per annum\n"
            "- 181 days to 364 days: 6.00% per annum\n"
            "- 1 year to less than 2 years: 6.80% per annum\n"
            "- 2 years to less than 3 years: 7.00% per annum\n"
            "- 3 years to less than 5 years: 6.90% per annum\n"
            "- 5 years to 10 years: 6.50% per annum\n"
            "Senior citizens receive an additional 0.50% per annum on all tenures. "
            "Interest is compounded quarterly. Premature withdrawal attracts a 1% penalty on the applicable rate."
        ),
    },

    {
        "title": "Savings Account Interest Rates",
        "category": "rate_card",
        "content": (
            "Savings account interest rates effective August 2026:\n"
            "- Balance below Rs 1 lakh: 3.50% per annum\n"
            "- Balance Rs 1 lakh to Rs 10 lakh: 4.00% per annum\n"
            "- Balance above Rs 10 lakh: 4.50% per annum\n"
            "Interest is calculated on daily closing balance and credited monthly. "
            "Minimum average monthly balance (AMB) required: Rs 5,000 for regular accounts, "
            "Rs 10,000 for premium accounts. Non-maintenance charge: Rs 500 per quarter."
        ),
    },

    {
        "title": "Home Loan Interest Rates",
        "category": "rate_card",
        "content": (
            "Home loan interest rates (floating, linked to RLLR) effective August 2026:\n"
            "- Loan up to Rs 30 lakh: RLLR + 0.25% (currently 8.50% per annum)\n"
            "- Loan Rs 30 lakh to Rs 75 lakh: RLLR + 0.50% (currently 8.75% per annum)\n"
            "- Loan above Rs 75 lakh: RLLR + 0.75% (currently 9.00% per annum)\n"
            "Current RLLR (Repo Linked Lending Rate): 8.25% per annum. "
            "Fixed rate option available at a premium of 0.50% over floating rate. "
            "Processing fee: 0.50% of loan amount, minimum Rs 5,000, maximum Rs 25,000."
        ),
    },

    {
        "title": "Personal Loan Interest Rates",
        "category": "rate_card",
        "content": (
            "Personal loan interest rates effective August 2026:\n"
            "- Salaried customers (salary account with bank): 10.50% to 13.00% per annum\n"
            "- Salaried customers (external salary): 11.00% to 14.50% per annum\n"
            "- Self-employed professionals: 12.00% to 15.50% per annum\n"
            "Rate depends on CIBIL score, income, and relationship tenure. "
            "Loan tenure: 12 to 60 months. Processing fee: 1.50% to 2.50% of loan amount. "
            "No prepayment charges after 6 EMIs."
        ),
    },

    # ── PRODUCT SHEETS ────────────────────────────────────────────────────────

    {
        "title": "Fixed Deposit — Product Sheet",
        "category": "product_sheet",
        "content": (
            "PRODUCT: Fixed Deposit (FD)\n"
            "Type: Debt instrument, bank deposit.\n"
            "Minimum deposit: Rs 1,000. No maximum limit.\n"
            "Tenure: 7 days to 10 years.\n"
            "Interest payout options: Monthly, quarterly, half-yearly, annually, or at maturity.\n"
            "Nomination: Available.\n"
            "Loan against FD: Up to 90% of FD value at FD rate + 2%.\n"
            "Auto-renewal: Available on maturity at prevailing rate.\n"
            "Tax: TDS applicable if annual interest exceeds Rs 40,000 (Rs 50,000 for seniors). "
            "FD under Section 80C (5-year tax-saver FD): Rs 1.5 lakh deduction limit, lock-in 5 years, premature withdrawal not allowed.\n"
            "RISK DISCLOSURE: Fixed deposits are insured by DICGC up to Rs 5 lakh per depositor per bank. "
            "Returns are fixed and not linked to market performance. "
            "Premature withdrawal may reduce effective yield due to penalty."
        ),
    },

    {
        "title": "Equity Mutual Fund — Product Sheet",
        "category": "product_sheet",
        "content": (
            "PRODUCT: Equity Mutual Fund (Large Cap / Flexi Cap categories)\n"
            "Type: Market-linked investment. Not a bank product. Distributed by bank as AMFI-registered distributor.\n"
            "Risk level: HIGH. Suitable for investors with 5+ year investment horizon and high risk tolerance.\n"
            "Returns: Not guaranteed. Historical returns of 10-15% CAGR are not indicative of future performance.\n"
            "NAV-based: Units allotted at applicable NAV. No fixed interest rate.\n"
            "Liquidity: Redeemable on any business day at current NAV (T+2 settlement for equity funds).\n"
            "Minimum investment: Rs 500 (SIP), Rs 1,000 (lump sum).\n"
            "Exit load: 1% if redeemed within 1 year.\n"
            "Expense ratio: 0.50% to 1.20% per annum (direct plan lower than regular).\n"
            "Taxation: LTCG above Rs 1.25 lakh taxed at 12.5%. STCG taxed at 20%.\n"
            "RISK DISCLOSURE: Mutual fund investments are subject to market risks. "
            "Read all scheme-related documents carefully before investing. "
            "Past performance is not a guarantee of future returns. "
            "The bank acts as a distributor, not an investment advisor. "
            "Investment decisions are the sole responsibility of the investor."
        ),
    },

    {
        "title": "ULIP — Unit Linked Insurance Plan Product Sheet",
        "category": "product_sheet",
        "content": (
            "PRODUCT: Unit Linked Insurance Plan (ULIP)\n"
            "Type: Insurance-cum-investment product. Regulated by IRDAI.\n"
            "Dual benefit: Life cover + market-linked investment returns.\n"
            "Sum assured: Minimum 10x annualised premium.\n"
            "Premium allocation: After deducting premium allocation charges (up to 5% in year 1).\n"
            "Fund options: Equity fund, balanced fund, debt fund — switchable.\n"
            "Lock-in period: 5 years. Partial withdrawal allowed after 5 years.\n"
            "Mortality charges: Deducted monthly from fund value based on age and sum assured.\n"
            "Policy administration charges: Rs 500/month.\n"
            "Risk level: MEDIUM to HIGH depending on fund choice.\n"
            "Tax benefit: Premium up to Rs 1.5 lakh deductible under Section 80C. "
            "Maturity proceeds tax-free under Section 10(10D) subject to conditions.\n"
            "RISK DISCLOSURE: ULIPs are insurance products with market-linked investment component. "
            "The investment risk is borne entirely by the policyholder. "
            "Returns are not guaranteed. Charges can significantly impact net returns, especially in early years. "
            "Not suitable for investors seeking guaranteed returns or short-term liquidity."
        ),
    },

    # ── POLICY SNIPPETS ───────────────────────────────────────────────────────

    {
        "title": "Policy: Advice vs Information — RM Guidelines",
        "category": "policy",
        "content": (
            "POLICY: Distinction between Information and Investment Advice (SEBI/RBI Guidelines)\n\n"
            "PERMITTED (Information — RM can provide):\n"
            "- Stating product features, interest rates, and charges from approved rate cards\n"
            "- Explaining how a product works (FD tenure, mutual fund categories, loan EMI calculation)\n"
            "- Sharing historical NAV data or past performance with mandatory disclaimer\n"
            "- Describing eligibility criteria and documentation requirements\n"
            "- Comparing bank's own products on objective parameters (rate, tenure, charges)\n\n"
            "NOT PERMITTED (Investment Advice — must escalate or refer to SEBI-registered advisor):\n"
            "- Recommending whether a specific customer should buy/sell/switch a market-linked product\n"
            "- Predicting future returns or assuring returns on market-linked products\n"
            "- Advising asset allocation (e.g., 'put 60% in equity, 40% in FD')\n"
            "- Recommending liquidation of existing investments to buy bank products\n"
            "- Using phrases like 'you should invest in', 'this is best for you', 'guaranteed returns'\n\n"
            "When in doubt: Provide factual information only and say 'Please consult a SEBI-registered investment advisor for personalised advice.'"
        ),
    },

    {
        "title": "Policy: KYC Requirements Summary",
        "category": "policy",
        "content": (
            "POLICY: Know Your Customer (KYC) Requirements\n\n"
            "All new account openings, loan applications, and investment purchases require valid KYC.\n\n"
            "Acceptable Identity Proof (any one):\n"
            "- Aadhaar card (mandatory for most transactions above Rs 50,000)\n"
            "- PAN card (mandatory for investments above Rs 50,000)\n"
            "- Passport\n"
            "- Voter ID\n"
            "- Driving licence\n\n"
            "Acceptable Address Proof (any one):\n"
            "- Aadhaar card\n"
            "- Utility bill (not older than 3 months)\n"
            "- Bank statement (not older than 3 months)\n"
            "- Passport\n\n"
            "PAN mandatory for:\n"
            "- Cash deposits/withdrawals above Rs 50,000 in a single day\n"
            "- Fixed deposits above Rs 50,000\n"
            "- Mutual fund investments above Rs 50,000\n"
            "- Any loan above Rs 2 lakh\n\n"
            "Re-KYC: Required every 2 years for high-risk customers, every 8 years for low-risk customers. "
            "Accounts with pending re-KYC may be restricted."
        ),
    },

    {
        "title": "Policy: Grievance Redressal and Escalation",
        "category": "policy",
        "content": (
            "POLICY: Customer Grievance Redressal\n\n"
            "Level 1 — Branch/RM: Resolve within 7 working days.\n"
            "Level 2 — Nodal Officer: Escalate if unresolved at Level 1. Resolution within 15 working days.\n"
            "Level 3 — Banking Ombudsman (RBI): Customer may approach if unresolved within 30 days.\n\n"
            "RM Responsibilities:\n"
            "- Log all customer complaints in CRM within 24 hours of receipt\n"
            "- Do not make verbal promises of resolution timelines beyond policy\n"
            "- Do not share another customer's information when addressing complaints\n"
            "- All refund/waiver decisions above Rs 5,000 require manager approval\n\n"
            "Prohibited: Discouraging customers from filing formal complaints. "
            "Every customer has the right to a written acknowledgment of their complaint."
        ),
    },

    {
        "title": "Policy: Anti-Money Laundering (AML) — RM Obligations",
        "category": "policy",
        "content": (
            "POLICY: Anti-Money Laundering (AML) and Suspicious Transaction Reporting\n\n"
            "Mandatory Reporting (Suspicious Transaction Report — STR):\n"
            "- Cash transactions above Rs 10 lakh in a single day\n"
            "- Multiple cash transactions structured to avoid Rs 10 lakh threshold (structuring)\n"
            "- Transactions inconsistent with customer's known business/income profile\n"
            "- Customer refuses to provide KYC documents without valid reason\n"
            "- Transaction requested by an unknown third party on behalf of customer\n\n"
            "RM Action:\n"
            "- Do NOT alert the customer that an STR is being filed (tipping off is a criminal offence)\n"
            "- File STR through internal compliance portal within 7 working days\n"
            "- Do not process the transaction if there is strong reason to suspect money laundering\n\n"
            "Penalties for non-compliance: PMLA 2002 — imprisonment up to 7 years + fine."
        ),
    },

    # ── FAQs ──────────────────────────────────────────────────────────────────

    {
        "title": "FAQ: FD Eligibility and Opening Process",
        "category": "faq",
        "content": (
            "Q: Who can open a Fixed Deposit with the bank?\n"
            "A: Any individual (resident Indian, NRI), HUF, company, trust, or institution can open an FD. "
            "Minors can open FDs jointly with a guardian.\n\n"
            "Q: What documents are needed to open an FD?\n"
            "A: Existing customers — no additional documents needed if KYC is up to date. "
            "New customers — PAN card + one address proof + one photo ID (Aadhaar preferred).\n\n"
            "Q: Can I open an FD online?\n"
            "A: Yes, through net banking or mobile app for amounts up to Rs 5 crore. "
            "Physical visit required for amounts above Rs 5 crore or for joint FDs.\n\n"
            "Q: What happens if I miss renewing my FD?\n"
            "A: If auto-renewal is enabled, FD renews at the prevailing rate for the same tenure. "
            "If not, matured amount is transferred to linked savings account."
        ),
    },

    {
        "title": "FAQ: Home Loan Eligibility",
        "category": "faq",
        "content": (
            "Q: Who is eligible for a home loan?\n"
            "A: Salaried individuals aged 21 to 60 years, and self-employed individuals aged 21 to 65 years. "
            "Minimum net monthly income: Rs 25,000 for salaried, Rs 2 lakh per annum for self-employed.\n\n"
            "Q: What is the maximum loan amount?\n"
            "A: Up to 80% of the property's market value (loan-to-value ratio). "
            "Maximum loan: Rs 5 crore for tier-1 cities, Rs 2 crore for other locations.\n\n"
            "Q: What documents are required?\n"
            "A: Identity proof, address proof, last 3 months salary slips, last 6 months bank statements, "
            "last 2 years ITR, property documents (sale agreement, title deed, NOC from builder).\n\n"
            "Q: How long does approval take?\n"
            "A: In-principle approval within 48 hours. Final sanction within 7 working days after document verification. "
            "Disbursement within 3 working days after legal and technical clearance."
        ),
    },

    {
        "title": "FAQ: Mutual Fund Investment Process",
        "category": "faq",
        "content": (
            "Q: How do I invest in mutual funds through the bank?\n"
            "A: Complete KYC (if not done), fill mutual fund application form, provide bank account details for redemption. "
            "Online: Available through mobile banking app under 'Investments' section.\n\n"
            "Q: What is the minimum SIP amount?\n"
            "A: Rs 500 per month for most equity funds. Rs 1,000 per month for ELSS (tax-saving) funds.\n\n"
            "Q: Can I pause or stop my SIP?\n"
            "A: Yes, give at least 7 working days' notice before the next debit date. "
            "Pausing is available for up to 3 months in some fund houses.\n\n"
            "Q: How do I redeem mutual fund units?\n"
            "A: Submit redemption request online or at branch. "
            "Amount credited to registered bank account within T+2 business days for equity funds, "
            "T+1 for liquid/overnight funds.\n\n"
            "IMPORTANT DISCLAIMER: The bank is an AMFI-registered distributor. "
            "Mutual fund investments are subject to market risks. Past performance does not guarantee future results."
        ),
    },

    {
        "title": "FAQ: Personal Loan — Common Questions",
        "category": "faq",
        "content": (
            "Q: What is the maximum personal loan amount?\n"
            "A: Up to Rs 40 lakh for salaried customers with salary account at the bank. "
            "Up to Rs 25 lakh for other customers. Based on income, CIBIL score, and existing obligations.\n\n"
            "Q: What CIBIL score is needed?\n"
            "A: Minimum 720 for best rates. Scores between 650-719 may be approved at higher rates. "
            "Below 650: typically rejected.\n\n"
            "Q: Are there any hidden charges?\n"
            "A: No hidden charges. All charges disclosed upfront: processing fee (1.5%-2.5%), "
            "GST on processing fee (18%), stamp duty as applicable, and late payment penalty (2% per month on overdue amount).\n\n"
            "Q: How quickly can I get the loan?\n"
            "A: Pre-approved customers (existing bank customers with good profile): Within 4 hours, fully digital. "
            "New customers: 2-3 working days after document submission."
        ),
    },

    {
        "title": "FAQ: NRI Banking and Deposits",
        "category": "faq",
        "content": (
            "Q: What types of accounts can NRIs open?\n"
            "A: NRE (Non-Resident External) — principal and interest fully repatriable, tax-free in India. "
            "NRO (Non-Resident Ordinary) — for income earned in India; repatriation limited to USD 1 million per year; interest taxable.\n\n"
            "Q: What FD rates apply for NRI deposits?\n"
            "A: NRE FD: Same rates as domestic FD (6.80%-7.00% for 1-2 years). "
            "NRO FD: Same rates as domestic FD. FCNR (B) — rates in foreign currency, currently 5.00%-5.50% for USD, 1-3 years.\n\n"
            "Q: What documents are required for NRI account opening?\n"
            "A: Passport copy, valid visa/OCI card, overseas address proof, Indian PAN (or Form 60), "
            "photograph. All documents must be self-attested and notarised or attested by Indian Embassy/Consulate."
        ),
    },

    {
        "title": "FAQ: Online and Mobile Banking",
        "category": "faq",
        "content": (
            "Q: What services are available on mobile banking?\n"
            "A: Fund transfers (IMPS/NEFT/RTGS/UPI), FD opening and management, account statements, "
            "loan EMI payments, mutual fund investments, credit card payments, and cheque book requests.\n\n"
            "Q: What are the daily transaction limits?\n"
            "A: IMPS: Rs 5 lakh per day. NEFT/RTGS: Rs 10 lakh per day (can be enhanced to Rs 25 lakh for premium customers). "
            "UPI: Rs 1 lakh per transaction (Rs 2 lakh for verified merchants).\n\n"
            "Q: How do I reset my net banking password?\n"
            "A: Online: Use 'Forgot Password' on login page — requires OTP on registered mobile + Aadhaar/PAN verification. "
            "Alternatively, visit branch with valid ID proof. Password reset not available on phone banking for security reasons."
        ),
    },

    {
        "title": "FAQ: Loan Prepayment and Foreclosure",
        "category": "faq",
        "content": (
            "Q: Can I prepay my home or personal loan?\n"
            "A: Yes. Floating rate home loans: No prepayment penalty (RBI directive). "
            "Fixed rate home loans: 2% penalty on prepaid amount. "
            "Personal loans: No penalty after 6 EMIs. Before 6 EMIs: 3% penalty.\n\n"
            "Q: How do I foreclose my loan?\n"
            "A: Submit foreclosure request at branch or through net banking. "
            "Obtain foreclosure statement showing outstanding principal, interest, and charges. "
            "Pay via NEFT/cheque. NOC (No Objection Certificate) issued within 7 working days of full payment. "
            "Property documents returned within 15 working days."
        ),
    },
]
