from typing import Dict, Any, Optional

class FinacleAdapter:
    """Mock RPA Connector for Infosys Finacle Core Banking Solution."""

    def fetch_account_ledger(self, customer_id: Optional[str] = None, account_no: Optional[str] = None) -> Dict[str, Any]:
        return {
            "system": "FINACLE_CORE_BANKING",
            "account_summary": {
                "account_number_masked": account_no or "XXXX10029384",
                "account_type": "SAVINGS_ACCOUNT",
                "operating_status": "ACTIVE",
                "ledger_balance": 184500.50,
                "currency": "INR"
            },
            "recent_audit_transactions": [
                {
                    "txn_date": "2026-10-28",
                    "narration": "NEFT FORECLOSURE RECOVERY HDFC000192837",
                    "amount": 3315000.0,
                    "type": "DEBIT",
                    "status": "POSTED"
                }
            ]
        }
