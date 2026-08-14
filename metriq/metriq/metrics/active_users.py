"""Active users metric: distinct user counts overall and per calendar date.

Pure computation only — no IO, no printing.
"""

from __future__ import annotations

from metriq.models import Events, MetricResult


def compute(events: Events) -> MetricResult:
    """Compute distinct active-user counts from engagement events.

    Args:
        events: The full list of parsed engagement events.

    Returns:
        A `MetricResult` with:
            - `summary["total_distinct_users"]`: count of distinct user_id
              values across all events.
            - `details["active_users_by_date"]`: a dict mapping
              "YYYY-MM-DD" (sorted ascending) to the count of distinct
              user_id values active on that date.
    """
    users_by_date: dict[str, set[str]] = {}
    all_users: set[str] = set()

    for event in events:
        all_users.add(event.user_id)
        date_key = event.event_timestamp.date().isoformat()
        users_by_date.setdefault(date_key, set()).add(event.user_id)

    active_users_by_date = {
        date_key: len(users_by_date[date_key]) for date_key in sorted(users_by_date)
    }

    return MetricResult(
        name="active_users",
        title="Active Users",
        summary={"total_distinct_users": len(all_users)},
        details={"active_users_by_date": active_users_by_date},
    )
