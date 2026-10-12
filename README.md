# QwenSimul

A small text-based town with Qwen characters and Jev judgments about permissions
and reported incidents. The town simulation is not available yet.

## Windows setup

Open PowerShell in the `qwensimul` folder, then run:

```powershell
py -3.12 -m venv .venv
.\.venv\Scripts\python -m pip install -e .
Copy-Item .env.example .env
```

Python 3.12 or newer is required. If the `py` launcher is unavailable, use the
full path to your Python interpreter.

## Configuration

Edit `.env` with your settings. Add your `TYPESAFE_API_KEY`, ensure Ollama is
running at `OLLAMA_HOST`, and set `QWEN_MODEL` to an already downloaded model.
Keep your API key private; `.env` is ignored by Git.

| Variable | Default | Purpose |
| --- | --- | --- |
| `OLLAMA_HOST` | `http://localhost:11434` | Ollama server address |
| `QWEN_MODEL` | `qwen3.5:4b` | Installed Qwen model |
| `TYPESAFE_API_KEY` | Unset | Required for the Jev endpoint check |
| `QWEN_TIMEOUT_SECONDS` | `120` | Qwen request timeout in seconds |
| `JEV_TIMEOUT_SECONDS` | `30` | Jev request timeout in seconds |
| `MAX_ROUNDS` | `20` | Round limit for the future simulation |
| `DATA_DIR` | `data` | Output directory for the future simulation |

Environment variables override `.env`. Timeouts and round limits must be
positive; relative output paths use the project directory.

## Endpoint checks

The planned commands for testing Qwen and Jev are
`.\.venv\Scripts\python -m qwensimul check qwen` and
`.\.venv\Scripts\python -m qwensimul check jev`, respectively.
These commands will be available when the terminal interface is added.
