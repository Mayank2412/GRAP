from typing import Dict, Any, Optional

class CRMNextAdapter:
    """Mock RPA Connector for CRMNext Customer Relationship Management."""

    def __init__(self):
        self.customers = {
            "CUST902184": {
                "customer_id": "CUST902184",
                "full_name": "Rajiv Malhotra",
                "segment": "BURGUNDY_WEALTH",
                "relationship_years": 8,
                "kyc_status": "VERIFIED_TIER_1",
                "total_relationship_value_inr": 4200000,
                "past_grievance_count_12m": 0,
                "nps_score": 9,
                "contact_email": "rajiv.malhotra82@gmail.com",
                "contact_mobile": "+91 9820123456"
            },
            "CUST441029": {
                "customer_id": "CUST441029",
                "full_name": "Priya Sharma",
                "segment": "RETAIL_PRIORITY",
                "relationship_years": 5,
                "kyc_status": "VERIFIED_TIER_1",
                "total_relationship_value_inr": 6800000,
                "past_grievance_count_12m": 1,
                "nps_score": 8,
                "contact_email": "priya.sharma@outlook.com",
                "contact_mobile": "+91 9811223344"
            }
        }

    def fetch_customer_360(self, customer_id: Optional[str] = None, email: Optional[str] = None) -> Dict[str, Any]:
        if customer_id and customer_id in self.customers:
            return {"status": "SUCCESS", "data": self.customers[customer_id]}
        for cust in self.customers.values():
            if email and cust["contact_email"].lower() == email.lower():
                return {"status": "SUCCESS", "data": cust}
        # Fallback profile
        return {
            "status": "NOT_FOUND",
            "data": {
                "customer_id": customer_id or "UNKNOWN",
                "segment": "RETAIL_STANDARD",
                "kyc_status": "PENDING_VERIFICATION",
                "total_relationship_value_inr": 0,
                "past_grievance_count_12m": 0
            }
        }
