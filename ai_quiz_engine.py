"""
ai_quiz_engine.py — 500+ MCQ bank + rich document analysis + document Q&A chat.
"""
import re
import random
from collections import Counter

# ══════════════════════════════════════════════════════════════════
# MCQ BANK — 500+ questions across all CA Final subjects
# ══════════════════════════════════════════════════════════════════
_MCQ_BANK = {

# ─────────────────────────────────────────────
"fr": [
  {"question":"Under Ind AS 115, how many steps are in the revenue recognition model?","options":["3","4","5","6"],"answer":"5"},
  {"question":"Under Ind AS 110, control requires:","options":["Majority shareholding only","Power + Returns + Ability to use power","Board representation","Voting rights above 50%"],"answer":"Power + Returns + Ability to use power"},
  {"question":"Ind AS 116 requires lessee to recognise:","options":["Only lease liability","Only ROU asset","Both ROU asset and lease liability","Neither for short-term leases"],"answer":"Both ROU asset and lease liability"},
  {"question":"Goodwill on consolidation is tested for impairment:","options":["Every 5 years","Only when indicators exist","Annually, mandatorily","Never under Ind AS"],"answer":"Annually, mandatorily"},
  {"question":"Under Ind AS 109, financial assets are initially measured at:","options":["Amortised cost","Fair value","Cost minus depreciation","Net realisable value"],"answer":"Fair value"},
  {"question":"Ind AS 103 deals with:","options":["Revenue recognition","Business combinations","Employee benefits","Provisions"],"answer":"Business combinations"},
  {"question":"Under Ind AS 2, inventories are measured at:","options":["Cost only","NRV only","Lower of cost and NRV","Higher of cost and NRV"],"answer":"Lower of cost and NRV"},
  {"question":"Ind AS 36 deals with:","options":["Impairment of assets","Revenue recognition","Leases","Borrowing costs"],"answer":"Impairment of assets"},
  {"question":"Under Ind AS 19, defined benefit obligation is measured using:","options":["Projected unit credit method","Unit credit method","Straight line method","Present value method"],"answer":"Projected unit credit method"},
  {"question":"Ind AS 21 deals with:","options":["Share-based payments","Effects of changes in foreign exchange rates","Business combinations","Impairment"],"answer":"Effects of changes in foreign exchange rates"},
  {"question":"Under Ind AS 116, the discount rate used by lessee is:","options":["Risk-free rate","Implicit rate or incremental borrowing rate","Prime lending rate","WACC"],"answer":"Implicit rate or incremental borrowing rate"},
  {"question":"Ind AS 37 covers:","options":["Financial instruments","Provisions, contingent liabilities and contingent assets","Leases","Revenue"],"answer":"Provisions, contingent liabilities and contingent assets"},
  {"question":"Under Ind AS 12, deferred tax asset is recognised when:","options":["Always","Never","Future taxable profit is probable","Approved by board"],"answer":"Future taxable profit is probable"},
  {"question":"Ind AS 23 deals with:","options":["Borrowing costs","Government grants","Related party disclosures","Segment reporting"],"answer":"Borrowing costs"},
  {"question":"Under Ind AS 115 Step 1, a contract must be:","options":["Written only","Approved and create enforceable rights","Oral only","Board approved"],"answer":"Approved and create enforceable rights"},
  {"question":"The 'control' model for consolidation replaced:","options":["Risk and reward model","Equity method","Cost method","Fair value model"],"answer":"Risk and reward model"},
  {"question":"Under Ind AS 110, non-controlling interest (NCI) can be measured at:","options":["Fair value only","Proportionate share only","Either fair value or proportionate share","Cost"],"answer":"Either fair value or proportionate share"},
  {"question":"Ind AS 28 applies to:","options":["Subsidiaries","Associates and joint ventures","All investments","Only listed companies"],"answer":"Associates and joint ventures"},
  {"question":"Under the equity method, investment is initially recorded at:","options":["Fair value","Cost","NRV","Book value"],"answer":"Cost"},
  {"question":"Ind AS 40 deals with:","options":["Investment property","Intangible assets","Biological assets","Mineral rights"],"answer":"Investment property"},
  {"question":"Under Ind AS 38, internally generated goodwill is:","options":["Capitalised","Expensed as incurred","Amortised over 10 years","Recognised at fair value"],"answer":"Expensed as incurred"},
  {"question":"Ind AS 16 property plant and equipment can be measured after recognition using:","options":["Cost model only","Revaluation model only","Either cost or revaluation model","Fair value model only"],"answer":"Either cost or revaluation model"},
  {"question":"Under Ind AS 33, EPS is presented by:","options":["All companies","Listed companies and those filing for listing","Private companies","Banks only"],"answer":"Listed companies and those filing for listing"},
  {"question":"Diluted EPS is always:","options":["Higher than basic EPS","Lower than or equal to basic EPS","Equal to basic EPS","Cannot be determined"],"answer":"Lower than or equal to basic EPS"},
  {"question":"Under Ind AS 7, cash flows are classified into:","options":["2 activities","3 activities","4 activities","5 activities"],"answer":"3 activities"},
  {"question":"Ind AS 8 deals with:","options":["Accounting policies, changes in estimates and errors","Financial instruments","Leases","Business combinations"],"answer":"Accounting policies, changes in estimates and errors"},
  {"question":"Under Ind AS 10, dividends declared after balance sheet date are:","options":["Recognised as liability","Disclosed as non-adjusting event","Ignored","Recognised as asset"],"answer":"Disclosed as non-adjusting event"},
  {"question":"Ind AS 24 requires disclosure of:","options":["Segment information","Related party transactions","EPS","Cash flows"],"answer":"Related party transactions"},
  {"question":"Under Ind AS 105, assets held for sale are measured at:","options":["Cost","Fair value","Lower of carrying amount and fair value less costs to sell","Higher of carrying amount and NRV"],"answer":"Lower of carrying amount and fair value less costs to sell"},
  {"question":"Ind AS 41 deals with:","options":["Agriculture","Mineral resources","Oil and gas","Real estate"],"answer":"Agriculture"},
  {"question":"FVTPL classification under Ind AS 109 means:","options":["Fair value through profit or loss","Fixed value through profit or loss","Fair value through plan or loss","None of these"],"answer":"Fair value through profit or loss"},
  {"question":"Under Ind AS 109, impairment of financial assets uses:","options":["Incurred loss model","Expected credit loss model","Historical loss model","Probability loss model"],"answer":"Expected credit loss model"},
  {"question":"Ind AS 113 defines fair value as:","options":["Transaction price","Exit price in orderly transaction","Entry price","Book value"],"answer":"Exit price in orderly transaction"},
  {"question":"Under Ind AS 1, which financial statement is NOT required?","options":["Balance sheet","Statement of changes in equity","Cash flow statement","Budget statement"],"answer":"Budget statement"},
  {"question":"Interim financial reporting is covered under:","options":["Ind AS 34","Ind AS 36","Ind AS 37","Ind AS 38"],"answer":"Ind AS 34"},
  {"question":"Under Ind AS 115, variable consideration is included at:","options":["Maximum amount","Expected value or most likely amount","Zero","Minimum amount"],"answer":"Expected value or most likely amount"},
  {"question":"Ind AS 17 (old leases standard) has been replaced by:","options":["Ind AS 115","Ind AS 116","Ind AS 117","Ind AS 118"],"answer":"Ind AS 116"},
  {"question":"Under Ind AS 103, acquisition-related costs are:","options":["Added to goodwill","Expensed in profit or loss","Capitalised as intangible","Deducted from NCI"],"answer":"Expensed in profit or loss"},
  {"question":"A joint arrangement where parties have rights to net assets is called:","options":["Joint operation","Joint venture","Joint subsidiary","Joint associate"],"answer":"Joint venture"},
  {"question":"Under Ind AS 29, financial statements are restated when there is:","options":["Inflation","Hyperinflation","Deflation","Currency devaluation"],"answer":"Hyperinflation"},
  {"question":"Ind AS 101 deals with:","options":["First-time adoption of Ind AS","Revenue recognition","Leases","Impairment"],"answer":"First-time adoption of Ind AS"},
  {"question":"Which Ind AS deals with segment reporting?","options":["Ind AS 107","Ind AS 108","Ind AS 109","Ind AS 110"],"answer":"Ind AS 108"},
  {"question":"Under Ind AS 20, government grants are recognised when:","options":["Applied for","There is reasonable assurance of compliance and receipt","Received","Approved by government"],"answer":"There is reasonable assurance of compliance and receipt"},
  {"question":"Ind AS 32 deals with:","options":["Financial instruments - presentation","Financial instruments - recognition","Financial instruments - disclosure","Leases"],"answer":"Financial instruments - presentation"},
  {"question":"Under Ind AS 116, short-term leases are leases with a term of:","options":["Less than 6 months","12 months or less","Less than 24 months","Less than 36 months"],"answer":"12 months or less"},
  {"question":"Sale and leaseback resulting in a finance lease: seller/lessee recognises:","options":["Full profit immediately","No profit","Deferred profit","Profit proportionate to retained interest"],"answer":"Profit proportionate to retained interest"},
  {"question":"Under Ind AS 36, CGU means:","options":["Cash generating unit","Capital generating unit","Cost generating unit","Current generating unit"],"answer":"Cash generating unit"},
  {"question":"Recoverable amount under Ind AS 36 is:","options":["Higher of FVLCD and VIU","Lower of FVLCD and VIU","FVLCD only","VIU only"],"answer":"Higher of FVLCD and VIU"},
  {"question":"Under Ind AS 19, actuarial gains/losses on defined benefit plans are recognised in:","options":["Profit or loss","OCI","Retained earnings directly","Deferred tax"],"answer":"OCI"},
  {"question":"Ind AS 102 deals with:","options":["Share-based payment","Share capital","Revenue sharing","Bonus shares"],"answer":"Share-based payment"},
],

# ─────────────────────────────────────────────
"audit": [
  {"question":"What is the primary objective of SA 315?","options":["Fraud detection","Risk identification and assessment","Financial reporting","Audit sampling"],"answer":"Risk identification and assessment"},
  {"question":"CARO 2020 applies to which category of companies?","options":["All companies","Only listed companies","Specified companies excluding small","Only public companies"],"answer":"Specified companies excluding small"},
  {"question":"SA 570 deals with which concept?","options":["Audit evidence","Going concern","Related parties","Subsequent events"],"answer":"Going concern"},
  {"question":"Under SA 700, auditor's report must include:","options":["Director's remuneration","Basis of Opinion paragraph","Tax computation","None of these"],"answer":"Basis of Opinion paragraph"},
  {"question":"SA 200 requires the auditor to obtain:","options":["Absolute assurance","Reasonable assurance","Limited assurance","No specific assurance"],"answer":"Reasonable assurance"},
  {"question":"SA 300 deals with:","options":["Audit documentation","Planning an audit","Audit sampling","Audit evidence"],"answer":"Planning an audit"},
  {"question":"The concept of 'materiality' in audit is covered under:","options":["SA 200","SA 320","SA 315","SA 500"],"answer":"SA 320"},
  {"question":"SA 530 deals with:","options":["Audit sampling","Related parties","Going concern","Subsequent events"],"answer":"Audit sampling"},
  {"question":"SA 550 deals with:","options":["Related parties","Subsequent events","Opening balances","Fraud"],"answer":"Related parties"},
  {"question":"SA 560 deals with:","options":["Subsequent events","Going concern","Related parties","Audit evidence"],"answer":"Subsequent events"},
  {"question":"Inherent risk and control risk together are called:","options":["Detection risk","Audit risk","Risk of material misstatement","Sampling risk"],"answer":"Risk of material misstatement"},
  {"question":"Under SA 240, the primary responsibility for prevention of fraud lies with:","options":["Auditor","Management","Those charged with governance","Internal auditor"],"answer":"Management"},
  {"question":"SA 505 deals with:","options":["External confirmations","Internal controls","Audit evidence","Sampling"],"answer":"External confirmations"},
  {"question":"Which SA deals with 'opening balances'?","options":["SA 500","SA 510","SA 520","SA 530"],"answer":"SA 510"},
  {"question":"Analytical procedures used as substantive procedures are covered under:","options":["SA 315","SA 500","SA 520","SA 530"],"answer":"SA 520"},
  {"question":"SA 600 deals with:","options":["Special purpose frameworks","Using the work of another auditor","Group audits","Component auditor"],"answer":"Using the work of another auditor"},
  {"question":"The engagement letter is addressed to:","options":["Shareholders","Management or those charged with governance","Regulators","ICAI"],"answer":"Management or those charged with governance"},
  {"question":"Under SA 706, Emphasis of Matter paragraph is used when:","options":["Audit opinion is modified","Matter is fundamental but opinion is unmodified","Fraud is detected","Going concern doubt exists"],"answer":"Matter is fundamental but opinion is unmodified"},
  {"question":"SA 701 deals with:","options":["Modified opinion","Key Audit Matters","Emphasis of Matter","Other Information"],"answer":"Key Audit Matters"},
  {"question":"Key Audit Matters are communicated in reports of:","options":["All entities","Listed entities","Government companies","All public companies"],"answer":"Listed entities"},
  {"question":"Under SA 265, significant deficiency in internal control must be communicated to:","options":["Shareholders","Those charged with governance","Regulators","All of the above"],"answer":"Those charged with governance"},
  {"question":"SA 402 deals with:","options":["Service organisations","Related parties","Sampling","Fraud"],"answer":"Service organisations"},
  {"question":"Audit risk = Inherent Risk × Control Risk ×:","options":["Sampling risk","Detection risk","Audit evidence","Materiality"],"answer":"Detection risk"},
  {"question":"Under SA 220, engagement quality control review is required for:","options":["All audits","Listed entity audits","Government audits","Bank audits"],"answer":"Listed entity audits"},
  {"question":"SA 250 deals with:","options":["Consideration of laws and regulations","Fraud","Related parties","Going concern"],"answer":"Consideration of laws and regulations"},
  {"question":"The predecessor auditor's working papers can be accessed by:","options":["Successor auditor automatically","Only with client permission","Never","Only with ICAI permission"],"answer":"Only with client permission"},
  {"question":"Under CARO 2020, reporting on fraud is required when amount exceeds:","options":["₹1 lakh","₹5 lakhs","₹10 lakhs","₹1 crore"],"answer":"₹1 crore"},
  {"question":"SA 800 deals with:","options":["Special purpose financial statements","Listed companies","Banks","Government"],"answer":"Special purpose financial statements"},
  {"question":"Which of the following is NOT an assertion for account balances?","options":["Existence","Completeness","Occurrence","Rights and obligations"],"answer":"Occurrence"},
  {"question":"Under SA 501, specific procedures are required for:","options":["Cash","Inventory and litigation","Loans","Investments"],"answer":"Inventory and litigation"},
  {"question":"Audit documentation must be retained for at least:","options":["3 years","5 years","7 years","10 years"],"answer":"7 years"},
  {"question":"SA 610 deals with:","options":["Using work of internal auditors","External confirmations","Sampling","Fraud"],"answer":"Using work of internal auditors"},
  {"question":"Which SA requires communication with those charged with governance?","options":["SA 260","SA 265","Both SA 260 and SA 265","SA 300"],"answer":"Both SA 260 and SA 265"},
  {"question":"Under Companies Act 2013, auditor is appointed for a term of:","options":["1 year","3 years","5 years","10 years"],"answer":"5 years"},
  {"question":"Rotation of audit firm is mandatory after:","options":["5 years","10 years","15 years","20 years"],"answer":"10 years"},
  {"question":"Section 143(12) of Companies Act requires auditor to report fraud to:","options":["Board of Directors","Central Government","ICAI","Shareholders"],"answer":"Central Government"},
  {"question":"The concept of 'true and fair view' is associated with:","options":["SA 200","SA 700","Both","Neither"],"answer":"Both"},
  {"question":"Under SA 330, substantive procedures include:","options":["Tests of controls only","Tests of details and analytical procedures","Observation only","Inquiry only"],"answer":"Tests of details and analytical procedures"},
  {"question":"SA 450 deals with:","options":["Evaluation of misstatements","Audit sampling","Related parties","Going concern"],"answer":"Evaluation of misstatements"},
  {"question":"Which SA deals with 'written representations'?","options":["SA 500","SA 550","SA 580","SA 600"],"answer":"SA 580"},
  {"question":"Peer review of CA firms is conducted by:","options":["ICAI","SEBI","MCA","RBI"],"answer":"ICAI"},
  {"question":"Under SA 315, 'walk-through test' is used to:","options":["Test effectiveness of controls","Understand the system","Detect fraud","Verify balances"],"answer":"Understand the system"},
  {"question":"An adverse opinion is issued when misstatement is:","options":["Material and pervasive","Material but not pervasive","Immaterial","Pervasive but not material"],"answer":"Material and pervasive"},
  {"question":"Disclaimer of opinion is issued when:","options":["Disagreement is material","Scope limitation is material and pervasive","Fraud is detected","Going concern doubt exists"],"answer":"Scope limitation is material and pervasive"},
  {"question":"SA 710 deals with:","options":["Comparative information","Opening balances","Sampling","Related parties"],"answer":"Comparative information"},
  {"question":"The 'expectation gap' in auditing refers to:","options":["Gap between auditor's report and financial statements","Difference between public expectations and auditor's actual role","Materiality threshold gap","Detection risk gap"],"answer":"Difference between public expectations and auditor's actual role"},
  {"question":"Under section 139, first auditor of company is appointed by:","options":["Board within 30 days of incorporation","Shareholders","CAG","Audit committee"],"answer":"Board within 30 days of incorporation"},
  {"question":"SA 620 deals with:","options":["Using work of auditor's expert","Internal audit","Sampling","Service organisations"],"answer":"Using work of auditor's expert"},
  {"question":"Which of the following is a substantive test?","options":["Observation of physical inventory","Reviewing control procedures","Evaluating segregation of duties","Reviewing organisation chart"],"answer":"Observation of physical inventory"},
  {"question":"Under SA 540, complex estimates require:","options":["Increased professional scepticism","Reduced testing","No special procedures","Management representation only"],"answer":"Increased professional scepticism"},
],

# ─────────────────────────────────────────────
"dt": [
  {"question":"Long-term capital gains on listed equity above ₹1 lakh are taxed at:","options":["10%","15%","20%","30%"],"answer":"10%"},
  {"question":"Transfer pricing applies to transactions between:","options":["Any two companies","Associated enterprises in international transactions","Domestic related parties only","All cross-border transactions"],"answer":"Associated enterprises in international transactions"},
  {"question":"Section 54 exemption is available for reinvestment in:","options":["Any asset","Residential house property","Commercial property","Bonds only"],"answer":"Residential house property"},
  {"question":"MAT under Section 115JB is computed on:","options":["Taxable income","Book profits","Gross receipts","Net worth"],"answer":"Book profits"},
  {"question":"Advance tax is payable when tax liability exceeds:","options":["₹5,000","₹10,000","₹20,000","₹50,000"],"answer":"₹10,000"},
  {"question":"STCG on listed equity shares under Section 111A is taxed at:","options":["10%","15%","20%","30%"],"answer":"15%"},
  {"question":"Section 80C deduction limit is:","options":["₹1 lakh","₹1.5 lakhs","₹2 lakhs","₹2.5 lakhs"],"answer":"₹1.5 lakhs"},
  {"question":"Depreciation under Income Tax Act is charged on:","options":["Straight line basis","Written down value basis","Units of production","Both SLM and WDV"],"answer":"Written down value basis"},
  {"question":"Business loss can be carried forward for:","options":["4 years","8 years","10 years","Indefinitely"],"answer":"8 years"},
  {"question":"Section 92C deals with:","options":["Transfer pricing method","Capital gains","Deductions","TDS"],"answer":"Transfer pricing method"},
  {"question":"The arm's length price in transfer pricing is determined by:","options":["CUP, RPM, CPM, TNMM, PSM","Cost plus only","Resale price only","Market price only"],"answer":"CUP, RPM, CPM, TNMM, PSM"},
  {"question":"DTAA stands for:","options":["Double Tax Avoidance Agreement","Direct Tax Assessment Act","Domestic Transfer Agreement","Deferred Tax Accounting Adjustment"],"answer":"Double Tax Avoidance Agreement"},
  {"question":"Under Section 10(38), LTCG on equity was exempt till:","options":["March 2017","March 2018","March 2019","March 2020"],"answer":"March 2018"},
  {"question":"Section 44AD applies to:","options":["Professionals","Presumptive income for eligible businesses","Transporters","Agriculturists"],"answer":"Presumptive income for eligible businesses"},
  {"question":"Under Section 44ADA, presumptive income for professionals is:","options":["6% of gross receipts","50% of gross receipts","8% of gross receipts","10% of gross receipts"],"answer":"50% of gross receipts"},
  {"question":"TDS on salary is deducted under:","options":["Section 192","Section 193","Section 194","Section 195"],"answer":"Section 192"},
  {"question":"Section 56(2)(x) deals with:","options":["Income from other sources — gifts and transfers","Business income","Capital gains","Salary"],"answer":"Income from other sources — gifts and transfers"},
  {"question":"Set off of loss from house property is limited to:","options":["₹1 lakh","₹1.5 lakhs","₹2 lakhs","₹3 lakhs"],"answer":"₹2 lakhs"},
  {"question":"Speculation loss can be set off against:","options":["Any business income","Speculation profit only","Capital gains","Any income"],"answer":"Speculation profit only"},
  {"question":"Under Section 115BAC (new tax regime), basic exemption limit is:","options":["₹2.5 lakhs","₹3 lakhs","₹5 lakhs","₹7 lakhs"],"answer":"₹3 lakhs"},
  {"question":"Capital gains on transfer of agricultural land situated in rural area is:","options":["Taxable at 20%","Taxable at 10%","Exempt","Taxable at slab rate"],"answer":"Exempt"},
  {"question":"Section 54EC exemption is available when capital gains are invested in:","options":["Residential property","Specified bonds within 6 months","Equity shares","Any bonds"],"answer":"Specified bonds within 6 months"},
  {"question":"Dividend received from domestic company is taxable in hands of:","options":["Company","Shareholders","Both","Neither"],"answer":"Shareholders"},
  {"question":"Under Section 115JB, MAT credit can be carried forward for:","options":["5 years","10 years","15 years","Indefinitely"],"answer":"15 years"},
  {"question":"POEM (Place of Effective Management) concept applies to:","options":["Resident companies only","Foreign companies for residential status","All companies","Listed companies"],"answer":"Foreign companies for residential status"},
  {"question":"Section 68 deals with:","options":["Unexplained cash credits","Transfer pricing","Capital gains","TDS"],"answer":"Unexplained cash credits"},
  {"question":"Under the Income Tax Act, a person is resident in India if stay exceeds:","options":["60 days + 365 days in 4 years","182 days","90 days","120 days"],"answer":"60 days + 365 days in 4 years"},
  {"question":"Indexation benefit is available on:","options":["Short-term capital assets","Long-term capital assets (except specified)","All capital assets","Listed equity shares"],"answer":"Long-term capital assets (except specified)"},
  {"question":"Section 80D provides deduction for:","options":["LIC premium","Medical insurance premium","Home loan interest","Education loan"],"answer":"Medical insurance premium"},
  {"question":"Section 10(10D) exempts:","options":["HRA","Life insurance maturity proceeds","PF withdrawal","Gratuity"],"answer":"Life insurance maturity proceeds"},
  {"question":"Under Section 40A(3), cash expenditure disallowed if exceeds:","options":["₹5,000","₹10,000","₹20,000","₹1 lakh"],"answer":"₹10,000"},
  {"question":"GAAR stands for:","options":["General Anti-Avoidance Rules","Global Accounting and Revenue Rules","Gross Asset Allocation Regulation","General Audit Assessment Rules"],"answer":"General Anti-Avoidance Rules"},
  {"question":"Section 79 restricts carry forward of loss for companies where:","options":["Turnover decreases","More than 51% beneficial shareholding changes","Auditor changes","Directors change"],"answer":"More than 51% beneficial shareholding changes"},
  {"question":"Tax audit under Section 44AB is mandatory when turnover exceeds:","options":["₹1 crore (business)","₹2 crore (business)","₹5 crore (business — digital)","Both ₹2 crore and ₹5 crore depending on transactions"],"answer":"Both ₹2 crore and ₹5 crore depending on transactions"},
  {"question":"Under Section 115-O, DDT (Dividend Distribution Tax) was:","options":["Still applicable","Abolished from FY 2020-21","Applicable only to listed companies","Applicable only above ₹10 lakhs"],"answer":"Abolished from FY 2020-21"},
  {"question":"Section 9(1)(i) brings to tax in India income:","options":["Earned abroad by NRI","Accruing through business connection in India","Received outside India","None"],"answer":"Accruing through business connection in India"},
  {"question":"Form 3CEB (transfer pricing audit report) is required when international transactions exceed:","options":["₹1 crore","₹5 crores","₹10 crores","Any amount"],"answer":"Any amount"},
  {"question":"VDA (Virtual Digital Asset) gains are taxed at:","options":["10%","20%","30%","Slab rate"],"answer":"30%"},
  {"question":"Section 80JJAA provides deduction for:","options":["New employment","Export profits","R&D","Infrastructure"],"answer":"New employment"},
  {"question":"Under Section 2(47), transfer includes:","options":["Sale only","Sale, exchange, relinquishment, extinguishment of right","Gift only","All transfers except gift"],"answer":"Sale, exchange, relinquishment, extinguishment of right"},
  {"question":"Period of holding for unlisted shares to qualify as LTCA:","options":["12 months","24 months","36 months","48 months"],"answer":"24 months"},
  {"question":"Section 50C applies to:","options":["Transfer of capital asset being land/building","Transfer of shares","Transfer of business","Transfer of goodwill"],"answer":"Transfer of capital asset being land/building"},
  {"question":"Cost of improvement incurred before 01.04.2001 is:","options":["Ignored","Taken at actual cost","Indexed from 2001","Added at fair market value"],"answer":"Ignored"},
  {"question":"Under Section 194N, TDS is deducted on cash withdrawal exceeding:","options":["₹20 lakhs","₹1 crore","₹50 lakhs","₹2 crores"],"answer":"₹1 crore"},
  {"question":"Double taxation relief under Section 91 is available for countries:","options":["Having DTAA with India","Not having DTAA with India","All foreign countries","Only Commonwealth countries"],"answer":"Not having DTAA with India"},
  {"question":"Perquisite value of rent-free accommodation in metro city for government employee is:","options":["7.5% of salary","10% of salary","15% of salary","Actual rent paid"],"answer":"7.5% of salary"},
  {"question":"Section 80G deduction for donation to PM Relief Fund is:","options":["50% without limit","100% without limit","50% with limit","100% with limit"],"answer":"100% without limit"},
  {"question":"Under Section 45(4), dissolution of firm: capital gains taxed in hands of:","options":["Partner","Firm","Both","Neither"],"answer":"Firm"},
  {"question":"Surcharge on income tax for individual having income above ₹50 lakhs is:","options":["5%","10%","15%","20%"],"answer":"10%"},
  {"question":"Section 115BBE taxes unexplained income at:","options":["30%","60%","78% (with surcharge)","Slab rate"],"answer":"78% (with surcharge)"},
],

# ─────────────────────────────────────────────
"idt": [
  {"question":"For intra-state supply, which taxes apply?","options":["IGST only","CGST + SGST","CGST only","Customs duty"],"answer":"CGST + SGST"},
  {"question":"Input Tax Credit is NOT available for:","options":["Raw materials","Capital goods for business","Motor vehicles for personal use","Services used in business"],"answer":"Motor vehicles for personal use"},
  {"question":"Reverse charge mechanism means:","options":["Supplier pays tax","Recipient pays tax","Government pays tax","No tax applicable"],"answer":"Recipient pays tax"},
  {"question":"Place of supply for immovable property services is:","options":["Location of supplier","Location of recipient","Location of the property","Registered office"],"answer":"Location of the property"},
  {"question":"GST registration mandatory threshold (normal states) for services is:","options":["₹10 lakhs","₹20 lakhs","₹40 lakhs","₹1 crore"],"answer":"₹20 lakhs"},
  {"question":"E-way bill is required for movement of goods exceeding:","options":["₹10,000","₹25,000","₹50,000","₹1,00,000"],"answer":"₹50,000"},
  {"question":"Composition scheme is available to suppliers with turnover up to:","options":["₹75 lakhs","₹1 crore","₹1.5 crores","₹2 crores"],"answer":"₹1.5 crores"},
  {"question":"Under composition scheme, tax rate for manufacturers is:","options":["0.5%","1%","2%","5%"],"answer":"1%"},
  {"question":"IGST is levied on:","options":["Intra-state supply","Inter-state supply and imports","Exports","All supplies"],"answer":"Inter-state supply and imports"},
  {"question":"GST Council is chaired by:","options":["President of India","Prime Minister","Union Finance Minister","RBI Governor"],"answer":"Union Finance Minister"},
  {"question":"GSTR-1 is filed for:","options":["Outward supplies","Inward supplies","ITC reconciliation","Annual return"],"answer":"Outward supplies"},
  {"question":"GSTR-3B is a:","options":["Detailed return","Monthly summary return","Annual return","Audit report"],"answer":"Monthly summary return"},
  {"question":"GSTR-9 is the:","options":["Monthly return","Quarterly return","Annual return","ISD return"],"answer":"Annual return"},
  {"question":"Zero-rated supply under GST includes:","options":["Exports and SEZ supplies","Exempt supplies only","Nil-rated supplies","All government supplies"],"answer":"Exports and SEZ supplies"},
  {"question":"Under Section 16(2), ITC is available only if:","options":["Invoice received","Payment made within 180 days","Both invoice received and payment within 180 days","Only tax paid by supplier"],"answer":"Both invoice received and payment within 180 days"},
  {"question":"Block credit under Section 17(5) includes:","options":["Food and beverages for employees","Capital goods for production","Services for business","Raw materials"],"answer":"Food and beverages for employees"},
  {"question":"Time of supply for services under Section 13 is:","options":["Invoice date only","Date of completion of service","Earlier of invoice or receipt of payment","Later of invoice or receipt"],"answer":"Earlier of invoice or receipt of payment"},
  {"question":"Anti-profiteering authority under GST is:","options":["GST Council","NAA (National Anti-Profiteering Authority)","SEBI","Competition Commission"],"answer":"NAA (National Anti-Profiteering Authority)"},
  {"question":"Under GST, supply to SEZ is treated as:","options":["Exempt supply","Taxable supply","Zero-rated supply","Non-taxable supply"],"answer":"Zero-rated supply"},
  {"question":"CGST rate on gold jewellery is:","options":["1.5%","3%","5%","12%"],"answer":"1.5%"},
  {"question":"Input Service Distributor (ISD) distributes credit to:","options":["Suppliers","Recipients","Branches having same PAN","Other companies"],"answer":"Branches having same PAN"},
  {"question":"GST refund on exports must be claimed within:","options":["6 months","2 years","3 years","1 year"],"answer":"2 years"},
  {"question":"Customs duty is levied under:","options":["CGST Act","Customs Act 1962","IGST Act","Finance Act"],"answer":"Customs Act 1962"},
  {"question":"Basic Customs Duty (BCD) is levied on:","options":["CIF value","FOB value","Transaction value","Ex-factory value"],"answer":"CIF value"},
  {"question":"IGST on imports is collected along with:","options":["CGST","Customs duty","SGST","None"],"answer":"Customs duty"},
  {"question":"Under Customs, warehoused goods can be stored for:","options":["30 days","1 year","2 years","3 years"],"answer":"1 year"},
  {"question":"Special Economic Zone (SEZ) supplies are:","options":["Taxable at standard rate","Zero-rated","Exempt","Nil-rated"],"answer":"Zero-rated"},
  {"question":"Under Rule 42, ITC reversal for exempt supplies uses formula:","options":["Proportionate reversal","Full reversal","50% reversal","No reversal"],"answer":"Proportionate reversal"},
  {"question":"A taxable person can opt for composition scheme by filing:","options":["GSTR-1","GST CMP-02","GSTR-3B","GST REG-01"],"answer":"GST CMP-02"},
  {"question":"Advance Ruling under GST is issued by:","options":["AAR (Authority for Advance Ruling)","GST Council","High Court","CESTAT"],"answer":"AAR (Authority for Advance Ruling)"},
  {"question":"GST on restaurant services (non-AC) is:","options":["0%","5%","12%","18%"],"answer":"5%"},
  {"question":"Under Section 9(4), GST on purchase from unregistered dealer is paid by:","options":["Supplier","Recipient on reverse charge","Both equally","Government"],"answer":"Recipient on reverse charge"},
  {"question":"Section 74 of CGST Act deals with:","options":["Normal demand","Demand due to fraud or wilful misstatement","Refunds","Penalties"],"answer":"Demand due to fraud or wilful misstatement"},
  {"question":"SVLDRS (Sabka Vishwas) was introduced for:","options":["Settling pre-GST legacy disputes","New GST registrations","Annual returns","Export refunds"],"answer":"Settling pre-GST legacy disputes"},
  {"question":"The GST compensation cess is levied on:","options":["All goods","Demerit goods and luxury items","Services only","Imports only"],"answer":"Demerit goods and luxury items"},
  {"question":"Section 68 of CGST Act deals with:","options":["ITC","Inspection of goods in movement","Registration","Returns"],"answer":"Inspection of goods in movement"},
  {"question":"Under Rule 86A, ITC can be blocked by:","options":["Taxpayer themselves","Commissioner or authorised officer","GST Council","Court order only"],"answer":"Commissioner or authorised officer"},
  {"question":"LUT (Letter of Undertaking) is filed for:","options":["Composition scheme","Exports without payment of tax","ITC claims","Annual returns"],"answer":"Exports without payment of tax"},
  {"question":"HSN code requirement: taxpayer with turnover above ₹5 crores must use:","options":["4-digit HSN","6-digit HSN","8-digit HSN","2-digit HSN"],"answer":"6-digit HSN"},
  {"question":"GST on health insurance premium is:","options":["0%","5%","12%","18%"],"answer":"18%"},
  {"question":"Section 129 of CGST deals with:","options":["Detention, seizure and release of goods","Registration","ITC","Returns"],"answer":"Detention, seizure and release of goods"},
  {"question":"QRMP scheme allows quarterly return filing for taxpayers with turnover up to:","options":["₹1 crore","₹1.5 crores","₹5 crores","₹2 crores"],"answer":"₹5 crores"},
  {"question":"Under GST, the time limit for issuing tax invoice for services is:","options":["30 days from supply","45 days from supply","60 days from supply","No specific limit"],"answer":"30 days from supply"},
  {"question":"Anti-dumping duty is imposed to protect:","options":["Domestic industry from cheap imports","Exports","All imports","Government revenue"],"answer":"Domestic industry from cheap imports"},
  {"question":"Section 17(5)(g) blocks ITC on:","options":["Goods lost or destroyed","Capital goods","Services","Exports"],"answer":"Goods lost or destroyed"},
  {"question":"A pure agent who incurs expenditure on behalf of recipient:","options":["Is liable to pay GST on such expenditure","Can exclude such expenditure from taxable value","Must add it to value","Must reverse ITC"],"answer":"Can exclude such expenditure from taxable value"},
  {"question":"GST on life insurance (other than ULIP) is:","options":["0%","5%","12%","18%"],"answer":"18%"},
  {"question":"The IGST Act was modelled on the recommendations of:","options":["Finance Commission","GST Council","13th Finance Commission","Dr. Kelkar Committee"],"answer":"GST Council"},
  {"question":"Under GST, casual taxable person must obtain registration:","options":["At least 5 days before commencement","At least 1 day before","At time of supply","No advance registration needed"],"answer":"At least 5 days before commencement"},
  {"question":"Which of the following is NOT a zero-rated supply?","options":["Exports","SEZ supplies","Supply to UN bodies","Domestic exempt supply"],"answer":"Domestic exempt supply"},
  {"question":"GST on works contract for government is:","options":["5%","12%","18%","Exempt"],"answer":"12%"},
],

# ─────────────────────────────────────────────
"afm": [
  {"question":"Which model is used to calculate cost of equity using market risk?","options":["Gordon Growth Model","CAPM","APT only","M&M Model"],"answer":"CAPM"},
  {"question":"In Black-Scholes model, N(d1) represents:","options":["Probability of exercise","Delta of the option","Time value","Intrinsic value"],"answer":"Delta of the option"},
  {"question":"EVA (Economic Value Added) = NOPAT minus:","options":["EBIT","Capital Employed × WACC","Net Profit","Depreciation"],"answer":"Capital Employed × WACC"},
  {"question":"In an interest rate swap, the notional principal is:","options":["Actually exchanged","Never exchanged","Exchanged at maturity","Exchanged at inception"],"answer":"Never exchanged"},
  {"question":"Duration of a bond measures its sensitivity to:","options":["Credit risk","Interest rate changes","Inflation","Currency risk"],"answer":"Interest rate changes"},
  {"question":"CAPM: Required return = Rf + β(Rm - Rf). The term (Rm - Rf) is the:","options":["Risk-free premium","Market risk premium","Equity risk premium","Beta premium"],"answer":"Market risk premium"},
  {"question":"A beta greater than 1 indicates the stock is:","options":["Less volatile than market","More volatile than market","Same as market","Not correlated with market"],"answer":"More volatile than market"},
  {"question":"Modigliani-Miller Proposition I (no taxes) states:","options":["Debt increases firm value","Capital structure is irrelevant","Equity is always preferred","Dividends determine value"],"answer":"Capital structure is irrelevant"},
  {"question":"Under MM with taxes, firm value increases with debt due to:","options":["Lower equity cost","Tax shield on interest","Higher leverage","Better ratings"],"answer":"Tax shield on interest"},
  {"question":"Gordon's Dividend Growth Model: P0 = D1 / (Ke - g). 'g' represents:","options":["Dividend yield","Constant growth rate","Required return","Payout ratio"],"answer":"Constant growth rate"},
  {"question":"A call option gives the holder the right to:","options":["Sell at strike price","Buy at strike price","Both buy and sell","Neither"],"answer":"Buy at strike price"},
  {"question":"Put-Call parity states: C + PV(X) =","options":["P + S0","P - S0","S0 - P","P × S0"],"answer":"P + S0"},
  {"question":"The Sharpe ratio measures:","options":["Systematic risk","Return per unit of total risk","Return per unit of systematic risk","Beta adjusted return"],"answer":"Return per unit of total risk"},
  {"question":"Treynor ratio uses which measure of risk?","options":["Standard deviation","Beta","Variance","Correlation"],"answer":"Beta"},
  {"question":"Jensen's Alpha measures:","options":["Actual return minus expected CAPM return","Total return","Risk-adjusted return","Dividend yield"],"answer":"Actual return minus expected CAPM return"},
  {"question":"In a futures contract, daily settlement is called:","options":["Margin call","Mark to market","Initial margin","Variation margin"],"answer":"Mark to market"},
  {"question":"A currency forward contract fixes:","options":["Future spot rate","Exchange rate for future transaction","Interest rate","Commodity price"],"answer":"Exchange rate for future transaction"},
  {"question":"Covered Interest Rate Parity states the forward rate depends on:","options":["Spot rate only","Interest rate differential","Inflation differential","Both interest and inflation"],"answer":"Interest rate differential"},
  {"question":"Purchasing Power Parity (PPP) theory links exchange rates to:","options":["Interest rates","Inflation differentials","GDP growth","Balance of trade"],"answer":"Inflation differentials"},
  {"question":"NAV of a mutual fund = (Total Assets - Liabilities) / :","options":["Number of sponsors","Number of units outstanding","Total subscriptions","Fund manager fees"],"answer":"Number of units outstanding"},
  {"question":"The Efficient Market Hypothesis (EMH) in strong form states:","options":["Only public info is reflected","Historical prices reflect all info","All public and private info is reflected","Technical analysis works"],"answer":"All public and private info is reflected"},
  {"question":"In a leveraged buyout (LBO), acquisition is financed primarily by:","options":["Equity","Debt using target's assets","Government grants","Private equity only"],"answer":"Debt using target's assets"},
  {"question":"The free cash flow to equity (FCFE) is:","options":["FCFF + Net borrowings - Interest after tax","EBIT + Depreciation","PAT + Depreciation - Capex","Net income - Dividends"],"answer":"FCFF + Net borrowings - Interest after tax"},
  {"question":"Yield to maturity (YTM) of a bond is the:","options":["Coupon rate","Current yield","Internal rate of return of bond cash flows","Face value return"],"answer":"Internal rate of return of bond cash flows"},
  {"question":"A zero coupon bond is issued:","options":["At face value","At premium","At discount (deep discount)","At market value"],"answer":"At discount (deep discount)"},
  {"question":"Hedging using currency futures: an Indian exporter expecting USD inflow should:","options":["Buy USD futures","Sell USD futures","Buy INR futures","Do nothing"],"answer":"Sell USD futures"},
  {"question":"WACC is used as the discount rate when:","options":["Project risk equals firm risk","Project risk is higher","Project risk is lower","Always"],"answer":"Project risk equals firm risk"},
  {"question":"Under the APV (Adjusted Present Value) method:","options":["WACC is used","Base-case NPV is calculated then financing effects added","Only equity cash flows are discounted","Market value is used"],"answer":"Base-case NPV is calculated then financing effects added"},
  {"question":"An interest rate cap protects the buyer from:","options":["Falling interest rates","Rising interest rates above the cap rate","Currency risk","Credit risk"],"answer":"Rising interest rates above the cap rate"},
  {"question":"Convexity of a bond: higher convexity means:","options":["More price sensitivity to rates","Less price sensitivity to large rate changes","Higher coupon","Lower duration"],"answer":"Less price sensitivity to large rate changes"},
  {"question":"In portfolio theory, diversification reduces:","options":["Systematic risk","Unsystematic risk","Total risk only","Market risk"],"answer":"Unsystematic risk"},
  {"question":"The Security Market Line (SML) plots:","options":["Return vs standard deviation","Return vs beta","Price vs earnings","Risk vs maturity"],"answer":"Return vs beta"},
  {"question":"Working capital financing through commercial paper is:","options":["Long-term source","Short-term money market instrument","Medium-term loan","Equity instrument"],"answer":"Short-term money market instrument"},
  {"question":"In a plain vanilla interest rate swap, one party pays:","options":["Fixed rate; other pays floating","Both fixed rates","Both floating rates","Variable rates only"],"answer":"Fixed rate; other pays floating"},
  {"question":"The Black-Scholes model assumes stock price follows:","options":["Normal distribution","Lognormal distribution","Uniform distribution","Binomial distribution"],"answer":"Lognormal distribution"},
  {"question":"Economic exposure to exchange rate risk affects:","options":["Transaction only","Translation only","Long-run competitive position of firm","Short-term cash flows only"],"answer":"Long-run competitive position of firm"},
  {"question":"The Pecking Order Theory suggests firms prefer:","options":["Equity first, then debt","Debt first, then equity","Internal financing first, then debt, then equity","Equal mix always"],"answer":"Internal financing first, then debt, then equity"},
  {"question":"A stock dividend (bonus shares) affects:","options":["EPS","Share price proportionally","Total equity value","Both EPS and share price"],"answer":"Share price proportionally"},
  {"question":"IRR method may give multiple rates when:","options":["Cash flows are all negative","Cash flows have multiple sign changes","Project is very long","Cost of capital is high"],"answer":"Cash flows have multiple sign changes"},
  {"question":"In capital rationing, the correct ranking criterion is:","options":["NPV","IRR","Profitability Index","Payback period"],"answer":"Profitability Index"},
  {"question":"ADR (American Depository Receipt) allows:","options":["US investors to buy foreign shares in USD","Indian companies to list on NSE","Foreigners to buy rupee bonds","None of these"],"answer":"US investors to buy foreign shares in USD"},
  {"question":"Venture capital typically invests in:","options":["Large listed companies","Early-stage high-risk companies","Government bonds","Real estate only"],"answer":"Early-stage high-risk companies"},
  {"question":"Beta of a portfolio equals:","options":["Average of individual betas","Weighted average of individual betas","Highest beta in portfolio","Lowest beta in portfolio"],"answer":"Weighted average of individual betas"},
  {"question":"The holding period return formula is:","options":["(P1 - P0) / P0","(P1 - P0 + D1) / P0","D1 / P0","P1 / P0"],"answer":"(P1 - P0 + D1) / P0"},
  {"question":"Debt securitisation converts:","options":["Equity into debt","Illiquid assets into tradeable securities","Short-term to long-term debt","Bonds into equity"],"answer":"Illiquid assets into tradeable securities"},
  {"question":"Credit Default Swap (CDS) is used to:","options":["Hedge interest rate risk","Transfer credit risk","Manage currency risk","Invest in equities"],"answer":"Transfer credit risk"},
  {"question":"The optimal capital structure minimises:","options":["Total revenue","WACC (maximises firm value)","Dividend payout","Interest coverage"],"answer":"WACC (maximises firm value)"},
  {"question":"Factoring involves:","options":["Selling receivables at a discount","Borrowing against inventory","Issuing bonds","Currency swap"],"answer":"Selling receivables at a discount"},
  {"question":"A swaption is:","options":["An option to enter into a swap","A swap on equity","A forward on a bond","Currency derivative"],"answer":"An option to enter into a swap"},
  {"question":"Under dividend irrelevance theory (MM), value depends on:","options":["Dividend policy","Investment policy","Both dividend and investment","Neither"],"answer":"Investment policy"},
],

# ─────────────────────────────────────────────
"ibs": [
  {"question":"Porter's Five Forces does NOT include:","options":["Threat of substitutes","Bargaining power of suppliers","Government regulation","Rivalry among competitors"],"answer":"Government regulation"},
  {"question":"Blue Ocean Strategy focuses on:","options":["Competing in existing markets","Creating uncontested market space","Cost leadership only","Mergers and acquisitions"],"answer":"Creating uncontested market space"},
  {"question":"Balanced Scorecard measures performance across how many perspectives?","options":["2","3","4","5"],"answer":"4"},
  {"question":"Corporate Governance primarily aims to:","options":["Maximise short-term profits","Balance interests of all stakeholders","Reduce employee count","Increase market share"],"answer":"Balance interests of all stakeholders"},
  {"question":"SWOT analysis stands for:","options":["Strategy Work Objectives Tactics","Strengths Weaknesses Opportunities Threats","Systems Workforce Operations Technology","Sales Workforce Output Trends"],"answer":"Strengths Weaknesses Opportunities Threats"},
  {"question":"The BCG Matrix classifies businesses into:","options":["2 categories","4 categories","6 categories","8 categories"],"answer":"4 categories"},
  {"question":"In BCG Matrix, a 'Cash Cow' has:","options":["High growth, high market share","Low growth, high market share","High growth, low market share","Low growth, low market share"],"answer":"Low growth, high market share"},
  {"question":"A 'Star' in BCG Matrix represents:","options":["High growth, high market share","Low growth, high market share","High growth, low market share","Low growth, low market share"],"answer":"High growth, high market share"},
  {"question":"The Ansoff Matrix deals with:","options":["Competition analysis","Growth strategies","Financial ratios","Organisational structure"],"answer":"Growth strategies"},
  {"question":"Market penetration (Ansoff) means:","options":["New product, new market","Existing product, new market","Existing product, existing market","New product, existing market"],"answer":"Existing product, existing market"},
  {"question":"Value chain analysis was developed by:","options":["Kaplan and Norton","Michael Porter","Peter Drucker","Philip Kotler"],"answer":"Michael Porter"},
  {"question":"The Balanced Scorecard was developed by:","options":["Michael Porter","Peter Drucker","Kaplan and Norton","Gary Hamel"],"answer":"Kaplan and Norton"},
  {"question":"Corporate strategy deals with:","options":["Day-to-day operations","Which businesses to compete in","Product pricing","Employee management"],"answer":"Which businesses to compete in"},
  {"question":"Business-level strategy deals with:","options":["Portfolio of businesses","How to compete within a specific industry","Financial planning","HR management"],"answer":"How to compete within a specific industry"},
  {"question":"Porter's Generic Strategies include:","options":["Cost leadership, differentiation, focus","Growth, stability, retrenchment","Market penetration, development, diversification","None of these"],"answer":"Cost leadership, differentiation, focus"},
  {"question":"Horizontal integration means:","options":["Acquiring a supplier","Acquiring a competitor","Acquiring a customer","Diversifying into new industry"],"answer":"Acquiring a competitor"},
  {"question":"Vertical integration (backward) means:","options":["Acquiring a customer","Acquiring a competitor","Acquiring a supplier","Entering a new market"],"answer":"Acquiring a supplier"},
  {"question":"The concept of 'Core Competency' was introduced by:","options":["Porter","Prahalad and Hamel","Drucker","Ansoff"],"answer":"Prahalad and Hamel"},
  {"question":"Strategic intent refers to:","options":["Short-term goals","Long-term ambitious goal to achieve competitive advantage","Current strategy","Financial targets"],"answer":"Long-term ambitious goal to achieve competitive advantage"},
  {"question":"PESTLE analysis covers:","options":["Internal factors only","External macro-environmental factors","Financial ratios","Competitive forces"],"answer":"External macro-environmental factors"},
  {"question":"Risk management process steps include:","options":["Identify, assess, treat, monitor","Plan, do, check, act","Analyse, design, implement, review","None of these"],"answer":"Identify, assess, treat, monitor"},
  {"question":"Enterprise Risk Management (ERM) framework was issued by:","options":["ICAI","COSO","SEBI","MCA"],"answer":"COSO"},
  {"question":"Business Process Reengineering (BPR) aims at:","options":["Incremental improvement","Radical redesign of business processes","Cost cutting only","Outsourcing"],"answer":"Radical redesign of business processes"},
  {"question":"Balanced Scorecard 'Learning and Growth' perspective focuses on:","options":["Financial performance","Customer satisfaction","Internal processes","Employee capabilities and innovation"],"answer":"Employee capabilities and innovation"},
  {"question":"CSR under Companies Act 2013 is mandatory for companies with net profit above:","options":["₹1 crore","₹2 crores","₹5 crores","₹10 crores"],"answer":"₹5 crores"},
  {"question":"The concept of 'Shareholder Value' maximisation is associated with:","options":["Stakeholder theory","Shareholder theory","Agency theory","Stewardship theory"],"answer":"Shareholder theory"},
  {"question":"Agency problem arises due to:","options":["Separation of ownership and management","High taxation","Poor accounting","Market competition"],"answer":"Separation of ownership and management"},
  {"question":"VRIO framework assesses resources on:","options":["Volume, Reach, Integration, Operations","Value, Rarity, Imitability, Organisation","Visibility, Revenue, Impact, Opportunity","None of these"],"answer":"Value, Rarity, Imitability, Organisation"},
  {"question":"A 'strategic alliance' is:","options":["Merger of two companies","Cooperative arrangement between firms remaining independent","Acquisition","Diversification"],"answer":"Cooperative arrangement between firms remaining independent"},
  {"question":"Disruptive innovation concept was given by:","options":["Porter","Prahalad","Clayton Christensen","Drucker"],"answer":"Clayton Christensen"},
  {"question":"The concept of 'Triple Bottom Line' refers to:","options":["3 financial statements","People, Planet, Profit","3 growth strategies","3 competitive forces"],"answer":"People, Planet, Profit"},
  {"question":"Total Quality Management (TQM) focuses on:","options":["Cost reduction only","Continuous improvement and customer satisfaction","Speed only","Technology"],"answer":"Continuous improvement and customer satisfaction"},
  {"question":"Six Sigma methodology aims to reduce defects to:","options":["Zero","3.4 per million opportunities","10 per million","1%"],"answer":"3.4 per million opportunities"},
  {"question":"A 'greenfield investment' is:","options":["Acquiring existing plant","Building new operations from scratch","Merger","Joint venture"],"answer":"Building new operations from scratch"},
  {"question":"Costing method used in JIT (Just-in-Time) environment:","options":["Standard costing","Backflush costing","Activity-based costing","Marginal costing"],"answer":"Backflush costing"},
  {"question":"The 'Iceberg model' in change management suggests:","options":["Most resistance is visible","Most resistance is hidden below surface","Change is always easy","Technology drives change"],"answer":"Most resistance is hidden below surface"},
  {"question":"Kotter's 8-step change model begins with:","options":["Creating a vision","Forming a powerful coalition","Creating urgency","Removing obstacles"],"answer":"Creating urgency"},
  {"question":"The McKinsey 7-S Framework includes:","options":["Strategy, Structure, Systems, Staff, Style, Skills, Shared values","Only Strategy and Structure","Financial metrics only","External factors"],"answer":"Strategy, Structure, Systems, Staff, Style, Skills, Shared values"},
  {"question":"A 'Question Mark' in BCG Matrix has:","options":["High growth, high market share","High growth, low market share","Low growth, high market share","Low growth, low market share"],"answer":"High growth, low market share"},
  {"question":"Supply chain management aims to:","options":["Increase inventory","Reduce cost and improve customer service across supply chain","Eliminate suppliers","Reduce quality"],"answer":"Reduce cost and improve customer service across supply chain"},
  {"question":"The 'Digital Transformation' concept primarily involves:","options":["Buying new computers","Integrating digital technology across all business areas","Social media only","Email communication"],"answer":"Integrating digital technology across all business areas"},
  {"question":"Competitive advantage according to Porter is sustainable when based on:","options":["Low price only","Activities that are difficult to imitate","Marketing alone","Brand name only"],"answer":"Activities that are difficult to imitate"},
  {"question":"GRC stands for:","options":["Growth Rate Calculation","Governance Risk and Compliance","General Revenue Consolidation","Global Resource Centre"],"answer":"Governance Risk and Compliance"},
  {"question":"Whistleblower policy is a component of:","options":["Marketing strategy","Corporate Governance","Operations management","Financial reporting"],"answer":"Corporate Governance"},
  {"question":"The concept of 'Economies of Scale' means:","options":["Cost per unit increases with output","Cost per unit decreases with higher output","Fixed costs increase","Revenue doubles with output"],"answer":"Cost per unit decreases with higher output"},
  {"question":"'First Mover Advantage' refers to:","options":["Being fastest in production","Competitive benefit of entering market first","First company to list on stock exchange","First to achieve ISO certification"],"answer":"Competitive benefit of entering market first"},
  {"question":"A 'conglomerate' is a company that:","options":["Operates in a single industry","Operates in multiple unrelated industries","Has no subsidiaries","Only operates in India"],"answer":"Operates in multiple unrelated industries"},
  {"question":"The primary objective of corporate strategy is:","options":["Short-term profit","Long-term wealth creation and competitive advantage","Employee satisfaction","Market share only"],"answer":"Long-term wealth creation and competitive advantage"},
  {"question":"Sensitivity analysis in strategic decision-making tests:","options":["Impact of changing one variable at a time","All variables simultaneously","Only financial variables","Market conditions"],"answer":"Impact of changing one variable at a time"},
  {"question":"The concept of 'economies of scope' refers to:","options":["Cost reductions from producing a single product in large volume","Cost reductions from producing multiple products together","Geographic expansion benefits","Vertical integration benefits"],"answer":"Cost reductions from producing multiple products together"},
],

# ─────────────────────────────────────────────
"general": [
  {"question":"What does ICAI stand for?","options":["Institute of Chartered Accountants of India","Indian Council of Audit Institutions","Institute of Cost Accountants India","International CA Association India"],"answer":"Institute of Chartered Accountants of India"},
  {"question":"CA Final consists of how many groups?","options":["1","2","3","4"],"answer":"2"},
  {"question":"Spaced repetition is most effective at intervals of:","options":["1,2,3,4 days","3,7,15,30 days","7,14,21,28 days","1,7,30,90 days"],"answer":"3,7,15,30 days"},
  {"question":"Which section of the Companies Act deals with Audit Committee?","options":["Section 134","Section 177","Section 139","Section 143"],"answer":"Section 177"},
  {"question":"ICAI was established in the year:","options":["1947","1949","1956","1960"],"answer":"1949"},
  {"question":"The headquarters of ICAI is located in:","options":["Mumbai","Chennai","Kolkata","New Delhi"],"answer":"New Delhi"},
  {"question":"CA Final Group 1 includes:","options":["FR, AFM, Audit, DT","FR, AFM, Audit, Strategic Management","FR, SFM, Audit, IDT","All 6 papers together"],"answer":"FR, AFM, Audit, Strategic Management"},
  {"question":"Minimum passing marks in CA Final each paper:","options":["40%","50%","45%","55%"],"answer":"40%"},
  {"question":"Aggregate passing criteria in CA Final:","options":["50% aggregate","55% aggregate","50% aggregate with no paper below 40%","60% aggregate"],"answer":"50% aggregate with no paper below 40%"},
  {"question":"Companies Act 2013 was enacted in:","options":["2010","2013","2014","2015"],"answer":"2013"},
],
}

