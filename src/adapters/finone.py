from typing import Dict, Any, Optional

class FinOneAdapter:
    """Mock RPA Connector for Nucleus Software FinnOne Loan Management System."""

    def fetch_loan_account_context(self, loan_account_no: Optional[str]) -> Dict[str, Any]:
        return {
            "system": "FINNONE_NEO",
            "loan_account": {
                "loan_account_number": loan_account_no or "LN-HL-99201940",
                "loan_type": "HOME_LOAN",
                "borrower_type": "INDIVIDUAL_NATURAL_PERSON", # Key regulatory distinction
                "interest_rate_type": "FLOATING_RATE_BENCHMARK_LINKED", # Key regulatory criteria
                "original_sanction_amount": 4500000.0,
                "outstanding_principal_at_closure": 3250000.0,
                "closure_request_date": "2026-10-28",
                "prepayment_charges_levied_inr": 65000.0, # 2% of 3.25M
                "noc_status": "WITHHELD_PENDING_CHARGES_PAYMENT"
            },
            "regulatory_compliance_check": {
                "rbi_circular_ref": "RBI/2014-15/121 DBOD.Dir.BC.No.107/13.03.00/2013-14",
                "rule": "Banks shall not charge foreclosure charges/pre-payment penalties on floating rate term loans sanctioned to individual borrowers",
                "is_charge_legally_permitted": False, # Explicit policy violation
                "recommended_action": "FULL_WAIVER_AND_IMMEDIATE_NOC_DISPATCH"
            }
        }
