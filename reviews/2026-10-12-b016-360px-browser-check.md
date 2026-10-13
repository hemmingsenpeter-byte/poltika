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
- Correction (follow-up branch `fix/web-a11y-targets-20261012`): the "404 page" measured above was FastAPI's JSON 404 for an unknown path, not a Next page. `api/web.py` falls unknown paths through to the API, so a Next `not-found.tsx` would not be served without a Python change. Skipped; a decision for the owner of `api/web.py`.
- Follow-up on small targets, same branch: header link 83x22-23 to 83x28; provenance buttons 21 to 24px tall; Technical-tab model links 19 to 24px; the household example radios (radios, not checkboxes) 12-13px to 24x24. Chromium 360px re-measure.
- **Open for Pete: a human check on a real phone** (iOS Safari and Android Chrome): the drawer, tab strip swiping,
  scroll regions with a finger, and the browser address-bar resize.

## Re-measure after #210 and #211, 12 October 2026

Reviewer: Claude Code. Basis: branch `fix/followups-2-20261012` (on #211's head `f7313be`, which includes #210's
Task 14 audit-tab manifest). Same setup as above: a static export served by the real FastAPI app against a throwaway
PostgreSQL with the synthetic population, one stored run, viewport 360x740, scale 2, touch on; Playwright 1.49 with
Chromium 1148 and Playwright 1.40 with WebKit 17.4. Every visible link, button, radio, checkbox, tab, select and
`summary` was measured on Home, Scenarios, New scenario (household and policy change), Models, Data and all seven
workspace tabs (13 states per engine). Headless engines, not a phone.

- The #211 targets hold in both engines: header link 28px tall, provenance buttons, Technical-tab links, source links
  and household radios 24px or more.
- Found and fixed here: the Audit tab scrolled sideways (document 475px wide) because the run manifest's notes carry a
  64-character SHA-256 that could not wrap; the note line now has `break-words`. #210 added that block after the
  first check above.
- Found and fixed here: `summary` toggles below 24px: "Check evidence" on the Evidence tab (15px) and "Sources and
  assumptions" on Data (18-19px); "Original settings" on an edited scenario gets the same `min-h-[24px]` (not measured:
  it appears only when editing a stored scenario).
- After the fixes, both engines: no horizontal page scroll in any of the 13 states, and no target under 24px except
  the inline "classic calculator" link inside a sentence (107x16), which SC 2.5.8's inline exception covers.
- Still open for Pete: the real-phone check in the item above.

## Third pass on main, 13 October 2026

Reviewer: Claude Code. Basis: `main` at `7342e52` (after #216), static export served by the real FastAPI app against a
throwaway PostgreSQL 16 with the synthetic population; Playwright 1.49 with **Chromium 131** (build 1148) and
Playwright 1.45 with **WebKit 18.2** (macOS 12's frozen build `webkit_mac12_special-2009`; Playwright 1.49's protocol
does not drive it). Viewport 360x740, scale 2, touch on in Chromium (WebKit's build rejects touch emulation, so plain
360px there). Headless engines, not a phone.

States, both engines: Home, Models, a model page, Data, a dataset page, Scenarios, New scenario, the drawer, the
confirmation panel (policy change with a 72-character title), a stored run's workspace and all seven tabs, and a
two-option WFF compare run whose Overview draws the chart.

- Found and fixed: four `summary` toggles below 24px that the 12 October re-measure's 13 states did not reach:
  "Advanced settings" on the confirmation panel (18-19px, both engines), "Household facts" and "Current parameter
  sources and locators" on the household builder, and the chart's "Show as a table". All four get `min-h-[24px]`, and
  `responsive.test.tsx` now fails if any `<summary>` in `web/src` lacks it (shown to fail before the fix).
- After the fix, both engines, every state: no horizontal page scroll, no element outside the viewport except inside
  a scroller, axe colour-contrast zero violations, no target under 24px. Drawer panel 240px (cap 306px).
- Chart in greyscale print, both engines: solid and diagonal-hatch bars distinguishable; each bar prints its value
  and unit ("$73.3M per tax year", "-$63.1M per tax year"); the chart scrolls inside its region (298px of 540px) while
  the page stays 360px.
- Observation, not fixed (P3, for the owner of `api/web.py`): client-side navigation prefetches the export's RSC
  payload (`<route>.txt?_rsc=`). `WebAppMiddleware` serves `.txt` only at the top level, so `/scenarios/new.txt`
  falls through to the scenario API route (422) and `/models/<id>.txt`, `/data/<id>.txt` 404 (the export holds
  `models/_.txt`). Next falls back to a full page load, so every navigation tested still worked; the cost is a
  failed request and a reload per navigation, plus console errors. Serving the matching export `.txt` would likely
  restore soft navigation (pages read ids from the pathname), but that changes serving and needs its own tests.
- Still open for Pete, unchanged: a human check on a real phone (iOS Safari, Android Chrome).
