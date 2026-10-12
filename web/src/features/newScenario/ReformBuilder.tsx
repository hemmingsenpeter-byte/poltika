"use client";

import { useEffect, useRef, useState } from "react";

import { checkReform, getRegistry } from "@/api/services/registryService";
import { createScenario, type CreateScenarioRequest, type Operation, type Reform, runScenario } from "@/api/services/scenarioService";
import { ErrorState, Loading, Unavailable } from "@/components/states";
import { Button } from "@/components/ui/Button";
import type { CheckResult, Registry, ValidInstrument } from "@/domain";
import { humanise } from "@/lib/labels";
import { useAsync } from "@/lib/useAsync";

import { ConfirmationPanel, type ConfirmationItem } from "./ConfirmationPanel";

const DECIMAL = /^-?\d+(\.\d+)?$/;
const OPERATIONS: { value: Operation; label: string }[] = [
  { value: "set", label: "Set to" },
  { value: "add", label: "Add" },
  { value: "multiply", label: "Multiply by" },
];

type OptionForm = { label: string; instrumentId: string; parameterId: string; operation: Operation; value: string; reformId?: string; reformDescription?: string };

const INPUT = "h-10 w-full md:h-9 rounded-md border border-border-strong bg-surface px-2 text-sm";

function Field({ id, label, hint, error, children }: { id: string; label: string; hint?: string; error?: string | null; children: React.ReactNode }) {
  return (
    <div className="space-y-1">
      <label htmlFor={id} className="block text-sm font-medium">
        {label}
      </label>
      {children}
      {hint ? <p className="text-xs text-muted">{hint}</p> : null}
      {error ? (
        <p id={`${id}-error`} className="text-xs text-bad-fg">
          {error}
        </p>
      ) : null}
    </div>
  );
}

function runnable(registry: Registry): ValidInstrument[] {
  return registry.instruments.filter((i): i is ValidInstrument => i.valid && i.runnable);
}

function reformOf(option: OptionForm, index: number): Reform {
  return {
    reform_id: option.reformId ?? `option_${index + 1}`,
    description: option.reformDescription ?? option.label,
    overrides: [
      { policy_id: option.instrumentId, parameter_id: option.parameterId, operation: option.operation, value: option.value.trim() },
    ],
  };
}

// A cloned reform's id and description describe the settings it was cloned with.
// Once the override changes they would mislead, so drop them (reformOf then falls back).
function withoutStaleReform(prev: OptionForm, next: OptionForm): OptionForm {
  const changed =
    prev.instrumentId !== next.instrumentId || prev.parameterId !== next.parameterId ||
    prev.operation !== next.operation || prev.value !== next.value;
  return changed ? { ...next, reformId: undefined, reformDescription: undefined } : next;
}

function OptionFields({
  index,
  option,
  instruments,
  showLabel,
  labelError,
  valueError,
  onChange,
}: {
  index: number;
  option: OptionForm;
  instruments: ValidInstrument[];
  showLabel: boolean;
  labelError: string | null;
  valueError: string | null;
  onChange: (next: OptionForm) => void;
}) {
  const instrument = instruments.find((i) => i.id === option.instrumentId);
  const parameters = instrument?.parameters.filter((p) => p.editable) ?? [];
  const parameter = parameters.find((p) => p.id === option.parameterId);
  const p = `opt${index}`;
  return (
    <fieldset className="space-y-3 rounded-md border border-border p-3">
      <legend className="px-1 text-sm font-semibold">{showLabel ? `Option ${index + 1}` : "The change"}</legend>
      {showLabel ? (
        <Field id={`${p}-label`} label="Option label" hint="Up to 40 characters. Not “Status quo”." error={labelError}>
          <input
            id={`${p}-label`}
            className={INPUT}
            maxLength={40}
            value={option.label}
            aria-invalid={labelError ? true : undefined}
            onChange={(e) => onChange({ ...option, label: e.target.value })}
          />
        </Field>
      ) : null}
      <Field id={`${p}-policy`} label="Policy">
        <select
          id={`${p}-policy`}
          className={INPUT}
          value={option.instrumentId}
          onChange={(e) => onChange({ ...option, instrumentId: e.target.value, parameterId: "" })}
        >
          <option value="">Choose a policy</option>
          {instruments.map((i) => (
            <option key={i.id} value={i.id}>
              {i.title}
            </option>
          ))}
        </select>
      </Field>
      <Field
        id={`${p}-parameter`}
        label="Parameter"
        hint={
          parameter && parameter.current.value !== null
            ? `Current value: ${parameter.current.value} (${parameter.unit_label})`
            : undefined
        }
      >
        <select
          id={`${p}-parameter`}
          className={INPUT}
          value={option.parameterId}
          disabled={!instrument}
          onChange={(e) => onChange({ ...option, parameterId: e.target.value })}
        >
          <option value="">Choose a parameter</option>
          {parameters.map((q) => (
            <option key={q.id} value={q.id}>
              {humanise(q.id)}
            </option>
          ))}
        </select>
      </Field>
      <div className="grid gap-3 sm:grid-cols-2">
        <Field id={`${p}-operation`} label="Change">
          <select
            id={`${p}-operation`}
            className={INPUT}
            value={option.operation}
            onChange={(e) => onChange({ ...option, operation: e.target.value as Operation })}
          >
            {OPERATIONS.map((o) => (
              <option key={o.value} value={o.value}>
                {o.label}
              </option>
            ))}
          </select>
        </Field>
        <Field id={`${p}-value`} label="Value" hint="A decimal number, for example 0.25 or 6500." error={valueError}>
          <input
            id={`${p}-value`}
            className={INPUT}
            inputMode="decimal"
            value={option.value}
            aria-invalid={valueError ? true : undefined}
            aria-describedby={valueError ? `${p}-value-error` : undefined}
            onChange={(e) => onChange({ ...option, value: e.target.value })}
          />
        </Field>
      </div>
    </fieldset>
  );
}

