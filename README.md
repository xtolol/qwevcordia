# QwenSimul — early implementation

A small text-based town: one local Qwen model serves multiple characters,
hosted Jev interprets permission and police evidence, and Python owns the world.

**Configuration loading is implemented.** Model clients, town data, world
actions, CLI handlers, and persistence remain placeholders. Unimplemented
functions currently return `None`; their return annotations describe intended
contracts. No simulation or inference calls run yet.

## Windows setup

Extract the ZIP, open PowerShell in the `qwensimul` folder, then run:

```powershell
py -3.12 -m venv .venv
.\.venv\Scripts\python -m pip install -e .
Copy-Item .env.example .env
```

Add your real `TYPESAFE_API_KEY` to `.env`. Change `QWEN_MODEL` if you downloaded
a different Ollama model. `load_settings()` reads and validates these values.
Installing dependencies prepares your environment; it does not run the town.

The dependencies match the planned stack: `ollama`, `typesafe-sdk`, `pydantic`,
and `python-dotenv`. No SDK methods have been assumed or implemented.

## Configuration

`load_settings()` reads `.env` from the project directory containing this
source checkout. Existing environment variables take precedence, including
empty values. Loading settings does not change the process environment, create
output directories, or contact either inference service. Missing `.env` files
use defaults. Values are literal: `${VARIABLE}` interpolation is disabled.

| Variable | Default | Validation |
| --- | --- | --- |
| `OLLAMA_HOST` | `http://localhost:11434` | HTTP(S) URL without credentials, query, or fragment |
| `QWEN_MODEL` | `qwen3.5:4b` | Nonempty model name |
| `TYPESAFE_API_KEY` | Unset | Optional secret; blank means absent |
| `MAX_ROUNDS` | `20` | Positive integer |
| `DATA_DIR` | `data` | Nonempty path; an existing file is rejected |
| `QWEN_TIMEOUT_SECONDS` | `120` | Positive, finite seconds |
| `JEV_TIMEOUT_SECONDS` | `30` | Positive, finite seconds |

Relative data paths resolve against the project directory, independent of the
current working directory. Pass `load_settings(project_dir=Path(...))` to use
another directory for both `.env` and relative data paths. The key is optional
for local Qwen work; the future Jev check must require it. It is excluded from
settings representations and serialization. `ConfigurationError` reports
invalid variable names and requirements without including supplied values.

To verify configuration from the project folder after installation:

```powershell
.\.venv\Scripts\python -c "from qwensimul.config import load_settings; print(load_settings())"
```

Run the offline configuration tests:

```powershell
.\.venv\Scripts\python -m unittest discover -s tests -v
```

## Repository map

| Path | Intended responsibility |
| --- | --- |
| `src/qwensimul/__main__.py` | Future terminal entry point |
| `src/qwensimul/config.py` | Load and validate settings |
| `src/qwensimul/models.py` | Typed state, action, evidence, and result contracts |
| `src/qwensimul/clients/qwen.py` | Shared local Ollama inference client |
| `src/qwensimul/clients/jev.py` | Hosted Jev Choice adapter |
| `src/qwensimul/agents.py` | Character prompts and isolated memory |
| `src/qwensimul/observations.py` | Visibility and reported evidence |
| `src/qwensimul/world.py` | Deterministic validation and execution |
| `src/qwensimul/institutions.py` | Permission and police judgments |
| `src/qwensimul/scenarios.py` | Fixed initial town and policies |
| `src/qwensimul/simulation.py` | Turns, rounds, pause, and reset |
| `src/qwensimul/storage.py` | Snapshots, logs, and terminal events |
| `data/logs/` | Future JSONL logs |
| `data/snapshots/` | Future JSON snapshots |
| `.env.example` | Configuration template without credentials |
| `pyproject.toml` | Packaging and dependencies |

## Suggested implementation order

1. Implement `config.py` and standalone connection checks in both clients.
2. Define typed contracts in `models.py` and a fixed town in `scenarios.py`.
3. Implement and manually verify world actions before connecting agents.
4. Add observations, private memories, and Qwen action proposals.
5. Add Jev permission and police-evidence judgments.
6. Wire the bounded simulation loop, persistence, and terminal controls.

Before autonomous runs, verify money and item conservation, failed purchases,
permission scope, witness visibility, and reset behavior. Add meaningful tests
when these behaviors exist.

## Initial scope

Four characters (two residents, shopkeeper, police officer), three locations
(square, shop, station), money, owned items, and at most 20 sequential rounds.
Physical possession and legality are separate: an unauthorized taking may occur
and later be reported. Police reason from reported evidence rather than hidden
world truth.

## Start your Git history locally

```powershell
git init
git add .
git commit -m "Add QwenSimul skeleton"
```

The ZIP excludes Git metadata. No remote repository has been created.
