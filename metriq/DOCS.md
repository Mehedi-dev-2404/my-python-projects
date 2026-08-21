# metriq — Documentation

## Overview

`metriq` is a small, single-user, local command-line tool for turning a raw
CSV export of daily product-engagement events into a readable Markdown
report. You point it at a CSV of events (one row per user interaction) and
it produces a `report.md` summarizing four metrics:

- **Active users** — how many distinct users showed up, overall and per day.
- **Session duration** — how long user sessions lasted (mean/median/min/max).
- **Feature usage** — which features got used the most, ranked with counts and share of total events.
- **Retention rate** — of the users active on the first day in the data, what fraction came back on a later day.

It's built for a single person (Mehedi) to run manually and locally — there
is no server, no database, no external API calls, and no network access at
all. It runs anywhere Python 3.10+ is installed, using only the Python
standard library (no third-party runtime dependencies). Typical use case:
export a CSV of engagement events from wherever they're tracked, run
`metriq`, and read the resulting Markdown report.

## Architecture & Design Decisions

Source design doc: `workflows/metriq_design.md`.

**Stdlib-only, no pandas.** The dataset is a single local CSV and the
aggregations involved (group-by, count, mean/median) are simple enough that
`csv`, `statistics`, `datetime`, and `collections.Counter` cover everything
needed. This keeps the tool dependency-free, fast to start, and trivial to
run anywhere Python exists. The design doc explicitly notes this is a
reversible choice: if input files grow to millions of rows, pandas/polars
could be swapped in behind the `loader` module without touching any of the
metric calculators, because they only depend on the in-memory `Events` list,
not on how it was produced.

**Uniform `compute(events: Events) -> MetricResult` contract for all four
metrics.** Every calculator is a pure function with an identical signature:
takes the full parsed event list in, returns a small `MetricResult` out. No
IO, no printing, fully deterministic. This uniformity is the key
architectural decision — it's what let the four metrics be implemented as
fully independent, parallel build tasks with zero file overlap and no
awareness of each other. They never import each other, the loader, the
report module, or the CLI; they only depend on `metriq/models.py`.

**Strict module boundaries by responsibility.** `loader.py` is the only
module that touches the filesystem for input and knows about CSV parsing
details. `report.py` is the only module that knows about Markdown
formatting. `cli.py` contains no business logic — it's purely an
orchestrator that wires `load_events` → the four `compute()` calls →
`build_report`/`write_report`. This separation was chosen specifically to
enable the wave-based parallel build (see Build History) and to keep each
module easy to reason about and test in isolation.

**Frozen shared data model, single point of definition.** `models.py`
defines `EngagementEvent` (frozen/immutable dataclass — a parsed CSV row)
and `MetricResult` (the uniform output shape) once, in Wave 1, and every
other module treats it as read-only after that. This avoids the
coordination problems that would arise if multiple calculators tried to
define or adjust the shared shape independently.

**Strict-mode CSV validation by default, with an escape hatch.**
`load_events(..., strict=True)` (the default) raises `MetriqDataError` on
any malformed row — missing field or unparseable timestamp — rather than
silently dropping data. The alternative (silently skip bad rows) was kept
available via `strict=False` / `--no-strict`, but strict is the default
because for a metrics tool, silently under-counting due to skipped rows is
a worse failure mode than a loud error telling you your CSV is malformed.

**Graceful degradation for retention when only one date is present.**
Rather than erroring or returning a misleading `0%`, `retention_rate.compute`
explicitly returns `retention_rate: None` with a `note` explaining why
(`"single date in dataset"` or `"no events"`) when there isn't enough
date range in the data to measure retention. This was a deliberate,
documented assumption in the design doc rather than an accidental edge case.

**Timestamps parsed as naive local time when no offset is present.**
Documented as a known simplification (see design doc, Data Model section) —
acceptable because the tool is single-user/local and not aggregating across
timezones from multiple sources.

**Duplicate CSV rows are not deduplicated.** Each row is assumed to
represent a real, distinct event; deduplication was explicitly rejected as
a default behavior since the data model has no natural per-row identity
column that would distinguish "duplicate" from "two separate identical
events."

