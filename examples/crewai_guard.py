"""MolTrust CrewAI Integration - Trust guard for agent delegation"""

from moltrust import MolTrust

mt = MolTrust(api_key="mt_your_key_here")


class TrustGuard:
    """Verify agent trust before delegating tasks in CrewAI."""

    def __init__(self, min_score=3.0, min_ratings=3):
        self.min_score = min_score
        self.min_ratings = min_ratings

    def is_trusted(self, agent_did):
        if not mt.verify(agent_did):
            return False
        rep = mt.get_reputation(agent_did)
        return rep.score >= self.min_score and rep.total_ratings >= self.min_ratings

    def pre_task_check(self, agent_did, task_description):
        verified = mt.verify(agent_did)
        if not verified:
            return {"allowed": False, "reason": "Agent not registered"}
        rep = mt.get_reputation(agent_did)
        trusted = rep.score >= self.min_score and rep.total_ratings >= self.min_ratings
        if not trusted:
            return {"allowed": False, "reason": "Trust too low: " + str(rep.score)}
        vc = mt.issue_credential(agent_did, "TaskDelegationCredential")
        return {"allowed": True, "score": rep.score, "ratings": rep.total_ratings}

    def post_task_rate(self, rater_did, agent_did, score):
        mt.rate(rater_did, agent_did, score)
        return mt.get_reputation(agent_did)


if __name__ == "__main__":
    guard = TrustGuard()
    print("TrustGuard ready. Min score:", guard.min_score)
