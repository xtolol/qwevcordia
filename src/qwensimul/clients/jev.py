"""
Hosted Jev adapter through the TypeSafe SDK.

Eventually submit supplied evidence, policy, question, and explicit choices;
normalize returned probabilities and preserve request metadata for logging.
An API failure must be surfaced without silently committing a world change.
No SDK import, network request, or inference occurs yet.
"""


class JevClient:
    """Placeholder for the hosted institutional decision client."""

    def __init__(self, api_key: str) -> None:
        """Eventually initialize the SDK without logging the API key."""
        pass

    def check_connection(self) -> bool:
        """Eventually verify Jev access using a standalone sample request."""
        pass

    def choose(self, state: dict, question: str, choices: list[dict]) -> dict:
        """Eventually request and normalize a Jev Choice judgment."""
        pass
