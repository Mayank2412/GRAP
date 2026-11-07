from typing import Dict, Any

def render_approval_letter(customer_name: str, sr_id: str, decision: Dict[str, Any], docket: Dict[str, Any]) -> str:
    relief_amt = decision.get("monetary_relief_amount", 0.0)
    currency = decision.get("currency", "INR")
    reg_ref = decision.get("regulatory_framework_cited", "RBI Regulatory Directives")
    
    actions_formatted = "\n".join([f"  • {act}" for act in decision.get("action_items", [])])
    findings_formatted = "\n".join([f"  • {f}" for f in docket.get("key_findings", [])] or [f"  • {docket.get('intake_summary')}"])
    
    return f"""================================================================================
AXIS BANK LIMITED - REGULATORY GRIEVANCE REDRESSAL DIVISION
OFFICIAL RESOLUTION NOTICE & REDRESSAL ORDER
================================================================================

Date: {decision.get('dispatch_date', '07 Nov 2026')}
Service Request ID: {sr_id}
Customer Name: {customer_name}
Case Status: RESOLVED IN FAVOR OF CUSTOMER (FULL REDRESS APPROVED)

Dear {customer_name},

Sub: Redressal of Grievance regarding {decision.get('evaluated_domain')} - Service Request {sr_id}

We write with reference to your grievance dated regarding your recent financial dispute and escalation. The matter has been comprehensively investigated by our Regulatory Response Taskforce in accordance with {reg_ref}.

1. INVESTIGATION FINDINGS:
{findings_formatted}

2. RESOLUTION & FINANCIAL REDRESSAL:
In light of the verified evidence and applicable banking regulations, your grievance has been fully upheld. The following corrective actions have been authorized and executed:
{actions_formatted}

Total Financial Relief Approved: {currency} {relief_amt:,.2f}
Non-Financial Relief: {decision.get('non_monetary_relief', 'N/A')}

3. CLOSURE & REGULATORY ADHERENCE:
This matter is formally closed under our internal Service Request registry. If this grievance was lodged with or marked to the Reserve Bank of India (RBI) Ombudsman, a certified copy of this resolution has been submitted to the Ombudsman Secretariat.

Should you require any further assistance, you may contact our Principal Nodal Officer at pno@axisbank.bank.in.

Yours sincerely,

Grievance Redressal Officer
Regulatory & Compliance Operations
Axis Bank Limited
================================================================================
"""

def render_denial_letter(customer_name: str, sr_id: str, decision: Dict[str, Any], docket: Dict[str, Any]) -> str:
    reg_ref = decision.get("regulatory_framework_cited", "Banking Terms and Conditions")
    return f"""================================================================================
AXIS BANK LIMITED - REGULATORY GRIEVANCE REDRESSAL DIVISION
FORMAL DECISION NOTICE
================================================================================

Date: {decision.get('dispatch_date', '07 Nov 2026')}
Service Request ID: {sr_id}
Customer Name: {customer_name}
Case Status: INVESTIGATION CONCLUDED - REDRESS INELIGIBLE

Dear {customer_name},

Sub: Decision on Grievance {sr_id}

We write with reference to your grievance. Following detailed forensic and audit review across our core banking systems under {reg_ref}, we wish to advise that the disputed transaction was verified to be fully authorized under your credentials.

Consequently, financial redress cannot be considered under the extant regulatory policy. 

Right to Appeal:
If you are not satisfied with this decision, you have the right to appeal to our Principal Nodal Officer, or escalate to the Banking Ombudsman under the Reserve Bank of India Integrated Ombudsman Scheme, 2021 within statutory timelines.

Yours sincerely,

Grievance Redressal Officer
Axis Bank Limited
================================================================================
"""