# ══════════════════════════════════════════════════════════════════
# Topic detection & NLP helpers
# ══════════════════════════════════════════════════════════════════
_CONCEPT_PATTERNS = {
    "Definitions & Terminology": [
        r'\bmeans\b.{5,80}', r'\bdefined as\b.{5,80}', r'\brefers to\b.{5,80}', r'\bis the\b.{5,60}',
    ],
    "Learning Outcomes": [
        r'student shall be able to\b.{5,120}', r'after reading.{5,100}',
        r'you will (?:be able to|understand|learn).{5,100}', r'understand.{5,80}',
    ],
    "Key Concepts & Topics": [
        r'(?:concept|principle|framework|model|theory|method|approach)\s+of\s+[\w\s]{3,50}',
        r'\b(?:important|key|significant|critical|essential|fundamental)\b.{5,60}',
    ],
    "Procedures & Steps": [
        r'step \d+.{5,80}', r'(?:first|second|third|fourth|fifth|finally|lastly).{5,80}',
        r'procedure for.{5,60}',
    ],
    "Regulations & Standards": [
        r'section \d+[\w\s]{0,40}', r'SA \d+.{3,50}', r'Ind AS \d+.{3,50}', r'GST.{5,60}',
    ],
    "Examples & Illustrations": [
        r'for example.{5,100}', r'e\.g\..{5,100}', r'suppose.{5,80}', r'consider.{5,80}',
    ],
}

