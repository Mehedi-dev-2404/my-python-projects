"""All logic for the brewlog CLI: load/append JSON, print confirmation, print history."""

import argparse
import json
import os
import sys
from datetime import datetime
from pathlib import Path


def get_log_path() -> Path:
    """Return the path to the coffee log JSON file, honoring BREWLOG_FILE override."""
    override = os.environ.get("BREWLOG_FILE")
    if override:
        return Path(override)
    return Path.home() / ".brewlog" / "coffee_log.json"


def load_log() -> list:
    """Load the coffee log as a list of {timestamp, entry} dicts.

    Missing, empty, or corrupt files are treated as an empty list.
    """
    path = get_log_path()
    if not path.exists():
        return []
    try:
        text = path.read_text().strip()
        if not text:
            return []
        data = json.loads(text)
        if not isinstance(data, list):
            return []
        return data
    except (json.JSONDecodeError, OSError):
        return []


def append_entry(text: str) -> dict:
    """Append a new entry with the current local timestamp and return it."""
    path = get_log_path()
    path.parent.mkdir(parents=True, exist_ok=True)

    entries = load_log()
    now = datetime.now().astimezone()
    entry = {
        "timestamp": now.isoformat(timespec="seconds"),
        "entry": text,
    }
    entries.append(entry)
    path.write_text(json.dumps(entries, indent=2))
    return entry


def print_history(limit: int = None) -> None:
    """Print logged entries oldest to newest, optionally limited to the last N entries."""
    entries = load_log()
    if not entries:
        print("No coffee logged yet.")
        return

    if limit is not None:
        entries = entries[-limit:]

    for entry in entries:
        try:
            ts = datetime.fromisoformat(entry["timestamp"])
            formatted = ts.strftime("%Y-%m-%d %H:%M")
        except (KeyError, ValueError):
            formatted = entry.get("timestamp", "unknown")
        print(f"{formatted}  {entry.get('entry', '')}")


def log_main() -> None:
    """Console-script entry point for `log-coffee`."""
    parser = argparse.ArgumentParser(
        prog="log-coffee", description="Log a coffee entry."
    )
    parser.add_argument(
        "entry", nargs="*", help="the coffee entry text (quote it, or pass multiple words)"
    )
    args = parser.parse_args()

    text = " ".join(args.entry).strip()
    if not text:
        print("Error: entry text must not be empty.", file=sys.stderr)
        sys.exit(1)

    entry = append_entry(text)
    ts = datetime.fromisoformat(entry["timestamp"])
    formatted = ts.strftime("%Y-%m-%d %H:%M")
    print(f"Logged: {text}  @ {formatted}")


def history_main() -> None:
    """Console-script entry point for `coffee-history`."""
    parser = argparse.ArgumentParser(
        prog="coffee-history", description="Print the coffee log."
    )
    parser.add_argument(
        "-n", type=int, default=None, help="only show the last N entries"
    )
    args = parser.parse_args()

    print_history(limit=args.n)


if __name__ == "__main__":
    log_main()
