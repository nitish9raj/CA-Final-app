from datetime import datetime, timedelta
import pandas as pd
import database as db

def generate_daily_strategy(days_to_exam):
    weak_df = db.fetch_data(
        "SELECT subject FROM mock_tests WHERE total_marks>0 AND (marks_obtained*100.0/total_marks)<50")
    pending_df = db.fetch_data(
        "SELECT subject, count(*) as count FROM syllabus WHERE status='Pending' GROUP BY subject ORDER BY count DESC")
    rev_df = db.fetch_data(
        "SELECT s.subject FROM revisions r JOIN syllabus s ON r.chapter_id=s.id WHERE r.rev1_date=? AND r.rev1_status='Pending'",
        (datetime.now().strftime("%Y-%m-%d"),))

    lines = [f"**{max(0,days_to_exam)} days** until CA Final.\n"]
    lines.append("### 📋 Tomorrow's Recommended Plan")

    if not pending_df.empty:
        top = pending_df.iloc[0]
        lines.append(f"- 📚 **{top['subject']}** — 3 hrs *(highest pending chapters)*")
    else:
        lines.append("- 📚 **General Revision** — 3 hrs *(syllabus on track!)*")

    if not weak_df.empty:
        ws = weak_df.iloc[0]['subject']
        lines.append(f"- ⚠️ **{ws}** — 2 hrs *(low test score — needs focus)*")
    else:
        lines.append("- 📝 **Mock Test Practice** — 2 hrs")

    if not rev_df.empty:
        lines.append("- 🔁 **Revision** — 1 hr *(spaced repetition due today)*")

    lines.append("- 💪 **Practice Questions** — 1 hr")

    if days_to_exam < 30:
        lines.append("\n> 🚨 **Exam Sprint Mode:** Prioritise revision & full mocks over new chapters!")
    elif days_to_exam < 60:
        lines.append("\n> ⚡ **Final Stretch:** Balance new chapters with heavy revision.")

    return "\n".join(lines)

def check_burnout_risk():
    today = datetime.now()
    dates = [(today - timedelta(days=i)).strftime("%Y-%m-%d") for i in range(5)]
    ph = ','.join(['?']*5)
    df = db.fetch_data(
        f"SELECT date, sum(duration_minutes) as total_mins FROM study_sessions WHERE date IN ({ph}) GROUP BY date",
        tuple(dates))
    if len(df) >= 2:
        recent = df.iloc[:2]['total_mins'].mean()
        older  = df.iloc[2:]['total_mins'].mean() if len(df) > 2 else 0
        if pd.isna(recent): recent = 0
        if pd.isna(older):  older  = 0
        if older > 0 and recent < older * 0.6:
            return {"risk":"High",
                    "message":f"Hours dropped: recent avg {recent/60:.1f}h vs {older/60:.1f}h earlier.",
                    "plan":"Light day: 2h revision + 1h practice questions only."}
    return {"risk":"Low","message":"Pacing looks steady. Keep it up!","plan":"Continue standard targets."}

_CA_SYSTEM_PROMPT = """You are an expert CA Final tutor with deep knowledge of all six subjects:
1. Financial Reporting (FR) — Ind AS standards, consolidation, financial instruments
2. Advanced Financial Management (AFM) — derivatives, CAPM, EVA, M&A, forex, portfolio management
3. Auditing & Assurance (Audit) — SA standards, CARO 2020, audit reports, company audit
4. Direct Tax (DT) — capital gains, transfer pricing, MAT, deductions, international taxation
5. Indirect Tax (IDT) — GST provisions, customs duty, place of supply, ITC, returns
6. Integrated Business Solutions (IBS) — strategy frameworks, corporate governance, risk management

Your answers must be:
- Detailed and descriptive (minimum 200 words for any concept question)
- Structured with clear headings and bullet points
- Include relevant section numbers, SA numbers, or Ind AS numbers where applicable
- Include worked examples or illustrations for numerical topics
- End with 2-3 specific exam tips highlighting what is frequently tested
- Use Indian CA Final context (ICAI syllabus, rupee amounts, Indian tax rates)
- Format using markdown: **bold** for key terms, bullet points for lists, numbered steps for procedures

Always be thorough. A student's CA Final success depends on your answer quality."""


def _ask_claude(query, chat_history, api_key):
    import urllib.request, json, ssl
    messages = list(chat_history or []) + [{"role": "user", "content": query}]
    payload = json.dumps({
        "model": "claude-opus-4-5",
        "max_tokens": 1500,
        "system": _CA_SYSTEM_PROMPT,
        "messages": messages
    }).encode("utf-8")
    ctx = ssl.create_default_context()
    req = urllib.request.Request(
        "https://api.anthropic.com/v1/messages",
        data=payload,
        headers={"Content-Type": "application/json",
                 "anthropic-version": "2023-06-01",
                 "x-api-key": api_key},
        method="POST"
    )
    with urllib.request.urlopen(req, timeout=30, context=ctx) as resp:
        data = json.loads(resp.read().decode("utf-8"))
    parts = [b["text"] for b in data.get("content", []) if b.get("type") == "text"]
    return "\n".join(parts).strip()


