import { useState } from "react";

import type { AgeGroup, CreateSessionRequest, Sex } from "../types/api";

interface IntakeFormProps {
  disabled?: boolean;
  error?: string | null;
  onSubmit: (payload: CreateSessionRequest) => Promise<void>;
}

interface SelectOption {
  value: string;
  label: string;
}

interface SelectFieldProps {
  id: string;
  value: string;
  options: SelectOption[];
  onChange: (value: string) => void;
}

const ageGroups: SelectOption[] = [
  { value: "child", label: "Child (0-12)" },
  { value: "teen", label: "Teen (13-17)" },
  { value: "adult", label: "Adult (18-64)" },
  { value: "older_adult", label: "Older Adult (65+)" },
];

const sexOptions: SelectOption[] = [
  { value: "", label: "Optional" },
  { value: "female", label: "Female" },
  { value: "male", label: "Male" },
  { value: "other", label: "Other" },
  { value: "prefer_not_to_say", label: "Prefer not to say" },
];

function ChevronDownIcon() {
  return (
    <svg aria-hidden="true" viewBox="0 0 20 20" fill="none" className="h-5 w-5 text-slate-400">
      <path
        d="M5 7.5L10 12.5L15 7.5"
        stroke="currentColor"
        strokeWidth="1.8"
        strokeLinecap="round"
        strokeLinejoin="round"
      />
    </svg>
  );
}

function SelectField({ id, value, options, onChange }: SelectFieldProps) {
  return (
    <div className="relative mt-2">
      <select
        id={id}
        value={value}
        onChange={(event) => onChange(event.target.value)}
        className="w-full appearance-none rounded-2xl border border-slate-200 bg-white px-4 py-3.5 pr-16 text-base font-medium text-ink shadow-[0_6px_18px_rgba(15,23,40,0.04)] outline-none transition hover:border-slate-300 focus:border-accent focus:ring-4 focus:ring-accent/10"
      >
        {options.map((option) => (
          <option key={`${id}-${option.value || "empty"}`} value={option.value}>
            {option.label}
          </option>
        ))}
      </select>

      <span className="pointer-events-none absolute inset-y-0 right-5 flex items-center">
        <ChevronDownIcon />
      </span>
    </div>
  );
}

export function IntakeForm({ disabled, error, onSubmit }: IntakeFormProps) {
  const [alias, setAlias] = useState("");
  const [ageGroup, setAgeGroup] = useState<AgeGroup>("adult");
  const [sex, setSex] = useState<Sex | "">("");
  const [temperature, setTemperature] = useState("");
  const [disclaimerAccepted, setDisclaimerAccepted] = useState(false);
  const trimmedAlias = alias.trim();
  const isSubmitDisabled = Boolean(disabled) || !disclaimerAccepted || trimmedAlias.length === 0;
  const fieldClassName =
    "mt-2 w-full rounded-2xl border border-slate-200 bg-white px-4 py-3.5 text-base font-medium text-ink outline-none transition placeholder:text-slate-400 focus:border-accent focus:ring-4 focus:ring-accent/10";

  async function handleSubmit(event: React.FormEvent<HTMLFormElement>) {
    event.preventDefault();

    await onSubmit({
      alias: trimmedAlias,
      age_group: ageGroup,
      sex: sex || undefined,
      vitals: {
        temperature_c: temperature ? Number(temperature) : undefined,
      },
      disclaimer_accepted: disclaimerAccepted,
    });
  }

  return (
    <form
      className="rounded-[32px] border border-slate-200/70 bg-white/95 p-6 shadow-[0_30px_60px_rgba(15,23,40,0.16)] backdrop-blur sm:p-8"
      onSubmit={handleSubmit}
    >
      <div className="grid gap-4 sm:grid-cols-[minmax(0,1fr)_9.5rem] sm:items-start">
        <div className="min-w-0">
          <span className="inline-flex items-center rounded-full bg-accentSoft px-3 py-1 text-xs font-semibold uppercase tracking-[0.18em] text-accent">
            Start Consultation
          </span>
          <h2 className="mt-4 font-display text-4xl leading-tight text-ink sm:whitespace-nowrap">
            Set up the session
          </h2>
          <p className="mt-3 text-sm leading-6 text-slate-600">
            Start with an alias. Cura guides the rest.
          </p>
        </div>

        <div className="rounded-[24px] border border-slate-200/80 bg-cloud/80 px-4 py-4">
          <p className="text-xs font-semibold uppercase tracking-[0.16em] text-accent">
            What to expect
          </p>
          <p className="mt-2 text-sm leading-6 text-slate-600">
            Under a minute. No account. No clutter.
          </p>
        </div>
      </div>

      <div className="mt-6 grid gap-4 md:grid-cols-2">
        <label className="block text-sm font-semibold text-slate-700" htmlFor="alias">
          First name or alias
          <input
            id="alias"
            required
            value={alias}
            onChange={(event) => setAlias(event.target.value)}
            className={fieldClassName}
            placeholder="Ava"
          />
        </label>

        <div className="text-sm font-semibold text-slate-700">
          <label htmlFor="ageGroup">Age group</label>
          <SelectField
            id="ageGroup"
            value={ageGroup}
            options={ageGroups}
            onChange={(value) => setAgeGroup(value as AgeGroup)}
          />
        </div>

        <div className="text-sm font-semibold text-slate-700">
          <label htmlFor="sex">Sex</label>
          <SelectField
            id="sex"
            value={sex}
            options={sexOptions}
            onChange={(value) => setSex(value as Sex | "")}
          />
        </div>

        <label className="block text-sm font-semibold text-slate-700" htmlFor="temperature">
          Temperature (Celsius)
          <input
            id="temperature"
            type="number"
            step="0.1"
            inputMode="decimal"
            value={temperature}
            onChange={(event) => setTemperature(event.target.value)}
            className={fieldClassName}
            placeholder="38.6"
          />
        </label>
      </div>

      <label className="mt-5 flex items-start gap-3 rounded-[24px] border border-amber-200 bg-amber-50/90 px-4 py-4 text-amber-900">
        <input
          type="checkbox"
          required
          checked={disclaimerAccepted}
          onChange={(event) => setDisclaimerAccepted(event.target.checked)}
          className="mt-1 h-4 w-4 rounded border-amber-300 text-accent focus:ring-accent"
        />
        <span className="text-sm leading-6">
          <span className="font-semibold">Educational use only:</span> Non-emergency guidance, not
          a medical diagnosis tool.
        </span>
      </label>

      {error ? (
        <div className="mt-5 rounded-2xl border border-rose-200 bg-rose-50 px-4 py-3 text-sm text-rose-700">
          {error}
        </div>
      ) : null}

      <button
        type="submit"
        disabled={isSubmitDisabled}
        className="mt-5 inline-flex w-full items-center justify-center rounded-full bg-ink px-6 py-4 text-base font-semibold text-white shadow-[0_18px_38px_rgba(15,23,40,0.18)] transition duration-200 hover:-translate-y-0.5 hover:bg-slate-900 disabled:cursor-not-allowed disabled:opacity-60 disabled:hover:translate-y-0"
      >
        {disabled ? "Starting session..." : "Start consultation"}
      </button>

      <p className="mt-3 text-center text-xs leading-5 text-slate-500">
        {disclaimerAccepted
          ? "Guided symptom collection begins next."
          : "Accept the disclaimer to continue."}
      </p>
    </form>
  );
}
