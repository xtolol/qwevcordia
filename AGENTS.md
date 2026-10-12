# QwenSimul

## Introduction

- Build a small, persistent, text-based town to study autonomous characters and institutional decisions.
- One local Qwen model, served by Ollama, drives all characters; each has separate identity, goals, observations, and memory.
- Hosted Jev interprets contextual questions. Python owns authoritative state, validation, and execution.
- Stack: Python 3.12, Ollama, TypeSafe SDK, Pydantic, and python-dotenv. The repository currently contains stubs only.

## Planned MVP features

- Four characters: two residents, one shopkeeper, and one police officer.
- Three locations: square, shop, and police station; persistent money, items, ownership, and borrowing permissions.
- Structured actions: move, talk, buy, request permission, take an item, report an incident, and wait.
- Jev judgments for borrowing permission and reported policy violations, including unclear or insufficient-evidence outcomes.
- Character-specific visibility and private memory; police receive reported evidence rather than hidden world truth.
- Deterministic checks for funds, stock, valid targets, and reachability; conserve money and items.
- Keep physical possibility separate from legality: unauthorized taking can occur and later be investigated.
- Sequential turns, a 20-round default limit, single-step, pause, and reset controls.
- Terminal event feed, JSON snapshots, and JSONL logs of actions, rulings, outcomes, and inference measurements.

## Small roadmap

- 1. Load configuration and verify standalone Qwen and Jev connections.
- 2. Define typed contracts, the initial town, policies, and manually executable world actions.
- 3. Add limited observations, private memories, and structured Qwen action proposals.
- 4. Integrate narrow Jev judgments and explicit policy-defined consequences.
- 5. Connect the bounded simulation loop, persistence, controls, and meaningful checks for state consistency.

## Coding practices

- Prefer clear, straightforward Python: descriptive names, explicit loops and conditions, and small functions.
- Avoid clever one-liners, deeply nested comprehensions, unnecessary decorators, metaprogramming, and premature abstractions.
- Give every function and method a multiline docstring immediately inside its definition, with **Purpose**, **Params**, and **Return** sections. Explain each parameter and use `None` when there are no parameters or no returned value.
- Use type hints for inputs and outputs; keep comments focused on intent, rules, and non-obvious behavior.
- Keep inference clients, character reasoning, world mechanics, and institutional judgment separate; validate model output before execution.
- Implement incrementally along the roadmap; preserve unrelated stubs until their functionality is requested.
- Keep credentials in the ignored `.env`; never commit or log API keys. Failed inference calls must not partially apply a pending action.
