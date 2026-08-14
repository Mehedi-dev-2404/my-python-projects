"""Sanity checks that metriq is importable as a package and that
load_events on the sample fixture produces correctly-typed objects.

These are cheap smoke tests intended to catch packaging/import
regressions before Wave 2 (the metric calculator modules) is built on
top of models.py and loader.py.
"""

from datetime import datetime
from pathlib import Path

from metriq.loader import MetriqDataError, load_events
from metriq.models import EngagementEvent, Events, MetricResult

FIXTURE_DIR = Path(__file__).parent / "fixtures"
SAMPLE_CSV = FIXTURE_DIR / "sample_events.csv"


def test_top_level_symbols_importable():
    # Just re-affirms the imports above succeeded; a failure here would
    # surface as a collection-time ImportError instead.
    assert EngagementEvent is not None
    assert MetricResult is not None
    assert Events is not None
    assert load_events is not None
    assert MetriqDataError is not None


def test_load_events_returns_engagement_event_instances():
    events = load_events(SAMPLE_CSV)
    assert len(events) == 10
    assert all(isinstance(e, EngagementEvent) for e in events)


def test_load_events_timestamp_is_real_datetime():
    events = load_events(SAMPLE_CSV)
    first = events[0]
    assert isinstance(first.event_timestamp, datetime)
    assert first.event_timestamp == datetime(2026, 8, 12, 9, 14, 3)


def test_load_events_field_types_are_str():
    events = load_events(SAMPLE_CSV)
    for e in events:
        assert isinstance(e.user_id, str)
        assert isinstance(e.event_type, str)
        assert isinstance(e.feature_name, str)
        assert isinstance(e.session_id, str)
