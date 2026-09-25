"""v0.1.5 Phase 6 (decision D2): a thin analyst page, served by FastAPI.

`GET /analyst` returns one self-contained HTML page (no external scripts,
styles or fonts) that posts a household to `/household/calculate` and shows
each component's status, amount and "why": the deterministic explanation,
calculation steps, caller-asserted facts, and the rates and sources used.
`GET /analyst/examples` lists example requests built from the golden
households in the deployed `policy_specs/`, so a pilot user starts from a
real supported case.

The page only displays what the API returns. It computes nothing.
"""

from __future__ import annotations

from typing import Any

import yaml
from fastapi import APIRouter
from fastapi.responses import HTMLResponse

from poltika.api.accommodation_supplement import AS_POLICY_DIR
from poltika.api.wff import WFF_POLICY_DIR
from poltika.policy.loader import load_policy_spec

router = APIRouter(prefix="/analyst", tags=["analyst"])

# The Task 28.2 scenario-design dates the golden households were calculated
# for (docs/research/2026_09_24_scope_resolution.md): the WFF lookup date,
# and the AS week and lookup date. An analyst can change them in the page.
_WFF_LOOKUP = "2026-06-01"
_AS_WEEK = ("2026-06-01", "2026-06-08")


@router.get("/examples")
def examples() -> list[dict[str, Any]]:
    """Example `/household/calculate` requests, one per golden household."""
    golden = AS_POLICY_DIR.parent / "wff_as_interaction" / "golden_households.yaml"
    if not golden.is_file():
        return []
    wff_version = load_policy_spec(WFF_POLICY_DIR / "policy.yaml").policy_version
    as_version = load_policy_spec(AS_POLICY_DIR / "policy.yaml").policy_version
    requests = []
    for household in yaml.safe_load(golden.read_text())["households"]:
        requests.append(
            {
                "id": household["id"],
                "description": household.get("why", ""),
                "request": {
                    "wff": {**household["wff"], "modelled_date": _WFF_LOOKUP, "requested_policy_version": wff_version},
                    "accommodation_supplement": {
                        **household["accommodation_supplement"],
                        "modelled_date": _AS_WEEK[0],
                        "assessment_week_start": _AS_WEEK[0],
                        "assessment_week_end": _AS_WEEK[1],
                        "requested_policy_version": as_version,
                    },
                    "as_claimant_is_wff_claimant_or_partner": household["precondition"],
                },
            }
        )
    return requests


@router.get("", response_class=HTMLResponse)
def page() -> str:
    return _PAGE


