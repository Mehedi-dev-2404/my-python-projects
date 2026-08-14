"""Report combiner + writer for metriq.

Combines a list of `MetricResult`s into a single Markdown report string
and writes it to disk. `build_report` is a pure function (no IO);
`write_report` performs the only IO in this module.
"""

from __future__ import annotations

from datetime import datetime
from pathlib import Path
from typing import Any

from metriq.models import MetricResult


def _humanize_key(key: str) -> str:
    """Convert a snake_case dict key into a human-readable title.

    Example: "total_distinct_users" -> "Total Distinct Users".
    """
    return key.replace("_", " ").title()


def _format_value(key: str, value: Any) -> str:
    """Format a summary/detail value for display, humanizing floats.

    Retention-rate-style keys are rendered as percentages; other floats
    are rendered to 2 decimal places.
    """
    if value is None:
        return "N/A"
    if isinstance(value, bool):
        return str(value)
    if isinstance(value, float):
        if "rate" in key or "share" in key:
            return f"{value * 100:.2f}%"
        return f"{value:.2f}"
    return str(value)


def _render_scalar_bullets(data: dict[str, Any], indent: str = "") -> list[str]:
    """Render a flat dict of scalar values as a Markdown bullet list."""
    lines = []
    for key, value in data.items():
        lines.append(f"{indent}- {_humanize_key(key)}: {_format_value(key, value)}")
    return lines


def _render_table(rows: list[dict[str, Any]]) -> list[str]:
    """Render a list of same-shaped dicts as a Markdown table."""
    if not rows:
        return ["*(no data)*"]

    columns = list(rows[0].keys())
    header = "| " + " | ".join(_humanize_key(col) for col in columns) + " |"
    separator = "| " + " | ".join("---" for _ in columns) + " |"
    lines = [header, separator]
    for row in rows:
        cells = [_format_value(col, row.get(col)) for col in columns]
        lines.append("| " + " | ".join(cells) + " |")
    return lines


def _render_details(details: dict[str, Any]) -> list[str]:
    """Render a `MetricResult.details` dict, choosing a shape-appropriate format.

    - Empty dict: a short note.
    - A dict containing a single list-of-dicts value (e.g. `usage_by_feature`):
      rendered as a Markdown table, with any other scalar keys as bullets.
    - A dict of scalar values: bullet list.
    - Anything else (e.g. dict-of-dict, nested structures): nested bullet list.
    """
    if not details:
        return ["*(no details)*"]

    lines: list[str] = []

    # Detect a single list-of-dicts value, which we render as a table.
    list_of_dicts_keys = [
        key
        for key, value in details.items()
        if isinstance(value, list) and value and all(isinstance(item, dict) for item in value)
    ]

    if list_of_dicts_keys:
        for key, value in details.items():
            if key in list_of_dicts_keys:
                lines.append(f"**{_humanize_key(key)}**")
                lines.append("")
                lines.extend(_render_table(value))
                lines.append("")
            elif isinstance(value, dict):
                lines.append(f"**{_humanize_key(key)}**")
                lines.extend(_render_scalar_bullets(value))
            else:
                lines.append(f"- {_humanize_key(key)}: {_format_value(key, value)}")
        return lines

    # All scalar values (str/int/float/None) -> flat bullet list.
    if all(not isinstance(value, (dict, list)) for value in details.values()):
        return _render_scalar_bullets(details)

    # Fallback: nested bullet list, one sub-list per key.
    for key, value in details.items():
        lines.append(f"**{_humanize_key(key)}**")
        if isinstance(value, dict):
            lines.extend(_render_scalar_bullets(value, indent="  "))
        elif isinstance(value, list):
            for item in value:
                lines.append(f"  - {item}")
        else:
            lines.append(f"  - {_format_value(key, value)}")
    return lines


def build_report(
    results: list[MetricResult], *, source_path: str, generated_at: datetime
) -> str:
    """Combine metric results into a single Markdown report string.

    Args:
        results: The computed `MetricResult`s to include, one section each.
        source_path: Path to the source CSV, noted at the top of the report.
        generated_at: Timestamp of report generation, rendered in ISO format.

    Returns:
        The full Markdown report as a string. Pure function, no IO.
    """
    lines: list[str] = ["# metriq Report", ""]
    lines.append(f"Source: `{source_path}`  ")
    lines.append(f"Generated: {generated_at.isoformat()}")
    lines.append("")

    for result in results:
        lines.append(f"## {result.title}")
        lines.append("")
        lines.extend(_render_scalar_bullets(result.summary))
        lines.append("")
        lines.append("### Details")
        lines.append("")
        lines.extend(_render_details(result.details))
        lines.append("")

    return "\n".join(lines).rstrip() + "\n"


def write_report(markdown: str, output_path: str | Path) -> None:
    """Write the report Markdown to `output_path`, creating parent dirs as needed.

    Args:
        markdown: The report content to write (e.g. from `build_report`).
        output_path: Destination file path. Overwritten if it already exists.
    """
    path = Path(output_path)
    path.parent.mkdir(parents=True, exist_ok=True)
    path.write_text(markdown, encoding="utf-8")
