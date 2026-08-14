# brewlog

A tiny local CLI for logging coffee entries to a JSON file. Solo-dev personal utility — no cloud, no scheduling, no external APIs, no approval prompts.

## Purpose

Run `log-coffee "flat white, oat milk"` from anywhere in the terminal to append a timestamped entry to `~/.brewlog/coffee_log.json`. Run `coffee-history` to view the log.

## Stack

- Python 3, standard library only (`argparse`, `json`, `datetime`, `pathlib`)
- Packaged via `pyproject.toml` with `console_scripts` entry points (`log-coffee`, `coffee-history`)
- Installed locally with `pip install -e .`

## Component Breakdown

- `brewlog/cli.py` — all logic: load/append JSON, print confirmation, print history, `log_main()`/`history_main()` entry points
- `pyproject.toml` — packaging + console_scripts
- Data file: `~/.brewlog/coffee_log.json` (JSON array of `{timestamp, entry}` objects), overridable via `BREWLOG_FILE` env var

Full design rationale: `workflows/brewlog_design.md`.

## Workflow note

This project was scaffolded using the multi-instance subagent workflow (architect → builder → tester → fixer → deployer). Given its small size, it uses a single build wave with no deploy step (local CLI only, no hosting).
