# metriq — Design Document

## Overview

`metriq` is a single-user, local CLI tool that ingests a CSV of raw daily engagement events, computes four independent metrics (active users, session duration, feature usage, retention rate), combines them, and writes a Markdown report to disk. It runs manually as one command, makes no network calls, and requires no human approval steps.

**Language/runtime choice:** Python 3.11+ using the **standard library only** (`csv`, `statistics`, `datetime`, `collections`, `argparse`, `pathlib`, `dataclasses`). No pandas. Rationale: the dataset is a single local CSV, the aggregations are simple group-by/count/mean operations, and stdlib keeps the tool dependency-free, fast to start, and trivial to run anywhere. If the CSVs grow to millions of rows later, pandas/polars can be swapped in behind the loader interface without touching the metric calculators.

**Design principle:** every metric calculator consumes the same in-memory, already-parsed event list and returns a small, serializable result object. The loader is the only module that knows about CSV/IO details; the report writer is the only module that knows about Markdown. This isolation is what makes the parallel build plan clean.

---

## 1. Component Breakdown

All modules live under a `metriq/` package. Each metric calculator is a separate file exposing a single pure function with an identical shape, so they can be built independently and called uniformly.

### `metriq/models.py` — shared data model (foundational)
Defines the canonical in-memory representation shared by every other module. No IO, no business logic.

- `@dataclass(frozen=True) EngagementEvent` — one parsed CSV row:
  - `user_id: str`
  - `event_timestamp: datetime`
  - `event_type: str`
  - `feature_name: str`
  - `session_id: str`
- `@dataclass MetricResult` — uniform return type for every calculator:
  - `name: str` (e.g. `"active_users"`)
  - `title: str` (human-readable, e.g. `"Active Users"`)
  - `summary: dict[str, Any]` (headline numbers)
  - `details: dict[str, Any]` (optional breakdown for the report body)
- Type aliases: `Events = list[EngagementEvent]`.

### `metriq/loader.py` — CSV loader + validation (foundational)
The only module that touches the filesystem for input and parses raw strings.

- `load_events(csv_path: str | Path) -> Events`
  - Opens the CSV, validates the header against the expected schema, parses each row into an `EngagementEvent`.
  - Parses `event_timestamp` (ISO 8601) into `datetime`.
  - Raises `MetriqDataError` (defined here) with a clear message on: missing file, missing/renamed columns, unparseable timestamp, empty file.
  - Skips/collects malformed rows according to a `strict: bool = True` flag (strict raises; non-strict logs and drops).
- `class MetriqDataError(Exception)` — shared, importable exception type.

### `metriq/metrics/active_users.py`
- `compute(events: Events) -> MetricResult`
- Responsibility: count distinct `user_id`. Because the input is "daily engagement data," report total distinct users (DAU for the day/window represented in the file) and, if events span multiple dates, distinct active users per calendar date.

### `metriq/metrics/session_duration.py`
- `compute(events: Events) -> MetricResult`
- Responsibility: group events by `session_id`, compute each session's duration as `max(event_timestamp) - min(event_timestamp)`, then report mean, median, min, max, and total session count. Uses `statistics`.

### `metriq/metrics/feature_usage.py`
- `compute(events: Events) -> MetricResult`
- Responsibility: count events per `feature_name` (and/or `event_type`), report a ranked usage table and each feature's share of total events. Uses `collections.Counter`.

### `metriq/metrics/retention_rate.py`
- `compute(events: Events) -> MetricResult`
- Responsibility: measure repeat engagement. For a single-file/multi-date dataset, compute the fraction of users active on the first date who are also active on any later date. If only one date is present, report retention as `N/A` with an explanatory note (documented assumption — see Data Model).

