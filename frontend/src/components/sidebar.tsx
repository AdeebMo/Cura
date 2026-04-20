import type {
  Diagnosis,
  NormalizedInput,
  SafetyAlert,
  SessionState,
} from "../types/api";

interface SidebarProps {
  state: SessionState;
  diagnoses: Diagnosis[];
  redFlags: SafetyAlert[];
  normalizedInput?: NormalizedInput | null;
  explanationTrace: string[];
}

function titleize(value: string) {
  return value.replace(/_/g, " ").replace(/\b\w/g, (character) => character.toUpperCase());
}

function ChipList({
  items,
  tone = "neutral",
}: {
  items: string[];
  tone?: "neutral" | "positive" | "warning" | "danger";
}) {
  if (items.length === 0) {
    return <p className="text-sm text-slate-500">No items yet.</p>;
  }

  const palette =
    tone === "positive"
      ? "border-emerald-200 bg-emerald-50 text-emerald-700"
      : tone === "warning"
        ? "border-amber-200 bg-amber-50 text-amber-700"
        : tone === "danger"
          ? "border-rose-200 bg-rose-50 text-rose-700"
          : "border-slate-200 bg-slate-50 text-slate-600";

  return (
    <div className="flex flex-wrap gap-2">
      {items.map((item) => (
        <span
          key={item}
          className={`rounded-full border px-3 py-1 text-xs font-medium ${palette}`}
        >
          {titleize(item)}
        </span>
      ))}
    </div>
  );
}

function EvidenceList({
  label,
  items,
  tone,
}: {
  label: string;
  items: string[];
  tone: "positive" | "warning" | "danger";
}) {
  if (items.length === 0) {
    return null;
  }

  return (
    <div>
      <h4 className="mb-2 text-[11px] font-semibold uppercase tracking-[0.18em] text-slate-500">
        {label}
      </h4>
      <ChipList items={items} tone={tone} />
    </div>
  );
}

function StrengthBadge({ value }: { value: string }) {
  const palette =
    value.toLowerCase() === "strong"
      ? "bg-emerald-100 text-emerald-700"
      : value.toLowerCase() === "moderate"
        ? "bg-accentSoft text-accent"
        : "bg-slate-100 text-slate-600";

  return (
    <span className={`rounded-full px-3 py-1 text-[11px] font-semibold uppercase tracking-[0.18em] ${palette}`}>
      {value}
    </span>
  );
}

function SectionHeading({ eyebrow, title }: { eyebrow: string; title: string }) {
  return (
    <div>
      <p className="text-xs font-semibold uppercase tracking-[0.24em] text-accent">{eyebrow}</p>
      <h2 className="mt-2 text-xl font-semibold text-ink">{title}</h2>
    </div>
  );
}

