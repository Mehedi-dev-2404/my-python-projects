# brewlog — Design Document

A tiny local CLI for logging coffee entries to a JSON file. Solo-dev personal utility. Intentionally minimal — no cloud, no scheduling, no approval prompts, no extensibility scaffolding.

## Overview

- **Input → Process → Output:** A CLI command logs one coffee entry → appends `{timestamp, entry}` to a local JSON file → prints a confirmation line.
- **User:** The developer themselves. Technical, comfortable with the terminal.
- **Execution:** Local CLI only, run manually.
- **Data:** A single local JSON file (`coffee_log.json`). No external sources.
- **Approvals:** None. Every run logs immediately.
- **Success criteria:** `log-coffee "..."` works from anywhere and appends a timestamped entry; a history command prints the log.

## Component Breakdown

Keep it to one Python module plus packaging config.

| File | Purpose |
|------|---------|
| `brewlog/cli.py` | All logic: argument parsing, load/append JSON, print confirmation, print history. Contains `main()` entry point. |
| `pyproject.toml` | Packaging + `console_scripts` entry points so `log-coffee` is on PATH. Installed via `pip install -e .`. |
| `README.md` | One-paragraph usage note (optional but nice for a solo dev returning later). |

Design notes:
- **Single module.** No package sprawl. One `cli.py` with a handful of small functions (`load_log`, `append_entry`, `print_history`, `main`).
- **Standard library only.** `argparse`, `json`, `datetime`, `pathlib`, `os`. No third-party dependencies.
- **File location:** Store `coffee_log.json` in a fixed, discoverable home-dir path so the command works from *anywhere* regardless of cwd:
  - Default: `~/.brewlog/coffee_log.json` (created on first run, including parent dir).
  - Optional override via `BREWLOG_FILE` env var — trivial to add, useful for testing. Keep this as the one small flex point.

## Data Model

The JSON file is a single top-level array of entry objects. Each entry:

```json
{
  "timestamp": "2026-08-13T09:41:22-04:00",
  "entry": "flat white, oat milk"
}
```

| Field | Type | Notes |
|-------|------|-------|
| `timestamp` | string (ISO 8601, local time with offset) | Set automatically at log time. Not user-provided. |
| `entry` | string | The free-text coffee description passed on the CLI. Required, non-empty. |

File shape:

```json
[
  { "timestamp": "2026-08-13T08:02:10-04:00", "entry": "espresso, double" },
  { "timestamp": "2026-08-13T09:41:22-04:00", "entry": "flat white, oat milk" }
]
```

Behavior:
- Missing file → treat as empty list `[]`, create on first write.
- Empty/corrupt file → treat as empty list (do not crash on a personal utility; just start fresh append). Keep this forgiving.
- Append is read-modify-write of the whole array. Fine at personal scale (hundreds/thousands of rows).

## CLI Surface

Two console-script entry points, both wired to the same `main()` dispatch (or two tiny wrappers — pick whichever is cleaner in `cli.py`).

### `log-coffee` — log an entry (primary command)

```
log-coffee "flat white, oat milk"
```

- Positional arg: the entry text (one string; quote it in the shell). If multiple words are passed unquoted, join them with spaces.
- No flags required.
- Output (stdout):
  ```
  Logged: flat white, oat milk  @ 2026-08-13 09:41
  ```
- Exit code `0` on success; non-zero with a short stderr message if entry text is empty.

### History — view logged entries

Provide via a subcommand on a second entry point so it also runs from anywhere:

```
coffee-history            # prints all entries, oldest → newest
coffee-history -n 10      # prints last 10 entries
```

- Output: one line per entry, e.g.:
  ```
  2026-08-13 08:02  espresso, double
  2026-08-13 09:41  flat white, oat milk
  ```
- Empty/missing log → print `No coffee logged yet.` and exit `0`.

`pyproject.toml` `console_scripts`:

```
log-coffee     = brewlog.cli:log_main
coffee-history = brewlog.cli:history_main
```

(Both live in the same module; `log_main`/`history_main` are thin wrappers around shared helpers.)

### Install

```
cd brewlog
pip install -e .
```

Editable install puts both commands on PATH via the active Python environment. Simplest reasonable approach for a solo dev on macOS — no manual alias juggling, and edits to `cli.py` take effect immediately.

## Parallel Build Plan

Honest assessment: this project is a single module plus a packaging file. There is not enough surface area to split across parallel builders without file-scope overlap (`cli.py` is the whole app). One builder, one wave.

### Wave 0

**Task 0.1 — Build the brewlog CLI**

- **Scope (files owned, no overlap):**
  - `brewlog/pyproject.toml`
  - `brewlog/brewlog/__init__.py`
  - `brewlog/brewlog/cli.py`
  - `brewlog/README.md` (optional)
- **Inputs:** This design document (data model, CLI surface, file-location rules).
- **Work:**
  1. Implement `cli.py`: `load_log()`, `append_entry(text)`, `print_history(limit=None)`, plus `log_main()` and `history_main()` entry wrappers. Stdlib only.
  2. Storage at `~/.brewlog/coffee_log.json` (create parent dir on first write); honor `BREWLOG_FILE` override. Forgiving on missing/corrupt file (treat as `[]`).
  3. `pyproject.toml` with the two `console_scripts` entry points above.
- **Outputs / done criteria:**
  - `pip install -e brewlog` succeeds.
  - `log-coffee "espresso"` appends a `{timestamp, entry}` object and prints a confirmation.
  - `coffee-history` prints logged entries (and `-n N` limits the tail); empty log prints `No coffee logged yet.`
  - Both commands work from any working directory.
- **Dependencies:** None.

No Wave 1. Nothing to parallelize.
