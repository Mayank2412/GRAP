from typing import Dict, Any, Optional

class CTLPrimeAdapter:
    """Mock RPA Connector for CTL Prime Card Management System (CMS)."""

    def fetch_card_dispute_context(self, card_number_masked: Optional[str], txn_ref: Optional[str]) -> Dict[str, Any]:
        return {
            "system": "CTL_PRIME",
            "card_summary": {
                "card_number_masked": card_number_masked or "XXXX4491",
                "card_product": "Axis Bank Magnus Credit Card",
                "card_status": "BLOCKED_CUSTOMER_HOTLISTED",
                "credit_limit": 500000,
                "available_limit": 421500
            },
            "transaction_record": {
                "auth_code": "AUTH982019",
                "transaction_reference": txn_ref or "TXN88921049",
                "merchant_name": "LUXE RETAIL DUBAI",
                "merchant_category_code": "5311",
                "pos_entry_mode": "E-COMMERCE_NON_3DS", # Key evidence: No OTP triggered
                "currency": "AED",
                "billed_inr_amount": 48500.0,
                "settlement_status": "SETTLED",
                "card_present": False,
                "otp_authenticated": False
            },
            "dispute_guidelines": {
                "chargeback_rights_available": True,
                "reason_code": "4837_NO_CARDHOLDER_AUTHORIZATION",
                "visa_mastercard_filing_deadline_days": 120,
                "provisional_credit_mandated_by_rbi": True # RBI Zero Liability Circular: customer notified within 3 days
            }
        }
