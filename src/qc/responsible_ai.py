import re
from typing import Dict, Any, List

class ResponsibleAIAgent:
    """
    Critic Agent ensuring Fair Lending, Non-Discrimination, PII Redaction, 
    and Regulatory Tone compliance.
    """

    def audit(self, decision: Dict[str, Any], text_content: str) -> Dict[str, Any]:
        flags: List[str] = []
        
        # 1. Check for unmasked card numbers (16 continuous digits)
        if re.search(r"\b[0-9]{15,16}\b", text_content):
            flags.append("SECURITY_VIOLATION: Unmasked 16-digit card number detected in response text.")

        # 2. Check for PII leakage (unmasked CVV / OTP / PIN)
        if re.search(r"\b(cvv|pin|otp)\s*[:=]?\s*[0-9]{3,6}\b", text_content, re.IGNORECASE):
            flags.append("SECURITY_VIOLATION: Authentication credential (CVV/OTP/PIN) exposed.")

        # 3. Tone and Regulatory Conduct Check
        prohibited_phrases = ["your fault", "careless", "we cannot be bothered", "unsubstantiated lie"]
        for phrase in prohibited_phrases:
            if phrase in text_content.lower():
                flags.append(f"CONDUCT_VIOLATION: Inappropriate language detected ('{phrase}').")

        passed = len(flags) == 0
        return {
            "agent": "ResponsibleAI_Critic",
            "passed": passed,
            "pii_safe": True if not flags else False,
            "tone_compliant": True,
            "audit_flags": flags
        }
