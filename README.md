# Qwevcordia

A small text-based town: one local Qwen model serves multiple characters,
hosted Jev interprets permission and police evidence, and Python owns the world.

**No functionality is implemented.** Every function contains a docstring and
`pass`; all data classes are placeholders. There are no model calls, state
changes, CLI handlers, persistence operations, or tests. Stub return annotations
describe intended contracts; the stubs currently return `None`.

## Windows setup

Extract the ZIP, open PowerShell in the `qwensimul` folder, then run:

```powershell
py -3.12 -m venv .venv
.\.venv\Scripts\python -m pip install -e .
Copy-Item .env.example .env
```

Add your real `TYPESAFE_API_KEY` to `.env`. Change `QWEN_MODEL` if you downloaded
a different Ollama model. The skeleton does not read these values yet.
Installing dependencies prepares your environment; it does not run the town.

The dependencies match the planned stack: `ollama`, `typesafe-sdk`, `pydantic`,
and `python-dotenv`. No SDK methods have been assumed or implemented.

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
