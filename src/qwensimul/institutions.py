"""
Narrow institutional questions and policy interpretation.

Eventually construct Jev cases for permission and reported policy violations.
Use permission_granted / permission_denied / unclear for permission, and
supported / unsupported / insufficient_evidence for submitted allegations.
Supply applicable policy and evidence provenance. Exact affordability and
physical feasibility belong in world.py. Do not treat uncertainty as approval.
"""


def requires_judgment(action: object, context: dict) -> bool:
    """Eventually determine whether this action needs a contextual ruling."""
    pass


def judge_permission(request: object, reply: str, policy: dict, jev: object) -> object:
    """Eventually interpret the reply, including scope and borrowing conditions."""
    pass


def judge_report(evidence: object, policy: dict, jev: object) -> object:
    """Eventually assess only the allegation and evidence given to police."""
    pass