type Checked = { items: ConfirmationItem[]; request: CreateScenarioRequest };

export function ReformBuilder({
  compare,
  navigate,
  initial,
}: {
  compare: boolean;
  navigate: (href: string) => void;
  initial?: CreateScenarioRequest;
}) {
  const registry = useAsync(getRegistry, "registry");
  if (registry.status === "loading") return <Loading label="Loading the supported policies" />;
  if (registry.status === "error") return <ErrorState error={registry.error} onRetry={registry.reload} />;
  if (initial && (
    initial.options.length < 1 || initial.options.length > 2 ||
    initial.options.some((o) => o.reform.overrides.length !== 1 || !registry.data.instruments.some((i) =>
      i.valid && i.runnable && i.id === o.reform.overrides[0]?.policy_id &&
      i.parameters.some((p) => p.editable && p.id === o.reform.overrides[0]?.parameter_id),
    ))
  )) {
    return <div className="space-y-4">
      <Unavailable title="These settings cannot be edited here" reason="This form supports one parameter per option, for up to two options from the current supported policies. The original settings are shown below." />
      <details><summary className="min-h-[24px] cursor-pointer text-sm">Original settings</summary><pre className="mt-2 overflow-auto text-xs">{JSON.stringify(initial, null, 2)}</pre></details>
    </div>;
  }
  return <ReformForm registry={registry.data} compare={compare} navigate={navigate} initial={initial} />;
}