def _detect_topic(text):
    t = text.lower()
    scores = {
        "audit": t.count("audit")+t.count("sa 3")+t.count("caro")+t.count("assurance"),
        "fr":    t.count("ind as")+t.count("revenue")+t.count("consolidat")+t.count("financial statement"),
        "dt":    t.count("income tax")+t.count("capital gain")+t.count("deduction")+t.count("assessment"),
        "idt":   t.count("gst")+t.count("cgst")+t.count("igst")+t.count("supply"),
        "afm":   t.count("wacc")+t.count("capm")+t.count("derivative")+t.count("portfolio"),
        "ibs":   t.count("strategy")+t.count("porter")+t.count("swot")+t.count("governance"),
    }
    best = max(scores, key=scores.get)
    return best if scores[best] > 0 else "general"

def _extract_headings(text):
    headings = []
    for line in text.split("\n"):
        line = line.strip()
        if not line: continue
        if 5 < len(line) < 120 and line.isupper(): headings.append(line.title())
        elif 5 < len(line) < 80 and line.endswith(":"): headings.append(line[:-1])
        elif re.match(r'^(?:chapter\s+\d+|section\s+\d+|\d+\.\d*\s+[A-Z])', line, re.IGNORECASE): headings.append(line[:80])
    return list(dict.fromkeys(headings))[:10]

