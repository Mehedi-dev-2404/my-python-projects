"""Tests for metriq.metrics.retention_rate."""

import unittest
from datetime import datetime
from pathlib import Path

from metriq.loader import load_events
from metriq.metrics.retention_rate import compute
from metriq.models import EngagementEvent

FIXTURE_DIR = Path(__file__).parent / "fixtures"
SAMPLE_CSV = FIXTURE_DIR / "sample_events.csv"


class ComputeRetentionRateHappyPathTests(unittest.TestCase):
    def test_retention_rate(self) -> None:
        events = load_events(SAMPLE_CSV)
        result = compute(events)
        # first_date = 2026-08-12, users: u_1001, u_1002, u_1003 (3 users)
        # all 3 also appear on 2026-08-13 -> retained_users = 3
        self.assertEqual(result.summary["first_date_users"], 3)
        self.assertEqual(result.summary["retained_users"], 3)
        self.assertEqual(result.summary["retention_rate"], 1.0)

    def test_details(self) -> None:
        events = load_events(SAMPLE_CSV)
        result = compute(events)
        self.assertEqual(result.details["first_date"], "2026-08-12")
        self.assertEqual(
            result.details["retained_user_ids"], ["u_1001", "u_1002", "u_1003"]
        )

    def test_result_metadata(self) -> None:
        events = load_events(SAMPLE_CSV)
        result = compute(events)
        self.assertEqual(result.name, "retention_rate")
        self.assertEqual(result.title, "Retention Rate")


class ComputeRetentionRateEdgeCaseTests(unittest.TestCase):
    def test_single_date_returns_none(self) -> None:
        events = [
            EngagementEvent(
                user_id="u_1",
                event_timestamp=datetime(2026, 8, 12, 9, 0, 0),
                event_type="view",
                feature_name="dashboard",
                session_id="s_1",
            ),
            EngagementEvent(
                user_id="u_2",
                event_timestamp=datetime(2026, 8, 12, 10, 0, 0),
                event_type="view",
                feature_name="dashboard",
                session_id="s_2",
            ),
        ]
        result = compute(events)
        self.assertIsNone(result.summary["retention_rate"])
        self.assertEqual(result.summary["note"], "single date in dataset")
        self.assertEqual(result.details, {})
        self.assertEqual(result.name, "retention_rate")
        self.assertEqual(result.title, "Retention Rate")

    def test_empty_events_returns_none(self) -> None:
        result = compute([])
        self.assertIsNone(result.summary["retention_rate"])
        self.assertEqual(result.summary["note"], "no events")
        self.assertEqual(result.details, {})
        self.assertEqual(result.name, "retention_rate")
        self.assertEqual(result.title, "Retention Rate")


if __name__ == "__main__":
    unittest.main()