def _ask_openai(query, chat_history, api_key):
    import urllib.request, json, ssl
    messages = [{"role": "system", "content": _CA_SYSTEM_PROMPT}]
    for m in (chat_history or []):
        messages.append(m)
    messages.append({"role": "user", "content": query})
    # Try gpt-4o-mini first (cheaper, higher rate limit), fall back to gpt-3.5-turbo
    for model in ["gpt-4o-mini", "gpt-3.5-turbo"]:
        payload = json.dumps({
            "model": model,
            "max_tokens": 1500,
            "messages": messages
        }).encode("utf-8")
        ctx = ssl.create_default_context()
        req = urllib.request.Request(
            "https://api.openai.com/v1/chat/completions",
            data=payload,
            headers={"Content-Type": "application/json",
                     "Authorization": f"Bearer {api_key}"},
            method="POST"
        )
        try:
            with urllib.request.urlopen(req, timeout=30, context=ctx) as resp:
                data = json.loads(resp.read().decode("utf-8"))
            return data["choices"][0]["message"]["content"].strip()
        except Exception as e:
            if "429" in str(e) and model != "gpt-3.5-turbo":
                continue  # try next model
            raise


def _ask_gemini(query, chat_history, api_key):
    import urllib.request, json, ssl
    contents = []
    for m in (chat_history or []):
        role = "user" if m["role"] == "user" else "model"
        contents.append({"role": role, "parts": [{"text": m["content"]}]})
    contents.append({"role": "user", "parts": [{"text": query}]})
    payload = json.dumps({
        "system_instruction": {"parts": [{"text": _CA_SYSTEM_PROMPT}]},
        "contents": contents,
        "generationConfig": {"maxOutputTokens": 1500}
    }).encode("utf-8")
    ctx = ssl.create_default_context()
    # Try multiple Gemini models in order
    models = ["gemini-2.0-flash", "gemini-1.5-flash", "gemini-1.5-flash-latest", "gemini-pro"]
    last_err = None
    for model in models:
        url = f"https://generativelanguage.googleapis.com/v1beta/models/{model}:generateContent?key={api_key}"
        req = urllib.request.Request(url, data=payload,
            headers={"Content-Type": "application/json"}, method="POST")
        try:
            with urllib.request.urlopen(req, timeout=30, context=ctx) as resp:
                data = json.loads(resp.read().decode("utf-8"))
            return data["candidates"][0]["content"]["parts"][0]["text"].strip()
        except Exception as e:
            last_err = e
            if "404" in str(e) or "400" in str(e):
                continue  # try next model
            raise
    raise last_err


def get_doubt_resolution(query, chat_history=None, provider="auto"):
    """
    Query one or all AI providers. provider = 'claude'|'openai'|'gemini'|'auto'
    'auto' tries all configured keys and returns results from each that responds.
    Returns dict: {"claude": "...", "openai": "...", "gemini": "...", "errors": {...}}
    """
    import ai_keys
    keys = ai_keys.load_keys()
    results = {}
    errors  = {}

    providers_to_try = (
        ["claude", "openai", "gemini"] if provider == "auto"
        else [provider]
    )

    for p in providers_to_try:
        k = keys.get(p, "").strip()
        if not k:
            errors[p] = "No API key configured"
            continue
        try:
            if p == "claude":
                results[p] = _ask_claude(query, chat_history, k)
            elif p == "openai":
                results[p] = _ask_openai(query, chat_history, k)
            elif p == "gemini":
                results[p] = _ask_gemini(query, chat_history, k)
        except Exception as e:
            errors[p] = str(e)

    # If nothing worked, fall back to local KB
    if not results:
        first_err = next(iter(errors.values()), "No keys configured")
        results["kb"] = _local_kb_fallback(query, first_err)

    return {"answers": results, "errors": errors}


