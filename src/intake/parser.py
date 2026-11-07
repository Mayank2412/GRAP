import re
import uuid
import email
from email import policy
from email.parser import BytesParser
from datetime import datetime
from typing import Dict, Any, Tuple

try:
    from .models import (
        GrievanceCaseOutput,
        ProductDomain,
        PriorityLevel,
        GrievanceSubCategory,
        CustomerIdentifiers,
        FinancialDispute,
        RegulatoryDetails
    )
except (ImportError, ValueError):
    from models import (
        GrievanceCaseOutput,
        ProductDomain,
        PriorityLevel,
        GrievanceSubCategory,
        CustomerIdentifiers,
        FinancialDispute,
        RegulatoryDetails
    )

class EmailGrievanceParser:
    """
    Gen-AI supported RPA Parser for Regulatory and Banking Grievance Ingestion.
    Extracts structured entities, detects regulatory urgency, maps to core banking 
    adapters, and outputs validated Pydantic JSON.
    """

    def parse_raw_email(self, raw_bytes_or_str: bytes | str) -> GrievanceCaseOutput:
        """Parses an RFC 822 / MIME format raw email."""
        if isinstance(raw_bytes_or_str, str):
            raw_bytes = raw_bytes_or_str.encode("utf-8")
        else:
            raw_bytes = raw_bytes_or_str

        msg = BytesParser(policy=policy.default).parsebytes(raw_bytes)

        sender = msg.get("From", "")
        sender_name, sender_email = self._extract_name_and_email(sender)
        subject = msg.get("Subject", "No Subject")
        date_str = msg.get("Date", datetime.utcnow().isoformat())

        body = ""
        if msg.is_multipart():
            for part in msg.walk():
                content_type = part.get_content_type()
                content_disposition = str(part.get("Content-Disposition", ""))
                if content_type == "text/plain" and "attachment" not in content_disposition:
                    body += part.get_payload(decode=True).decode(part.get_content_charset() or "utf-8", errors="replace") + "\n"
        else:
            body = msg.get_payload(decode=True).decode(msg.get_content_charset() or "utf-8", errors="replace")

        return self.process_email_payload({
            "sender_name": sender_name,
            "sender_email": sender_email,
            "subject": subject,
            "body": body,
            "received_at": date_str
        })

    def process_email_payload(self, payload: Dict[str, Any]) -> GrievanceCaseOutput:
        """Processes dictionary email payload into validated GrievanceCaseOutput."""
        subject = payload.get("subject", "")
        body = payload.get("body", "")
        full_text = f"{subject}\n{body}"
        sender_name = payload.get("sender_name") or "Valued Customer"
        sender_email = payload.get("sender_email") or "unknown@domain.com"
        received_at = payload.get("received_at") or datetime.utcnow().isoformat()

        # 1. Generate unique Service Request ID
        timestamp_prefix = datetime.utcnow().strftime("%Y%m%d")
        unique_token = uuid.uuid4().hex[:6].upper()
        sr_id = f"SR-REG-{timestamp_prefix}-{unique_token}"

        # 2. Extract Customer Identifiers
        identifiers = self._extract_identifiers(full_text)

        # 3. Extract Financial Dispute Details
        dispute = self._extract_financials(full_text)

        # 4. Detect Regulatory Escalation
        regulatory = self._extract_regulatory_details(full_text)

        # 5. Classify Domain & Sub-Category
        domain, sub_category = self._classify_domain_and_category(full_text)

        # 6. Determine Priority
        priority = PriorityLevel.P3_STANDARD
        if regulatory.is_regulatory_escalation:
            priority = PriorityLevel.P1_CRITICAL
        elif dispute.disputed_amount and dispute.disputed_amount >= 50000:
            priority = PriorityLevel.P1_CRITICAL
        elif dispute.disputed_amount or sub_category in [
            GrievanceSubCategory.UNAUTHORIZED_TRANSACTION,
            GrievanceSubCategory.LOAN_FORECLOSURE_DISPUTE
        ]:
            priority = PriorityLevel.P2_HIGH

        # 7. Map Target Skilled Adapters (RPA Integration Targets)
        adapters = self._determine_adapters(domain)

        # 8. Synthesize Narrative & Demand
        summary = self._summarize_narrative(full_text, domain, sub_category, dispute)
        remedy = self._extract_demanded_remedy(full_text)

        return GrievanceCaseOutput(
            sr_id=sr_id,
            intake_channel="EMAIL",
            received_at=received_at,
            sender_name=sender_name,
            sender_email=sender_email,
            subject=subject,
            product_domain=domain,
            sub_category=sub_category,
            priority=priority,
            customer_identifiers=identifiers,
            financial_dispute=dispute,
            regulatory_details=regulatory,
            narrative_summary=summary,
            demanded_remedy=remedy,
            target_skilled_adapters=adapters,
            requires_human_oversight=regulatory.is_regulatory_escalation
        )

    def _extract_name_and_email(self, sender_header: str) -> Tuple[str, str]:
        match = re.match(r"(.*?)\s*<(.+@.+)>", sender_header)
        if match:
            name = match.group(1).strip("\"' ")
            email_addr = match.group(2).strip()
            return name or email_addr.split("@")[0], email_addr
        if "@" in sender_header:
            return sender_header.split("@")[0], sender_header.strip()
        return "Customer", sender_header

    def _extract_identifiers(self, text: str) -> CustomerIdentifiers:
        def mask_num(num: str, keep_last: int = 4) -> str:
            clean = re.sub(r"\D", "", num)
            if len(clean) <= keep_last:
                return clean
            return "X" * (len(clean) - keep_last) + clean[-keep_last:]

        acct_match = re.search(r"(?:a/c|acct|account(?:\s+no\.?|\s+number)?)\s*[:#-]?\s*([0-9Xx\*\-]{9,18})", text, re.IGNORECASE)
        acct_val = mask_num(acct_match.group(1)) if acct_match else None

        card_match = re.search(r"(?:card(?:\s+no\.?|\s+number)?)\s*[:#-]?\s*([0-9Xx\*\-]{14,19})", text, re.IGNORECASE)
        card_val = mask_num(card_match.group(1)) if card_match else None

        # Specific Customer ID/Code regex (excluding generic Support/Service words)
        cust_match = re.search(r"(?:customer\s*(?:id|code|no\.?|number)|cust\s*(?:id|code|no\.?))(?:\s+is|\s*[:#\-])\s*([A-Z0-9]{6,12})", text, re.IGNORECASE)
        if not cust_match:
            cust_match = re.search(r"(CUST[0-9]{5,10})", text, re.IGNORECASE)
        cust_val = cust_match.group(1).upper() if cust_match else None

        loan_match = re.search(r"(?:loan(?:\s+account|\s+a/c|\s+acct)?(?:\s+no\.?|\s+number)?)(?:\s+is|\s*[:#\-])\s*([A-Za-z0-9\-]{8,24})", text, re.IGNORECASE)
        loan_val = loan_match.group(1).upper() if loan_match else None

        phone_match = re.search(r"(?:\+91[\-\s]?)?[6-9]\d{9}", text)
        phone_val = phone_match.group(0) if phone_match else None

        return CustomerIdentifiers(
            customer_id=cust_val,
            account_number=acct_val,
            card_number=card_val,
            loan_account_number=loan_val,
            phone_number=phone_val
        )

    def _extract_financials(self, text: str) -> FinancialDispute:
        amt_match = re.search(r"(?:Rs\.?|INR|₹|\$)\s*([0-9]{1,3}(?:,[0-9]{2,3})*(?:\.[0-9]{1,2})?|[0-9]+(?:\.[0-9]{1,2})?)", text, re.IGNORECASE)
        amount = None
        if amt_match:
            raw_amt = amt_match.group(1).replace(",", "")
            try:
                amount = float(raw_amt)
            except ValueError:
                amount = None

        currency = "INR"
        if "$" in text:
            currency = "USD"
        elif "EUR" in text or "€" in text:
            currency = "EUR"

        utr_match = re.search(r"(?:utr|rrn|ref(?:erence)?(?:\s+no\.?|\s+number)?|txn\s*(?:id|no\.?))\s*[:#-]?\s*([A-Za-z0-9]{8,22})", text, re.IGNORECASE)
        ref = utr_match.group(1) if utr_match else None

        date_match = re.search(r"\b(\d{1,2}[/-]\d{1,2}[/-]\d{2,4}|\d{1,2}(?:st|nd|rd|th)?\s+(?:Jan|Feb|Mar|Apr|May|Jun|Jul|Aug|Sep|Oct|Nov|Dec)[a-z]*\s+\d{2,4})\b", text, re.IGNORECASE)
        txn_date = date_match.group(1) if date_match else None

        return FinancialDispute(
            disputed_amount=amount,
            currency=currency,
            transaction_reference=ref,
            transaction_date=txn_date
        )

    def _extract_regulatory_details(self, text: str) -> RegulatoryDetails:
        reg_keywords = ["ombudsman", "rbi", "banking ombudsman", "consumer court", "ncdrc", "sebi", "legal notice", "statutory notice"]
        is_reg = any(re.search(r"\b" + re.escape(kw) + r"\b", text, re.IGNORECASE) for kw in reg_keywords)
        
        body_name = None
        tat_hours = 720
        if is_reg:
            if re.search(r"\b(rbi|banking ombudsman)\b", text, re.IGNORECASE):
                body_name = "Reserve Bank of India (RBI) Ombudsman"
                tat_hours = 48
            elif re.search(r"\bconsumer court\b", text, re.IGNORECASE):
                body_name = "Consumer Disputes Redressal Forum"
                tat_hours = 72
            else:
                body_name = "Regulatory / Legal Escalation"
                tat_hours = 96

        return RegulatoryDetails(
            is_regulatory_escalation=is_reg,
            regulatory_body=body_name,
            tat_deadline_hours=tat_hours
        )

    def _classify_domain_and_category(self, text: str) -> Tuple[ProductDomain, GrievanceSubCategory]:
        t = text.lower()

        if any(w in t for w in ["credit card", "debit card", "card", "ctl prime", "cvv", "chargeback", "pos transaction", "swiped"]):
            if "unauthorized" in t or "fraud" in t or "scam" in t or "without otp" in t:
                return ProductDomain.CARDS, GrievanceSubCategory.UNAUTHORIZED_TRANSACTION
            if "annual fee" in t or "overlimit" in t or "finance charge" in t or "billing statement" in t:
                return ProductDomain.CARDS, GrievanceSubCategory.BILLING_DISPUTE
            return ProductDomain.CARDS, GrievanceSubCategory.FAILED_REFUND_CHARGEBACK

        if any(w in t for w in ["loan", "emi", "foreclosure", "pre-closure", "noc", "sanction", "finone", "disbursement", "home loan", "personal loan"]):
            if "foreclosure" in t or "pre-payment" in t or "penalty" in t:
                return ProductDomain.LENDING_ASSETS, GrievanceSubCategory.LOAN_FORECLOSURE_DISPUTE
            if "interest" in t or "roi" in t or "floating" in t:
                return ProductDomain.LENDING_ASSETS, GrievanceSubCategory.INTEREST_RATE_MISCALCULATION
            return ProductDomain.LENDING_ASSETS, GrievanceSubCategory.LOAN_FORECLOSURE_DISPUTE

        if any(w in t for w in ["fixed deposit", "fd", "recurring deposit", "rd", "term deposit", "tds", "maturity"]):
            return ProductDomain.LIABILITIES, GrievanceSubCategory.INTEREST_RATE_MISCALCULATION

        if any(w in t for w in ["savings account", "current account", "atm", "cash deposit", "neft", "rtgs", "imps", "upi", "finacle", "min balance"]):
            if "atm" in t and ("dispense" in t or "cash not dispensed" in t or "debited but not" in t):
                return ProductDomain.ACCOUNTS_AND_DEPOSITS, GrievanceSubCategory.ATM_DISPENSE_FAILURE
            if "unauthorized" in t or "fraud" in t:
                return ProductDomain.ACCOUNTS_AND_DEPOSITS, GrievanceSubCategory.UNAUTHORIZED_TRANSACTION
            if "freeze" in t or "dormant" in t or "lien" in t:
                return ProductDomain.ACCOUNTS_AND_DEPOSITS, GrievanceSubCategory.ACCOUNT_FREEZE_MAINTENANCE
            return ProductDomain.ACCOUNTS_AND_DEPOSITS, GrievanceSubCategory.BILLING_DISPUTE

        return ProductDomain.GENERAL_SERVICES, GrievanceSubCategory.SERVICE_DELAY_STAFF_CONDUCT

    def _determine_adapters(self, domain: ProductDomain) -> list[str]:
        base = ["CRMNext", "Domain Data Lake"]
        if domain == ProductDomain.ACCOUNTS_AND_DEPOSITS:
            return ["Finacle"] + base
        elif domain == ProductDomain.CARDS:
            return ["CTL PRime", "Finacle"] + base
        elif domain == ProductDomain.LENDING_ASSETS:
            return ["FinOne", "Finacle"] + base
        elif domain == ProductDomain.LIABILITIES:
            return ["Liabilities", "Finacle"] + base
        return ["CRMNext", "Domain Data Lake"]

    def _summarize_narrative(self, text: str, domain: ProductDomain, sub_category: GrievanceSubCategory, dispute: FinancialDispute) -> str:
        amt_str = f" of {dispute.currency} {dispute.disputed_amount:,.2f}" if dispute.disputed_amount else ""
        txn_ref = f" under ref {dispute.transaction_reference}" if dispute.transaction_reference else ""
        return (
            f"Grievance registered in {domain.value} regarding {sub_category.value.replace('_', ' ').lower()}"
            f"{amt_str}{txn_ref}. Escalated via inbound email channel."
        )

    def _extract_demanded_remedy(self, text: str) -> str:
        t = text.lower()
        if "reversal" in t or "refund" in t or "credit back" in t:
            return "Full financial refund / dispute chargeback reversal"
        if "waiver" in t or "waive" in t:
            return "Charges / penalty waiver"
        if "noc" in t or "closure certificate" in t:
            return "Issuance of No Objection Certificate (NOC) and loan closure"
        if "cibil" in t or "credit score" in t or "bureau" in t:
            return "Rectification of adverse bureau (CIBIL/Experian) reporting"
        return "Investigation, corrective resolution, and formal written explanation"
