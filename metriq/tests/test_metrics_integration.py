"""Integration check across all four Wave 2 metric calculators.

Verifies that the four independently-built `compute()` functions can be
called against the SAME `Events` list without crashing, without mutating
the shared input, and without colliding on `MetricResult.name`.
"""

from __future__ import annotations

import copy
import unittest
from pathlib import Path

from metriq.loader import load_events
from metriq.models import Events, MetricResult
from metriq.metrics import active_users, feature_usage, retention_rate, session_duration

FIXTURE_PATH = Path(__file__).parent / "fixtures" / "sample_events.csv"

CALCULATORS = [active_users, feature_usage, retention_rate, session_duration]

EXPECTED_NAMES = {
    "active_users",
    "session_duration",
    "feature_usage",
    "retention_rate",
}


class MetricsIntegrationTests(unittest.TestCase):
    def setUp(self) -> None:
        self.events: Events = load_events(FIXTURE_PATH)
        self.assertTrue(self.events, "fixture produced no events")
        # Snapshot for post-call comparison.
        self._original_id = id(self.events)
        self._original_length = len(self.events)
        self._original_copy = copy.deepcopy(self.events)

    def test_all_calculators_run_against_shared_events_without_mutation(self) -> None:
        results: list[MetricResult] = []

        for module in CALCULATORS:
            result = module.compute(self.events)
            results.append(result)

            # No crash implied by reaching here; verify contract shape.
            self.assertIsInstance(
                result, MetricResult, f"{module.__name__}.compute did not return MetricResult"
            )
            self.assertIsInstance(result.name, str)
            self.assertIsInstance(result.title, str)
            self.assertIsInstance(result.summary, dict)
            self.assertIsInstance(result.details, dict)

            # The shared list must be untouched after each call — check
            # after every single call, not just at the very end, so we can
            # pinpoint exactly which module is responsible for mutation.
            self.assertEqual(
                id(self.events),
                self._original_id,
                f"{module.__name__}.compute rebound/reassigned the events list "
                "reference (should be impossible for a list param, but "
                "checking defensively)",
            )
            self.assertEqual(
                len(self.events),
                self._original_length,
                f"{module.__name__}.compute mutated the length of the shared events list",
            )
            self.assertEqual(
                self.events,
                self._original_copy,
                f"{module.__name__}.compute mutated the contents of the shared events list",
            )

        # Field-naming / non-collision checks against the spec.
        names = [r.name for r in results]
        self.assertEqual(
            len(names), len(set(names)), f"duplicate MetricResult.name values found: {names}"
        )
        self.assertEqual(
            set(names),
            EXPECTED_NAMES,
            f"MetricResult.name values do not match spec: got {set(names)}, "
            f"expected {EXPECTED_NAMES}",
        )

        # Final full-list equality check after all four calls combined.
        self.assertEqual(
            self.events,
            self._original_copy,
            "shared events list was mutated across the full sequence of compute() calls",
        )
        self.assertEqual(id(self.events), self._original_id)

    def test_calculators_are_deterministic_on_repeated_calls(self) -> None:
        """Re-running compute() on the same input should be side-effect-free
        and produce identical results (pure function contract)."""
        for module in CALCULATORS:
            first = module.compute(self.events)
            second = module.compute(self.events)
            self.assertEqual(
                first.summary,
                second.summary,
                f"{module.__name__}.compute is non-deterministic across repeated calls",
            )
            self.assertEqual(first.details, second.details)

    def test_original_input_list_object_never_replaced(self) -> None:
        """Sanity check: compute() must not (and cannot, given Python
        semantics) rebind the caller's list variable; this documents that
        expectation explicitly for future waves (report/cli) that will
        pass the same events list into all four calculators sequentially.
        """
        before_id = id(self.events)
        for module in CALCULATORS:
            module.compute(self.events)
        self.assertEqual(id(self.events), before_id)


if __name__ == "__main__":
    unittest.main()
