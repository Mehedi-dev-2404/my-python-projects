"""Tests for metriq.loader."""

import tempfile
import unittest
from pathlib import Path

from metriq.loader import MetriqDataError, load_events

FIXTURE_DIR = Path(__file__).parent / "fixtures"
SAMPLE_CSV = FIXTURE_DIR / "sample_events.csv"


class LoadEventsHappyPathTests(unittest.TestCase):
    def test_loads_sample_fixture(self) -> None:
        events = load_events(SAMPLE_CSV)
        self.assertEqual(len(events), 10)
        first = events[0]
        self.assertEqual(first.user_id, "u_1001")
        self.assertEqual(first.event_type, "view")
        self.assertEqual(first.feature_name, "dashboard")
        self.assertEqual(first.session_id, "s_88f2")
        self.assertEqual(first.event_timestamp.year, 2026)

    def test_spans_multiple_dates(self) -> None:
        events = load_events(SAMPLE_CSV)
        dates = {e.event_timestamp.date() for e in events}
        self.assertGreaterEqual(len(dates), 2)

    def test_multi_event_session_present(self) -> None:
        events = load_events(SAMPLE_CSV)
        sessions: dict[str, int] = {}
        for e in events:
            sessions[e.session_id] = sessions.get(e.session_id, 0) + 1
        self.assertTrue(any(count >= 2 for count in sessions.values()))

    def test_repeat_user_across_dates(self) -> None:
        events = load_events(SAMPLE_CSV)
        user_dates: dict[str, set] = {}
        for e in events:
            user_dates.setdefault(e.user_id, set()).add(e.event_timestamp.date())
        self.assertTrue(any(len(dates) >= 2 for dates in user_dates.values()))

    def test_z_suffix_timestamp_parses(self) -> None:
        with tempfile.TemporaryDirectory() as tmp:
            path = Path(tmp) / "z.csv"
            path.write_text(
                "user_id,event_timestamp,event_type,feature_name,session_id\n"
                "u_1,2026-08-12T09:14:03Z,view,dashboard,s_1\n"
            )
            events = load_events(path)
            self.assertEqual(len(events), 1)
            self.assertIsNotNone(events[0].event_timestamp.tzinfo)


class LoadEventsErrorTests(unittest.TestCase):
    def test_missing_file_raises(self) -> None:
        with self.assertRaises(MetriqDataError):
            load_events("/nonexistent/path/events.csv")

    def test_missing_required_column_raises(self) -> None:
        with tempfile.TemporaryDirectory() as tmp:
            path = Path(tmp) / "bad_header.csv"
            path.write_text(
                "user_id,event_timestamp,event_type,feature_name\n"
                "u_1,2026-08-12T09:14:03,view,dashboard\n"
            )
            with self.assertRaises(MetriqDataError):
                load_events(path)

    def test_empty_file_raises(self) -> None:
        with tempfile.TemporaryDirectory() as tmp:
            path = Path(tmp) / "empty.csv"
            path.write_text("")
            with self.assertRaises(MetriqDataError):
                load_events(path)

    def test_header_only_no_data_rows_raises(self) -> None:
        with tempfile.TemporaryDirectory() as tmp:
            path = Path(tmp) / "header_only.csv"
            path.write_text(
                "user_id,event_timestamp,event_type,feature_name,session_id\n"
            )
            with self.assertRaises(MetriqDataError):
                load_events(path)

    def test_malformed_row_strict_raises(self) -> None:
        with tempfile.TemporaryDirectory() as tmp:
            path = Path(tmp) / "malformed.csv"
            path.write_text(
                "user_id,event_timestamp,event_type,feature_name,session_id\n"
                "u_1,not-a-timestamp,view,dashboard,s_1\n"
            )
            with self.assertRaises(MetriqDataError):
                load_events(path, strict=True)

    def test_malformed_row_non_strict_skipped(self) -> None:
        with tempfile.TemporaryDirectory() as tmp:
            path = Path(tmp) / "malformed.csv"
            path.write_text(
                "user_id,event_timestamp,event_type,feature_name,session_id\n"
                "u_1,not-a-timestamp,view,dashboard,s_1\n"
                "u_2,2026-08-12T09:14:03,view,dashboard,s_2\n"
            )
            events = load_events(path, strict=False)
            self.assertEqual(len(events), 1)
            self.assertEqual(events[0].user_id, "u_2")

    def test_missing_field_non_strict_skipped(self) -> None:
        with tempfile.TemporaryDirectory() as tmp:
            path = Path(tmp) / "missing_field.csv"
            path.write_text(
                "user_id,event_timestamp,event_type,feature_name,session_id\n"
                ",2026-08-12T09:14:03,view,dashboard,s_1\n"
                "u_2,2026-08-12T09:14:03,view,dashboard,s_2\n"
            )
            events = load_events(path, strict=False)
            self.assertEqual(len(events), 1)
            self.assertEqual(events[0].user_id, "u_2")


if __name__ == "__main__":
    unittest.main()