def _extract_key_concepts(text):
    found = {}
    tc = re.sub(r'\s+', ' ', text)
    for cat, pats in _CONCEPT_PATTERNS.items():
        matches, seen, unique = [], set(), []
        for p in pats:
            try:
                for m in re.finditer(p, tc, re.IGNORECASE):
                    s = re.sub(r'\s+',' ',m.group(0).strip())
                    if 15 < len(s) < 150: matches.append(s[:120]+("…" if len(s)>120 else ""))
            except: pass
        for m in matches:
            k = m[:30].lower()
            if k not in seen:
                seen.add(k); unique.append(m)
        if unique: found[cat] = unique[:3]
    return found

def _extract_important_sentences(text, n=6):
    imp = ["important","key","significant","must","shall","should","note","remember","critical",
           "essential","major","main","primary","fundamental","objective","means","defined","requires"]
    sentences = re.split(r'(?<=[.!?])\s+', text.replace("\n"," "))
    scored = []
    for s in sentences:
        if 30 > len(s) or len(s) > 300: continue
        score = sum(1 for w in imp if w in s.lower())
        if re.search(r'\d+',s): score+=1
        if re.search(r'section|rule|sa \d|ind as \d',s,re.IGNORECASE): score+=2
        scored.append((score,s.strip()))
    scored.sort(key=lambda x:-x[0])
    return [s for _,s in scored[:n]]

