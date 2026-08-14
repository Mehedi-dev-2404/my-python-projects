# metriq

## Purpose
A single-user, local CLI tool that reads a CSV of raw daily engagement events, computes four metrics in parallel (active users, session duration, feature usage, retention rate), and writes a combined Markdown report (`report.md`).

## Stack
- Python 3.11+, standard library only (`csv`, `statistics`, `datetime`, `collections`, `argparse`, `pathlib`, `dataclasses`)
- No external APIs, no network calls, no third-party runtime dependencies
- Run manually via CLI: `metriq events.csv -o report.md`

## Component Breakdown
- `metriq/models.py` — shared data model: `EngagementEvent`, `MetricResult`, `Events` alias
- `metriq/loader.py` — CSV loading + validation, raises `MetriqDataError`
- `metriq/metrics/active_users.py` — distinct user count (overall + per date)
- `metriq/metrics/session_duration.py` — session duration stats (mean/median/min/max)
- `metriq/metrics/feature_usage.py` — event counts ranked by feature
- `metriq/metrics/retention_rate.py` — repeat engagement across dates
- `metriq/report.py` — combines `MetricResult`s into Markdown, writes to disk
- `metriq/cli.py` — orchestrator/entrypoint (`metriq` console script)

Full design doc: `workflows/metriq_design.md`

## Workflow note
This project uses the multi-instance subagent workflow: **architect → builder → tester → fixer → deployer**. When extending metriq, follow the same pattern — design changes go through architect, implementation through builder, verification through tester/fixer, and shipping through deployer.
