"""MolTrust CrewAI Integration - Trust guard for agent delegation"""

from moltrust import MolTrust

mt = MolTrust(api_key="mt_your_key_here")


class TrustGuard:
    """Verify agent trust before delegating tasks in CrewAI."""

    def __init__(self, min_score: float = 3.0, min_ratings: int = 3):
        self.min_score = min_score
        self.min_ratings = min_ratings

    def is_trusted(self, agent_did: str) -> bool:
        """Check if agent meets trust threshold."""
        if not mt.verify(agent_did):
            return False
        rep = mt.get_reputation(agent_did)
        return rep.score >= self.min_score and rep.total_ratings >= self.min_ratings

    def pre_task_check(self, agent_did: str, task_description: str) -> dict:
        """Run before delegating a task. Returns trust assessment."""
        verified = mt.verify(agent_did)
        if not verified:
            return {"allowed": False, "reason": "Agent not registered"}

        rep = mt.get_reputation(agent_did)
        trusted = rep.score >= self.min_score and rep.total_ratings >= self.min_ratings

        if not trusted:
            return {
                "allowed": False,
                "reason": f"Trust too low: {rep.score}/5 ({rep.total_ratings} ratings)",
                "suggestion": "Use a higher-rated agent or lower the threshold"
            }

        vc = mt.issue_credential(agent_did, "TaskDelegationCredential")
        return {
            "allowed": True,
            "score": rep.score,
            "ratings": rep.total_ratings,
            "credential": vc.subject_did,
            "task": task_description
        }

    def post_task_rate(self, rater_did: str, agent_did: str, score: int):
        """Rate agent after task completion."""
        mt.rate(rater_did, agent_did, score)
        return mt.get_reputation(agent_did)


if __name__ == "__main__":
    guard = TrustGuard(min_score=3.0)
    print("TrustGuard initialized")
    print(f"  Min score: {guard.min_score}")
    print(f"  Min ratings: {guard.min_ratings}")
    print("\nUsage:")
    print("  guard = TrustGuard(min_score=3.0)")
    print('  result = guard.pre_task_check("did:moltrust:abc123", "Analyze data")')
    print("  if result['allowed']: delegate_task()")