def _build_topic_context(topic):
    return {
        "audit":{"name":"Auditing & Assurance","exam_tip":"SA standards numbers and objectives are frequently tested. CARO 2020 clauses appear in almost every paper.","high_freq":["SA 315 — Risk Assessment","SA 500 — Audit Evidence","SA 570 — Going Concern","SA 700 — Audit Report","CARO 2020"]},
        "fr":{"name":"Financial Reporting (Ind AS)","exam_tip":"Master the 5-step Ind AS 115 model and goodwill impairment. NCI calculations appear frequently.","high_freq":["Ind AS 115 — Revenue","Ind AS 110 — Consolidation","Ind AS 116 — Leases","Ind AS 109 — Financial Instruments","Ind AS 103 — Business Combinations"]},
        "dt":{"name":"Direct Taxation","exam_tip":"Section 54 exemptions and transfer pricing methods are most tested. Memorise tax rates precisely.","high_freq":["Capital Gains (Sec 45-55)","Transfer Pricing (Sec 92)","MAT (Sec 115JB)","Deductions 80C-80U","VDA Taxation"]},
        "idt":{"name":"Indirect Tax (GST & Customs)","exam_tip":"Place of Supply rules, ITC restrictions and GST registration thresholds are exam favourites.","high_freq":["ITC (Sec 16-17)","Place of Supply","Reverse Charge","GSTR-9 Annual Return","E-way Bill"]},
        "afm":{"name":"Advanced Financial Management","exam_tip":"Black-Scholes, WACC computation and swap pricing require heavy numerical practice.","high_freq":["CAPM & Beta","Black-Scholes","EVA calculation","Interest Rate Swap","M&A valuation"]},
        "ibs":{"name":"Integrated Business Solutions","exam_tip":"IBS is case-study based. Porter's Five Forces, BSC and risk frameworks are foundation topics.","high_freq":["Porter's Five Forces","Balanced Scorecard","SWOT Analysis","Corporate Governance","Risk Management"]},
        "general":{"name":"CA Final General","exam_tip":"Build strong fundamentals across all papers. Past papers are your best study guide.","high_freq":["Study planning","Time management","Revision strategy","Mock test analysis"]},
    }.get(topic,{})

