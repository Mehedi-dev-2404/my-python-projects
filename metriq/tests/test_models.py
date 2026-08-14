"""Tests for metriq.models."""

import dataclasses
from datetime import datetime

import pytest

from metriq.models import EngagementEvent, MetricResult, Events


def _make_event(**overrides) -> EngagementEvent:
    defaults = dict(
        user_id="u_1",
        event_timestamp=datetime(2026, 8, 12, 9, 14, 3),
        event_type="view",
        feature_name="dashboard",
        session_id="s_1",
    )
    defaults.update(overrides)
    return EngagementEvent(**defaults)


class TestEngagementEvent:
    def test_field_values_round_trip(self):
        ts = datetime(2026, 8, 12, 9, 14, 3)
        event = EngagementEvent(
            user_id="u_1001",
            event_timestamp=ts,
            event_type="view",
            feature_name="dashboard",
            session_id="s_88f2",
        )
        assert event.user_id == "u_1001"
        assert event.event_timestamp == ts
        assert event.event_type == "view"
        assert event.feature_name == "dashboard"
        assert event.session_id == "s_88f2"

    def test_is_frozen_immutable(self):
        event = _make_event()
        with pytest.raises(dataclasses.FrozenInstanceError):
            event.user_id = "someone_else"

    def test_is_hashable(self):
        # Frozen dataclasses are hashable by default; metric calculators may
        # want to dedupe events in sets, so this must hold.
        event = _make_event()
        assert isinstance(hash(event), int)
        assert len({event, _make_event()}) == 1

    def test_equality_by_value(self):
        e1 = _make_event()
        e2 = _make_event()
        assert e1 == e2
        e3 = _make_event(user_id="u_2")
        assert e1 != e3


class TestMetricResult:
    def test_construct_with_required_fields_only(self):
        result = MetricResult(
            name="active_users",
            title="Active Users",
            summary={"total": 5},
        )
        assert result.name == "active_users"
        assert result.title == "Active Users"
        assert result.summary == {"total": 5}
        assert result.details == {}

    def test_details_defaults_are_independent_per_instance(self):
        # Guard against the classic mutable-default-argument bug: each
        # MetricResult must get its own details dict.
        r1 = MetricResult(name="a", title="A", summary={})
        r2 = MetricResult(name="b", title="B", summary={})
        r1.details["x"] = 1
        assert r2.details == {}

    def test_is_mutable(self):
        # MetricResult is a plain (non-frozen) dataclass; metric modules may
        # want to build it up incrementally.
        result = MetricResult(name="a", title="A", summary={})
        result.summary["total"] = 10
        assert result.summary == {"total": 10}


class TestEventsAlias:
    def test_events_alias_accepts_list_of_engagement_events(self):
        events: Events = [_make_event(), _make_event(user_id="u_2")]
        assert len(events) == 2
        assert all(isinstance(e, EngagementEvent) for e in events)
