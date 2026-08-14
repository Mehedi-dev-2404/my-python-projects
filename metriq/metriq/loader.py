"""CSV loading and validation for metriq.

Reads a raw engagement-events CSV and parses it into a list of
`EngagementEvent` objects. All IO/data problems raise `MetriqDataError`.
"""

from __future__ import annotations

import csv
from datetime import datetime
from pathlib import Path

from metriq.models import EngagementEvent, Events

REQUIRED_COLUMNS = {
    "user_id",
    "event_timestamp",
    "event_type",
    "feature_name",
    "session_id",
}


class MetriqDataError(Exception):
    """Raised when the input CSV is missing, empty, malformed, or invalid."""


def _parse_timestamp(raw: str) -> datetime:
    value = raw.strip()
    if value.endswith("Z"):
        value = value[:-1] + "+00:00"
    return datetime.fromisoformat(value)


def load_events(csv_path: str | Path, *, strict: bool = True) -> Events:
    """Load and validate engagement events from a CSV file.

    Args:
        csv_path: Path to the input CSV file.
        strict: If True (default), any row with a missing field or an
            unparseable timestamp raises `MetriqDataError`. If False,
            such rows are silently skipped.

    Returns:
        A list of `EngagementEvent` objects.

    Raises:
        MetriqDataError: On missing file, empty file, missing required
            columns, or (in strict mode) any malformed row.
    """
    path = Path(csv_path)

    if not path.exists():
        raise MetriqDataError(f"CSV file not found: {path}")

    if not path.is_file():
        raise MetriqDataError(f"Not a file: {path}")

    try:
        with path.open("r", newline="", encoding="utf-8") as fh:
            reader = csv.DictReader(fh)

            if reader.fieldnames is None:
                raise MetriqDataError(f"CSV file is empty (no header row): {path}")

            header_columns = {name.strip() for name in reader.fieldnames}
            missing = REQUIRED_COLUMNS - header_columns
            if missing:
                raise MetriqDataError(
                    "CSV file is missing required column(s): "
                    f"{', '.join(sorted(missing))}"
                )

            events: Events = []
            row_count = 0
            for row_number, row in enumerate(reader, start=2):
                row_count += 1
                try:
                    user_id = (row.get("user_id") or "").strip()
                    event_type = (row.get("event_type") or "").strip()
                    feature_name = (row.get("feature_name") or "").strip()
                    session_id = (row.get("session_id") or "").strip()
                    raw_timestamp = (row.get("event_timestamp") or "").strip()

                    if not (
                        user_id
                        and event_type
                        and feature_name
                        and session_id
                        and raw_timestamp
                    ):
                        raise MetriqDataError(
                            f"Row {row_number}: missing required field(s)"
                        )

                    try:
                        event_timestamp = _parse_timestamp(raw_timestamp)
                    except ValueError as exc:
                        raise MetriqDataError(
                            f"Row {row_number}: unparseable event_timestamp "
                            f"{raw_timestamp!r}"
                        ) from exc

                    events.append(
                        EngagementEvent(
                            user_id=user_id,
                            event_timestamp=event_timestamp,
                            event_type=event_type,
                            feature_name=feature_name,
                            session_id=session_id,
                        )
                    )
                except MetriqDataError:
                    if strict:
                        raise
                    continue

            if row_count == 0:
                raise MetriqDataError(f"CSV file has no data rows: {path}")

    except OSError as exc:
        raise MetriqDataError(f"Failed to read CSV file {path}: {exc}") from exc

    return events