function ReformForm({ registry, compare, navigate, initial }: { registry: Registry; compare: boolean; navigate: (href: string) => void; initial?: CreateScenarioRequest }) {
  const instruments = runnable(registry);
  const blank = (label: string): OptionForm => ({ label, instrumentId: "", parameterId: "", operation: "set", value: "" });
  const [title, setTitle] = useState(initial?.title ?? "");
  const [description, setDescription] = useState(initial?.description ?? "");
  const [options, setOptions] = useState<OptionForm[]>(initial ? initial.options.map((o) => ({
    label: o.label,
    instrumentId: o.reform.overrides[0]!.policy_id,
    parameterId: o.reform.overrides[0]!.parameter_id,
    operation: o.reform.overrides[0]!.operation,
    value: o.reform.overrides[0]!.value,
    reformId: o.reform.reform_id,
    reformDescription: o.reform.description,
  })) : compare ? [blank("Option A"), blank("Option B")] : [blank("Proposed change")]);
  const [checked, setChecked] = useState<Checked | null>(null);
  const [checking, setChecking] = useState(false);
  const [running, setRunning] = useState(false);
  const [error, setError] = useState<unknown>(null);
  const [touched, setTouched] = useState(false);
  const checkRequest = useRef<AbortController | null>(null);
  const runRequest = useRef<AbortController | null>(null);

  useEffect(() => () => {
    checkRequest.current?.abort();
    runRequest.current?.abort();
  }, []);

  const statusQuo = registry.status_quo_label.trim().toLowerCase();
  const labels = options.map((o) => o.label.trim());
  const labelError = (i: number): string | null => {
    if (!compare) return null;
    const label = labels[i] ?? "";
    if (label === "") return "Give this option a label.";
    if (label.toLowerCase() === statusQuo) return `The label cannot be “${registry.status_quo_label}”.`;
    if (labels.some((other, j) => j !== i && other.toLowerCase() === label.toLowerCase())) return "Labels must be different.";
    return null;
  };
  const valueError = (o: OptionForm): string | null =>
    o.value.trim() === "" ? "Enter a value." : DECIMAL.test(o.value.trim()) ? null : "Enter a decimal number, such as 0.25.";
  const titleError = title.trim() === "" ? "A title is required." : title.length > 80 ? "At most 80 characters." : null;
  const descriptionError = description.length > 500 ? "At most 500 characters." : null;
  const optionReady = (o: OptionForm, i: number) => o.instrumentId !== "" && o.parameterId !== "" && !valueError(o) && !labelError(i);
  const ready = !titleError && !descriptionError && options.every(optionReady);

  function edit(update: () => void) {
    if (runRequest.current) return;
    checkRequest.current?.abort();
    checkRequest.current = null;
    setChecking(false);
    update();
    setChecked(null);
    setError(null);
  }

  async function review() {
    setTouched(true);
    if (!ready || checkRequest.current || runRequest.current) return;
    const controller = new AbortController();
    checkRequest.current = controller;
    const request: CreateScenarioRequest = {
      title: title.trim(),
      description: description.trim(),
      options: options.map((o, i) => ({ label: o.label.trim(), reform: reformOf(o, i) })),
    };
    setChecking(true);
    setChecked(null);
    setError(null);
    try {
      const results: CheckResult[] = await Promise.all(request.options.map((o) => checkReform(o.reform, controller.signal)));
      if (controller.signal.aborted) return;
      const items = options.map((o, i): ConfirmationItem | null => {
        const instrument = instruments.find((x) => x.id === o.instrumentId);
        const parameter = instrument?.parameters.find((q) => q.id === o.parameterId);
        const check = results[i];
        if (!instrument || !parameter || !check) return null;
        const op = OPERATIONS.find((x) => x.value === o.operation)?.label.toLowerCase() ?? o.operation;
        return {
          label: compare ? o.label.trim() : null,
          asked: `${op} ${humanise(parameter.id)} (${instrument.title}) ${o.operation === "set" ? "to " : ""}${o.value.trim()}`,
          instrument,
          parameter,
          check,
        };
      });
      const resolved = items.filter((x): x is ConfirmationItem => x !== null);
      if (resolved.length !== options.length) {
        // Never show a panel (or enable Run) with an option left unchecked.
        throw new Error("An option no longer matches a supported instrument or parameter.");
      }
      setChecked({
        items: resolved,
        request,
      });
    } catch (e) {
      if (!controller.signal.aborted) setError(e);
    } finally {
      if (checkRequest.current === controller) {
        checkRequest.current = null;
        if (!controller.signal.aborted) setChecking(false);
      }
    }
  }

  async function run() {
    if (!checked || !checked.items.every((i) => i.check.ok) || runRequest.current || checkRequest.current) return;
    const controller = new AbortController();
    runRequest.current = controller;
    setRunning(true);
    setError(null);
    try {
      const scenarioId = await createScenario(checked.request, controller.signal);
      if (controller.signal.aborted) return;
      const created = await runScenario(scenarioId, controller.signal);
      if (controller.signal.aborted) return;
      navigate(`/scenarios/${created.scenario_id}/runs/${created.run_id}`);
    } catch (e) {
      if (!controller.signal.aborted) setError(e);
    } finally {
      if (runRequest.current === controller) {
        runRequest.current = null;
        if (!controller.signal.aborted) setRunning(false);
      }
    }
  }

  return (
    <div className="space-y-6">
      <form
        className="space-y-4"
        onSubmit={(e) => {
          e.preventDefault();
          void review();
        }}
        noValidate
      >
        <fieldset disabled={running} className="space-y-4">
        <Field id="title" label="Title" error={touched ? titleError : null}>
          <input id="title" className={INPUT} maxLength={80} value={title} onChange={(e) => edit(() => setTitle(e.target.value))} />
        </Field>
        <Field id="description" label="Description (optional)" hint="Up to 500 characters." error={touched ? descriptionError : null}>
          <textarea
            id="description"
            className="min-h-20 w-full rounded-md border border-border-strong bg-surface p-2 text-sm"
            maxLength={500}
            value={description}
            onChange={(e) => edit(() => setDescription(e.target.value))}
          />
        </Field>
        {options.map((o, i) => (
          <OptionFields
            key={i}
            index={i}
            option={o}
            instruments={instruments}
            showLabel={compare}
            labelError={touched ? labelError(i) : null}
            valueError={touched ? valueError(o) : null}
            onChange={(next) => edit(() => setOptions(options.map((x, j) => (j === i ? withoutStaleReform(x, next) : x))))}
          />
        ))}
        <Button type="submit" variant="secondary" disabled={checking || running}>
          {checking ? "Checking…" : "Review before running"}
        </Button>
        {touched && !ready ? <p className="text-sm text-bad-fg">Complete the fields marked above to continue.</p> : null}
        </fieldset>
      </form>

      {error ? <ErrorState error={error} onRetry={checked ? run : review} /> : null}
      {running ? <Loading label="Running on the synthetic population — about 30–60 seconds" /> : null}
      {checked ? (
        <div className="space-y-2">
          <ConfirmationPanel
          items={checked.items}
          limitations={registry.limitations}
          reformJson={checked.request.options}
          onRun={run}
          running={running}
          />
          <p className="text-xs text-muted">Identical settings reuse the same stored scenario. Its original title and description are retained.</p>
        </div>
      ) : null}
    </div>
  );
}