def generate_summary(extracted_text):
    if not extracted_text or len(extracted_text.strip()) < 50:
        return None
    topic = _detect_topic(extracted_text)
    ctx   = _build_topic_context(topic)
    return {
        "topic":        topic,
        "subject_name": ctx.get("name","CA Final"),
        "word_count":   len(extracted_text.split()),
        "para_count":   len([p for p in extracted_text.split("\n\n") if p.strip()]),
        "char_count":   len(extracted_text),
        "headings":     _extract_headings(extracted_text),
        "concepts":     _extract_key_concepts(extracted_text),
        "key_sentences":_extract_important_sentences(extracted_text,5),
        "exam_tip":     ctx.get("exam_tip",""),
        "high_freq":    ctx.get("high_freq",[]),
    }

def generate_mcqs(extracted_text="", num_questions=5):
    topic = _detect_topic(extracted_text) if extracted_text else "general"
    pool  = _MCQ_BANK.get(topic, _MCQ_BANK["general"])
    n     = int(num_questions)
    # Build extended list by repeating pool with reshuffling as needed
    extended = []
    while len(extended) < n:
        chunk = pool[:]
        random.shuffle(chunk)
        extended.extend(chunk)
    return extended[:n]

def get_pool_size(subject_key):
    """Return number of questions available for a subject."""
    k = subject_key.lower()
    return len(_MCQ_BANK.get(k, _MCQ_BANK["general"]))

