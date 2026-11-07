from typing import Dict, Any

try:
    from .domain_agents import (
        CardsDecisionAgent,
        AssetsDecisionAgent,
        AccountsDecisionAgent,
        LiabilitiesDecisionAgent,
        GeneralServicesDecisionAgent
    )
except (ImportError, ValueError):
    from domain_agents import (
        CardsDecisionAgent,
        AssetsDecisionAgent,
        AccountsDecisionAgent,
        LiabilitiesDecisionAgent,
        GeneralServicesDecisionAgent
    )

class IntelligentDecisionEngine:
    """
    Intelligent Decisioning Engine that routes the Investigation Docket
    to the specialized domain decision agent based on product domain.
    """

    def __init__(self):
        self.agents = {
            "CARDS": CardsDecisionAgent(),
            "LENDING_ASSETS": AssetsDecisionAgent(),
            "ACCOUNTS_AND_DEPOSITS": AccountsDecisionAgent(),
            "LIABILITIES": LiabilitiesDecisionAgent(),
            "GENERAL_SERVICES": GeneralServicesDecisionAgent()
        }

    def evaluate(self, docket: Dict[str, Any], domain: str) -> Dict[str, Any]:
        agent = self.agents.get(domain, self.agents["GENERAL_SERVICES"])
        decision_result = agent.decide(docket)
        decision_result["evaluated_domain"] = domain
        decision_result["sr_id"] = docket["sr_id"]
        return decision_result
