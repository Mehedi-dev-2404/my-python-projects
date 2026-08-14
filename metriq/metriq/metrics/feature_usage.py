"""Feature usage metric: event counts ranked by feature.

Pure computation only — no IO, no printing.
"""

from __future__ import annotations

from collections import Counter

from metriq.models import Events, MetricResult


def compute(events: Events) -> MetricResult:
    """Compute per-feature usage counts and shares from engagement events.

    Args:
        events: The full list of parsed engagement events.

    Returns:
        A `MetricResult` with:
            - `summary["total_events"]`: total number of events.
            - `summary["distinct_features"]`: count of distinct feature_name
              values across all events.
            - `details["usage_by_feature"]`: a list of
              `{"feature_name": str, "count": int, "share": float}` dicts,
              sorted by count descending, ties broken alphabetically by
              feature_name.
    """
    total_events = len(events)
    counts = Counter(event.feature_name for event in events)

    usage_by_feature = [
        {
            "feature_name": feature_name,
            "count": count,
            "share": (count / total_events) if total_events else 0.0,
        }
        for feature_name, count in sorted(
            counts.items(), key=lambda item: (-item[1], item[0])
        )
    ]

    return MetricResult(
        name="feature_usage",
        title="Feature Usage",
        summary={
            "total_events": total_events,
            "distinct_features": len(counts),
        },
        details={"usage_by_feature": usage_by_feature},
    )