_PAGE = """<!doctype html>
<html lang="en">
<head>
<meta charset="utf-8">
<meta name="viewport" content="width=device-width, initial-scale=1">
<title>Poltika analyst</title>
<link rel="icon" href="data:,">
<style>
  :root { --fg:#1b1f24; --muted:#57606a; --bg:#ffffff; --panel:#f6f8fa; --line:#d0d7de;
          --ok:#1a7f37; --review:#9a6700; --unsup:#cf222e; }
  @media (prefers-color-scheme: dark) {
    :root { --fg:#e6edf3; --muted:#9198a1; --bg:#0d1117; --panel:#161b22; --line:#30363d;
            --ok:#3fb950; --review:#d29922; --unsup:#f85149; }
  }
  body { font: 15px/1.5 system-ui, sans-serif; color: var(--fg); background: var(--bg);
         margin: 0 auto; max-width: 980px; padding: 16px; }
  h1 { font-size: 1.4rem; margin: 0 0 4px; }
  .note { color: var(--muted); font-size: .9rem; }
  textarea { width: 100%; min-height: 220px; font: 13px/1.4 ui-monospace, monospace;
             background: var(--panel); color: var(--fg); border: 1px solid var(--line); box-sizing: border-box; }
  select, button { font: inherit; padding: 4px 10px; }
  .card { border: 1px solid var(--line); border-radius: 6px; margin: 12px 0; padding: 10px 14px; background: var(--panel); }
  .status { display: inline-block; font-weight: 700; padding: 1px 8px; border-radius: 4px;
            border: 2px solid currentColor; font-size: .85rem; letter-spacing: .02em; }
  .calculated { color: var(--ok); } .needs_review { color: var(--review); } .unsupported { color: var(--unsup); }
  .amount { font-size: 1.3rem; font-weight: 700; margin-left: 8px; }
  table { border-collapse: collapse; width: 100%; font-size: .88rem; }
  td, th { border-top: 1px solid var(--line); padding: 4px 6px; text-align: left; vertical-align: top; }
  details { margin-top: 6px; } summary { cursor: pointer; font-weight: 600; }
  .error { color: var(--unsup); white-space: pre-wrap; }
</style>
</head>
<body>
<h1>Poltika analyst</h1>
<p class="note">A conditional simulation from the facts you assert, not an entitlement
determination. Every number shown comes from the API; this page computes nothing.</p>

<p><label>Start from an example household:
  <select id="examples"><option value="">(loading)</option></select></label></p>
<p><label for="request">Household request (JSON, as sent to <code>/household/calculate</code>)</label></p>
<textarea id="request" spellcheck="false"></textarea>
<p><button id="run">Calculate</button> <button id="download" disabled>Download case report (JSON)</button></p>
<div id="error" class="error" role="alert"></div>
<div id="results"></div>

<script>
const LABELS = {family_tax_credit: "Family tax credit", in_work_tax_credit: "In-work tax credit",
  minimum_family_tax_credit: "Minimum family tax credit", best_start: "Best Start",
  accommodation_supplement: "Accommodation Supplement"};
const STATUS_TEXT = {calculated: "CALCULATED", needs_review: "NEEDS REVIEW", unsupported: "UNSUPPORTED"};
let examples = [], lastReport = null;

function el(tag, attrs = {}, ...children) {
  const node = document.createElement(tag);
  for (const [k, v] of Object.entries(attrs)) node.setAttribute(k, v);
  for (const c of children) node.append(c instanceof Node ? c : document.createTextNode(String(c)));
  return node;
}

async function loadExamples() {
  const select = document.getElementById("examples");
  examples = await (await fetch("/analyst/examples")).json();
  select.replaceChildren(el("option", {value: ""}, "(choose)"),
    ...examples.map((e, i) => el("option", {value: i}, e.id)));
  if (examples.length) { select.value = "0"; fill(0); }
}

function fill(i) {
  document.getElementById("request").value = JSON.stringify(examples[i].request, null, 2);
}

function component(id, result, explanation) {
  const card = el("div", {class: "card"});
  const status = el("span", {class: "status " + result.outcome}, STATUS_TEXT[result.outcome]);
  const head = el("div", {}, el("strong", {}, LABELS[id] + " "), status);
  if (result.outcome === "calculated") head.append(el("span", {class: "amount"}, "$" + result.value,
      id === "accommodation_supplement" ? " a week" : " a year"));
  card.append(head, el("p", {}, explanation.summary));
  if (result.code) card.append(el("p", {class: "note"}, "Code: " + result.code +
      (result.category ? " (" + result.category.replace("_", " ") + ")" : "")));
  const why = el("details", {}, el("summary", {}, "Why?"));
  if (explanation.steps.length) {
    const table = el("table", {}, el("tr", {}, el("th", {}, "Step"), el("th", {}, "Rule"), el("th", {}, "What happened")));
    explanation.steps.forEach(s => table.append(el("tr", {}, el("td", {}, s.step_id), el("td", {}, s.rule_id), el("td", {}, s.text))));
    why.append(el("h4", {}, "Calculation"), table);
  }
  if (explanation.assumptions.length) {
    const list = el("ul");
    explanation.assumptions.forEach(a => list.append(el("li", {}, a)));
    why.append(el("h4", {}, "Facts you asserted"), list);
  }
  if (explanation.evidence.length) {
    const table = el("table", {}, el("tr", {}, el("th", {}, "Rate or threshold"), el("th", {}, "Value"),
      el("th", {}, "In force"), el("th", {}, "Source"), el("th", {}, "Status")));
    explanation.evidence.forEach(e => table.append(el("tr", {}, el("td", {}, e.parameter_id),
      el("td", {}, e.value ?? "(none)"), el("td", {}, e.effective_from ? e.effective_from + " to " + (e.effective_to ?? "open") : ""),
      el("td", {}, e.source_id ? e.source_id + ", " + e.locator : ""), el("td", {}, e.review_status ?? ""))));
    why.append(el("h4", {}, "Rates and sources"), table);
  }
  card.append(why);
  return card;
}

async function run() {
  const error = document.getElementById("error"), results = document.getElementById("results");
  error.textContent = ""; results.replaceChildren();
  let body;
  try { body = JSON.parse(document.getElementById("request").value); }
  catch (e) { error.textContent = "The request is not valid JSON: " + e.message; return; }
  const response = await fetch("/household/calculate", {method: "POST",
    headers: {"content-type": "application/json"}, body: JSON.stringify(body)});
  const data = await response.json();
  if (!response.ok) { error.textContent = "HTTP " + response.status + ": " + JSON.stringify(data.detail, null, 2); return; }
  lastReport = data;
  document.getElementById("download").disabled = false;
  results.append(el("p", {class: "note"}, "WFF period " + data.wff_period.join(" to ") +
    "; Accommodation Supplement week " + data.accommodation_supplement_period.join(" to ") +
    ". Result id " + data.result_id + (data.reproducible ? " (reproducible)" : " (not reproducible)") + "."));
  if (data.contradictions.length) {
    const list = el("ul");
    data.contradictions.forEach(c => list.append(el("li", {}, c)));
    results.append(el("div", {class: "card"}, el("strong", {}, "The two policies' facts disagree"), list));
  }
  for (const id of ["family_tax_credit", "in_work_tax_credit", "minimum_family_tax_credit", "best_start"])
    results.append(component(id, data.wff[id], data.explanations[id]));
  results.append(component("accommodation_supplement", data.accommodation_supplement,
    data.explanations.accommodation_supplement));
}

document.getElementById("examples").addEventListener("change", e => { if (e.target.value !== "") fill(+e.target.value); });
document.getElementById("run").addEventListener("click", run);
document.getElementById("download").addEventListener("click", () => {
  const blob = new Blob([JSON.stringify(lastReport, null, 2)], {type: "application/json"});
  const link = el("a", {href: URL.createObjectURL(blob), download: "poltika_case_" + lastReport.result_id.slice(0, 12) + ".json"});
  link.click();
});
loadExamples().catch(e => { document.getElementById("error").textContent = "Could not load examples: " + e; });
</script>
</body>
</html>
"""
