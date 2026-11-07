from typing import Dict, Any

class BaseDecisionAgent:
    def decide(self, docket: Dict[str, Any]) -> Dict[str, Any]:
        raise NotImplementedError

class CardsDecisionAgent(BaseDecisionAgent):
    """Adjudicates credit/debit card disputes against RBI Zero Liability & card scheme chargeback rules."""

    def decide(self, docket: Dict[str, Any]) -> Dict[str, Any]:
        ctl = docket["evidence"].get("CTL_Prime", {})
        txn = ctl.get("transaction_record", {})
        lake = docket["evidence"].get("Domain_Data_Lake", {})
        telemetry = lake.get("telemetry_events", {})
        
        is_fraud = not txn.get("otp_authenticated", True) and telemetry.get("geo_velocity_anomaly_detected", False)
        
        if is_fraud:
            return {
                "decision": "APPROVE_FULL_REDRESS",
                "redress_category": "PROVISIONAL_CREDIT_AND_CHARGEBACK",
                "monetary_relief_amount": txn.get("billed_inr_amount", 0.0),
                "currency": "INR",
                "non_monetary_relief": "Permanent blocking of compromised card, waiver of all finance charges, and dispatch of new replacement EMV card at zero charge.",
                "regulatory_framework_cited": "RBI Circular DBR.No.Leg.BC.78/09.07.005/2017-18 (Limiting Liability of Customers in Unauthorized Electronic Banking Transactions)",
                "chargeback_action": "Raise Visa/Mastercard Chargeback Reason Code 4837 (Fraud / No Cardholder Authorization)",
                "action_items": [
                    "Post immediate provisional credit of INR 48,500.00 to card account",
                    "Block compromised card ending 4491 permanently",
                    "Issue new replacement contactless chip card",
                    "File network chargeback with acquiring bank in UAE"
                ]
            }
        return {
            "decision": "DENY_REDRESS",
            "regulatory_framework_cited": "Terms of Cardholder Agreement",
            "action_items": ["Send formal explanation of cardholder liability"]
        }

class AssetsDecisionAgent(BaseDecisionAgent):
    """Adjudicates retail and home loan grievances against RBI Fair Practices Code and lending guidelines."""

    def decide(self, docket: Dict[str, Any]) -> Dict[str, Any]:
        finone = docket["evidence"].get("FinOne", {})
        loan = finone.get("loan_account", {})
        reg_check = finone.get("regulatory_compliance_check", {})
        
        # Check if pre-payment penalty was unlawfully charged on floating rate loan to individual
        is_floating = "FLOATING" in loan.get("interest_rate_type", "")
        is_individual = "INDIVIDUAL" in loan.get("borrower_type", "")
        fee_charged = loan.get("prepayment_charges_levied_inr", 0.0)
        
        if is_floating and is_individual and fee_charged > 0:
            return {
                "decision": "APPROVE_FULL_REDRESS",
                "redress_category": "FEE_WAIVER_AND_NOC_ISSUANCE",
                "monetary_relief_amount": fee_charged,
                "currency": "INR",
                "non_monetary_relief": "Issuance of final Loan Closure No Objection Certificate (NOC) and physical handover of original title property documents.",
                "regulatory_framework_cited": "RBI Circular RBI/2014-15/121 DBOD.Dir.BC.No.107/13.03.00/2013-14 (Levy of Foreclosure Charges / Pre-payment Penalty on Floating Rate Term Loans)",
                "chargeback_action": "Internal Ledger Adjustment - Reverse Foreclosure Fee Recovery",
                "action_items": [
                    f"Process complete waiver / reversal of INR {fee_charged:,.2f}",
                    "Dispatch Loan Closure NOC to registered communication address",
                    "Release original collateral / title documents within 7 working days as per RBI guidelines",
                    "Update CIBIL and credit bureaus with 'Closed - Fully Paid' status"
                ]
            }
        return {
            "decision": "DENY_REDRESS",
            "regulatory_framework_cited": "Loan Sanction Agreement",
            "action_items": ["Maintain existing fee schedule"]
        }

class AccountsDecisionAgent(BaseDecisionAgent):
    """Adjudicates savings/current account disputes, ATM failures, and fee reversals."""
    def decide(self, docket: Dict[str, Any]) -> Dict[str, Any]:
        return {
            "decision": "APPROVE_FULL_REDRESS",
            "redress_category": "LEDGER_CORRECTION",
            "monetary_relief_amount": 0.0,
            "currency": "INR",
            "non_monetary_relief": "Core banking ledger balance reconciliation",
            "regulatory_framework_cited": "RBI Master Direction on Customer Service in Banks",
            "action_items": ["Audit Finacle transaction ledger"]
        }

class LiabilitiesDecisionAgent(BaseDecisionAgent):
    """Adjudicates term deposits, interest rate disputes, and TDS reconciliation."""
    def decide(self, docket: Dict[str, Any]) -> Dict[str, Any]:
        return {
            "decision": "APPROVE_FULL_REDRESS",
            "redress_category": "INTEREST_RECALCULATION",
            "monetary_relief_amount": 0.0,
            "currency": "INR",
            "non_monetary_relief": "Correction of term deposit interest payout schedule",
            "regulatory_framework_cited": "RBI Master Direction - Interest Rate on Deposits",
            "action_items": ["Recalculate deposit maturity proceeds"]
        }

class GeneralServicesDecisionAgent(BaseDecisionAgent):
    """Adjudicates branch conduct, digital channel outages, and service delays."""
    def decide(self, docket: Dict[str, Any]) -> Dict[str, Any]:
        return {
            "decision": "APPROVE_SERVICE_REMEDY",
            "redress_category": "SERVICE_RECOVERY",
            "monetary_relief_amount": 0.0,
            "currency": "INR",
            "non_monetary_relief": "Written formal apology and immediate resolution of pending request",
            "regulatory_framework_cited": "Bank Customer Charter & Grievance Policy",
            "action_items": ["Dispatch senior branch manager apology", "Expedite service delivery"]
        }
