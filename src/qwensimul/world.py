"""
Authoritative world mechanics.

Eventually check IDs, locations, reachability, funds, stock, and prerequisites.
Execute deterministic commands and emit events only after validation succeeds.
Money and items must be conserved. Taking can be physically possible even
when prohibited; recording an incident and adjudicating it are separate steps.
"""


def validate_action(world: object, action: object) -> object:
    """Eventually check physical prerequisites and return validation feedback."""
    pass


def execute_action(world: object, action: object, judgment: object = None) -> object:
    """Eventually dispatch and atomically apply one validated world command."""
    pass


def move(world: object, action: object) -> object:
    """Eventually move a character between connected locations."""
    pass


def talk(world: object, action: object) -> object:
    """Eventually deliver speech and record who can hear it."""
    pass


def buy(world: object, action: object) -> object:
    """Eventually transfer payment, possession, and ownership atomically."""
    pass


def request_permission(world: object, action: object) -> object:
    """Eventually deliver a permission request to the relevant owner."""
    pass


def take_item(world: object, action: object) -> object:
    """Eventually transfer physical possession and record witnessed facts."""
    pass


def report_incident(world: object, action: object) -> object:
    """Eventually deliver a complaint and evidence to the police officer."""
    pass


def wait(world: object, action: object) -> object:
    """Eventually record a character choosing to take no other action."""
    pass


def apply_consequence(world: object, judgment: object) -> object:
    """Eventually execute only policy-defined consequences for a ruling."""
    pass


def check_invariants(world: object) -> list[str]:
    """Eventually identify negative balances, duplicate items, or invalid IDs."""
    pass
