"""Tests for metriq.metrics.active_users."""

import unittest
from pathlib import Path

from metriq.loader import load_events
from metriq.metrics.active_users import compute

FIXTURE_DIR = Path(__file__).parent / "fixtures"
SAMPLE_CSV = FIXTURE_DIR / "sample_events.csv"


class ComputeActiveUsersHappyPathTests(unittest.TestCase):
    def test_total_distinct_users(self) -> None:
        events = load_events(SAMPLE_CSV)
        result = compute(events)
        # Distinct user_ids in the fixture: u_1001, u_1002, u_1003, u_1004, u_1005
        self.assertEqual(result.summary["total_distinct_users"], 5)

    def test_active_users_by_date(self) -> None:
        events = load_events(SAMPLE_CSV)
        result = compute(events)
        # 2026-08-12: u_1001, u_1002, u_1003 -> 3 distinct users
        # 2026-08-13: u_1001, u_1002, u_1004, u_1003, u_1005 -> 5 distinct users
        self.assertEqual(
            result.details["active_users_by_date"],
            {"2026-08-12": 3, "2026-08-13": 5},
        )

    def test_dates_sorted_ascending(self) -> None:
        events = load_events(SAMPLE_CSV)
        result = compute(events)
        dates = list(result.details["active_users_by_date"].keys())
        self.assertEqual(dates, sorted(dates))

    def test_result_metadata(self) -> None:
        events = load_events(SAMPLE_CSV)
        result = compute(events)
        self.assertEqual(result.name, "active_users")
        self.assertEqual(result.title, "Active Users")


class ComputeActiveUsersEdgeCaseTests(unittest.TestCase):
    def test_empty_events_returns_zeros(self) -> None:
        result = compute([])
        self.assertEqual(result.summary["total_distinct_users"], 0)
        self.assertEqual(result.details["active_users_by_date"], {})
        self.assertEqual(result.name, "active_users")
        self.assertEqual(result.title, "Active Users")


if __name__ == "__main__":
    unittest.main()
