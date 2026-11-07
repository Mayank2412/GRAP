from datetime import datetime
from typing import Dict, Any

try:
    from .templates import render_approval_letter, render_denial_letter
    from ..storage.db import SRRepository
except (ImportError, ValueError):
    from templates import render_approval_letter, render_denial_letter
    from db import SRRepository

class OutboundResponseSystem:
    """
    Outbound Response System handling Denial of Service and Case Handover.
    Generates formal customer and regulatory letters and updates the SR state machine.
    """

    def __init__(self, repo: SRRepository):
        self.repo = repo

    def dispatch(self, docket: Dict[str, Any], decision: Dict[str, Any], qc_result: Dict[str, Any], customer_name: str) -> Dict[str, Any]:
        sr_id = docket["sr_id"]
        decision["dispatch_date"] = datetime.utcnow().strftime("%d %b %Y")
        
        if not qc_result.get("certified_for_dispatch", False):
            return {
                "status": "HALTED_BY_QC",
                "message": "Dispatch blocked: QC validation failed.",
                "qc_flags": qc_result.get("factual_validation_flags", [])
            }

        is_approved = decision.get("decision") == "APPROVE_FULL_REDRESS"
        
        if is_approved:
            # Case Handover Agent
            final_letter = render_approval_letter(customer_name, sr_id, decision, docket)
            dispatch_type = "CASE_HANDOVER_APPROVED"
        else:
            # Denial of Service Agent
            final_letter = render_denial_letter(customer_name, sr_id, decision, docket)
            dispatch_type = "DENIAL_OF_SERVICE"

        # Update SR database to DISPATCHED
        now = datetime.utcnow().isoformat()
        conn = self.repo.db_path
        import sqlite3
        con = sqlite3.connect(conn)
        cur = con.cursor()
        cur.execute("""
            UPDATE service_requests
            SET status = 'DISPATCHED', decision_json = ?, qc_json = ?, final_response = ?, updated_at = ?
            WHERE sr_id = ?
        """, (str(decision), str(qc_result), final_letter, now, sr_id))
        
        cur.execute("""
            INSERT INTO audit_logs (sr_id, action, actor, details, timestamp)
            VALUES (?, ?, ?, ?, ?)
        """, (sr_id, "RESPONSE_DISPATCHED", "OutboundCaseHandoverAgent", f"Dispatch type: {dispatch_type}. Final letter certified and sent to customer and Ombudsman.", now))
        con.commit()
        con.close()

        return {
            "sr_id": sr_id,
            "status": "DISPATCHED",
            "dispatch_type": dispatch_type,
            "final_letter": final_letter
        }