**Report rendering picks its Markdown shape based on the shape of the
data**, rather than each metric module needing to know about Markdown.
`report.py`'s `_render_details` inspects each `MetricResult.details` dict:
a single list-of-dicts renders as a table (e.g. feature usage), a flat dict
of scalars renders as a bullet list, and anything else falls back to a
nested bullet list. This means new metrics can be added later without
`report.py` needing metric-specific rendering logic, as long as they stick
to the `MetricResult` contract.

## Build History

### Wave 1 — Foundation (initial build)
Three foundational tasks (scaffolding, shared data model, CSV loader),
executed with `models.py` and `pyproject.toml`/`__init__.py` files done
first/concurrently, then the loader built against the frozen model:
- Created `pyproject.toml`, `metriq/__init__.py`, `metriq/metrics/__init__.py` (project scaffolding, `metriq` console-script entrypoint).
- Created `metriq/models.py` (`EngagementEvent`, `MetricResult`, `Events` alias — frozen dataclasses, no logic).
- Created `metriq/loader.py` (`load_events`, `MetriqDataError`) plus `tests/fixtures/sample_events.csv` and `tests/test_loader.py`.
- **Tester pass:** 24/24 tests passed (12 original + 12 additional model/import sanity tests the tester added).
- **Bug found & fixed:** `pyproject.toml` declared `requires-python = ">=3.11"` but the local interpreter was Python 3.10.11. Fixed by relaxing the constraint to `>=3.10` (coordinator-level fix, not a full builder/fixer cycle).

### Wave 2 — Independent metric calculators (4 parallel builder tasks)
Built fully in parallel, each importing only `metriq.models`, with no
cross-imports between metric modules:
- `metriq/metrics/active_users.py` + `tests/test_active_users.py`
- `metriq/metrics/session_duration.py` + `tests/test_session_duration.py`
- `metriq/metrics/feature_usage.py` + `tests/test_feature_usage.py`
- `metriq/metrics/retention_rate.py` + `tests/test_retention_rate.py`
- **Tester pass:** integration pass covering shared-events-list mutation safety, determinism, and metric-name-collision checks. 34/34 tests passed, no bugs found.

### Wave 3 — Combiner + orchestration (2 sequential builder tasks)
- `metriq/report.py` (`build_report`, `write_report`) built first, combining the four `MetricResult`s into Markdown. 45/45 tests passing after this task.
- `metriq/cli.py` (`main()`, argparse-based orchestrator wiring loader → 4 calculators → report) built second. Final full suite: **48/48 tests passing**, plus a manual end-to-end CLI smoke test confirmed working output: `metriq: wrote ... (4 metrics, 10 events)`.
- No fixer invocations were needed at any wave — all builder output passed tester review on the first pass.

### Documentation pass (2026-08-13)
- Generated this `DOCS.md` from the design doc (`workflows/metriq_design.md`), `CLAUDE.md`, and direct source inspection of all modules under `metriq/` and `tests/`.
- Note for future maintainers: the test suite currently contains **60 passing tests** (`pytest -q` → `60 passed`), more than the 48 recorded at the end of Wave 3 — indicating additional tests were added to the suite after the last recorded build wave. If you run another build wave, please append a new entry here describing what changed and re-verify this count.

## Reference

### `metriq/models.py` — shared data model
No IO, no business logic. Imported by every other module.

- `@dataclass(frozen=True) EngagementEvent` — one parsed CSV row.
  - Fields: `user_id: str`, `event_timestamp: datetime`, `event_type: str`, `feature_name: str`, `session_id: str`
- `@dataclass MetricResult` — uniform return type for every metric calculator.
  - Fields: `name: str`, `title: str`, `summary: dict[str, Any]`, `details: dict[str, Any] = field(default_factory=dict)`
- `Events = list[EngagementEvent]` — type alias used throughout the codebase.

### `metriq/loader.py` — CSV loading + validation
The only module that reads the input file from disk.

