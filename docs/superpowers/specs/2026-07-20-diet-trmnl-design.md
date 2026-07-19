# Diet Plan on TRMNL OG — Design

Date: 2026-07-20
Status: Approved (delivery, day-mapping, and layout chosen by the user via Q&A)

## Goal

Show "what to prepare today" from a doctor-prescribed 7-day diet plan on a
TRMNL OG e-ink display (800x480, 4-color B/W/R/Y), glanceable from across the
kitchen, with zero ongoing maintenance.

## Decisions

1. **Delivery: TRMNL Private Plugin (Liquid markup, no polling).**
   All 7 days of data are embedded in the markup itself; Liquid picks the
   day at render time. No hosting, no endpoint, nothing to keep alive.
2. **Day mapping: weekday-based.** Day 1 = Monday … Day 7 = Sunday,
   repeating weekly (doctor's plan repeats until weight plateau).
3. **Layout: full day at a glance.** All meal slots (early morning, breakfast,
   mid-morning, lunch, evening snack, dinner) in a grid with household-measure
   portions. Red/yellow accents highlight the current/upcoming meal slot and
   key daily rules (3L water, 60-min walk).

## Data source

The doctor's diet prescription PDF (7 day-sheets, one per weekday).
Portions shown in household measures (cups/bowls/no.) per the dietitian's
instruction — gram quantities are for calculation only and are omitted.
Abbreviations expanded (Slad with lme → Salad with lime, Snd vege → Seasoned
vegetables, etc.). Daily calorie total shown per day as a footer stat.

## Components

- `data/diet-plan.json` — structured 7-day plan (source of truth, human-editable)
- `src/markup.liquid` — the private plugin markup (data embedded, generated
  from JSON by `scripts/build.py` so the JSON stays the single source of truth)
- `preview/index.html` — local 800x480 preview harness using TRMNL's hosted
  framework CSS, for visual verification before pasting into trmnl.com
- `README.md` — how to create the private plugin and paste the markup

## Error handling / edge cases

- Timezone: use TRMNL's user timezone variable if available (verify in docs),
  fallback to IST; day boundary at local midnight.
- Meal highlight is based on render time; TRMNL refreshes on its own schedule,
  so the highlight may lag by one refresh interval — acceptable.
- 4-color support: verify framework color classes for B/W/R/Y devices; if the
  framework build on the device is B/W-only, design must degrade gracefully
  (accents become black fills).

## Testing

Browser preview at exactly 800x480 with the TRMNL framework CSS; screenshot
check for overflow/legibility for the densest day (Day 2 has 20 items).
