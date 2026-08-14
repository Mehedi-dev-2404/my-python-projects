"""Session duration metric for metriq.

Groups engagement events by `session_id` and computes each session's
duration in seconds, then aggregates those durations into summary
statistics. Pure computation only — no IO, no printing.
"""

from __future__ import annotations

import statistics

from metriq.models import Events, MetricResult


def compute(events: Events) -> MetricResult:
    """Compute session duration statistics from a list of events.

    Args:
        events: The full list of engagement events.

    Returns:
        A `MetricResult` with name "session_duration". `summary` contains
        total session count and mean/median/min/max duration in seconds.
        `details["session_durations_seconds"]` maps each session_id to
        its duration in seconds.
    """
    sessions: dict[str, list] = {}
    for event in events:
        sessions.setdefault(event.session_id, []).append(event.event_timestamp)

    session_durations: dict[str, float] = {
        session_id: (max(timestamps) - min(timestamps)).total_seconds()
        for session_id, timestamps in sessions.items()
    }

    durations = list(session_durations.values())

    if durations:
        summary = {
            "total_sessions": len(durations),
            "mean_duration_seconds": statistics.mean(durations),
            "median_duration_seconds": statistics.median(durations),
            "min_duration_seconds": min(durations),
            "max_duration_seconds": max(durations),
        }
    else:
        summary = {
            "total_sessions": 0,
            "mean_duration_seconds": 0.0,
            "median_duration_seconds": 0.0,
            "min_duration_seconds": 0.0,
            "max_duration_seconds": 0.0,
        }

    return MetricResult(
        name="session_duration",
        title="Session Duration",
        summary=summary,
        details={"session_durations_seconds": session_durations},
    )