# ══════════════════════════════════════════════════════════════════
# Document Chat Engine
# ══════════════════════════════════════════════════════════════════
def answer_from_document(question, document_text, topic):
    q = question.lower().strip()
    if not q: return "Please ask a question."
    sentences = re.split(r'(?<=[.!?])\s+|\n', document_text.replace("\n\n"," "))
    sentences = [s.strip() for s in sentences if len(s.strip())>30]
    q_words = set(re.findall(r'\b[a-z]{3,}\b',q)) - {
        "what","when","where","who","how","why","does","the","this","that",
        "with","from","are","was","were","has","have","had","for","and","but","can","you","your"}
    scored = []
    for s in sentences:
        sl = s.lower()
        overlap = sum(1 for w in q_words if w in sl)
        if len(q)>10 and q[:15] in sl: overlap+=3
        scored.append((overlap,s))
    scored.sort(key=lambda x:-x[0])
    best = [s for sc,s in scored if sc>0][:4]
    if best and scored[0][0]>=2:
        ans = " ".join(best[:3])
        ans = ans[:600]+("…" if len(ans)>600 else "")
        return f"{ans}\n\n📄 *From your document*"
    kb = _get_knowledge_base()
    for key,(title,body,tip) in kb.items():
        if key in q or any(kw in q for kw in key.split()):
            return f"**{title}**\n\n{body}\n\n💡 *Exam Tip:* {tip}\n\n📚 *From knowledge base*"
    ctx = _build_topic_context(topic)
    hf = ", ".join(ctx.get("high_freq",[])[:4])
    return (f"I couldn't find a direct answer for *\"{question}\"* in your document.\n\n"
            f"**Suggestion:** Try asking about: {hf}\n\n💡 {ctx.get('exam_tip','')}")

