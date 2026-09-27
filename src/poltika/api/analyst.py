"""v0.1.5 Phase 6 (decision D2): a thin analyst page, served by FastAPI.

`GET /analyst` returns one self-contained HTML page (no external scripts,
styles or fonts) that posts a household to `/household/calculate` and shows
each component's status, amount and "why": the deterministic explanation,
calculation steps, caller-asserted facts, and the rates and sources used.

v0.3 Task 1b.5 (ADR-0016): "Ask me first" drives `/household/intake`. It
asks the catalogue's questions one at a time, accepts "don't know", and
then shows the result. When facts are still missing, the page shows the
API's conditional answer: each branch, the ranges, and the next question.
The page writes no question or answer of its own: every question and
answer label is the catalogue's, and every figure is the API's.
`GET /analyst/examples` lists example requests built from the golden
households in the deployed `policy_specs/`, so a pilot user starts from a
real supported case.

The page only displays what the API returns. It computes nothing.
"""

from __future__ import annotations

import copy
from typing import Any

import yaml
from fastapi import APIRouter
from fastapi.responses import HTMLResponse

from poltika.api.accommodation_supplement import AS_POLICY_DIR
from poltika.api.wff import WFF_POLICY_DIR
from poltika.engines.assurance.evidence import evidence_coverage
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


# v0.1.5 Sprint 2 (S2.2): the pilot case pack. Each case is a golden
# household with named facts changed, and a question for the pilot user.
# It fixes inputs only; every answer comes from Poltika. Paths are
# (section, field) or (section, field, subfield); None means not supplied.
_PILOT_CASES: tuple[tuple[str, str, str, dict[tuple[str, ...], Any]], ...] = (
    ("p01_couple_two_children", "g2_couple_two_children_income_abated_both",
     "Where does each number come from? Pick one and trace it to its source.", {}),
    ("p02_sole_parent_two_children", "g1_sole_parent_two_children_non_beneficiary",
     "Which facts did Poltika take from you, and which did it check?", {}),
    ("p03_single_jobseeker_cap", "g4_single_jobseeker_cap_binds",
     "Why is the Accommodation Supplement not 70% of the costs over the threshold?", {}),
    ("p04_supported_living_couple", "g5_supported_living_couple_two_children",
     "Why is there no Working for Families total?", {}),
    ("p05_best_start_child", "g6_sole_parent_support_best_start_child",
     "Which rule gives the Best Start amount?", {}),
    ("p06_asset_imputation", "g7_sole_parent_asset_imputation_and_income_reduction",
     "How do cash assets change the Accommodation Supplement?", {}),
    ("p07_partner_income_unknown", "g2_couple_two_children_income_abated_both",
     "The partner's income is not supplied. What can and can't Poltika say?",
     {("wff", "family_scheme_income", "partner_amount"): None}),
    ("p08_children_disagree", "g2_couple_two_children_income_abated_both",
     "The two policies are told different numbers of children. What happens?",
     {("accommodation_supplement", "dependent_children_count"): 3}),
    ("p09_assets_over_ceiling", "g1_sole_parent_two_children_non_beneficiary",
     "Cash assets are $20,000. Is this 'not entitled' or 'not modelled'?",
     {("accommodation_supplement", "cash_assets"): "20000"}),
    ("p10_homeowner", "g1_sole_parent_two_children_non_beneficiary",
     "The household owns its home. What does Poltika tell you?",
     {("accommodation_supplement", "tenure_type"): "homeowner"}),
    ("p11_area_unknown", "g4_single_jobseeker_cap_binds",
     "The area is not known. Why doesn't Poltika assume one?",
     {("accommodation_supplement", "statistical_area_unit"): None}),
    ("p12_high_income", "g2_couple_two_children_income_abated_both",
     "Income is $150,000. Which credits abate to zero, and how can you tell?",
     {("wff", "family_scheme_income", "claimant_amount"): "130000"}),
    ("p13_main_benefit_payment", "g2_couple_two_children_income_abated_both",
     "A main benefit was received during the year. Which credits does it affect?",
     {("wff", "mc6b_disqualifying_payment"): "excluded"}),
    ("p14_no_accommodation_costs", "g1_sole_parent_two_children_non_beneficiary",
     "There are no accommodation costs. Why is that not a calculated $0?",
     {("accommodation_supplement", "weekly_accommodation_costs"): "0"}),
    ("p15_claimant_link_unverified", "g2_couple_two_children_income_abated_both",
     "It isn't verified that the AS claimant is in the WFF family. What changes?",
     {("as_claimant_is_wff_claimant_or_partner",): "unknown"}),
)


