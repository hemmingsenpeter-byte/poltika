"use client";

import { useState } from "react";

import { checkReform, getRegistry } from "@/api/services/registryService";
import { createScenario, type Operation, type Reform, runScenario } from "@/api/services/scenarioService";
import { ErrorState, Loading } from "@/components/states";
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

type OptionForm = { label: string; instrumentId: string; parameterId: string; operation: Operation; value: string };

const INPUT = "h-9 w-full rounded-md border border-border-strong bg-surface px-2 text-sm";

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
    reform_id: `option_${index + 1}`,
    description: option.label,
    overrides: [
      { policy_id: option.instrumentId, parameter_id: option.parameterId, operation: option.operation, value: option.value.trim() },
    ],
  };
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

type Checked = { items: ConfirmationItem[]; reform: unknown };

export function ReformBuilder({
  compare,
  navigate,
}: {
  compare: boolean;
  navigate: (href: string) => void;
}) {
  const registry = useAsync(getRegistry, "registry");
  if (registry.status === "loading") return <Loading label="Loading the supported policies" />;
  if (registry.status === "error") return <ErrorState error={registry.error} onRetry={registry.reload} />;
  return <ReformForm registry={registry.data} compare={compare} navigate={navigate} />;
}

function ReformForm({ registry, compare, navigate }: { registry: Registry; compare: boolean; navigate: (href: string) => void }) {
  const instruments = runnable(registry);
  const blank = (label: string): OptionForm => ({ label, instrumentId: "", parameterId: "", operation: "set", value: "" });
  const [title, setTitle] = useState("");
  const [description, setDescription] = useState("");
  const [options, setOptions] = useState<OptionForm[]>(compare ? [blank("Option A"), blank("Option B")] : [blank("Proposed change")]);
  const [checked, setChecked] = useState<Checked | null>(null);
  const [checking, setChecking] = useState(false);
  const [running, setRunning] = useState(false);
  const [error, setError] = useState<unknown>(null);
  const [touched, setTouched] = useState(false);

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
    update();
    setChecked(null);
    setError(null);
  }

  async function review() {
    setTouched(true);
    if (!ready) return;
    setChecking(true);
    setError(null);
    try {
      const results: CheckResult[] = await Promise.all(options.map((o, i) => checkReform(reformOf(o, i))));
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
      setChecked({
        items: items.filter((x): x is ConfirmationItem => x !== null),
        reform: options.map((o, i) => ({ label: o.label.trim(), reform: reformOf(o, i) })),
      });
    } catch (e) {
      setError(e);
    } finally {
      setChecking(false);
    }
  }

  async function run() {
    setRunning(true);
    setError(null);
    try {
      const scenarioId = await createScenario({
        title: title.trim(),
        description: description.trim(),
        options: options.map((o, i) => ({ label: o.label.trim(), reform: reformOf(o, i) })),
      });
      const created = await runScenario(scenarioId);
      navigate(`/scenarios/${created.scenario_id}/runs/${created.run_id}`);
    } catch (e) {
      setError(e);
      setRunning(false);
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
            onChange={(next) => edit(() => setOptions(options.map((x, j) => (j === i ? next : x))))}
          />
        ))}
        <Button type="submit" variant="secondary" disabled={checking || running}>
          {checking ? "Checking…" : "Review before running"}
        </Button>
        {touched && !ready ? <p className="text-sm text-bad-fg">Complete the fields marked above to continue.</p> : null}
      </form>

      {error ? <ErrorState error={error} onRetry={checked ? run : review} /> : null}
      {running ? <Loading label="Running on the synthetic population — about 30–60 seconds" /> : null}
      {checked ? (
        <ConfirmationPanel
          items={checked.items}
          limitations={registry.limitations}
          reformJson={checked.reform}
          onRun={run}
          running={running}
        />
      ) : null}
    </div>
  );
}
