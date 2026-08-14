# brewlog

A tiny local CLI for logging coffee entries to a JSON file. No cloud, no
scheduling, no external APIs — just a personal log at
`~/.brewlog/coffee_log.json`.

## Install

```bash
cd brewlog
pip install -e .
```

This puts `log-coffee` and `coffee-history` on your PATH.

## Usage

Log an entry:

```bash
log-coffee "flat white, oat milk"
```

```
Logged: flat white, oat milk  @ 2026-08-13 09:41
```

View the log:

```bash
coffee-history            # all entries, oldest -> newest
coffee-history -n 10      # last 10 entries
```

```
2026-08-13 08:02  espresso, double
2026-08-13 09:41  flat white, oat milk
```

Override the log file location (useful for testing) with the `BREWLOG_FILE`
environment variable.
