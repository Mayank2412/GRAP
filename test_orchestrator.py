import sys
base = '/working_dir/c_091f4c4879d0f9ea/grievance_automation'
sys.path.extend([
    base,
    f'{base}/src',
    f'{base}/src/intake',
    f'{base}/src/storage',
    f'{base}/src/adapters',
    f'{base}/src/orchestration'
])

import json
from parser import EmailGrievanceParser
from db import SRRepository
from orchestrator import CaseHandlingOrchestrator

sample_email_1 = """From: Rajiv Malhotra <rajiv.malhotra82@gmail.com>
To: grievance.redressal@axisbank.bank.in
Date: Fri, 06 Nov 2026 14:22:00 +0530
Subject: URGENT: Unauthorized transaction on Credit Card - Escalation to RBI Ombudsman

Dear Nodal Officer / Grievance Team,

I am writing to register an urgent grievance regarding an unauthorized charge of Rs. 48,500.00 on my Axis Bank Credit Card ending in 4491 (Card No: 4532-XXXX-XXXX-4491, Customer ID: CUST902184).

On 04 Nov 2026, I received an SMS stating a POS transaction took place at 'LUXE RETAIL DUBAI' under Ref No: TXN88921049 for INR 48,500. I was physically in Mumbai and never shared my OTP or CVV. 

I called customer care immediately and blocked the card, but no provisional credit has been provided yet. If this amount is not reversed within 48 hours, I will formally escalate this complaint to the Banking Ombudsman under the Reserve Bank of India (RBI) Integrated Ombudsman Scheme, 2021.

Contact: +91 9820123456
Demanding immediate reversal and temporary credit.

Regards,
Rajiv Malhotra
"""

sample_email_2 = """From: Priya Sharma <priya.sharma@outlook.com>
To: loans.grievance@axisbank.bank.in
Date: Sat, 07 Nov 2026 09:15:00 +0530
Subject: Illegal Foreclosure Penalty on Floating Rate Home Loan

To Customer Support,

My Home Loan Account Number is LN-HL-99201940 and Customer Code is CUST441029. 

I requested complete pre-closure of my home loan on 28th October 2026. However, your team has levied a 2% foreclosure charge of Rs. 65,000 against UTR HDFC000192837. 

As per RBI circular guidelines, banks are strictly prohibited from levying foreclosure charges on floating-rate term loans sanctioned to individual borrowers. I demand an immediate waiver of Rs. 65,000 and issuance of my loan NOC and original title deeds without delay.

Phone: +91 9811223344
"""

if __name__ == "__main__":
    repo = SRRepository()
    parser = EmailGrievanceParser()
    orch = CaseHandlingOrchestrator(repo)

    print("=" * 65)
    print("TEST CASE 1: Credit Card Dispute (CTL Prime, Finacle, Data Lake)")
    print("=" * 65)
    case_1 = parser.parse_raw_email(sample_email_1)
    docket_1 = orch.process_case(case_1.dict())
    print("\n[INVESTIGATION DOCKET SUMMARY]")
    print(f"SR ID: {docket_1['sr_id']}")
    print(f"Systems Queried: {list(docket_1['evidence'].keys())}")
    print("Key Findings:")
    for finding in docket_1['key_findings']:
        print(f" - {finding}")
    
    stored_1 = repo.get_sr(case_1.sr_id)
    print(f"Database Status: {stored_1['status']}")

    print("\n" + "=" * 65)
    print("TEST CASE 2: Home Loan Foreclosure Charge Dispute (FinOne Neo)")
    print("=" * 65)
    case_2 = parser.parse_raw_email(sample_email_2)
    docket_2 = orch.process_case(case_2.dict())
    print("\n[INVESTIGATION DOCKET SUMMARY]")
    print(f"SR ID: {docket_2['sr_id']}")
    print(f"Systems Queried: {list(docket_2['evidence'].keys())}")
    print("Policy Violations Detected:")
    for v in docket_2['policy_violations_detected']:
        print(f" - Circular: {v['circular_ref']}")
        print(f"   Violation: {v['violation']}")
    
    stored_2 = repo.get_sr(case_2.sr_id)
    print(f"Database Status: {stored_2['status']}")
