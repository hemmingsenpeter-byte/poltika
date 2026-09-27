"""v0.2 Task 10.2: the population analyst page, `GET /analyst/microsim`.

One self-contained HTML page (no external scripts, styles or fonts). It
picks a parameter from `/microsim/parameters`, posts a reform to
`/microsim/runs`, and shows the result in tabs: Overview, Distribution,
Households, Areas, Fiscal, Evidence and Methodology. The population's
label is shown on every tab. Like the household page, it computes nothing,
and every number comes from the API.
"""

from __future__ import annotations

from fastapi import APIRouter
from fastapi.responses import HTMLResponse

router = APIRouter(prefix="/analyst", tags=["analyst"])


@router.get("/microsim", response_class=HTMLResponse)
def page() -> str:
    return _PAGE


_PAGE = """<!doctype html>
<html lang="en">
<head>
<meta charset="utf-8">
<meta name="viewport" content="width=device-width, initial-scale=1">
<title>Poltika population runs</title>
<link rel="icon" href="data:,">
<style>
  :root { --fg:#1b1f24; --muted:#57606a; --bg:#ffffff; --panel:#f6f8fa; --line:#d0d7de; --warn:#9a6700; --bad:#cf222e; }
  @media (prefers-color-scheme: dark) {
    :root { --fg:#e6edf3; --muted:#9198a1; --bg:#0d1117; --panel:#161b22; --line:#30363d; --warn:#d29922; --bad:#f85149; }
  }
  body { font: 15px/1.5 system-ui, sans-serif; color: var(--fg); background: var(--bg);
         margin: 0 auto; max-width: 1080px; padding: 16px; }
  h1 { font-size: 1.4rem; margin: 0 0 4px; }
  .note { color: var(--muted); font-size: .9rem; }
  .label { border: 2px solid var(--warn); color: var(--warn); font-weight: 700; padding: 4px 10px; border-radius: 6px; margin: 8px 0; }
  .card { border: 1px solid var(--line); border-radius: 6px; margin: 12px 0; padding: 10px 14px; background: var(--panel); }
  select, input, button { font: inherit; padding: 3px 8px; background: var(--bg); color: var(--fg); border: 1px solid var(--line); border-radius: 4px; }
  table { border-collapse: collapse; width: 100%; font-size: .88rem; }
  td, th { border-top: 1px solid var(--line); padding: 4px 6px; text-align: left; vertical-align: top; }
  td.n { text-align: right; font-variant-numeric: tabular-nums; }
  .tabs button { margin: 0 4px 4px 0; } .tabs button[aria-selected=true] { font-weight: 700; border-color: var(--fg); }
  .error { color: var(--bad); white-space: pre-wrap; }
  pre { white-space: pre-wrap; font: 13px/1.4 ui-monospace, monospace; }
  .grid { display: grid; grid-template-columns: repeat(auto-fit, minmax(200px, 1fr)); gap: 8px; align-items: end; }
  .grid select, .grid input { width: 100%; box-sizing: border-box; }
  .grid .wide { grid-column: 1 / -1; }
</style>
</head>
<body>
<h1>Poltika population runs</h1>
<p class="note">Static first-order results: every valid household is run through the v0.1 engines under the
baseline and the reform. Costs are entitlement at full take-up, not expenditure. This page computes nothing.</p>
<div id="population" class="card">Loading population...</div>

<div class="card">
  <div class="grid">
    <label class="wide">Parameter<br><select id="parameter"></select></label>
    <label>Operation<br><select id="operation"><option>set</option><option>add</option><option>multiply</option></select></label>
    <label>Value<br><input id="value" type="text" inputmode="decimal"></label>
    <label>Measure<br><select id="components">
      <option value="family_tax_credit">family tax credit (per tax year)</option>
      <option value="best_start">Best Start (per tax year)</option>
      <option value="family_tax_credit,in_work_tax_credit,minimum_family_tax_credit,best_start">all WFF components (per tax year)</option>
      <option value="accommodation_supplement">Accommodation Supplement (per week)</option>
    </select></label>
    <button id="run">Run</button>
  </div>
  <p id="baseline" class="note"></p>
  <div id="error" class="error"></div>
</div>

<div id="result" hidden>
  <div class="label" id="result-label"></div>
  <div class="tabs" role="tablist"></div>
  <div id="panel" class="card"></div>
</div>

<script>
const $ = (id) => document.getElementById(id);
const esc = (s) => String(s ?? "").replace(/[&<>"]/g, (c) => ({"&":"&amp;","<":"&lt;",">":"&gt;",'"':"&quot;"}[c]));
const money = (s) => s == null ? "" : Number(s).toLocaleString(undefined, {minimumFractionDigits: 2, maximumFractionDigits: 2});
let params = [], last = null;

async function init() {
  const pop = await fetch("/microsim/population");
  if (!pop.ok) { $("population").innerHTML = `<span class="error">${esc((await pop.json()).detail)}</span>`; return; }
  const p = await pop.json();
  $("population").innerHTML = (p.synthetic ? `<div class="label">${esc(p.label)}</div>` : "") +
    `<b>${esc(p.population_id)}</b> v${p.version}: ${p.households} households, total weight ${money(p.total_weight)}.
     <span class="note">sha256 ${esc(p.content_sha256)}</span>`;
  params = (await (await fetch("/microsim/parameters")).json());
  $("parameter").innerHTML = params.map((r, i) =>
    `<option value="${i}">${esc(r.policy_id)} / ${esc(r.parameter_id)} (${esc(r.modelled_date)})</option>`).join("");
  $("parameter").onchange = showBaseline; showBaseline();
}

function showBaseline() {
  const r = params[$("parameter").value]; if (!r) return;
  $("baseline").textContent = `Baseline: ${r.outcome === "resolved" ? r.value + " " + r.unit + " from " + r.source_id : r.outcome}.`;
}

$("run").onclick = async () => {
  const r = params[$("parameter").value]; $("error").textContent = "";
  const body = { reform: { reform_id: `${r.parameter_id} ${$("operation").value} ${$("value").value}`,
    overrides: [{ policy_id: r.policy_id, parameter_id: r.parameter_id, operation: $("operation").value, value: $("value").value }] },
    component_set: $("components").value.split(",") };
  $("run").disabled = true;
  try {
    const res = await fetch("/microsim/runs", { method: "POST", headers: {"content-type": "application/json"}, body: JSON.stringify(body) });
    const data = await res.json();
    if (!res.ok) { $("error").textContent = typeof data.detail === "string" ? data.detail : JSON.stringify(data.detail, null, 2); return; }
    last = data; render("Overview");
  } finally { $("run").disabled = false; }
};

const TABS = ["Overview", "Distribution", "Households", "Areas", "Fiscal", "Evidence", "Methodology"];

function render(tab) {
  $("result").hidden = false;
  $("result-label").textContent = last.synthetic ? last.label : "";
  $("result-label").hidden = !last.synthetic;
  document.querySelector(".tabs").innerHTML = TABS.map((t) =>
    `<button role="tab" aria-selected="${t === tab}" onclick="render('${t}')">${t}</button>`).join("");
  $("panel").innerHTML = ({
    Overview: () => summaryTable("All households", last.tables.overall) + `<h3>Explanation</h3><pre>${esc(last.explanation)}</pre>` +
      (last.explanation_problems.length ? `<p class="error">Explanation check failed: ${esc(last.explanation_problems.join("; "))}</p>` : ""),
    Distribution: () => summaryTable("By gross household income decile", last.tables.decile),
    Households: () => summaryTable("By household type", last.tables.household_type) + summaryTable("By dependent children", last.tables.children),
    Areas: () => summaryTable("By Accommodation Supplement area", last.tables.as_area) + summaryTable("By region", last.tables.region),
    Fiscal: fiscal,
    Evidence: evidence,
    Methodology: methodology,
  })[tab]();
}

function summaryTable(title, t) {
  const rows = Object.entries(t.groups).map(([g, s]) => `<tr><td>${esc(g)}</td><td class="n">${money(s.weight)}</td>
    <td class="n">${money(s.by_class.gain)}</td><td class="n">${money(s.by_class.loss)}</td><td class="n">${money(s.by_class.no_change)}</td>
    <td class="n">${money(s.by_class.needs_review)}</td><td class="n">${money(s.by_class.unsupported)}</td>
    <td class="n">${money(s.mean_gain)}</td><td class="n">${money(s.total_change)}</td></tr>`).join("");
  const left = Object.entries(t.left_out || {}).map(([k, w]) => `${esc(k)}: weight ${money(w)}`).join("; ");
  return `<h3>${esc(title)}</h3><p class="note">${esc(t.component_set.join(" + "))}, ${esc(t.unit)}.
    Weights are households represented. Needs-review and unsupported households are never counted as zero.</p>
    <table><tr><th>Group</th><th>Weight</th><th>Gain</th><th>Loss</th><th>No change</th><th>Needs review</th><th>Unsupported</th>
    <th>Mean gain</th><th>Total change</th></tr>${rows}</table>${left ? `<p class="note">Left out: ${left}</p>` : ""}`;
}

function fiscal() {
  const rows = Object.values(last.fiscal).map((f) => `<tr><td>${esc(f.component)}</td><td>${esc(f.unit)}</td>
    <td class="n">${money(f.baseline_total)}</td><td class="n">${money(f.reform_total)}</td><td class="n">${money(f.delta_total)}</td>
    <td class="n">${money(f.coverage.calculated)}</td><td class="n">${money(f.coverage.needs_review)}</td><td class="n">${money(f.coverage.unsupported)}</td></tr>`).join("");
  return `<p class="note">Static entitlement at full take-up, not expenditure. Totals cover only households calculated in both runs.
    WFF (per tax year) and the Accommodation Supplement (per week) are never added together.</p>
    <table><tr><th>Component</th><th>Unit</th><th>Baseline</th><th>Reform</th><th>Change</th>
    <th>Calculated weight</th><th>Needs review</th><th>Unsupported</th></tr>${rows}</table>${ranges()}`;
}

// v0.3 Task 1b.6: what can be said about needs-review households, kept apart
// from the calculated totals above and never added to them.
function ranges() {
  if (!last.fiscal_ranges) return "";
  const rows = Object.values(last.fiscal_ranges).map((r) => `<tr><td>${esc(r.component)}</td><td>${esc(r.unit)}</td>
    <td class="n">${money(r.calculated_delta)}</td>
    <td class="n">${r.bounded_households ? money(r.delta_low) + " to " + money(r.delta_high) : "none"}</td>
    <td class="n">${money(r.bounded_weight)} (${r.bounded_households})</td>
    <td class="n">${money(r.unboundable_weight)}</td></tr>`).join("");
  return `<h3>Needs-review households</h3><p class="note">For households waiting on a fact, Poltika reruns each possible
    answer. Where every answer is calculated, the household's lowest and highest change give a range. The rest are
    unboundable (a missing amount, a rate still under review, or an answer that isn't modelled). These three figures are
    separate: the range is never added to the calculated change.</p>
    <table><tr><th>Component</th><th>Unit</th><th>Calculated change</th><th>Range of change (bounded households)</th>
    <th>Bounded weight (households)</th><th>Unboundable weight</th></tr>${rows}</table>`;
}

function evidence() {
  const o = last.overridden.map((x) => `<tr><td>${esc(x.policy_id)}.${esc(x.parameter_id)}</td><td>${esc(x.baseline_value)}</td>
    <td>${esc(x.baseline_source_id)}</td><td>${esc(x.baseline_locator)}</td><td>${esc(x.reform_value)} (scenario assumption)</td></tr>`).join("");
  const a = last.policy_artifacts.map(([p, h]) => `<tr><td>${esc(p)}</td><td><code>${esc(h)}</code></td></tr>`).join("");
  return `<h3>What the reform changed</h3><table><tr><th>Parameter</th><th>Baseline</th><th>Source</th><th>Locator</th><th>Reform</th></tr>${o}</table>
    <h3>Policy files the run was bound to</h3><table>${a}</table>`;
}

function methodology() {
  const v = Object.entries(last.validation).map(([s, [n, w]]) => `<tr><td>${esc(s)}</td><td class="n">${n}</td><td class="n">${money(w)}</td></tr>`).join("");
  return `<h3>Reproducibility</h3><table>
    <tr><td>run_id</td><td><code>${esc(last.run_id)}</code></td></tr>
    <tr><td>results_sha256</td><td><code>${esc(last.results_sha256)}</code></td></tr>
    <tr><td>population</td><td>${esc(last.population.id)} v${last.population.version}, <code>${esc(last.population.sha256)}</code></td></tr>
    <tr><td>reform_sha256</td><td><code>${esc(last.reform_sha256)}</code></td></tr>
    <tr><td>code</td><td>${esc(JSON.stringify(last.code))}</td></tr></table>
    <h3>Population records</h3><table><tr><th>Status</th><th>Households</th><th>Weight</th></tr>${v}</table>
    <p class="note">Invalid households are not run. A needs-review record gets needs-review results. Static and first-order:
    no behavioural response, take-up modelling, income tax or other benefits. Rerunning the same reform on the same
    population and code gives the same run_id and results_sha256.</p>`;
}

init();
</script>
</body>
</html>
"""