def _with(request: dict[str, Any], changes: dict[tuple[str, ...], Any]) -> dict[str, Any]:
    changed = copy.deepcopy(request)
    for path, value in changes.items():
        target = changed
        for key in path[:-1]:
            target = target[key]
        target[path[-1]] = value
    return changed


@router.get("/pilot-cases")
def pilot_cases() -> list[dict[str, Any]]:
    """The pilot case pack (v0.1.5 S2.2): 15 households spanning every
    outcome, each with a question for the pilot user."""
    golden = {e["id"]: e["request"] for e in examples()}
    return [
        {"id": case_id, "description": question, "request": _with(golden[base], changes)}
        for case_id, base, question, changes in _PILOT_CASES
        if base in golden
    ]


@router.get("/evidence")
def evidence() -> list[dict[str, Any]]:
    """v0.1.5 Phase 1: each deployed policy's evidence coverage summary and
    any gaps, so a pilot user can see what the numbers rest on."""
    reports = [evidence_coverage(d) for d in (WFF_POLICY_DIR, AS_POLICY_DIR)]
    return [{k: r[k] for k in ("policy_id", "policy_version", "summary", "problems")} for r in reports]


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
  fieldset { border: 1px solid var(--line); border-radius: 6px; margin: 8px 0; padding: 6px 10px; }
  legend { font-weight: 600; padding: 0 4px; }
  .field { display: grid; grid-template-columns: minmax(180px, 40%) 1fr; gap: 8px; align-items: center; margin: 3px 0; }
  .field input[type=text], .field select { font: inherit; padding: 2px 4px; background: var(--bg); color: var(--fg);
    border: 1px solid var(--line); border-radius: 4px; max-width: 100%; }
  @media (max-width: 600px) { .field { grid-template-columns: 1fr; } }
  .ask { border: 2px solid var(--review); }
  .ask h3 { margin: 0 0 6px; font-size: 1.05rem; }
  .ask label.option { display: block; margin: 4px 0; }
  .ask input[type=text] { font: inherit; padding: 2px 6px; background: var(--bg); color: var(--fg);
    border: 1px solid var(--line); border-radius: 4px; }
  .pill { display: inline-block; border: 1px solid var(--line); border-radius: 10px; padding: 0 8px;
          margin: 2px 4px 2px 0; font-size: .82rem; }
  .scroll { overflow-x: auto; }
</style>
</head>
<body>
<h1>Poltika analyst</h1>
<p class="note">A conditional simulation from the facts you assert, not an entitlement
determination. Every number shown comes from the API; this page computes nothing.</p>

<p><label>Start from an example household:
  <select id="examples"><option value="">(loading)</option></select></label></p>
<p id="question" class="note"></p>
<div id="form"></div>
<details><summary>Edit as JSON</summary>
<p><label for="request">Household request, as sent to <code>/household/calculate</code></label></p>
<textarea id="request" spellcheck="false"></textarea>
<p><button id="apply-json">Apply JSON to the form</button></p>
</details>
<p><button id="ask-first">Ask me first</button> <button id="run">Calculate</button>
  <button id="download" disabled>Download case report (JSON)</button></p>
<p class="note">"Ask me first" asks for any fact the calculation is missing, one question at a
time. Answer "Don't know" to skip one: Poltika then shows what it can say without it.</p>
<div id="ask"></div>
<p id="evidence" class="note"></p>
<div id="error" class="error" role="alert"></div>
<div id="results"></div>

<script>
const LABELS = {family_tax_credit: "Family tax credit", in_work_tax_credit: "In-work tax credit",
  minimum_family_tax_credit: "Minimum family tax credit", best_start: "Best Start",
  accommodation_supplement: "Accommodation Supplement"};
const STATUS_TEXT = {calculated: "CALCULATED", needs_review: "NEEDS REVIEW", unsupported: "UNSUPPORTED"};
let examples = [], lastReport = null;
let intake = null;  // {answers: [], declined: []} while asking

function el(tag, attrs = {}, ...children) {
  const node = document.createElement(tag);
  for (const [k, v] of Object.entries(attrs)) node.setAttribute(k, v);
  for (const c of children) node.append(c instanceof Node ? c : document.createTextNode(String(c)));
  return node;
}

