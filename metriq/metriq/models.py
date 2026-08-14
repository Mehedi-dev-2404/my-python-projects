"""Shared data model for metriq.

Pure data structures only — no IO, no business logic. Other modules
(loader, metrics/*, report, cli) import from this module.
"""

from dataclasses import dataclass, field
from datetime import datetime
from typing import Any


@dataclass(frozen=True)
class EngagementEvent:
    """A single raw engagement event parsed from the input CSV."""

    user_id: str
    event_timestamp: datetime
    event_type: str
    feature_name: str
    session_id: str


@dataclass
class MetricResult:
    """The output of a single metric calculator."""

    name: str
    title: str
    summary: dict[str, Any]
    details: dict[str, Any] = field(default_factory=dict)


Events = list[EngagementEvent]
