from typing import Dict, Any
import json
from datetime import datetime

try:
    from ..storage.db import SRRepository
    from ..adapters import (
        CRMNextAdapter,
        CTLPrimeAdapter,
        FinOneAdapter,
        FinacleAdapter,
        DomainDataLakeAdapter
    )
except (ImportError, ValueError):
    from db import SRRepository
    from crmnext import CRMNextAdapter
    from ctl_prime import CTLPrimeAdapter
    from finone import FinOneAdapter
    from finacle import FinacleAdapter
    from data_lake import DomainDataLakeAdapter

class CaseHandlingOrchestrator:
    """
    Case Handling Orchestrator for Grievance Redressal Automation.
    Coordinates between deterministic RPA adapters and compiles the Investigation Docket.
    """

    def __init__(self, repo: SRRepository):
        self.repo = repo
        self.crmnext = CRMNextAdapter()
        self.ctl_prime = CTLPrimeAdapter()
        self.finone = FinOneAdapter()
        self.finacle = FinacleAdapter()
        self.data_lake = DomainDataLakeAdapter()

    def process_case(self, intake_case: Dict[str, Any]) -> Dict[str, Any]:
        sr_id = intake_case["sr_id"]
        cust_id = intake_case.get("customer_identifiers", {}).get("customer_id")
        domain = intake_case.get("product_domain")
        adapters = intake_case.get("target_skilled_adapters", [])
        
        # 1. Register SR in state store
        self.repo.register_sr(intake_case)
        
        # 2. Gather Evidence Dossier from targeted adapters
        evidence_docket: Dict[str, Any] = {
            "sr_id": sr_id,
            "intake_summary": intake_case.get("narrative_summary"),
            "regulatory_flag": intake_case.get("regulatory_details", {}).get("is_regulatory_escalation", False),
            "tat_hours": intake_case.get("regulatory_details", {}).get("tat_deadline_hours", 720),
            "evidence": {},
            "key_findings": [],
            "policy_violations_detected": []
        }

        # Query CRMNext (Customer 360)
        c360 = self.crmnext.fetch_customer_360(
            customer_id=cust_id,
            email=intake_case.get("sender_email")
        )
        evidence_docket["evidence"]["CRMNext"] = c360

        # Query Finacle (Core Banking Ledger)
        if "Finacle" in adapters:
            finacle_data = self.finacle.fetch_account_ledger(
                customer_id=cust_id,
                account_no=intake_case.get("customer_identifiers", {}).get("account_number")
            )
            evidence_docket["evidence"]["Finacle"] = finacle_data

        # Query CTL Prime (Cards)
        if "CTL PRime" in adapters or domain == "CARDS":
            ctl_data = self.ctl_prime.fetch_card_dispute_context(
                card_number_masked=intake_case.get("customer_identifiers", {}).get("card_number"),
                txn_ref=intake_case.get("financial_dispute", {}).get("transaction_reference")
            )
            evidence_docket["evidence"]["CTL_Prime"] = ctl_data
            
            # Rule check: 3DS OTP vs Non-3DS
            if not ctl_data["transaction_record"]["otp_authenticated"]:
                evidence_docket["key_findings"].append("Transaction completed without Two-Factor Authentication (Non-3DS international transaction).")
                evidence_docket["key_findings"].append("Customer reported within 3 days; eligible for zero customer liability under RBI circular on unauthorized electronic banking transactions.")

        # Query FinOne (Lending / Assets)
        if "FinOne" in adapters or domain == "LENDING_ASSETS":
            finone_data = self.finone.fetch_loan_account_context(
                loan_account_no=intake_case.get("customer_identifiers", {}).get("loan_account_number")
            )
            evidence_docket["evidence"]["FinOne"] = finone_data
            
            # Rule check: Floating rate loan foreclosure charge
            reg_check = finone_data["regulatory_compliance_check"]
            if not reg_check["is_charge_legally_permitted"]:
                evidence_docket["policy_violations_detected"].append({
                    "rule": reg_check["rule"],
                    "circular_ref": reg_check["rbi_circular_ref"],
                    "violation": "Prepayment / foreclosure penalty charged on individual floating rate home loan."
                })

        # Query Domain Data Lake (Telemetry & Logs)
        if "Domain Data Lake" in adapters:
            lake_data = self.data_lake.fetch_telemetry_audit(
                customer_id=cust_id,
                mobile=intake_case.get("customer_identifiers", {}).get("phone_number")
            )
            evidence_docket["evidence"]["Domain_Data_Lake"] = lake_data
            if lake_data["telemetry_events"]["geo_velocity_anomaly_detected"]:
                evidence_docket["key_findings"].append(lake_data["telemetry_events"]["details"])

        # 3. Update SR with compiled evidence docket
        self.repo.update_evidence(sr_id, evidence_docket)
        
        return evidence_docket