- `load_events(csv_path: str | Path, *, strict: bool = True) -> Events`
  - Opens the CSV, validates the header contains all of `REQUIRED_COLUMNS` (`user_id`, `event_timestamp`, `event_type`, `feature_name`, `session_id`), and parses each row into an `EngagementEvent`.
  - Timestamps are parsed via `_parse_timestamp` (ISO 8601; a trailing `Z` is normalized to `+00:00` before calling `datetime.fromisoformat`).
  - **Raises `MetriqDataError`** on: file not found, path not a file, empty file (no header), missing required column(s), a data file with zero data rows, or (only in strict mode) any row with a missing field or unparseable timestamp.
  - **`strict=False`** silently skips malformed rows instead of raising (rows with missing fields or bad timestamps are dropped, not counted).
  - OS-level read errors are wrapped and re-raised as `MetriqDataError`.
- `class MetriqDataError(Exception)` — the single exception type used for every data/IO problem in this module; imported by `cli.py` to decide the process exit code.
- `REQUIRED_COLUMNS: set[str]` — the five required CSV column names.

**Expected CSV schema:**

| Column | Type | Required | Description |
|---|---|---|---|
| `user_id` | string | yes | Stable unique identifier for the user. |
| `event_timestamp` | ISO 8601 datetime (optional `Z`/offset) | yes | When the event occurred. |
| `event_type` | string | yes | Category of interaction, e.g. `click`, `view`, `submit`. |
| `feature_name` | string | yes | Product feature the event belongs to, e.g. `dashboard`, `export`. |
| `session_id` | string | yes | Groups events into a session for the duration calc. |

Sample fixture: `tests/fixtures/sample_events.csv`.

### `metriq/metrics/active_users.py`
- `compute(events: Events) -> MetricResult`
  - `summary["total_distinct_users"]` — count of distinct `user_id` across all events.
  - `details["active_users_by_date"]` — `dict["YYYY-MM-DD", int]`, sorted ascending by date, count of distinct users active that day.

### `metriq/metrics/session_duration.py`
- `compute(events: Events) -> MetricResult`
  - Groups events by `session_id`; each session's duration = `(max(event_timestamp) - min(event_timestamp)).total_seconds()` (a single-event session has duration `0.0`).
  - `summary`: `total_sessions`, `mean_duration_seconds`, `median_duration_seconds` (via `statistics.mean`/`median`), `min_duration_seconds`, `max_duration_seconds`. All zeroed out if there are no sessions.
  - `details["session_durations_seconds"]` — `dict[session_id, float]`.

### `metriq/metrics/feature_usage.py`
- `compute(events: Events) -> MetricResult`
  - `summary["total_events"]` — total event count. `summary["distinct_features"]` — count of distinct `feature_name` values.
  - `details["usage_by_feature"]` — `list[{"feature_name": str, "count": int, "share": float}]`, sorted by count descending, ties broken alphabetically by feature name. `share` is `count / total_events` (or `0.0` if there are no events).

### `metriq/metrics/retention_rate.py`
- `compute(events: Events) -> MetricResult`
  - Computes the fraction of users active on the earliest calendar date in the dataset who are also active on any later date.
  - `summary["retention_rate"]` — float in `[0, 1]`, or `None` when not computable.
    - `None` with `summary["note"] == "no events"` if `events` is empty.
    - `None` with `summary["note"] == "single date in dataset"` if only one distinct calendar date is present.
  - When computable: `summary["first_date_users"]` and `summary["retained_users"]` (counts), plus `details["first_date"]` ("YYYY-MM-DD") and `details["retained_user_ids"]` (sorted list of user ids).

> All four `compute()` functions above share the identical contract
> `compute(events: Events) -> MetricResult` — pure, deterministic, no IO —
> and never import each other, the loader, the report module, or the CLI.

### `metriq/report.py` — report combiner + writer
The only module that knows about Markdown formatting.

