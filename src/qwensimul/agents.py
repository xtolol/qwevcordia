"""
Character reasoning and private memory.

Eventually maintain one identity, goal set, and memory stream per character.
Use a single shared Qwen client while keeping character contexts separate.
Start with recent relevant events; defer embeddings and reflection.
"""


def build_prompt(character: object, observation: dict, memories: list) -> str:
    """Eventually combine identity, goals, visible state, and allowed actions."""
    pass


def choose_action(character: object, observation: dict, memories: list, qwen: object) -> object:
    """Eventually ask the shared Qwen client for this character's next action."""
    pass


def remember(character_id: str, visible_events: list, memory_store: dict) -> None:
    """Eventually append only events the character is allowed to observe."""
    pass


def retrieve_memories(character_id: str, memory_store: dict, limit: int = 10) -> list:
    """Eventually return a bounded selection of this character's memories."""
    pass
