# diet-trmnl

A 7-day rotating diet/meal plan as a [TRMNL](https://trmnl.com) private
plugin, built for the TRMNL OG B/W/R/Y e-ink display (800x480, framework v3).

The screen shows **today's full day at a glance** — six meal slots (early
morning, breakfast, mid-morning, lunch, evening, dinner) with household-measure
portions — and highlights the current meal slot in yellow with a red chip.
Day 1 = Monday … Day 7 = Sunday, repeating weekly. A legend strip explains the
household measures.

Markup and data are fully separated:

- `dist/markup.liquid` — a ~2 KB generic Liquid template, pasted once.
- `dist/data.json` — the meal plan as merge variables (Static Data or polled).

## Privacy

Personal meal data is **gitignored** (`data/diet-plan.json`, `dist/data.json`,
`preview/index.html`, `data/PLAN-NOTES.private.md`). The repo only ships
[`data/diet-plan.example.json`](data/diet-plan.example.json) with dummy meals —
your real plan lives only in your local `data/diet-plan.json` and on TRMNL,
never in git.

## Enter your own plan

Copy the example and edit it — it is the single source of truth:

```bash
cp data/diet-plan.example.json data/diet-plan.json
```

`data/diet-plan.json` has three top-level keys:

- **`meta`** — display strings shown on every screen:
  - `title` — title-bar text (e.g. `"Diet Plan"`).
  - `reminders` — one short line shown top-right (e.g.
    `"3 L water/day · 60-min walk"`).
  - `legend` — the household-measures strip (e.g.
    `"1 cup = 200 ml · 1 bowl = 250 ml"`).
  - `notes` / `day_mapping` — for your own reference; not rendered.
- **`slots`** — the meal slots, in display order. Each has a `key` (referenced
  by every day's `meals`), a display `name` and `time`, and `start` — the
  local wall-clock time as an HMM/HHMM integer (`0` = midnight, `800` = 8:00,
  `1930` = 19:30) from which that slot is highlighted. The slot whose `start`
  was passed most recently is the active one. Add or remove slots freely; the
  grid is 3 columns, so 6 slots fill it nicely.
- **`days`** — exactly 7 entries, `day` 1–7 with `weekday` Monday–Sunday
  (Day 1 = Monday; the plan repeats weekly). Each has `kcal` (a number,
  shown as "~1,500 kcal") and `meals`: a map from slot `key` to a list of
  `{"food": "...", "portion": "..."}` items. Keep foods to a few words and
  portions in household measures so rows fit the e-ink screen.

Then build and check it locally:

```bash
python3 scripts/build.py     # regenerates dist/data.json + preview/index.html
```

Without a `data/diet-plan.json`, the build falls back to the example file, so
you can try everything with dummy data first.

## Install on the TRMNL

1. Make sure your timezone is set correctly in your TRMNL account
   (the template uses `trmnl.user.utc_offset` to pick the day and meal slot).
2. On [trmnl.com](https://trmnl.com): **Plugins → Private Plugin → Add New**.
3. Name it (e.g. "Diet Plan"), choose **Strategy: Static Data**, and paste the
   contents of `dist/data.json` into the Static Data field. Save.
4. Open **Edit Markup**, paste the contents of
   [`dist/markup.liquid`](dist/markup.liquid) into the **Full** layout, save.
5. Add the plugin to your playlist. Done — it re-renders on your device's
   refresh schedule, so the highlighted slot advances through the day.

Alternative: host `dist/data.json` anywhere (e.g. a private GitHub raw URL or
gist) and use **Strategy: Polling** with that URL — same merge variables, and
the device picks up plan changes on its own.

## Updating the plan later

Edit `data/diet-plan.json`, run `python3 scripts/build.py`, then re-paste
**only `dist/data.json`** into the plugin's Static Data field (or push, if you
use polling). The markup stays untouched.

## Preview locally

```bash
pip install python-liquid    # preview renders through the real template
python3 scripts/build.py
python3 -m http.server 8321
# open http://localhost:8321/preview/index.html
```

The preview pins the exact 800x480 screen with TRMNL's framework CSS and
fonts (vendored into `preview/vendor/`, gitignored) and has controls to switch
the day and simulate the time of day. Screens are rendered through the real
Liquid template, so the preview cannot drift from what the device shows.

## Test

```bash
pip install python-liquid
python3 scripts/test_markup.py
```

Renders the template at eight simulated wall-clock times and asserts the
correct weekday, exactly one highlighted slot, and expected foods. The test
always runs against `data/diet-plan.example.json`, so it passes regardless of
your private plan — it verifies the template logic, not your data. (TRMNL
renders on UTC servers; the test forces `TZ=UTC` to match.)