- `build_report(results: list[MetricResult], *, source_path: str, generated_at: datetime) -> str`
  - Pure function. Produces a Markdown string: `# metriq Report` title, source path, ISO-formatted generation timestamp, then one `##` section per `MetricResult` — a bullet list of `summary` values followed by a `### Details` subsection.
  - Value formatting (`_format_value`): `None` → `"N/A"`; floats whose key contains `"rate"` or `"share"` → percentage (`12.34%`); other floats → 2 decimal places; everything else → `str(value)`.
  - Details rendering (`_render_details`) auto-selects a shape: a dict containing a list-of-dicts value (e.g. `usage_by_feature`) → Markdown table via `_render_table`; an all-scalar dict → bullet list; anything else → nested bullet list; empty dict → `*(no details)*`.
- `write_report(markdown: str, output_path: str | Path) -> None`
  - The only IO in this module. Creates parent directories as needed (`mkdir(parents=True, exist_ok=True)`) and overwrites `output_path` with `markdown`.

### `metriq/cli.py` — CLI entrypoint
Orchestrator only — no business logic of its own.

- `main(argv: list[str] | None = None) -> int`
  - Parses args via `_build_parser()`, calls `load_events(args.input_csv, strict=args.strict)`, then runs all four `compute()` functions in sequence (`active_users`, `session_duration`, `feature_usage`, `retention_rate`), calls `build_report(...)` with `generated_at=datetime.now()`, and `write_report(...)`.
  - Prints `metriq: wrote {output} ({n} metrics, {n} events)` to stdout unless `--quiet`/`-q`.
  - **Exit codes:** `0` success, `1` on `MetriqDataError` (message printed to stderr), `2` on argparse usage errors (argparse's own behavior).
  - Registered as the `metriq` console script in `pyproject.toml` (`metriq = "metriq.cli:main"`).

**CLI arguments** (`_build_parser`):

| Arg / Flag | Type | Default | Description |
|---|---|---|---|
| `input_csv` (positional, optional) | path | `events.csv` | Path to the input events CSV. |
| `--output`, `-o` | path | `report.md` | Where the Markdown report is written. |
| `--strict` / `--no-strict` | bool | `True` (strict) | Strict fails on malformed rows; non-strict skips them. Uses `argparse.BooleanOptionalAction` when available (Python 3.9+), with a manual fallback. |
| `--quiet`, `-q` | flag | `False` | Suppress the stdout success summary. |

### `pyproject.toml`
- `name = "metriq"`, `version = "0.1.0"`, `requires-python = ">=3.10"`.
- No runtime dependencies (`dependencies = []`).
- Console script entrypoint: `metriq = "metriq.cli:main"`.
- Build backend: `setuptools.build_meta` (`setuptools>=68.0`).

### `CLAUDE.md`
Project-level context file for future Claude sessions: purpose, stack,
component breakdown, and a note that this project follows the
architect → builder → tester → fixer → deployer subagent workflow for
future extensions.

## Usage

### Install
From the project root:
```bash
pip install -e .
```
This registers the `metriq` console command (via `pyproject.toml`'s
`[project.scripts]` entry). No third-party dependencies are installed —
`metriq` uses only the Python standard library. Requires Python 3.10+.

### Run
After installing:
```bash
metriq events.csv -o report.md
```
Or without installing, from the project root:
```bash
python -m metriq.cli events.csv -o report.md
```

Both forms accept the same arguments:
```
metriq [INPUT_CSV] [--output PATH] [--strict | --no-strict] [--quiet]
```
- `INPUT_CSV` — defaults to `events.csv` in the current directory if omitted.
- `--output` / `-o` — defaults to `report.md`.
- `--strict` (default) — malformed rows abort the run with an error; `--no-strict` skips them instead.
- `--quiet` / `-q` — suppress the one-line success message.

On success, prints:
```
metriq: wrote report.md (4 metrics, N events)
```
and exits `0`. On a data/CSV problem, prints an error to stderr and exits
`1`. On a bad command-line invocation, argparse prints usage and exits `2`.

### Configure
No environment variables or config files are used — all configuration is
via CLI arguments. The input CSV must contain the columns `user_id`,
`event_timestamp`, `event_type`, `feature_name`, `session_id` (see Reference
above for the schema).

### Run tests
```bash
pip install -e ".[test]"   # or: pip install pytest
pytest -q
```
As of this documentation pass, `pytest -q` reports 60 passed.
