"""Pytest suite for the brewlog CLI (log-coffee / coffee-history).

Run with the brewlog package installed (pip install -e .) so BREWLOG_FILE
env var isolation works against brewlog.cli.get_log_path().
"""

import json
import subprocess
import sys

import pytest


def run(args, env):
    """Run a console-script style invocation via `python -m brewlog.cli` equivalent."""
    return subprocess.run(args, capture_output=True, text=True, env=env)


@pytest.fixture
def log_env(tmp_path, monkeypatch):
    log_file = tmp_path / "coffee_log.json"
    env = {**__import__("os").environ, "BREWLOG_FILE": str(log_file)}
    return log_file, env


def test_log_coffee_basic(log_env):
    log_file, env = log_env
    result = run(["log-coffee", "espresso, double"], env)
    assert result.returncode == 0
    assert "Logged: espresso, double  @ " in result.stdout
    assert log_file.exists()
    data = json.loads(log_file.read_text())
    assert isinstance(data, list) and len(data) == 1
    assert data[0]["entry"] == "espresso, double"
    assert "timestamp" in data[0]


def test_multiple_appends_preserve_order(log_env):
    log_file, env = log_env
    for entry in ["cortado", "americano", "latte"]:
        r = run(["log-coffee", entry], env)
        assert r.returncode == 0
    data = json.loads(log_file.read_text())
    assert [e["entry"] for e in data] == ["cortado", "americano", "latte"]


def test_unquoted_multiword_entry(log_env):
    log_file, env = log_env
    result = run(["log-coffee", "flat", "white", "oat", "milk"], env)
    assert result.returncode == 0
    data = json.loads(log_file.read_text())
    assert data[-1]["entry"] == "flat white oat milk"


def test_coffee_history_prints_all_oldest_to_newest(log_env):
    log_file, env = log_env
    for entry in ["one", "two", "three"]:
        run(["log-coffee", entry], env)
    result = run(["coffee-history"], env)
    assert result.returncode == 0
    lines = result.stdout.strip().splitlines()
    assert len(lines) == 3
    assert lines[0].endswith("one")
    assert lines[1].endswith("two")
    assert lines[2].endswith("three")


def test_coffee_history_limit_n(log_env):
    log_file, env = log_env
    for entry in ["one", "two", "three"]:
        run(["log-coffee", entry], env)
    result = run(["coffee-history", "-n", "1"], env)
    assert result.returncode == 0
    lines = result.stdout.strip().splitlines()
    assert len(lines) == 1
    assert lines[0].endswith("three")


def test_empty_entry_rejected(log_env):
    log_file, env = log_env
    result = run(["log-coffee", ""], env)
    assert result.returncode != 0
    assert "Error" in result.stderr
    assert not log_file.exists()


def test_no_args_rejected(log_env):
    log_file, env = log_env
    result = run(["log-coffee"], env)
    assert result.returncode != 0
    assert not log_file.exists()


def test_missing_log_file_history(log_env):
    log_file, env = log_env
    assert not log_file.exists()
    result = run(["coffee-history"], env)
    assert result.returncode == 0
    assert result.stdout.strip() == "No coffee logged yet."


def test_corrupt_json_treated_as_empty(log_env):
    log_file, env = log_env
    log_file.write_text("{not valid json!!!")
    result = run(["coffee-history"], env)
    assert result.returncode == 0
    assert result.stdout.strip() == "No coffee logged yet."

    # log-coffee should still work and overwrite with a fresh valid array
    result = run(["log-coffee", "recovery test"], env)
    assert result.returncode == 0
    data = json.loads(log_file.read_text())
    assert data == [{"timestamp": data[0]["timestamp"], "entry": "recovery test"}]


def test_works_from_different_cwd(log_env, tmp_path):
    log_file, env = log_env
    other_dir = tmp_path / "some" / "other" / "dir"
    other_dir.mkdir(parents=True)
    result = run(["log-coffee", "cwd test"], env)
    # rerun with cwd set elsewhere
    result = subprocess.run(
        ["coffee-history"], capture_output=True, text=True, env=env, cwd=str(other_dir)
    )
    assert result.returncode == 0
    assert "cwd test" in result.stdout
