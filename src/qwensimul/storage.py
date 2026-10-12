"""
Persistence, event feed, and measurement boundary.

Eventually write JSON snapshots and append-only JSONL records containing
proposed actions, validation feedback, redacted Jev cases/results, applied
changes, model identity, latency, and token usage. Never record API keys.
No directories are created and no files are written by these stubs.
"""


class Storage:
    """Placeholder for local persistence and terminal output."""

    def __init__(self, data_dir: str) -> None:
        """Eventually configure snapshot and log destinations."""
        pass

    def save_snapshot(self, world: object, memories: dict) -> None:
        """Eventually persist world state and isolated character memories."""
        pass

    def load_snapshot(self, path: str) -> object:
        """Eventually restore a validated snapshot."""
        pass

    def append_record(self, record: dict) -> None:
        """Eventually append one redacted structured record to a JSONL log."""
        pass

    def display_event(self, event: object) -> None:
        """Eventually render a readable terminal event."""
        pass
