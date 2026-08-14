"""Tests for metriq.report."""

import tempfile
import unittest
from datetime import datetime
from pathlib import Path

from metriq.models import MetricResult
from metriq.report import build_report, write_report


def _sample_results() -> list[MetricResult]:
    """Build a small set of hand-constructed MetricResults covering all 4 shapes."""
    active_users = MetricResult(
        name="active_users",
        title="Active Users",
        summary={"total_distinct_users": 3},
        details={"active_users_by_date": {"2024-01-01": 2, "2024-01-02": 1}},
    )
    session_duration = MetricResult(
        name="session_duration",
        title="Session Duration",
        summary={
            "total_sessions": 2,
            "mean_duration_seconds": 125.5,
            "median_duration_seconds": 125.5,
            "min_duration_seconds": 100.0,
            "max_duration_seconds": 151.0,
        },
        details={"session_durations_seconds": {"s1": 100.0, "s2": 151.0}},
    )
    feature_usage = MetricResult(
        name="feature_usage",
        title="Feature Usage",
        summary={"total_events": 10, "distinct_features": 2},
        details={
            "usage_by_feature": [
                {"feature_name": "dashboard", "count": 6, "share": 0.6},
                {"feature_name": "settings", "count": 4, "share": 0.4},
            ]
        },
    )
    retention_rate = MetricResult(
        name="retention_rate",
        title="Retention Rate",
        summary={
            "retention_rate": 0.5,
            "first_date_users": 2,
            "retained_users": 1,
        },
        details={"first_date": "2024-01-01", "retained_user_ids": ["u1"]},
    )
    return [active_users, session_duration, feature_usage, retention_rate]


class BuildReportTests(unittest.TestCase):
    def test_report_is_nonempty_string(self) -> None:
        markdown = build_report(
            _sample_results(),
            source_path="events.csv",
            generated_at=datetime(2024, 1, 15, 12, 0, 0),
        )
        self.assertIsInstance(markdown, str)
        self.assertTrue(markdown.strip())

    def test_report_contains_top_heading(self) -> None:
        markdown = build_report(
            _sample_results(),
            source_path="events.csv",
            generated_at=datetime(2024, 1, 15, 12, 0, 0),
        )
        self.assertIn("# metriq Report", markdown)

    def test_report_contains_each_metric_title(self) -> None:
        results = _sample_results()
        markdown = build_report(
            results,
            source_path="events.csv",
            generated_at=datetime(2024, 1, 15, 12, 0, 0),
        )
        for result in results:
            self.assertIn(f"## {result.title}", markdown)

    def test_report_contains_source_path_and_timestamp(self) -> None:
        generated_at = datetime(2024, 1, 15, 12, 0, 0)
        markdown = build_report(
            _sample_results(),
            source_path="data/events.csv",
            generated_at=generated_at,
        )
        self.assertIn("data/events.csv", markdown)
        self.assertIn(generated_at.isoformat(), markdown)

    def test_report_renders_table_for_list_of_dicts(self) -> None:
        markdown = build_report(
            _sample_results(),
            source_path="events.csv",
            generated_at=datetime(2024, 1, 15, 12, 0, 0),
        )
        self.assertIn("| Feature Name | Count | Share |", markdown)
        self.assertIn("dashboard", markdown)

    def test_report_humanizes_summary_keys(self) -> None:
        markdown = build_report(
            _sample_results(),
            source_path="events.csv",
            generated_at=datetime(2024, 1, 15, 12, 0, 0),
        )
        self.assertIn("Total Distinct Users", markdown)
        self.assertIn("Mean Duration Seconds", markdown)

    def test_report_handles_none_retention_rate(self) -> None:
        no_retention = MetricResult(
            name="retention_rate",
            title="Retention Rate",
            summary={"retention_rate": None, "note": "single date in dataset"},
            details={},
        )
        markdown = build_report(
            [no_retention],
            source_path="events.csv",
            generated_at=datetime(2024, 1, 15, 12, 0, 0),
        )
        self.assertIn("## Retention Rate", markdown)
        self.assertIn("N/A", markdown)
        self.assertIn("*(no details)*", markdown)


class WriteReportTests(unittest.TestCase):
    def test_write_report_creates_file_with_expected_content(self) -> None:
        markdown = "# metriq Report\n\nHello, world.\n"
        with tempfile.TemporaryDirectory() as tmp_dir:
            output_path = Path(tmp_dir) / "report.md"
            write_report(markdown, output_path)
            self.assertTrue(output_path.exists())
            self.assertEqual(output_path.read_text(encoding="utf-8"), markdown)

    def test_write_report_creates_missing_parent_dirs(self) -> None:
        markdown = "# metriq Report\n"
        with tempfile.TemporaryDirectory() as tmp_dir:
            output_path = Path(tmp_dir) / "nested" / "dir" / "report.md"
            self.assertFalse(output_path.parent.exists())
            write_report(markdown, output_path)
            self.assertTrue(output_path.exists())
            self.assertEqual(output_path.read_text(encoding="utf-8"), markdown)

    def test_write_report_accepts_string_path(self) -> None:
        markdown = "# metriq Report\n"
        with tempfile.TemporaryDirectory() as tmp_dir:
            output_path = str(Path(tmp_dir) / "report.md")
            write_report(markdown, output_path)
            self.assertTrue(Path(output_path).exists())

    def test_write_report_overwrites_existing_file(self) -> None:
        with tempfile.TemporaryDirectory() as tmp_dir:
            output_path = Path(tmp_dir) / "report.md"
            write_report("first\n", output_path)
            write_report("second\n", output_path)
            self.assertEqual(output_path.read_text(encoding="utf-8"), "second\n")


if __name__ == "__main__":
    unittest.main()