def _local_kb_fallback(query, error_msg=""):
    """Rich local KB fallback when API is unavailable."""
    q = query.lower()
    kb = {
        "115": ("📖 Ind AS 115 — Revenue from Contracts with Customers",
"""**Overview:** Ind AS 115 provides a comprehensive 5-step framework for revenue recognition applicable to all contracts with customers (with limited exceptions like leases, financial instruments, insurance contracts).

**The 5-Step Model:**
1. **Identify the contract** — Agreement creating enforceable rights & obligations; must be approved, have commercial substance, and collection be probable
2. **Identify performance obligations** — Distinct goods/services promised. A good/service is distinct if customer can benefit from it on its own AND it is separately identifiable from other promises
3. **Determine the transaction price** — Amount expected to be received. Includes variable consideration (estimated at expected value or most likely amount), subject to constraint
4. **Allocate transaction price** — Allocate to each performance obligation based on relative stand-alone selling prices
5. **Recognise revenue** — When (or as) each performance obligation is satisfied by transferring control

**Key Concepts:**
- **Point-in-time vs Over-time recognition** — Over-time if customer simultaneously receives and consumes, asset created at customer's site, or no alternative use + right to payment
- **Contract modifications** — Treated as new contract, modification of existing, or combination
- **Principal vs Agent** — Principal recognises gross revenue; agent recognises only commission

**💡 Exam Tips:**
- Step 2 (identifying separate performance obligations) is most frequently tested — remember the 'distinct' criteria
- Variable consideration constraint and bill-and-hold arrangements appear frequently
- Contrast with old AS 9: Ind AS 115 uses control model (not risk & reward)"""),

        "consolidation": ("📖 Ind AS 110 — Consolidated Financial Statements",
"""**Control Model:** Under Ind AS 110, an investor controls an investee when it has:
1. **Power** over the investee (existing rights giving ability to direct relevant activities)
2. **Exposure** to variable returns from its involvement
3. **Ability** to use its power to affect those returns — all three must be present simultaneously

**Consolidation Procedure:**
- Combine like items of assets, liabilities, equity, income and expenses
- Eliminate investment in subsidiary against parent's share of subsidiary's equity
- **Goodwill** = Fair value of consideration + NCI at acquisition − Net identifiable assets at FV
- Eliminate intra-group transactions (sales, dividends, loans, unrealised profits)

**Non-Controlling Interest (NCI):**
- Can be measured at: (a) Fair value, OR (b) Proportionate share of net identifiable assets
- Method choice affects goodwill amount
- NCI share of profit allocated; NCI share of losses allocated even if NCI goes negative

**Key Areas:**
- **Step acquisitions** — Previously held interest remeasured at FV through P&L on date control obtained
- **Loss of control** — Retained interest remeasured at FV; gain/loss recognised on entire interest
- **Associates (Ind AS 28)** — Equity method; 20-50% holding creates presumption of significant influence

**💡 Exam Tips:**
- NCI calculation (fair value vs proportionate share) changes goodwill — a very common exam trap
- Unrealised profit elimination: upstream (sub to parent) — NCI shares the elimination; downstream (parent to sub) — 100% to parent
- Mid-year acquisitions require time-weighting of profits"""),

        "gst": ("📖 GST — Goods and Services Tax",
"""**Structure:** India follows a dual GST model:
- **CGST** (Central GST) + **SGST** (State GST) for intra-state supply
- **IGST** (Integrated GST) for inter-state supply and imports
- **UTGST** for union territories

**Key Provisions:**

**Registration (Section 22-30):**
- Mandatory if aggregate turnover > ₹20 lakhs (₹10 lakhs for NE/special category states)
- Mandatory for: inter-state suppliers, e-commerce operators, reverse charge recipients (regardless of turnover)

**Input Tax Credit (Section 16-17):**
- Available on goods/services used in course of business for taxable supply
- Conditions: possess invoice, receive goods/services, tax paid by supplier, return filed
- **Block credit (Section 17(5)):** Motor vehicles for personal use, food & beverages, club memberships, works contract for immovable property (if not in business)
- Time limit: Earlier of due date of Sept return of next FY or filing of annual return

**Place of Supply (Section 10-13):**
- Immovable property → location of property
- Restaurant services → location of restaurant
- Telecom services → subscriber's location
- Import of services → location of recipient

**Returns:**
- GSTR-1 (outward supplies), GSTR-3B (monthly summary), GSTR-9 (annual)

**💡 Exam Tips:**
- Place of Supply rules are highest-frequency topic — memorise all exceptions
- Blocked ITC under Section 17(5) list must be memorised completely
- E-way bill threshold is ₹50,000; exemptions (certain goods, movements < 10km) are frequently tested"""),

        "capital gain": ("📖 Capital Gains — Direct Tax",
"""**Classification:**
- **Short-Term Capital Asset (STCA):** Held ≤ 12 months (equity shares/units), ≤ 24 months (unlisted shares/immovable property), ≤ 36 months (other assets)
- **Long-Term Capital Asset (LTCA):** Held beyond above periods

**Tax Rates:**
| Asset Type | STCG | LTCG |
|---|---|---|
| Listed equity/units (STT paid) | 15% (Sec 111A) | 10% above ₹1L (Sec 112A) |
| Other assets | Slab rate | 20% with indexation (Sec 112) |
| Unlisted shares | Slab rate | 20% with indexation |

**Important Provisions:**
- **Section 48:** Cost of acquisition + Cost of improvement + Transfer expenses
- **Indexation:** CII-based indexation applies to non-equity LTCA (not available for bonds/debentures)
- **Section 50C:** For land/building, if consideration < stamp duty value, stamp duty value is deemed consideration
- **Section 55(2):** For assets acquired before 01.04.2001, FMV on 01.04.2001 can be taken as cost

**Exemptions:**
- **Section 54:** Reinvestment in residential house (1 house; purchase within 1 yr before/2 yrs after, construction 3 yrs)
- **Section 54EC:** Investment in specified bonds within 6 months (max ₹50L)
- **Section 54F:** Any LTCA → residential house (proportionate if not full investment)
- **VDA (Crypto):** Taxed at 30% flat, no deduction except cost, no set-off

**💡 Exam Tips:**
- Period of holding (12/24/36 months) for different assets — very commonly tested
- Section 54 vs 54EC vs 54F conditions and exemption limits appear in every exam
- Cost of improvement before 01.04.2001 is ignored (common adjustment in sums)"""),

        "audit": ("📖 Auditing — SA Standards",
"""**Key SA Standards:**

**Risk & Planning:**
- **SA 200** — Overall objectives; reasonable (not absolute) assurance; professional scepticism
- **SA 300** — Planning; audit strategy and audit plan
- **SA 315** — Identifying & assessing RMM; understand entity, environment, internal controls; identify significant risks
- **SA 320** — Materiality; performance materiality; revision of materiality

**Evidence & Procedures:**
- **SA 500** — Audit evidence; sufficient and appropriate; AEIOU (Analytical, Enquiry, Inspection, Observation, reperformance, recalculation, Confirmation)
- **SA 505** — External confirmations; positive vs negative
- **SA 520** — Analytical procedures; used in planning, substantive procedures, overall review
- **SA 530** — Audit sampling; statistical vs non-statistical

**Specific Areas:**
- **SA 240** — Fraud; management primarily responsible; auditor obtains reasonable assurance
- **SA 250** — Laws & regulations; non-compliance reporting
- **SA 550** — Related parties; higher risk of fraud
- **SA 570** — Going concern; 12-month assessment; types of audit modification

**Reporting:**
- **SA 700** — Audit report; Basis of Opinion; Key Audit Matters (listed entities only)
- **SA 701** — Key Audit Matters; why significant, how addressed
- **SA 705** — Modified opinions: Qualified (material not pervasive), Adverse (material & pervasive), Disclaimer (scope limitation material & pervasive)
- **SA 706** — Emphasis of Matter (unmodified opinion, fundamental matter)

**CARO 2020:** Applies to specified companies; 21 reporting clauses including fraud reporting (>₹1 crore to Central Govt), NBFCs, loans, investments, auditor's qualifications

**💡 Exam Tips:**
- SA numbers must be memorised — examiners test "which SA covers X"
- Difference between Emphasis of Matter vs Modified opinion is a classic question
- CARO 2020 fraud reporting threshold (₹1 crore) and timeframe (30 days to board, 45 days to Central Govt) are tested"""),

        "deferred tax": ("📖 Deferred Tax — Ind AS 12",
"""**Concept:** Deferred tax arises from temporary differences between the carrying amount of an asset/liability in the balance sheet and its tax base.

**Types:**
- **Taxable temporary difference** → **Deferred Tax Liability (DTL)** — future taxable amounts (e.g., accelerated depreciation for tax)
- **Deductible temporary difference** → **Deferred Tax Asset (DTA)** — future deductible amounts (e.g., provision for doubtful debts, carry-forward losses)

**Recognition:**
- **DTL:** Recognised for ALL taxable temporary differences (with limited exceptions: goodwill, initial recognition exception)
- **DTA:** Recognised ONLY when it is probable that sufficient future taxable profit will be available
- **Unused tax losses/credits:** DTA recognised when future taxable profit is probable

**Measurement:** 
- Tax rates enacted or substantively enacted at balance sheet date
- Reflects the manner in which the entity expects to recover the asset / settle the liability

**Presentation:**
- Deferred tax is always non-current
- DTA and DTL are offset only if legally enforceable right to offset AND same taxing authority

**OCI Items:** Deferred tax on items recognised in OCI (e.g., revaluation surplus, remeasurement of defined benefit plans) is also recognised in OCI

**💡 Exam Tips:**
- DTA recognition — "probable future taxable profit" is the key condition; assessed at each year end
- Deferred tax is NOT recognised on non-deductible goodwill — this is a very common exam point
- Undistributed profits of subsidiaries: DTL recognised unless parent can control timing of reversal"""),

        "lease": ("📖 Ind AS 116 — Leases",
"""**Lessee Accounting (Single Model):**
All leases (except short-term ≤12 months and low-value assets) are recognised on balance sheet:
- **Right-of-Use (ROU) Asset** = PV of lease payments + initial direct costs + restoration costs - lease incentives received
- **Lease Liability** = PV of lease payments (fixed payments + variable based on index, residual value guarantees, purchase option if reasonably certain, penalty for early termination)
- **Discount rate** = Interest rate implicit in lease OR lessee's incremental borrowing rate

**Subsequent Measurement:**
- ROU Asset: Depreciated over shorter of lease term or useful life (if ownership transfers/purchase option)
- Lease Liability: Effective interest method; reduced by lease payments

**P&L Impact:** Depreciation on ROU asset + Finance charge on lease liability (front-loaded — higher charge in early years)

**Lessor Accounting (Unchanged from AS 17):**
- **Finance Lease:** Lessor derecognises asset; recognises receivable; recognises finance income
- **Operating Lease:** Asset remains; lease income recognised on straight-line basis

**Key Topics:**
- **Sale and Leaseback:** If genuine sale (Ind AS 115), seller-lessee recognises only proportion of gain relating to rights transferred; buyer-lessor accounts normally
- **Lease modifications:** Depends on whether modification increases scope by adding right-of-use AND at commensurate price
- **Variable lease payments:** Only index/rate-based included in liability; performance-based are expensed

**💡 Exam Tips:**
- Numerical question on initial recognition of ROU asset and lease liability is extremely common
- Sale and leaseback — partial gain recognition is a frequent examiner favourite
- Short-term and low-value lease exemptions: payments recognised straight-line in P&L"""),

        "transfer pricing": ("📖 Transfer Pricing — Section 92",
"""**Applicability:**
- International transactions between **Associated Enterprises (AEs)**
- Specified domestic transactions above ₹20 crore

**Associated Enterprises (Section 92A):**
- Direct/indirect participation in management, control, or capital of the other
- Includes: >26% shareholding, common directors, loan > 51% of book value, complete dependence, etc.

**Arm's Length Price Methods (Section 92C):**
1. **CUP (Comparable Uncontrolled Price)** — Compare with uncontrolled transaction price; most direct method
2. **RPM (Resale Price Method)** — Resale price minus gross margin of comparable uncontrolled transaction; for distributors
3. **CPM (Cost Plus Method)** — Cost plus markup in comparable transaction; for manufacturers
4. **TNMM (Transactional Net Margin Method)** — Net profit margin compared with comparable transactions; most commonly used
5. **PSM (Profit Split Method)** — Split combined profit based on relative contribution; for integrated transactions

**Documentation Requirements:**
- **Form 3CEB:** CA's certificate (mandatory for all international transactions, any amount)
- **Master File & CbCR** — For large MNCs (turnover > ₹500 crore)
- **Safe Harbour Rules** — IT/ITES/KPO with margins >17-18%
- **APA (Advance Pricing Agreement)** — Pre-agreement with CBDT

**💡 Exam Tips:**
- TNMM is most widely used — understand why (ease, data availability)
- Form 3CEB: no minimum threshold — even ₹1 transaction needs it
- APA (unilateral/bilateral/multilateral) and MAP under DTAA are increasingly tested"""),

        # ── AFM Topics ──────────────────────────────────────────
        "capm": ("📖 CAPM — Capital Asset Pricing Model (AFM)",
"""**Formula:** E(R) = Rf + β × [E(Rm) − Rf]

Where:
- **E(R)** = Expected return on security
- **Rf** = Risk-free rate (typically 91-day T-Bill rate)
- **β (Beta)** = Systematic risk of the security
- **E(Rm)** = Expected market return
- **[E(Rm) − Rf]** = Market risk premium

**Beta Interpretation:**
- β = 1 → moves with market (average risk)
- β > 1 → more volatile than market (aggressive stock)
- β < 1 → less volatile than market (defensive stock)
- β = 0 → risk-free asset
- β < 0 → moves opposite to market (e.g., gold stocks)

**Key Concepts:**
- **Systematic (Market) Risk** — Cannot be diversified away; measured by Beta
- **Unsystematic (Specific) Risk** — Can be eliminated by diversification
- **Security Market Line (SML)** — Plots E(R) vs Beta; all correctly priced assets lie on SML
- **Capital Market Line (CML)** — Plots E(R) vs Total Risk (σ); only efficient portfolios lie on CML

**Portfolio Beta:** Weighted average of individual betas
- β_portfolio = Σ (weight × β_individual)

**Adjusted Beta:** Beta tends to revert to 1 over time
- Adjusted β = (2/3 × Historical β) + (1/3 × 1.0)

**Assumptions of CAPM:**
- Investors are rational and risk-averse
- Perfect capital markets (no taxes, no transaction costs)
- All investors have same expectations (homogeneous)
- Single period investment horizon

**💡 Exam Tips:**
- CAPM numerical: calculate required return → compare with expected return → overvalued/undervalued
- Portfolio beta calculation (weighted average) appears in almost every AFM paper
- SML vs CML distinction: SML uses beta (systematic risk), CML uses standard deviation (total risk)"""),

        "derivative": ("📖 Derivatives — Futures, Options & Swaps (AFM)",
"""**Types of Derivatives:**

### 1. Futures Contracts
- Standardised exchange-traded contracts to buy/sell asset at future date at agreed price
- **Hedging with Futures:** Short hedge (seller) or Long hedge (buyer)
- **Hedge Ratio** = (Portfolio Value / Futures Contract Value) × Beta
- **Number of Contracts** = (Portfolio Value × Beta_target) / (Futures Price × Lot Size)

### 2. Options
- **Call Option** — Right to BUY at strike price; buyer pays premium
- **Put Option** — Right to SELL at strike price; buyer pays premium

**Option Payoffs:**
- Call buyer profit = Max(S − K, 0) − Premium
- Put buyer profit = Max(K − S, 0) − Premium
- Option writers (sellers) have opposite payoffs

**Black-Scholes Model** (European Options):
- C = S·N(d1) − K·e^(−rT)·N(d2)
- d1 = [ln(S/K) + (r + σ²/2)T] / (σ√T)
- d2 = d1 − σ√T

**Greeks:** Delta (Δ), Gamma (Γ), Theta (Θ), Vega (ν), Rho (ρ)

**Option Strategies:**
- **Bull Spread** — Buy low strike call + Sell high strike call
- **Bear Spread** — Buy high strike put + Sell low strike put
- **Straddle** — Buy call + Buy put (same strike, same expiry); profit from high volatility
- **Strangle** — Buy OTM call + Buy OTM put; cheaper than straddle

### 3. Swaps
- **Interest Rate Swap** — Fixed rate ↔ Floating rate (LIBOR/SOFR based)
- **Currency Swap** — Exchange principal + interest in different currencies
- **Comparative Advantage** — Basis for swap; each party borrows where it has relative advantage

### 4. Forex Management
- **Forward Rate** using Interest Rate Parity: F = S × [(1 + r_d) / (1 + r_f)]
- **Purchasing Power Parity:** Expected rate = Spot × [(1 + Inflation_domestic) / (1 + Inflation_foreign)]

**💡 Exam Tips:**
- Number of futures contracts formula is tested EVERY year — memorise it
- Black-Scholes: know what each variable means even if full calculation not asked
- Swap: comparative advantage calculation and gain sharing between parties is classic"""),

        "afm": ("📖 Advanced Financial Management — Complete Overview",
"""AFM covers 6 major areas in CA Final:

### 1. Financial Policy & Corporate Strategy
- **EVA** = NOPAT − (WACC × Capital Employed)
- **MVA** = Market Value − Capital Invested
- **Value Drivers:** Revenue growth, operating margins, tax rate, WACC, investment in working capital

### 2. Risk Management
- **VaR (Value at Risk)** — Maximum loss at given confidence level over specified period
- **Types of Risk:** Market, Credit, Liquidity, Operational
- **Risk Mitigation:** Hedging, insurance, diversification, limits

### 3. Security Valuation
- **DDM (Gordon Growth Model):** P = D1 / (Ke − g)
- **P/E Multiple Approach:** Value = EPS × P/E ratio
- **DCF (Free Cash Flow):** Discount FCF at WACC to get Enterprise Value
- **Bond Valuation:** PV of future cash flows (coupons + redemption) at required yield

### 4. Portfolio Management
- **Markowitz Portfolio Theory** — Efficient Frontier
- **CAPM** — E(R) = Rf + β(Rm − Rf)
- **Sharpe Ratio** = (Rp − Rf) / σp — Risk-adjusted return per unit of total risk
- **Treynor Ratio** = (Rp − Rf) / βp — Return per unit of systematic risk
- **Jensen's Alpha** = Actual Return − CAPM Expected Return

### 5. Derivatives (see Derivatives topic for detail)
- Futures, Options (Black-Scholes), Swaps, Forex

### 6. Mergers & Acquisitions
- **EPS Accretion/Dilution** — Post-merger EPS vs pre-merger EPS
- **Exchange Ratio** = Price offered per target share / Acquirer's market price per share
- **Synergies** — Cost savings + Revenue enhancement
- **Leveraged Buyout (LBO)** — Acquisition financed primarily with debt

**💡 Exam Tips:**
- Portfolio performance measures (Sharpe, Treynor, Jensen) appear in every paper
- Futures hedging with number of contracts is always tested
- M&A: EPS post-merger calculation with exchange ratio is a favourite numerical"""),

        "portfolio": ("📖 Portfolio Management & Markowitz Theory (AFM)",
"""**Modern Portfolio Theory (Markowitz):**

**Expected Return of Portfolio:**
- E(Rp) = Σ wi × E(Ri) — Weighted average of individual returns

**Portfolio Variance (2 assets):**
- σ²p = w₁²σ₁² + w₂²σ₂² + 2·w₁·w₂·σ₁·σ₂·ρ₁₂
- ρ = Correlation coefficient (−1 to +1)
- When ρ = −1: Maximum diversification benefit
- When ρ = +1: No diversification benefit

**Efficient Frontier:** Set of portfolios with maximum return for a given risk level

**Performance Measures:**
| Measure | Formula | Denominator |
|---|---|---|
| Sharpe Ratio | (Rp − Rf) / σp | Total risk |
| Treynor Ratio | (Rp − Rf) / βp | Systematic risk |
| Jensen's Alpha | Rp − [Rf + β(Rm−Rf)] | — |
| Information Ratio | Active Return / Tracking Error | — |

**Systematic vs Unsystematic Risk:**
- Total Risk = Systematic + Unsystematic
- σ² = β²σ²m + σ²ε
- Systematic can't be diversified; unsystematic can be eliminated

**Capital Market Line (CML):**
- E(Rp) = Rf + [(E(Rm) − Rf)/σm] × σp
- Applies only to efficient portfolios (not individual assets)

**💡 Exam Tips:**
- 2-asset portfolio variance formula is most tested — know it cold
- Sharpe uses σ (total risk), Treynor uses β (systematic risk) — distinction is critical
- Minimum Variance Portfolio: find weights using calculus/formula"""),

        "eva": ("📖 EVA & Value-Based Management (AFM)",
"""**Economic Value Added (EVA):**
- **EVA** = NOPAT − (WACC × Capital Employed)
- Or: EVA = (ROCE − WACC) × Capital Employed
- **NOPAT** = Net Operating Profit After Tax = EBIT × (1 − Tax Rate)
- **ROCE** = NOPAT / Capital Employed

**EVA Adjustments (from accounting to economic):**
- Add back: R&D (capitalise and amortise), goodwill amortisation, restructuring charges, operating leases (capitalise)
- These convert accounting profit to economic profit

**Market Value Added (MVA):**
- MVA = Market Capitalisation − Capital Invested
- MVA > 0 → Wealth created; MVA < 0 → Wealth destroyed
- Link: MVA = PV of all future EVAs

**Shareholder Value Analysis (SVA — Rappaport):**
7 Value Drivers: Sales growth, Operating profit margin, Tax rate, Fixed capital investment, Working capital investment, Cost of capital, Competitive advantage period

**💡 Exam Tips:**
- EVA calculation: common trap is using PAT instead of NOPAT — always use NOPAT
- EVA adjustments list: R&D, operating leases, goodwill most important
- MVA vs EVA distinction and relationship must be clearly understood"""),

        "forex": ("📖 Foreign Exchange Management (AFM)",
"""**Exchange Rate Quotes:**
- **Direct Quote** — Foreign currency per unit of domestic (e.g., Rs/USD)
- **Indirect Quote** — Domestic currency per unit of foreign
- **Bid Rate** — Rate at which bank buys foreign currency
- **Ask/Offer Rate** — Rate at which bank sells foreign currency
- **Spread** = Ask − Bid

**Parity Conditions:**

**Interest Rate Parity (IRP):**
- F/S = (1 + r_d) / (1 + r_f)
- Forward Rate = Spot × [(1 + Domestic Rate) / (1 + Foreign Rate)]

**Purchasing Power Parity (PPP):**
- Expected Spot = Current Spot × [(1 + Inflation_domestic) / (1 + Inflation_foreign)]

**Hedging Techniques:**
- **Forward Contract** — Lock in exchange rate; no upside/downside flexibility
- **Money Market Hedge** — Borrow/invest in respective currencies to create synthetic forward
- **Options** — Right (not obligation) to convert at strike rate; floor/ceiling protection
- **Futures** — Standardised exchange-traded; margin-based

**Transaction vs Translation vs Economic Exposure:**
- Transaction: Specific cash flows affected
- Translation: Balance sheet re-measurement (Ind AS 21)
- Economic: Long-term impact on firm value

**💡 Exam Tips:**
- Money market hedge steps (borrow/invest/convert) tested heavily
- Always use BID rate when bank buys, ASK when bank sells — most common error
- Forward Rate calculation using IRP: practise with both direct and indirect quotes"""),

        # ── IBS Topics ──────────────────────────────────────────
        "porter": ("📖 Porter's Five Forces & Strategic Analysis (IBS)",
"""**Porter's Five Forces Framework:**

1. **Threat of New Entrants** — Barriers to entry: economies of scale, capital requirements, brand loyalty, access to distribution, regulatory requirements
2. **Bargaining Power of Suppliers** — High when: few suppliers, unique products, high switching costs, suppliers can integrate forward
3. **Bargaining Power of Buyers** — High when: few buyers, standardised products, low switching costs, buyers can integrate backward
4. **Threat of Substitute Products** — High when: close substitutes available, low switching costs, better price-performance ratio
5. **Rivalry Among Competitors** — High when: many competitors, slow industry growth, high exit barriers, low differentiation

**Porter's Generic Strategies:**
- **Cost Leadership** — Lowest cost producer; compete on price
- **Differentiation** — Unique product/service; premium pricing
- **Focus (Cost Focus / Differentiation Focus)** — Narrow segment

**Value Chain Analysis:**
- Primary: Inbound logistics → Operations → Outbound logistics → Marketing & Sales → Service
- Support: Firm Infrastructure, HRM, Technology Development, Procurement

**SWOT Analysis:** Strengths, Weaknesses (internal) | Opportunities, Threats (external)

**PESTLE:** Political, Economic, Social, Technological, Legal, Environmental

**💡 Exam Tips:**
- Five Forces — always identify which force is most relevant in the given case
- Generic strategies: a firm stuck in middle (neither cost leader nor differentiator) earns below-average returns
- Value chain: identify which activities create competitive advantage"""),

        "risk management": ("📖 Risk Management Framework (IBS/AFM)",
"""**Types of Risk:**
- **Strategic Risk** — Wrong strategic decisions, competitor actions
- **Operational Risk** — Process failures, human error, system failures
- **Financial Risk** — Credit risk, market risk, liquidity risk, interest rate risk
- **Compliance/Legal Risk** — Regulatory non-compliance

**Risk Management Process:**
1. **Identify** — Risk register, SWOT, scenario analysis
2. **Assess** — Probability × Impact matrix; inherent vs residual risk
3. **Respond** — 4Ts: Transfer (insurance/hedging), Tolerate, Treat, Terminate
4. **Monitor** — KRIs, internal audit, board oversight

**Enterprise Risk Management (ERM — COSO Framework):**
8 Components: Internal Environment → Objective Setting → Event Identification → Risk Assessment → Risk Response → Control Activities → Information & Communication → Monitoring

**Corporate Governance:**
- **Board Composition:** Independent directors ≥ 1/3 (listed companies); Audit, Nomination, Remuneration committees
- **SEBI LODR** — Quarterly compliance, related party disclosures, whistle-blower policy
- **Business Responsibility Reporting** — ESG disclosures

**💡 Exam Tips:**
- 4Ts of risk response (Transfer/Tolerate/Treat/Terminate) — tested in case studies
- COSO ERM components — match to scenario given
- Corporate governance: SEBI LODR requirements for listed companies is very frequently tested"""),

        # ── General / Cross-topic ──────────────────────────────
        "mat": ("📖 Minimum Alternate Tax (MAT) — Section 115JB",
"""**Applicability:** Companies (not LLPs/individuals) when regular tax < 15% of Book Profit

**MAT Rate:** 15% of Book Profit (plus surcharge + cess)

**Book Profit Calculation:**
Start with: Net Profit as per P&L account
Add back: Income tax provision, proposed dividend, reserves created, depreciation debited to P&L, losses brought forward (if lower than unabsorbed depreciation)
Deduct: Depreciation as per Companies Act, brought forward losses (actual if lower than depreciation)

**MAT Credit (Section 115JAA):**
- MAT paid − Regular Tax = MAT Credit
- Carry forward for **15 years**
- Set off against regular tax in subsequent years when regular tax > MAT
- No interest earned on MAT credit

**AMT (Section 115JC):** For non-corporate taxpayers (LLP, individuals with business income)
- Rate: 18.5% of Adjusted Total Income

**💡 Exam Tips:**
- Book Profit adjustments: additions and deductions list must be memorised
- MAT credit carry forward period is 15 years (changed from 10 — common error)
- AMT vs MAT distinction and who it applies to"""),

        "ind as 12": ("📖 Ind AS 12 — Income Taxes (Deferred Tax)",
"""**Concept:** Deferred tax arises from temporary differences between carrying amount (accounting) and tax base of assets/liabilities.

**Types:**
- **Taxable Temporary Difference** → **DTL** (future taxable amounts, e.g., accelerated tax depreciation)
- **Deductible Temporary Difference** → **DTA** (future deductible amounts, e.g., provisions)

**Recognition Rules:**
- DTL: Recognised for ALL taxable temporary differences (except goodwill initial recognition, initial recognition exception)
- DTA: Only when **probable** future taxable profit will be available against which DTA can be utilised
- Unused tax losses → DTA if probable future profits

**Measurement:** Tax rates enacted or substantively enacted at balance sheet date

**OCI Items:** Deferred tax on OCI items (revaluation, remeasurement of defined benefit plans) also goes to OCI

**Presentation:** Always non-current; offset DTL and DTA only if legally enforceable right AND same taxing authority

**💡 Exam Tips:**
- DTA recognition: "probable" future profit is key — must reassess at every year end
- Deferred tax NOT recognised on non-deductible goodwill — very common exam point
- Tax rate change: effect on opening deferred tax balance goes to P&L (not tax expense of current year's temporary differences)"""),
    }

    for key, (title, body) in kb.items():
        if key in q:
            return f"### {title}\n\n{body}\n\n---\n⚠️ *Live AI unavailable ({error_msg[:60]}). Showing from local knowledge base.*"

    # Smart partial match — check if any word in query matches a KB key
    q_words = set(q.replace("-","").replace("—","").split())
    for key, (title, body) in kb.items():
        key_words = set(key.replace(" ","").lower())
        if any(word in q for word in key.split()):
            return f"### {title}\n\n{body}\n\n---\n⚠️ *Live AI unavailable. Showing from local knowledge base.*"

    topics = "AFM (CAPM, Derivatives, Portfolio, EVA, Forex, Options), FR (Ind AS 115, Ind AS 110, Ind AS 116, Ind AS 12), GST, Capital Gains, Audit SA Standards, Transfer Pricing, MAT, Porter's Five Forces, Risk Management"
    return (f"### 📚 Knowledge Base — Topic Not Found\n\n"
            f"No specific answer for **\"{query}\"** in local KB.\n\n"
            f"**Available offline topics:** {topics}\n\n"
            f"**To get AI answers:** Add an API key in the 🔑 API Keys panel above.\n\n"
            f"{'⚠️ *Error: ' + error_msg[:100] + '*' if error_msg else ''}")