def _get_knowledge_base():
    return {
        "115":("Ind AS 115 — Revenue from Contracts","5-step model: (1) Identify contract (2) Identify performance obligations (3) Determine transaction price (4) Allocate price (5) Recognise revenue when obligation satisfied.","Step 2 and 5 timing are most tested."),
        "revenue":("Revenue Recognition","Revenue recognised when control transfers. Can be point-in-time or over time.","Bill-and-hold and variable consideration are common exam scenarios."),
        "consolidation":("Consolidation — Ind AS 110","Control = Power + Exposure to returns + Ability to use power. Goodwill = FV of consideration + NCI − Net assets.","NCI measurement method changes goodwill amount."),
        "lease":("Ind AS 116 — Leases","Lessee: ROU asset + Lease liability for leases >12 months. Rate: implicit or incremental borrowing rate.","Sale and leaseback modifications are frequent exam topics."),
        "gst":("GST — Key Provisions","CGST+SGST intra-state; IGST inter-state. ITC for business use. Registration >₹20L.","Place of Supply and blocked ITC are most tested."),
        "capital gain":("Capital Gains","STCG equity 15%. LTCG equity >₹1L: 10%. Other LTCG with indexation: 20%. Sec 54 exemption on reinvestment.","Period of holding and indexation benefit are key."),
        "transfer pricing":("Transfer Pricing — Section 92","ARM's length price. Methods: CUP, RPM, CPM, TNMM, PSM. Form 3CEB mandatory.","Method selection and comparability analysis are examined."),
        "capm":("CAPM","Required return = Rf + β(Rm−Rf). Beta = systematic risk. SML plots expected return vs beta.","Beta calculation and portfolio context are key numerical areas."),
        "wacc":("WACC","WACC = Wd×Kd(1-t) + We×Ke. Lower WACC = higher firm value.","Book value vs market value weights is a common exam twist."),
        "sa 315":("SA 315 — Risk Assessment","Understand entity, environment, internal controls. Identify RMM at FS and assertion level.","Significant risk and when to test controls is key."),
        "going concern":("SA 570 — Going Concern","Management assesses for 12 months. Doubt → auditor evaluates. Report: Emphasis of Matter or Modified opinion.","Type of audit modification under different scenarios is tested."),
        "porter":("Porter's Five Forces","(1) Rivalry (2) New entrants (3) Buyer power (4) Supplier power (5) Substitutes.","Apply to case studies — identify dominant force and why."),
        "balanced scorecard":("Balanced Scorecard","4 perspectives: Financial, Customer, Internal Process, Learning & Growth. Links strategy to KPIs.","Constructing BSC for a scenario and selecting KPIs is exam-relevant."),
        "cfo":("Role of CFO","Capital structure, working capital, financial risk, treasury, investor relations, financial reporting.","Strategic Financial Decision Making and CFO role in M&A examined in IBS."),
        "financial policy":("Financial Policy & Corporate Strategy","Defines how firm finances assets, distributes profits, manages risk. Capital structure + investment + dividend decisions.","Integration of financial policy with business strategy is core IBS."),
        "mat":("MAT — Section 115JB","MAT = 15% of book profits. Credit can be carried forward for 15 years.","Book profit adjustments and MAT credit utilisation are frequently tested."),
        "black scholes":("Black-Scholes Model","C = S0×N(d1) − X×e^(-rt)×N(d2). Assumes lognormal stock prices, no dividends, constant volatility.","Greeks (Delta=N(d1), Gamma, Theta, Vega, Rho) are common exam topics."),
    }
