"""
Local Qwen adapter through Ollama.

Eventually create one shared client, request schema-constrained actions,
and capture latency, token usage, and model identity. Character context
must be supplied per request rather than shared as global conversation.
No SDK import, network request, or inference occurs yet.
"""


class QwenClient:
    """Placeholder for the shared local inference client."""

    def __init__(self, host: str, model: str) -> None:
        """Eventually initialize the Ollama client with explicit settings."""
        pass

    def check_connection(self) -> bool:
        """Eventually verify that Ollama and the selected model are available."""
        pass

    def propose_action(self, prompt: str, action_schema: dict) -> dict:
        """Eventually request one structured character action from Qwen."""
        pass