export function Sidebar({
  state,
  diagnoses,
  redFlags,
  normalizedInput,
  explanationTrace,
}: SidebarProps) {
  const topDiagnoses = diagnoses.slice(0, 3);

  return (
    <aside className="overflow-hidden rounded-[32px] border border-white/70 bg-white/88 shadow-panel backdrop-blur xl:h-full xl:min-h-0">
      <div className="modern-scrollbar h-full overflow-y-auto px-4 py-4 sm:px-5 sm:py-5">
        <div className="grid gap-4 pb-1">
        <section
          className={`rounded-[28px] border p-5 shadow-panel backdrop-blur ${
            redFlags.length
              ? "border-orange-200 bg-orange-50"
              : "border-emerald-200 bg-[#f2fcf7]"
          }`}
        >
          <SectionHeading
            eyebrow="Safety"
            title={redFlags.length ? "Needs attention" : "No urgent warning flagged"}
          />
          <div className="mt-4 space-y-3">
            {redFlags.length ? (
              redFlags.map((flag) => (
                <article key={flag.id} className="rounded-[22px] bg-white px-4 py-4 shadow-sm">
                  <div className="flex items-start justify-between gap-3">
                    <h3 className="text-sm font-semibold text-warning">{titleize(flag.trigger)}</h3>
                    <span className="rounded-full bg-orange-100 px-3 py-1 text-[11px] font-semibold uppercase tracking-[0.18em] text-warning">
                      Review
                    </span>
                  </div>
                  <p className="mt-2 text-sm leading-6 text-orange-900">{flag.message}</p>
                </article>
              ))
            ) : (
              <p className="text-sm leading-6 text-emerald-800">
                No safety warning has been triggered from the current information.
              </p>
            )}
          </div>
        </section>

        <section className="rounded-[28px] border border-white/70 bg-white p-5 shadow-panel">
          <SectionHeading eyebrow="Assessment" title="Current leading conditions" />
          <div className="mt-4 space-y-3">
            {topDiagnoses.length === 0 ? (
              <p className="text-sm leading-6 text-slate-500">
                Likely conditions will appear here after the conversation gathers enough symptom
                detail.
              </p>
            ) : (
              topDiagnoses.map((diagnosis, index) => (
                <article
                  key={diagnosis.condition}
                  className={`rounded-[24px] border px-4 py-4 ${
                    index === 0
                      ? "border-accent/15 bg-accentSoft/35"
                      : "border-slate-200 bg-[#fbfdff]"
                  }`}
                >
                  <div className="flex items-start justify-between gap-3">
                    <div>
                      <p className="text-[11px] font-semibold uppercase tracking-[0.18em] text-slate-500">
                        {index === 0 ? "Most supported" : "Also considered"}
                      </p>
                      <h3 className="mt-1 text-base font-semibold text-ink">
                        {titleize(diagnosis.condition)}
                      </h3>
                    </div>
                    <StrengthBadge value={diagnosis.rule_strength} />
                  </div>
                  <p className="mt-3 text-sm leading-6 text-slate-600">{diagnosis.explanation}</p>
                  <div className="mt-4 space-y-3">
                    <EvidenceList
                      label="Matched symptoms"
                      items={diagnosis.matched_symptoms}
                      tone="positive"
                    />
                    <EvidenceList
                      label="Still useful to check"
                      items={diagnosis.missing_symptoms}
                      tone="warning"
                    />
                    <EvidenceList
                      label="Conflicting evidence"
                      items={diagnosis.conflicting_symptoms}
                      tone="danger"
                    />
                  </div>
                </article>
              ))
            )}
          </div>
        </section>

        <section className="rounded-[28px] border border-white/70 bg-white p-5 shadow-panel">
          <SectionHeading eyebrow="Patient Snapshot" title={state.alias} />
          <dl className="mt-4 grid gap-3 text-sm text-slate-600">
            <div className="flex items-center justify-between gap-4 rounded-2xl bg-[#fbfdff] px-4 py-3">
              <dt>Age group</dt>
              <dd className="font-semibold text-ink">{titleize(state.age_group)}</dd>
            </div>
            <div className="flex items-center justify-between gap-4 rounded-2xl bg-[#fbfdff] px-4 py-3">
              <dt>Sex</dt>
              <dd className="font-semibold text-ink">
                {state.sex ? titleize(state.sex) : "Not provided"}
              </dd>
            </div>
            <div className="flex items-center justify-between gap-4 rounded-2xl bg-[#fbfdff] px-4 py-3">
              <dt>Temperature</dt>
              <dd className="font-semibold text-ink">
                {state.vitals.temperature_c ? `${state.vitals.temperature_c} C` : "Not provided"}
              </dd>
            </div>
          </dl>
        </section>

        <section className="rounded-[28px] border border-white/70 bg-white p-5 shadow-panel">
          <SectionHeading eyebrow="Symptom Picture" title="Current evidence" />
          <div className="mt-4 space-y-5">
            <div>
              <h3 className="mb-2 text-sm font-semibold text-ink">Confirmed</h3>
              <ChipList items={state.confirmed_symptoms} tone="positive" />
            </div>
            <div>
              <h3 className="mb-2 text-sm font-semibold text-ink">Denied</h3>
              <ChipList items={state.denied_symptoms} tone="danger" />
            </div>
            <div>
              <h3 className="mb-2 text-sm font-semibold text-ink">Unknown</h3>
              <ChipList items={state.unknown_symptoms} tone="neutral" />
            </div>
            <div>
              <h3 className="mb-2 text-sm font-semibold text-ink">Canonical tokens</h3>
              <ChipList items={normalizedInput?.canonical_symptoms ?? []} tone="neutral" />
            </div>
          </div>
        </section>

        <details className="rounded-[28px] border border-white/70 bg-white p-5 shadow-panel">
          <summary className="cursor-pointer list-none">
            <div className="flex items-center justify-between gap-3">
              <SectionHeading eyebrow="Technical Details" title="Normalization and rule trace" />
              <span className="rounded-full bg-slate-100 px-3 py-1 text-[11px] font-semibold uppercase tracking-[0.18em] text-slate-500">
                Expand
              </span>
            </div>
          </summary>

          <div className="mt-5 space-y-5">
            <div>
              <h3 className="mb-2 text-sm font-semibold text-ink">Matched phrases</h3>
              {normalizedInput?.matched_phrases?.length ? (
                <div className="space-y-2">
                  {normalizedInput.matched_phrases.map((item) => (
                    <div
                      key={`${item.source}-${item.canonical}`}
                      className="rounded-2xl border border-slate-200 bg-[#fbfdff] px-3 py-3 text-sm text-slate-600"
                    >
                      "{item.source}" to {titleize(item.canonical)}
                    </div>
                  ))}
                </div>
              ) : (
                <p className="text-sm text-slate-500">No mapped phrases yet.</p>
              )}
            </div>

            <div>
              <h3 className="mb-2 text-sm font-semibold text-ink">Unmapped terms</h3>
              <ChipList items={normalizedInput?.unknown_terms ?? []} tone="neutral" />
            </div>

            <div>
              <h3 className="mb-2 text-sm font-semibold text-ink">Rule trace</h3>
              <div className="space-y-3">
                {explanationTrace.length === 0 ? (
                  <p className="text-sm leading-6 text-slate-500">
                    A reasoning trace will appear once diagnostic reasoning runs.
                  </p>
                ) : (
                  explanationTrace.map((line) => (
                    <div
                      key={line}
                      className="rounded-2xl border border-slate-200 bg-[#fbfdff] px-4 py-3 text-sm leading-6 text-slate-600"
                    >
                      {line}
                    </div>
                  ))
                )}
              </div>
            </div>
          </div>
        </details>
        </div>
      </div>
    </aside>
  );
}
