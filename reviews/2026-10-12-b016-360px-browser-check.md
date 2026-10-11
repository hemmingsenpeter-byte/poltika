# B0.1.6 real-browser check at 360px (PR #209), 12 October 2026

Reviewer: Claude Code (agent "b016-check"). Basis: branch `feat/b016-responsive-20261011` at `5f1e002`, plus the
small fixes below. This is the check `docs/web/FRONTEND.md` ("jsdom limits") says must be done once in a real
browser before B0.1.6 is accepted.

## What was run, and what it is not

- Static export built from the branch (`npm run build`), served by the real FastAPI app against a real
  PostgreSQL (a throwaway local server), with the synthetic population, so pages show real API data.
- Playwright 1.49 driving headless **Chromium 1148** (Chromium's engine) and Playwright 1.40 driving
  **WebKit 17.4** (the Safari engine, Playwright's build; macOS 12 would not run a newer one). Viewport 360x740, device
  scale 2, touch on.
- At each state: horizontal overflow (`documentElement.scrollWidth`, plus elements poking outside the viewport that
  are not inside a scroller), axe-core 4.14 with **colour-contrast enabled** (the jsdom axe tests have it off), target
  sizes, full-page screenshots, and a second screenshot with `filter: grayscale(1)`.
- This is **automated headless engines, not a person using Chrome or Safari on a device**. It does not cover the
  iOS Safari toolbar and viewport behaviour, real touch use, text-size or zoom settings, or reading the pages by eye.
  Screenshots (outside the repo): `coord/b016-360/` in the session scratchpad; I read about ten by eye.

States covered, both engines: Home, Scenarios list (including an 80-character unbroken title), New scenario (index,
policy change, compare, household), Models, a model page, Data, a dataset page, 404, navigation drawer (open, Escape
closes), a scenario workspace with every one of its 7 tabs (a one-option run, a long-title run, and a two-option compare
run whose Overview draws charts), and the confirmation panel after "Review before running" (policy change and compare,
80-character title). Gap: WebKit's long-title tab sweep did not run in the first pass and the compare run's tabs were
covered instead; the long-title workspace default state passed in both engines.

## Results by check item

| Item | Result |
| --- | --- |
| No horizontal page scroll | Pass after fix, both engines. Before the fix the Scenarios list scrolled sideways (document 731px) with a long unbroken title. The 404 page is Next's stock page (Chromium reports 980px wide); it is not an app page and is out of scope for #209. |
| Header | Pass. Wraps, menu button 44px, "Pilot · synthetic population" pill fits at 360px. |
| Nav drawer | Pass. Opens, stays within 85% of the viewport, labelled, items readable, Escape closes it, no axe findings. |
| Confirmation panel | Pass. Rows stack, long title and labels wrap, no overflow, Run button reachable. |
| Long ids | Pass. Scenario/run ids truncate with a copy button; the 80-character title and 40-character option label wrap (title fixed, see below). |
| Colour contrast | Pass: axe colour-contrast on every app state, both engines, zero violations. Automated contrast sampling does not cover text over gradients or images; there are none here. |
| Chart patterns in greyscale | Pass for what the data gave: a solid bar and a diagonal-hatch bar are clearly distinguishable in greyscale in both engines, and each bar prints its value. Only two options were drawn, so the dots and cross patterns were not seen rendered. |

## Defects found and fixed on the #209 branch

1. Scenarios list: a long unbroken title overflowed the page (`ScenariosPage.tsx`, `min-w-0 break-words`).
2. axe `scrollable-region-focusable` (serious), invisible to the jsdom tests, on `DataTable` (model change log, dataset
   source and variables tables; the chart's table alternative) and the fiscal-years strip. Both are now focusable,
   named `region`s like the chart and `TableBlock` already were. `FRONTEND.md` already claims scrollable regions are
   focusable and named; this makes it true for those two. One test added in `responsive.test.tsx`.

After the fixes: Chromium and WebKit show no horizontal scroll and zero axe violations (colour contrast on) on every
app state above. Web lint, typecheck and vitest: 157 passed.

## Not fixed, for Pete or a later slice

- Small targets measured (below 32px in either dimension): the "POLTIKA" header link (83x22-23), the workspace
  provenance buttons (21px tall), the Technical-tab model links (19px), and the household form's checkboxes (12-13px,
  default size, labelled). WCAG 2.2 AA's 24px minimum is borderline for the first and failed on the provenance buttons
  and links unless their spacing exempts them. Nothing here is a layout break, so I did not restyle.
- The 404 page has no title, `lang`, landmark or heading (axe: 5 findings, both engines); it comes from the Next export.
- **Open for Pete: a human check on a real phone** (iOS Safari and Android Chrome): the drawer, tab strip swiping,
  scroll regions with a finger, and the browser address-bar resize.
