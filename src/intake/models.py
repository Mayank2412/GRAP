from enum import Enum
from typing import Optional, List
from pydantic import BaseModel, Field

class ProductDomain(str, Enum):
    ACCOUNTS_AND_DEPOSITS = "ACCOUNTS_AND_DEPOSITS" # Routed to Finacle
    CARDS = "CARDS"                                 # Routed to CTL Prime
    LENDING_ASSETS = "LENDING_ASSETS"               # Routed to FinOne
    LIABILITIES = "LIABILITIES"                     # Routed to Liabilities / Finacle
    GENERAL_SERVICES = "GENERAL_SERVICES"           # Routed to CRMNext / Branch Ops

class PriorityLevel(str, Enum):
    P1_CRITICAL = "P1_CRITICAL"   # Regulatory Ombudsman, high amount, legal notice
    P2_HIGH = "P2_HIGH"           # Substantial financial loss, repeated follow-up
    P3_STANDARD = "P3_STANDARD"   # General inquiry, routine service turnaround

class GrievanceSubCategory(str, Enum):
    UNAUTHORIZED_TRANSACTION = "UNAUTHORIZED_TRANSACTION"
    BILLING_DISPUTE = "BILLING_DISPUTE"
    ATM_DISPENSE_FAILURE = "ATM_DISPENSE_FAILURE"
    LOAN_FORECLOSURE_DISPUTE = "LOAN_FORECLOSURE_DISPUTE"
    INTEREST_RATE_MISCALCULATION = "INTEREST_RATE_MISCALCULATION"
    FAILED_REFUND_CHARGEBACK = "FAILED_REFUND_CHARGEBACK"
    ACCOUNT_FREEZE_MAINTENANCE = "ACCOUNT_FREEZE_MAINTENANCE"
    SERVICE_DELAY_STAFF_CONDUCT = "SERVICE_DELAY_STAFF_CONDUCT"
    OTHER = "OTHER"

class CustomerIdentifiers(BaseModel):
    customer_id: Optional[str] = Field(None, description="Extracted bank customer ID")
    account_number: Optional[str] = Field(None, description="Masked account number")
    card_number: Optional[str] = Field(None, description="Masked card number")
    loan_account_number: Optional[str] = Field(None, description="Loan or asset reference")
    phone_number: Optional[str] = Field(None, description="Contact phone number")

class FinancialDispute(BaseModel):
    disputed_amount: Optional[float] = Field(None, description="Disputed amount")
    currency: str = Field("INR", description="Currency code (e.g. INR, USD)")
    transaction_reference: Optional[str] = Field(None, description="UTR, RRN, or Txn Ref")
    transaction_date: Optional[str] = Field(None, description="Date of disputed transaction")

class RegulatoryDetails(BaseModel):
    is_regulatory_escalation: bool = Field(False, description="Flagged if RBI/Ombudsman is cited")
    regulatory_body: Optional[str] = Field(None, description="e.g., RBI Ombudsman, Consumer Forum")
    tat_deadline_hours: int = Field(720, description="Statutory SLA (e.g., 30 days = 720h, urgent = 48h)")

class GrievanceCaseOutput(BaseModel):
    sr_id: str = Field(..., description="Unique Service Request identifier")
    intake_channel: str = Field("EMAIL", description="Channel of intake")
    received_at: str = Field(..., description="Timestamp of receipt")
    sender_name: str = Field(..., description="Extracted sender display name")
    sender_email: str = Field(..., description="Sender email address")
    subject: str = Field(..., description="Email subject")
    
    # Classification & Triaging
    product_domain: ProductDomain = Field(..., description="Primary product line")
    sub_category: GrievanceSubCategory = Field(..., description="Specific grievance type")
    priority: PriorityLevel = Field(..., description="Triage priority level")
    
    # Details & Entities
    customer_identifiers: CustomerIdentifiers
    financial_dispute: FinancialDispute
    regulatory_details: RegulatoryDetails
    
    # Narrative & Synthesis
    narrative_summary: str = Field(..., description="Structured summary of the issue")
    demanded_remedy: str = Field(..., description="Remedy demanded by customer")
    
    # RPA Routing Instructions
    target_skilled_adapters: List[str] = Field(..., description="Core systems to query (Finacle, CTL Prime, FinOne, etc.)")
    requires_human_oversight: bool = Field(False, description="If true, case handover must flag for compliance officer")
