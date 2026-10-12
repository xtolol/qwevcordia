"""
Application configuration boundary.

Eventually load .env and validate the Ollama host, Qwen model name, Jev API
key, maximum rounds, and output directory. Do not log credentials.
No environment variables are read in this skeleton.
"""


class Settings:
    """Placeholder for the future validated application settings."""
    pass


def load_settings() -> Settings:
    """Eventually load and validate configuration without exposing secrets."""
    pass
