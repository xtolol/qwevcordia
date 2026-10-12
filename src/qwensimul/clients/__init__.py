"""
External inference boundaries.

Keep Ollama and Jev SDK calls behind separate adapters so the world engine
can later be exercised independently. No clients are created on import.
"""