async function loadExamples() {
  schemas = (await (await fetch("/openapi.json")).json()).components.schemas;
  const select = document.getElementById("examples");
  const pilot = await (await fetch("/analyst/pilot-cases")).json();
  const golden = await (await fetch("/analyst/examples")).json();
  examples = [...pilot.map(e => ({...e, id: "Pilot: " + e.id})), ...golden.map(e => ({...e, id: "Golden: " + e.id}))];
  select.replaceChildren(el("option", {value: ""}, "(choose)"),
    ...examples.map((e, i) => el("option", {value: i}, e.id)));
  if (examples.length) { select.value = "0"; fill(0); }
}

let schemas = {}, request = null;

function fill(i) {
  document.getElementById("question").textContent = examples[i].description;
  request = structuredClone(examples[i].request);
  syncJson(); renderForm();
}

function syncJson() { document.getElementById("request").value = JSON.stringify(request, null, 2); }

function resolve(schema) {
  while (schema && schema.$ref) schema = schemas[schema.$ref.split("/").pop()];
  return schema || {};
}

// A property schema, its non-null variant, and whether null is allowed.
function variant(schema) {
  if (!schema.anyOf) return {base: resolve(schema), nullable: false};
  const options = schema.anyOf.filter(o => o.type !== "null");
  const text = options.find(o => o.type === "string" && !o.format) || options[0];
  return {base: resolve(options.find(o => o.$ref) || text), nullable: options.length < schema.anyOf.length};
}

// The property's own title, or its name -- never a referenced model's class
// name (e.g. "VerifiedIncomeRequest").
function label(key, schema) {
  const text = schema.$ref ? String(key) : (schema.title || String(key));
  const words = text.replace(/_/g, " ");
  return words.charAt(0).toUpperCase() + words.slice(1);
}

function setAt(path, value) {
  let target = request;
  for (const key of path.slice(0, -1)) target = target[key];
  target[path[path.length - 1]] = value;
  syncJson();
}

function field(key, schema, value, path) {
  const {base, nullable} = variant(schema);
  if (base.properties) {
    const box = el("fieldset", {}, el("legend", {}, label(key, schema)));
    if (nullable) {
      const toggle = el("input", {type: "checkbox"});
      toggle.checked = value === null || value === undefined;
      toggle.addEventListener("change", () => {
        setAt(path, toggle.checked ? null : Object.fromEntries(Object.keys(base.properties).map(k => [k, null])));
        renderForm();
      });
      box.append(el("label", {}, toggle, " not supplied"));
      if (value === null || value === undefined) return box;
    }
    for (const [k, s] of Object.entries(base.properties)) box.append(field(k, s, value[k], [...path, k]));
    return box;
  }
  if (base.type === "array") {
    const itemSchema = resolve(base.items);
    const box = el("fieldset", {}, el("legend", {}, label(key, schema) + " (" + value.length + ")"));
    value.forEach((item, i) => {
      const inner = field(key + " " + (i + 1), base.items, item, [...path, i]);
      const remove = el("button", {type: "button"}, "Remove");
      remove.addEventListener("click", () => { value.splice(i, 1); syncJson(); renderForm(); });
      inner.append(remove);
      box.append(inner);
    });
    const add = el("button", {type: "button"}, "Add");
    add.addEventListener("click", () => {
      const fresh = value.length ? structuredClone(value[value.length - 1])
        : Object.fromEntries(Object.entries(itemSchema.properties || {}).map(([k, s]) => [k, s.default ?? "unknown"]));
      value.push(fresh); syncJson(); renderForm();
    });
    box.append(add);
    return box;
  }
  const row = el("label", {class: "field"}, label(key, schema));
  let input;
  if (base.enum) {
    input = el("select");
    if (nullable) input.append(el("option", {value: ""}, "(not supplied)"));
    base.enum.forEach(v => input.append(el("option", {value: v}, v)));
    input.value = value ?? "";
    input.addEventListener("change", () => setAt(path, input.value === "" ? null : input.value));
  } else if (base.type === "boolean") {
    input = el("input", {type: "checkbox"});
    input.checked = !!value;
    input.addEventListener("change", () => setAt(path, input.checked));
  } else {
    input = el("input", {type: "text", placeholder: nullable ? "(not supplied)" : ""});
    input.value = value ?? "";
    input.addEventListener("change", () => {
      const text = input.value.trim();
      if (text === "") { setAt(path, nullable ? null : ""); return; }
      setAt(path, base.type === "integer" ? Number(text) : text);
    });
  }
  row.append(input);
  return row;
}

