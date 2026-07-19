#!/usr/bin/env python3
"""Smoke-test the Liquid template by rendering it the way TRMNL's servers do.

Renders against data/diet-plan.example.json, so the test is deterministic and
passes for everyone regardless of any private data/diet-plan.json. It checks
the template logic (weekday pick, active-slot highlight, item rendering) — the
data itself is interchangeable.

TRMNL renders Liquid on UTC servers and templates localize via
`plus: trmnl.user.utc_offset`, so this test forces TZ=UTC before rendering.
Requires: pip install python-liquid
"""

import os
import time

os.environ["TZ"] = "UTC"
time.tzset()

import datetime as dt
import json
import re
import sys
from pathlib import Path

from liquid import Environment

ROOT = Path(__file__).resolve().parent.parent
sys.path.insert(0, str(ROOT / "scripts"))

from build import TEMPLATE, build_data

IST = 19800  # +05:30

PLAN = json.loads((ROOT / "data" / "diet-plan.example.json").read_text())
DATA = build_data(PLAN)
ENV = Environment()


def render_at(local_str: str) -> str:
    """Render template + example data as if 'now' were the given IST time."""
    local = dt.datetime.strptime(local_str, "%Y-%m-%d %H:%M")
    utc_epoch = int(
        (local - dt.timedelta(seconds=IST)).replace(tzinfo=dt.timezone.utc).timestamp()
    )
    patched = TEMPLATE.replace('"now" | date: "%s"', str(utc_epoch))
    return ENV.from_string(patched).render(
        trmnl={"user": {"utc_offset": IST}}, **DATA
    )


TESTS = [
    # (IST local time, expected weekday, expected active slot prefix, expected item)
    ("2026-07-20 07:00", "Monday", "EARLY", "Warm water"),
    ("2026-07-20 08:30", "Monday", "BREAKFAST", "Oats porridge"),
    ("2026-07-21 13:30", "Tuesday", "LUNCH", "Mixed veg sabzi"),
    ("2026-07-23 17:00", "Thursday", "EVENING", "Roasted makhana"),
    ("2026-07-26 20:00", "Sunday", "DINNER", "Veg curry"),
    ("2026-07-25 23:59", "Saturday", "DINNER", "Roti"),
    ("2026-07-22 00:10", "Wednesday", "EARLY", "Warm water"),
    ("2026-07-24 10:45", "Friday", "MID", "Mixed nuts"),
]


def main() -> int:
    ok = True
    for when, weekday, slot_prefix, must_contain in TESTS:
        out = render_at(when)
        day_ok = f'value--large">{weekday}<' in out
        m = re.search(
            r'bg--yellow[^"]*"[^>]*>\s*<span class="label label--small label--error"[^>]*>([A-Za-z\- ]+)',
            out,
        )
        active = (m.group(1).strip() if m else "NONE").upper()
        slot_ok = active.startswith(slot_prefix)
        item_ok = must_contain in out
        single = out.count("bg--yellow") == 1
        line_ok = day_ok and slot_ok and item_ok and single
        ok = ok and line_ok
        print(
            f"{'ok ' if line_ok else 'FAIL'} {when} -> {weekday:9} active={active:13}"
            f" item={item_ok} single_highlight={single}"
        )
    print("PASS" if ok else "FAIL")
    return 0 if ok else 1


if __name__ == "__main__":
    sys.exit(main())
