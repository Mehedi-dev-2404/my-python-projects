"""Tests for the metriq CLI entrypoint."""

import os
import tempfile
import unittest

from metriq.cli import main

FIXTURE = os.path.join(os.path.dirname(__file__), "fixtures", "sample_events.csv")


class TestCliHappyPath(unittest.TestCase):
    def test_writes_report_and_returns_zero(self) -> None:
        with tempfile.TemporaryDirectory() as tmpdir:
            output_path = os.path.join(tmpdir, "report.md")
            rc = main([FIXTURE, "-o", output_path, "-q"])

            self.assertEqual(rc, 0)
            self.assertTrue(os.path.isfile(output_path))
            with open(output_path, encoding="utf-8") as f:
                content = f.read()
            self.assertIn("# metriq Report", content)


class TestCliMissingInput(unittest.TestCase):
    def test_missing_input_file_returns_one(self) -> None:
        with tempfile.TemporaryDirectory() as tmpdir:
            output_path = os.path.join(tmpdir, "report.md")
            missing_path = os.path.join(tmpdir, "does_not_exist.csv")
            rc = main([missing_path, "-o", output_path, "-q"])

            self.assertEqual(rc, 1)
            self.assertFalse(os.path.exists(output_path))


class TestCliBogusFlag(unittest.TestCase):
    def test_bogus_flag_raises_system_exit(self) -> None:
        with self.assertRaises(SystemExit):
            main(["--this-flag-does-not-exist"])


if __name__ == "__main__":
    unittest.main()
