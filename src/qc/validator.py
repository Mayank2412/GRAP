from typing import Dict, Any, List

try:
    from .responsible_ai import ResponsibleAIAgent
except (ImportError, ValueError):
    from responsible_ai import ResponsibleAIAgent

class RealTimeQCSystem:
    """
    Real-Time Quality Control System combining Response Validation with Responsible AI.
    Acts as the final automated gatekeeper before customer / ombudsman dispatch.
    """

    def __init__(self):
        self.rai_agent = ResponsibleAIAgent()

    def evaluate_response(self, docket: Dict[str, Any], decision: Dict[str, Any], draft_response: str) -> Dict[str, Any]:
        rai_result = self.rai_agent.audit(decision, draft_response)
        
        validation_flags: List[str] = []
        
        # 1. Fact-check monetary relief against evidence docket
        decided_relief = decision.get("monetary_relief_amount", 0.0)
        domain = decision.get("evaluated_domain")
        
        if domain == "CARDS":
            ctl = docket.get("evidence", {}).get("CTL_Prime", {})
            evidence_amt = ctl.get("transaction_record", {}).get("billed_inr_amount", 0.0)
            if decided_relief > 0 and abs(decided_relief - evidence_amt) > 0.01:
                validation_flags.append(f"FACTUAL_MISMATCH: Relief amount {decided_relief} does not match CTL Prime ledger {evidence_amt}.")
        elif domain == "LENDING_ASSETS":
            finone = docket.get("evidence", {}).get("FinOne", {})
            evidence_amt = finone.get("loan_account", {}).get("prepayment_charges_levied_inr", 0.0)
            if decided_relief > 0 and abs(decided_relief - evidence_amt) > 0.01:
                validation_flags.append(f"FACTUAL_MISMATCH: Relief amount {decided_relief} does not match FinOne ledger {evidence_amt}.")

        # 2. Verify Regulatory citation presence
        if not decision.get("regulatory_framework_cited"):
            validation_flags.append("COMPLIANCE_ERROR: Missing statutory regulatory citation for decision.")

        overall_passed = rai_result["passed"] and len(validation_flags) == 0

        return {
            "qc_verdict": "APPROVED" if overall_passed else "REJECTED_NEEDS_REVISION",
            "passed": overall_passed,
            "responsible_ai_audit": rai_result,
            "factual_validation_flags": validation_flags,
            "certified_for_dispatch": overall_passed
        }
