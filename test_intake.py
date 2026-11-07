import sys
sys.path.insert(0, '/working_dir/c_091f4c4879d0f9ea/grievance_automation/src/intake')

import json
from parser import EmailGrievanceParser

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
    parser = EmailGrievanceParser()
    
    print("=== Testing Sample 1: Credit Card Dispute with Ombudsman Escalation ===")
    res1 = parser.parse_raw_email(sample_email_1)
    print(res1.json(indent=2))
    
    print("\n=== Testing Sample 2: Home Loan Foreclosure Dispute ===")
    res2 = parser.parse_raw_email(sample_email_2)
    print(res2.json(indent=2))