function renderForm() {
  const root = resolve({$ref: "#/components/schemas/HouseholdCalculationRequest"});
  const form = document.getElementById("form");
  form.replaceChildren(...Object.entries(root.properties).map(([k, s]) => field(k, s, request[k], [k])));
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

function currentRequest() {
  return request ?? JSON.parse(document.getElementById("request").value);
}

async function post(url, body) {
  const response = await fetch(url, {method: "POST",
    headers: {"content-type": "application/json"}, body: JSON.stringify(body)});
  const data = await response.json();
  if (!response.ok) throw new Error("HTTP " + response.status + ": " + JSON.stringify(data.detail, null, 2));
  return data;
}

async function run() {
  const error = document.getElementById("error");
  error.textContent = ""; document.getElementById("results").replaceChildren();
  intake = null; document.getElementById("ask").replaceChildren();
  let body;
  try { body = currentRequest(); }
  catch (e) { error.textContent = "The request is not valid JSON: " + e.message; return; }
  try { show(await post("/household/calculate", body)); }
  catch (e) { error.textContent = e.message; }
}

function money(value, id) {
  if (value === null || value === undefined) return "";
  return "$" + value + (id === "accommodation_supplement" ? " a week" : " a year");
}

function show(data) {
  const results = document.getElementById("results");
  results.replaceChildren();
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
  if (data.resolution) results.append(conditional(data.resolution));
  for (const id of ["family_tax_credit", "in_work_tax_credit", "minimum_family_tax_credit", "best_start"])
    results.append(component(id, data.wff[id], data.explanations[id]));
  results.append(component("accommodation_supplement", data.accommodation_supplement,
    data.explanations.accommodation_supplement));
}

// ADR-0016: what the API can say without the missing facts. Every figure is
// the API's; the page only lays it out.
function conditional(res) {
  const card = el("div", {class: "card"});
  card.append(el("strong", {}, "What Poltika can say without the missing facts"));
  const missing = el("ul");
  res.missing.forEach(m => missing.append(el("li", {}, m.question + " ",
    el("span", {class: "note"}, "(" + m.fact + "; rule " + m.rule + (m.blocks.length ? "; needed for " +
      m.blocks.map(b => LABELS[b] || b).join(", ") : "") + ")"))));
  card.append(el("p", {}, "Poltika can't give one figure without these facts:"), missing);
  if (res.summary && res.summary.length > 1) {
    const said = el("details", {}, el("summary", {}, "In words"));
    res.summary.slice(1).forEach(t => said.append(el("p", {}, t)));
    card.append(said);
  }
  // Only the components a missing fact blocks; the others are as shown below.
  const blocked = new Set(res.missing.flatMap(m => m.blocks));
  const wff = ["family_tax_credit", "in_work_tax_credit", "minimum_family_tax_credit", "best_start"];
  if (wff.some(id => blocked.has(id))) blocked.add("wff_total");
  const ranged = Object.entries(res.bounds).filter(([id]) => blocked.has(id));
  if (ranged.length) {
    const list = el("ul");
    for (const [id, b] of ranged) {
      const name = LABELS[id] || (id === "wff_total" ? "WFF total" : id);
      let text;
      if (b.calculated === 0) text = "not calculable under any answer";
      else if (b.low === b.high) text = money(b.low, id) + (b.complete ? " under every answer" : " where calculable");
      else text = "between " + money(b.low, id) + " and " + money(b.high, id) + (b.complete ? "" : " where calculable");
      const points = b.kind === "points" ? "; values at these points, not bounds" : "";
      list.append(el("li", {}, name + ": " + text + " (calculated in " + b.calculated + " of " + b.branches + " cases" + points + ")"));
    }
    card.append(el("p", {}, "Ranges across the possible answers:"), list);
  }
  if (res.branches.length > 1 || (res.branches[0] && res.branches[0].assignment.length)) {
    const ids = ["family_tax_credit", "in_work_tax_credit", "minimum_family_tax_credit", "best_start", "accommodation_supplement"];
    const table = el("table", {}, el("tr", {}, el("th", {}, "If"), ...ids.map(id => el("th", {}, LABELS[id]))));
    for (const b of res.branches) {
      const cond = b.assignment.map(a => a.fact + ": " + a.label).join("; ") || "(as entered)";
      table.append(el("tr", {}, el("td", {}, cond), ...ids.map(id => {
        const c = b.components[id];
        return el("td", {class: c.outcome}, c.outcome === "calculated" ? money(c.value, id) : STATUS_TEXT[c.outcome]);
      })));
    }
    const why = el("details", {}, el("summary", {}, "Each possible answer (" + res.branches.length + ")"),
      el("div", {class: "scroll"}, table));
    card.append(why);
  }
  if (res.capped) card.append(el("p", {class: "note"}, "Too many combinations to show them all: " +
    "the facts that matter most are branched, and the rest are listed as still missing."));
  if (res.next_question) card.append(el("p", {}, el("strong", {}, "The answer that would narrow this most: "),
    res.next_question.question));
  return card;
}

async function askFirst() {
  const error = document.getElementById("error");
  error.textContent = "";
  try { currentRequest(); } catch (e) { error.textContent = "The request is not valid JSON: " + e.message; return; }
  intake = {answers: [], declined: []};
  await step();
}

async function step() {
  const error = document.getElementById("error"), ask = document.getElementById("ask");
  let data;
  error.textContent = "";
  try { data = await post("/household/intake", {household: currentRequest(), ...intake}); }
  catch (e) { error.textContent = e.message; return false; }
  show(data.calculation);
  ask.replaceChildren();
  const history = el("p", {class: "note"});
  intake.answers.forEach(a => history.append(el("span", {class: "pill"}, a.fact + " = " + a.answer)));
  intake.declined.forEach(f => history.append(el("span", {class: "pill"}, f + ": don't know")));
  if (data.status !== "ask") {
    const done = data.status === "ready" ? "Nothing the calculation needs is missing. The result is below."
      : "You didn't know some facts, so the result below says what Poltika can say without them.";
    const again = el("button", {type: "button"}, "Start over");
    again.addEventListener("click", askFirst);
    ask.append(el("div", {class: "card"}, el("strong", {}, done), history, again));
    return true;
  }
  const q = data.question;
  const card = el("div", {class: "card ask"});
  card.append(el("h3", {}, q.question), el("p", {class: "note"}, "Needed for " +
    q.blocks.map(b => LABELS[b] || b).join(", ") + " (rule " + q.rule + "). " +
    data.remaining.length + " question(s) may remain."));
  let read;
  if (q.answers.length) {
    const name = "answer-" + Math.random().toString(36).slice(2);
    q.answers.forEach((a, i) => {
      const input = el("input", {type: "radio", name: name, value: a.value});
      if (i === 0) input.checked = true;
      card.append(el("label", {class: "option"}, input, " " + a.label));
    });
    read = () => card.querySelector("input[name=" + name + "]:checked").value;
  } else {
    const input = el("input", {type: "text", inputmode: "decimal",
      placeholder: q.kind === "count" ? "a whole number" : (q.unit || "amount")});
    card.append(el("p", {}, input, q.unit ? " " + q.unit : ""));
    read = () => input.value.trim();
  }
  const answer = el("button", {type: "button"}, "Answer"), skip = el("button", {type: "button"}, "Don't know");
  answer.addEventListener("click", async () => {
    intake.answers.push({fact: q.fact, answer: read()});
    // A refused answer (422) is taken back, so the same question stays open.
    if (!(await step())) intake.answers.pop();
  });
  skip.addEventListener("click", () => { intake.declined.push(q.fact); step(); });
  card.append(el("p", {}, answer, " ", skip), history);
  ask.append(card);
  card.scrollIntoView({block: "nearest"});
  return true;
}

document.getElementById("examples").addEventListener("change", e => { if (e.target.value !== "") fill(+e.target.value); });
document.getElementById("run").addEventListener("click", run);
document.getElementById("ask-first").addEventListener("click", askFirst);
document.getElementById("apply-json").addEventListener("click", () => {
  const error = document.getElementById("error");
  try { request = JSON.parse(document.getElementById("request").value); error.textContent = ""; renderForm(); }
  catch (e) { error.textContent = "The JSON is not valid: " + e.message; }
});
document.getElementById("download").addEventListener("click", () => {
  const blob = new Blob([JSON.stringify(lastReport, null, 2)], {type: "application/json"});
  const link = el("a", {href: URL.createObjectURL(blob), download: "poltika_case_" + lastReport.result_id.slice(0, 12) + ".json"});
  link.click();
});
fetch("/analyst/evidence").then(r => r.json()).then(reports => {
  document.getElementById("evidence").textContent = "Evidence: " + reports.map(r =>
    r.policy_id + " " + r.policy_version + ": " + r.summary.parameter_values_with_ranked_source + "/" +
    r.summary.parameter_values + " rate values on ranked sources, " + r.summary.rules_citing_primary_legislation +
    "/" + r.summary.rules + " rules citing legislation" + (r.problems.length ? ", " + r.problems.length + " gap(s)" : "")).join("; ") + ".";
}).catch(() => {});
loadExamples().catch(e => { document.getElementById("error").textContent = "Could not load examples: " + e; });
</script>
</body>
</html>
"""
