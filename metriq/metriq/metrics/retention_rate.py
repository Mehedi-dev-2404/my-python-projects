"""Retention rate metric: repeat engagement across calendar dates.

Pure computation only — no IO, no printing.
"""

from __future__ import annotations

from metriq.models import Events, MetricResult


def compute(events: Events) -> MetricResult:
    """Compute the retention rate of users active on the earliest date.

    Args:
        events: The full list of parsed engagement events.

    Returns:
        A `MetricResult` with:
            - `summary["retention_rate"]`: fraction (0-1) of first_date
              users who were also active on at least one later date, or
              `None` if retention is not computable (fewer than two
              distinct dates in the dataset).
            - `summary["first_date_users"]` / `summary["retained_users"]`:
              present only when retention is computable.
            - `details["first_date"]`: the earliest calendar date
              ("YYYY-MM-DD"), present only when retention is computable.
            - `details["retained_user_ids"]`: sorted list of retained
              user ids, present only when retention is computable.
    """
    if not events:
        return MetricResult(
            name="retention_rate",
            title="Retention Rate",
            summary={"retention_rate": None, "note": "no events"},
            details={},
        )

    users_by_date: dict[str, set[str]] = {}
    for event in events:
        date_key = event.event_timestamp.date().isoformat()
        users_by_date.setdefault(date_key, set()).add(event.user_id)

    distinct_dates = sorted(users_by_date)

    if len(distinct_dates) == 1:
        return MetricResult(
            name="retention_rate",
            title="Retention Rate",
            summary={"retention_rate": None, "note": "single date in dataset"},
            details={},
        )

    first_date = distinct_dates[0]
    first_date_users = users_by_date[first_date]

    later_users: set[str] = set()
    for date_key in distinct_dates[1:]:
        later_users |= users_by_date[date_key]

    retained_users = first_date_users & later_users
    retention_rate = len(retained_users) / len(first_date_users)

    return MetricResult(
        name="retention_rate",
        title="Retention Rate",
        summary={
            "retention_rate": retention_rate,
            "first_date_users": len(first_date_users),
            "retained_users": len(retained_users),
        },
        details={
            "first_date": first_date,
            "retained_user_ids": sorted(retained_users),
        },
    )
