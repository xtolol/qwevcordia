"""
Visibility and knowledge boundary.

Eventually build character-specific observations from location, possession,
public events, witnesses, and received messages. Police get submitted evidence,
not hidden engine truth. Keep event delivery separate from state mutation.
"""


def build_observation(world: object, character_id: str) -> dict:
    """Eventually expose only the state visible to the specified character."""
    pass


def visible_events(events: list, character_id: str) -> list:
    """Eventually filter events by witnesses, recipients, and public visibility."""
    pass


def collect_report_evidence(world: object, reporter_id: str, report: object) -> object:
    """Eventually construct a report using the reporter's accessible evidence."""
    pass
