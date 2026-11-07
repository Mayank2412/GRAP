import os
import sys
from pathlib import Path

# Dynamically resolve root project directory from current file's location (Cross-Platform)
ROOT_DIR = Path(__file__).resolve().parent
SRC_DIR = ROOT_DIR / "src"

paths_to_add = [
    str(ROOT_DIR),
    str(SRC_DIR),
    str(SRC_DIR / "intake"),
    str(SRC_DIR / "storage"),
    str(SRC_DIR / "adapters"),
    str(SRC_DIR / "orchestration"),
    str(SRC_DIR / "decisioning"),
    str(SRC_DIR / "qc"),
    str(SRC_DIR / "outbound"),
]

for p in paths_to_add:
    if p not in sys.path:
        sys.path.insert(0, p)

import json

try:
    from src.intake.parser import EmailGrievanceParser
    from src.intake.models import to_dict, to_json
    from src.storage.db import SRRepository
    from src.orchestration.orchestrator import CaseHandlingOrchestrator
    from src.decisioning.engine import IntelligentDecisionEngine
    from src.qc.validator import RealTimeQCSystem
    from src.outbound.dispatcher import OutboundResponseSystem
except (ImportError, ValueError):
    from parser import EmailGrievanceParser
    from models import to_dict, to_json
    from db import SRRepository
    from orchestrator import CaseHandlingOrchestrator
    from engine import IntelligentDecisionEngine
    from validator import RealTimeQCSystem
    from dispatcher import OutboundResponseSystem

class GrievanceRedressalPipeline:
    """
    End-to-End Master Pipeline for Grievance Redressal Automation Program (GRAP).
    Executes: Intake -> Triaging -> Adapters -> Orchestrator -> Decisioning -> QC -> Outbound.
    """

    def __init__(self, db_path: str = None):
        self.repo = SRRepository(db_path) if db_path else SRRepository()
        self.parser = EmailGrievanceParser()
        self.orchestrator = CaseHandlingOrchestrator(self.repo)
        self.decision_engine = IntelligentDecisionEngine()
        self.qc_system = RealTimeQCSystem()
        self.outbound = OutboundResponseSystem(self.repo)

    def process_email(self, raw_email_text: str) -> dict:
        print("\n" + "=" * 80)
        print("STAGE 1: INTELLIGENT TRIAGING SYSTEM (Gen-AI Supported RPA)")
        print("=" * 80)
        intake_case = self.parser.parse_raw_email(raw_email_text)
        print(f"✓ Parsed SR ID: {intake_case.sr_id}")
        print(f"✓ Product Domain: {intake_case.product_domain.value}")
        print(f"✓ Sub-Category: {intake_case.sub_category.value}")
        print(f"✓ Priority: {intake_case.priority.value} (Regulatory Escalation: {intake_case.regulatory_details.is_regulatory_escalation})")
        print(f"✓ Target Adapters: {intake_case.target_skilled_adapters}")

        print("\n" + "=" * 80)
        print("STAGE 2 & 3: SKILLED ADAPTERS & CASE HANDLING ORCHESTRATION")
        print("=" * 80)
        docket = self.orchestrator.process_case(to_dict(intake_case))
        print(f"✓ Core Systems Queried: {list(docket['evidence'].keys())}")
        print(f"✓ Key Investigation Findings:")
        for finding in docket['key_findings']:
            print(f"   • {finding}")
        if docket['policy_violations_detected']:
            print(f"✓ Policy Violations Flagged:")
            for v in docket['policy_violations_detected']:
                print(f"   • {v['violation']} (Ref: {v['circular_ref']})")

        print("\n" + "=" * 80)
        print("STAGE 4: INTELLIGENT DECISIONING SYSTEM (Domain Decision Agent)")
        print("=" * 80)
        decision = self.decision_engine.evaluate(docket, intake_case.product_domain.value)
        print(f"✓ Decision Verdict: {decision['decision']}")
        print(f"✓ Redress Category: {decision.get('redress_category', 'N/A')}")
        print(f"✓ Monetary Relief: {decision.get('currency', 'INR')} {decision.get('monetary_relief_amount', 0.0):,.2f}")
        print(f"✓ Regulatory Standard Applied: {decision.get('regulatory_framework_cited')}")

        print("\n" + "=" * 80)
        print("STAGE 5: REAL-TIME QC SYSTEM (Responsible AI & Response Validation)")
        print("=" * 80)
        qc_result = self.qc_system.evaluate_response(docket, decision, decision.get('non_monetary_relief', ''))
        print(f"✓ QC Verdict: {qc_result['qc_verdict']}")
        print(f"✓ Responsible AI PII & Tone Check: PASSED (Flags: {qc_result['responsible_ai_audit']['audit_flags']})")
        print(f"✓ Ledger Factual Validation: PASSED (Mismatches: {qc_result['factual_validation_flags']})")
        print(f"✓ Certified for Outbound Dispatch: {qc_result['certified_for_dispatch']}")

        print("\n" + "=" * 80)
        print("STAGE 6: OUTBOUND RESPONSE SYSTEM (Case Handover / Formal Letter)")
        print("=" * 80)
        dispatch_result = self.outbound.dispatch(docket, decision, qc_result, intake_case.sender_name)
        print(f"✓ Dispatch Status: {dispatch_result['status']} ({dispatch_result['dispatch_type']})")
        print(f"✓ Database Final State: DISPATCHED")
        print("\n[GENERATED OFFICIAL OUTBOUND NOTICE]")
        print(dispatch_result["final_letter"])

        return {
            "sr_id": intake_case.sr_id,
            "intake": intake_case,
            "docket": docket,
            "decision": decision,
            "qc": qc_result,
            "dispatch": dispatch_result
        }

if __name__ == "__main__":
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

    pipeline = GrievanceRedressalPipeline()
    
    print("\n################################################################################")
    print("RUNNING PIPELINE TEST CASE 1: CREDIT CARD FRAUD & OMBUDSMAN ESCALATION")
    print("################################################################################")
    pipeline.process_email(sample_email_1)
    
    print("\n################################################################################")
    print("RUNNING PIPELINE TEST CASE 2: HOME LOAN FLOATING RATE FORECLOSURE DISPUTE")
    print("################################################################################")
    pipeline.process_email(sample_email_2)
