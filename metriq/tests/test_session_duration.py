"""Tests for metriq.metrics.session_duration."""

import unittest
from pathlib import Path

from metriq.loader import load_events
from metriq.metrics.session_duration import compute

FIXTURE_DIR = Path(__file__).parent / "fixtures"
SAMPLE_CSV = FIXTURE_DIR / "sample_events.csv"


class SessionDurationHappyPathTests(unittest.TestCase):
    def test_result_shape(self) -> None:
        events = load_events(SAMPLE_CSV)
        result = compute(events)
        self.assertEqual(result.name, "session_duration")
        self.assertEqual(result.title, "Session Duration")
        for key in (
            "total_sessions",
            "mean_duration_seconds",
            "median_duration_seconds",
            "min_duration_seconds",
            "max_duration_seconds",
        ):
            self.assertIn(key, result.summary)
        self.assertIn("session_durations_seconds", result.details)

    def test_session_count_matches_distinct_sessions(self) -> None:
        events = load_events(SAMPLE_CSV)
        result = compute(events)
        distinct_sessions = {e.session_id for e in events}
        self.assertEqual(result.summary["total_sessions"], len(distinct_sessions))
        self.assertEqual(
            set(result.details["session_durations_seconds"].keys()),
            distinct_sessions,
        )

    def test_multi_event_session_duration_positive(self) -> None:
        events = load_events(SAMPLE_CSV)
        result = compute(events)
        self.assertIn("s_88f2", result.details["session_durations_seconds"])
        self.assertGreater(
            result.details["session_durations_seconds"]["s_88f2"], 0.0
        )

    def test_min_max_bounds(self) -> None:
        events = load_events(SAMPLE_CSV)
        result = compute(events)
        durations = list(result.details["session_durations_seconds"].values())
        self.assertEqual(result.summary["min_duration_seconds"], min(durations))
        self.assertEqual(result.summary["max_duration_seconds"], max(durations))


class SessionDurationEdgeCaseTests(unittest.TestCase):
    def test_empty_events_returns_zeros(self) -> None:
        result = compute([])
        self.assertEqual(result.name, "session_duration")
        self.assertEqual(result.summary["total_sessions"], 0)
        self.assertEqual(result.summary["mean_duration_seconds"], 0.0)
        self.assertEqual(result.summary["median_duration_seconds"], 0.0)
        self.assertEqual(result.summary["min_duration_seconds"], 0.0)
        self.assertEqual(result.summary["max_duration_seconds"], 0.0)
        self.assertEqual(result.details["session_durations_seconds"], {})


if __name__ == "__main__":
    unittest.main()
