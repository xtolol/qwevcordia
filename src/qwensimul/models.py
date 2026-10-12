"""
Shared typed data contracts.

Eventually define Pydantic models for characters, locations, items, actions,
world state, events, execution results, evidence, and Jev rulings.
Actions: move, talk, buy, request_permission, take_item, report_incident, wait.
Keep physical possession, legal ownership, and borrowing permission distinct.
These classes have no fields or validation yet.
"""


class Character:
    """Identity, role, goals, location, balance, and possessed item IDs."""
    pass


class Location:
    """Stable location ID, description, and connected locations."""
    pass


class Item:
    """Stable item ID, owner, holder or location, and optional shop price."""
    pass


class Action:
    """Action kind, actor, target, item, destination, and message."""
    pass


class WorldState:
    """Authoritative clock, characters, locations, items, and permissions."""
    pass


class Event:
    """Recorded outcome with actor, timestamp, witnesses, and visibility."""
    pass


class ActionResult:
    """Execution success or failure, feedback, and emitted events."""
    pass


class Evidence:
    """Reported facts, testimony, and provenance available to an institution."""
    pass


class Judgment:
    """Decision label, option probabilities, and applicable policy ID."""
    pass
