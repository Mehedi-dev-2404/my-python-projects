"""Tests for metriq.metrics.feature_usage."""

import unittest
from pathlib import Path

from metriq.loader import load_events
from metriq.metrics.feature_usage import compute

FIXTURE_DIR = Path(__file__).parent / "fixtures"
SAMPLE_CSV = FIXTURE_DIR / "sample_events.csv"


class FeatureUsageHappyPathTests(unittest.TestCase):
    def test_summary_totals(self) -> None:
        events = load_events(SAMPLE_CSV)
        result = compute(events)
        self.assertEqual(result.name, "feature_usage")
        self.assertEqual(result.title, "Feature Usage")
        self.assertEqual(result.summary["total_events"], 10)
        self.assertEqual(result.summary["distinct_features"], 3)

    def test_usage_by_feature_ranked_with_shares(self) -> None:
        events = load_events(SAMPLE_CSV)
        result = compute(events)
        usage = result.details["usage_by_feature"]
        self.assertEqual(
            usage,
            [
                {"feature_name": "dashboard", "count": 5, "share": 0.5},
                {"feature_name": "export_report", "count": 3, "share": 0.3},
                {"feature_name": "settings", "count": 2, "share": 0.2},
            ],
        )

    def test_shares_sum_to_one(self) -> None:
        events = load_events(SAMPLE_CSV)
        result = compute(events)
        total_share = sum(item["share"] for item in result.details["usage_by_feature"])
        self.assertAlmostEqual(total_share, 1.0)


class FeatureUsageEmptyEventsTests(unittest.TestCase):
    def test_empty_events_returns_zeros(self) -> None:
        result = compute([])
        self.assertEqual(result.name, "feature_usage")
        self.assertEqual(result.title, "Feature Usage")
        self.assertEqual(result.summary["total_events"], 0)
        self.assertEqual(result.summary["distinct_features"], 0)
        self.assertEqual(result.details["usage_by_feature"], [])


if __name__ == "__main__":
    unittest.main()
