"""Command-line entrypoint for metriq.

Orchestrates loading events, computing all metrics, and writing the
combined Markdown report to disk.
"""

from __future__ import annotations

import argparse
import sys
from datetime import datetime

from metriq.loader import MetriqDataError, load_events
from metriq.metrics import active_users, feature_usage, retention_rate, session_duration
from metriq.report import build_report, write_report


def _build_parser() -> argparse.ArgumentParser:
    """Build the argparse parser for the metriq CLI."""
    parser = argparse.ArgumentParser(
        prog="metriq",
        description="Compute engagement metrics from a CSV of events and write a Markdown report.",
    )
    parser.add_argument(
        "input_csv",
        nargs="?",
        default="events.csv",
        help="Path to the input events CSV (default: events.csv)",
    )
    parser.add_argument(
        "--output",
        "-o",
        default="report.md",
        help="Path to write the Markdown report to (default: report.md)",
    )

    if hasattr(argparse, "BooleanOptionalAction"):
        parser.add_argument(
            "--strict",
            dest="strict",
            default=True,
            action=argparse.BooleanOptionalAction,
            help="Fail on malformed rows (default) or skip them with --no-strict.",
        )
    else:
        parser.add_argument(
            "--strict",
            dest="strict",
            action="store_true",
            default=True,
            help="Fail on malformed rows (default).",
        )
        parser.add_argument(
            "--no-strict",
            dest="strict",
            action="store_false",
            help="Skip malformed rows instead of failing.",
        )

    parser.add_argument(
        "--quiet",
        "-q",
        action="store_true",
        default=False,
        help="Suppress the success summary printed to stdout.",
    )
    return parser


def main(argv: list[str] | None = None) -> int:
    """Run the metriq CLI. Returns a process exit code."""
    parser = _build_parser()
    args = parser.parse_args(argv)

    try:
        events = load_events(args.input_csv, strict=args.strict)
    except MetriqDataError as exc:
        print(f"metriq: error: {exc}", file=sys.stderr)
        return 1

    results = [
        active_users.compute(events),
        session_duration.compute(events),
        feature_usage.compute(events),
        retention_rate.compute(events),
    ]

    markdown = build_report(results, source_path=args.input_csv, generated_at=datetime.now())
    write_report(markdown, args.output)

    if not args.quiet:
        print(f"metriq: wrote {args.output} ({len(results)} metrics, {len(events)} events)")

    return 0


if __name__ == "__main__":
    sys.exit(main())