> Contract shared by all four calculators (this uniformity is deliberate — it's what lets them be built in parallel by separate agents against only `models.py`):
> **`compute(events: Events) -> MetricResult`** — pure function, no IO, no printing, deterministic.

### `metriq/report.py` — report combiner + writer (final wave)
The only module that knows about Markdown output.

- `build_report(results: list[MetricResult], *, source_path: str, generated_at: datetime) -> str`
  - Combines results into a single Markdown string: title, generation timestamp, source file, a summary section, then one section per metric.
- `write_report(markdown: str, output_path: str | Path) -> None`
  - Writes the string to `report.md` (or the `--output` path).

### `metriq/cli.py` — CLI entrypoint (final wave)
Orchestrator. Wires loader → calculators → report. No business logic.

- `main(argv: list[str] | None = None) -> int`
  - Parses args, calls `load_events`, invokes the four `compute` functions (collecting `MetricResult`s), calls `build_report` + `write_report`, prints a one-line success summary to stdout, returns exit code (`0` success, `1` data error, `2` usage error).
- Registered as console script `metriq` via `pyproject.toml`.

### `metriq/__init__.py` / `metriq/metrics/__init__.py`
Package markers. `metrics/__init__.py` may optionally expose a `CALCULATORS` registry list, but to avoid file-scope overlap during the parallel wave, the registry is assembled in `cli.py` instead (see Parallel Build Plan).

### `pyproject.toml`
Project scaffolding, Python version pin, console-script entrypoint. No third-party runtime deps.

### `tests/` (optional, noted not mandated)
- `tests/test_loader.py`, `tests/test_active_users.py`, `tests/test_session_duration.py`, `tests/test_feature_usage.py`, `tests/test_retention_rate.py`, `tests/test_report.py`.
- A small `tests/fixtures/sample_events.csv` for shared use.
- Each metric's tests can be authored alongside that metric in the same wave/task (same owner, no overlap).

---

## 2. Data Model

### Assumption (stated explicitly)
We have **no real schema yet**, so we assume a reasonable "daily engagement event" shape: one row per user interaction event, with a session identifier so sessions can be reconstructed, a timestamp, and a feature/event label. The file may contain events for a single day or a small multi-day window; metrics that need multiple dates (retention) degrade gracefully when only one date is present.

### Expected CSV schema

| Column | Type | Required | Description |
|---|---|---|---|
| `user_id` | string | yes | Stable unique identifier for the user. |
| `event_timestamp` | ISO 8601 datetime (`YYYY-MM-DDTHH:MM:SS`, optional `Z`/offset) | yes | When the event occurred. |
| `event_type` | string | yes | Category of interaction, e.g. `click`, `view`, `submit`. |
| `feature_name` | string | yes | Product feature the event belongs to, e.g. `dashboard`, `export`. |
| `session_id` | string | yes | Groups events into a single session for duration calc. |

**Header (exact, order-independent but names must match):**
```
user_id,event_timestamp,event_type,feature_name,session_id
```

**Example rows:**
```
user_id,event_timestamp,event_type,feature_name,session_id
u_1001,2026-08-12T09:14:03,view,dashboard,s_88f2
u_1001,2026-08-12T09:15:41,click,export,s_88f2
u_1002,2026-08-12T11:02:10,view,dashboard,s_91a0
u_1001,2026-08-13T08:03:55,view,dashboard,s_9c31
```

### Modeling notes / edge cases the loader and calculators must handle
- **Empty file / header only:** loader raises `MetriqDataError`.
- **Single distinct date:** `retention_rate.compute` returns `summary={"retention_rate": None, "note": "single date in dataset"}`; other metrics work normally.
- **Session with one event:** duration = 0 seconds (valid).
- **Timezone:** parse as naive local if no offset present; be consistent within a run. Documented as a known simplification.
- **Duplicate rows:** not deduplicated by default (assumed each row is a real event).

---

## 3. API Surface

### CLI interface

```
metriq [INPUT_CSV] [--output PATH] [--strict/--no-strict] [--quiet]
```

| Arg / Flag | Type | Default | Description |
|---|---|---|---|
| `INPUT_CSV` (positional) | path | `events.csv` | Path to the raw engagement events CSV. |
| `--output`, `-o` | path | `report.md` | Where the combined Markdown report is written. |
| `--strict` / `--no-strict` | bool | `--strict` | Strict fails on any malformed row; non-strict drops and warns. |
| `--quiet`, `-q` | bool | `false` | Suppress the stdout success summary. |

**Exit codes:** `0` success · `1` data/IO error (`MetriqDataError`) · `2` usage error (bad args).

**Example invocation (satisfies success criteria):**
```
metriq events.csv -o report.md
# -> reads events.csv, computes 4 metrics, writes report.md, prints "metriq: wrote report.md (4 metrics, 1,204 events)"
```

### Internal function-level contracts (the seams between modules)

```python
# models.py
EngagementEvent(user_id, event_timestamp, event_type, feature_name, session_id)
MetricResult(name, title, summary: dict, details: dict)
Events = list[EngagementEvent]

# loader.py
load_events(csv_path: str | Path, *, strict: bool = True) -> Events
class MetriqDataError(Exception): ...

# each metric module (identical contract)
compute(events: Events) -> MetricResult

# report.py
build_report(results: list[MetricResult], *, source_path: str, generated_at: datetime) -> str
write_report(markdown: str, output_path: str | Path) -> None

# cli.py
main(argv: list[str] | None = None) -> int
```

The contract that unlocks parallelism: **all four calculators depend only on `models.py`**, take `Events`, and return `MetricResult`. They never import each other, the loader, the report, or the CLI.

---

## 4. Parallel Build Plan

Three waves. Within a wave, tasks have **zero file overlap** and can be executed by separate builder subagents with no shared context beyond the frozen interfaces in `models.py` (and, for Wave 3, the four `MetricResult`s).

### Wave 1 — Foundation (must complete before Waves 2 & 3)

**Task 1.1 — Project scaffolding**
- Description: Create the package structure, `pyproject.toml` with Python pin and `metriq` console-script entrypoint pointing at `metriq.cli:main`, empty `__init__.py` files.
- Owns: `pyproject.toml`, `metriq/__init__.py`, `metriq/metrics/__init__.py`
- Depends on: none

**Task 1.2 — Shared data model**
- Description: Define `EngagementEvent`, `MetricResult`, and the `Events` alias exactly as contracted. Frozen dataclasses, no logic.
- Owns: `metriq/models.py`
- Depends on: none (can run concurrently with 1.1)

**Task 1.3 — CSV loader + validation**
- Description: Implement `load_events` and `MetriqDataError`; header validation, ISO timestamp parsing, strict/non-strict handling, empty-file error.
- Owns: `metriq/loader.py`, `tests/fixtures/sample_events.csv`, `tests/test_loader.py`
- Depends on: 1.2 (imports `EngagementEvent`, `Events`)

> Wave 1 gate: `models.py` interfaces are frozen and `load_events` returns real `Events`. Only after this do Waves 2/3 start.

### Wave 2 — Independent metric calculators (fully parallel, 4 subagents)

Each task imports only `metriq.models`. No cross-imports.

**Task 2.1 — Active users**
- Owns: `metriq/metrics/active_users.py`, `tests/test_active_users.py`
- Depends on: 1.2

**Task 2.2 — Session duration**
- Owns: `metriq/metrics/session_duration.py`, `tests/test_session_duration.py`
- Depends on: 1.2

**Task 2.3 — Feature usage**
- Owns: `metriq/metrics/feature_usage.py`, `tests/test_feature_usage.py`
- Depends on: 1.2

**Task 2.4 — Retention rate**
- Owns: `metriq/metrics/retention_rate.py`, `tests/test_retention_rate.py`
- Depends on: 1.2 (must implement the single-date `N/A` behavior)

> All four take `Events` in and return `MetricResult` out — identical signature, so a subagent needs only `models.py` in context.

### Wave 3 — Combiner + orchestration (depends on all of Wave 2)

**Task 3.1 — Report combiner + writer**
- Description: Implement `build_report` (Markdown assembly from `list[MetricResult]`) and `write_report`. Depends on the *shape* of `MetricResult`, not on calculator internals, so this could technically start in Wave 2 against `models.py` alone — placed here to keep the dependency graph simple.
- Owns: `metriq/report.py`, `tests/test_report.py`
- Depends on: 1.2 (shape); validated end-to-end after Wave 2

**Task 3.2 — CLI entrypoint / orchestrator**
- Description: `argparse` wiring, call `load_events`, invoke all four `compute` functions, assemble the calculator registry, call `build_report`/`write_report`, print summary, return exit codes.
- Owns: `metriq/cli.py`
- Depends on: 1.3 (loader), 2.1–2.4 (all calculators), 3.1 (report)

### Dependency summary

```
Wave 1:  1.1 ─┐
         1.2 ─┼─> 1.3
Wave 2:  1.2 -> 2.1 | 2.2 | 2.3 | 2.4      (parallel)
Wave 3:  1.2 -> 3.1
         1.3 + 2.1..2.4 + 3.1 -> 3.2
```

No two tasks in the same wave share a file. The only globally shared file is `metriq/models.py`, which is written once in Wave 1 and read-only thereafter.
</content>
