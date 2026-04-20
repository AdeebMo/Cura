import { ChatPanel } from "../components/chat-panel";
import { IntakeForm } from "../components/intake-form";
import { Sidebar } from "../components/sidebar";
import { useConsultation } from "../features/consultation/useConsultation";

const onboardingSteps = [
  {
    title: "Create a lightweight profile",
    text: "An alias and a little context are enough to begin.",
  },
  {
    title: "Describe symptoms in plain language",
    text: "Users can explain symptoms naturally once the session starts.",
  },
  {
    title: "Receive guided follow-up questions",
    text: "Cura follows with focused, explainable next questions.",
  },
] as const;

const platformSlices = [
  {
    badge: "Python OOP",
    title: "Owns state and orchestration",
    text: "Session state, consultation history, duplicate-question control, and response coordination live in the application layer.",
  },
  {
    badge: "Common Lisp",
    title: "Normalizes user language",
    text: "Free-text symptom descriptions are reduced into canonical symbolic tokens before reasoning begins.",
  },
  {
    badge: "SWI-Prolog",
    title: "Applies transparent rule logic",
    text: "Diagnoses, follow-up question selection, and red-flag inference come from explainable rule evaluation.",
  },
] as const;

const trustSignals = ["Alias-friendly", "Non-emergency scope", "Explainable reasoning"] as const;

function titleize(value: string) {
  return value.replace(/_/g, " ").replace(/\b\w/g, (character) => character.toUpperCase());
}

export default function App() {
  const consultation = useConsultation();

  if (!consultation.session) {
    return (
      <main className="min-h-screen bg-app-gradient px-4 py-6 text-ink sm:px-6 sm:py-8 lg:px-8">
        <div className="mx-auto max-w-[1600px]">
          <section className="animate-rise-in relative overflow-hidden rounded-[40px] border border-white/70 bg-white/55 p-6 shadow-panel backdrop-blur-xl sm:p-8 lg:p-9">
            <div className="absolute inset-x-0 top-0 h-32 bg-gradient-to-r from-accent/10 via-white/0 to-accent/5" />
            <div className="absolute -left-20 top-24 h-56 w-56 rounded-full bg-accent/10 blur-3xl" />
            <div className="absolute -right-16 bottom-8 h-48 w-48 rounded-full bg-emerald-200/30 blur-3xl" />

            <div className="relative grid gap-8 lg:grid-cols-[1.18fr_1fr] xl:gap-8">
              <section className="max-w-[58rem] pt-2">
                <p className="text-sm font-semibold uppercase tracking-[0.24em] text-accent">
                  Educational Intake
                </p>
                <h1 className="mt-4 max-w-3xl font-display text-5xl leading-[0.96] text-ink sm:text-6xl">
                  A calmer first step into consultation.
                </h1>
                <p className="mt-4 max-w-[52rem] text-base leading-8 text-slate-600 sm:text-lg">
                  Cura gets users into the consultation faster. The opening screen sets scope
                  clearly, reduces friction, and keeps the next step obvious.
                </p>

                <div className="mt-6 flex flex-wrap gap-3">
                  {trustSignals.map((signal) => (
                    <span
                      key={signal}
                      className="inline-flex items-center rounded-full border border-white/80 bg-white/80 px-4 py-2 text-sm font-medium text-slate-700 shadow-sm"
                    >
                      {signal}
                    </span>
                  ))}
                </div>

                <div className="mt-8 grid gap-3 md:grid-cols-3">
                  {onboardingSteps.map((step, index) => (
                    <article
                      key={step.title}
                      className="rounded-[28px] border border-white/75 bg-white/72 p-4 shadow-[0_14px_32px_rgba(15,23,40,0.07)] transition duration-300 hover:-translate-y-1 hover:shadow-[0_20px_42px_rgba(15,23,40,0.1)]"
                    >
                      <div className="flex items-center justify-between gap-3">
                        <span className="inline-flex h-10 w-10 items-center justify-center rounded-full bg-accentSoft text-sm font-semibold text-accent">
                          0{index + 1}
                        </span>
                        <div className="h-px flex-1 bg-slate-200" />
                      </div>
                      <h2 className="mt-4 text-lg font-semibold leading-7 text-ink">
                        {step.title}
                      </h2>
                      <p className="mt-2 text-sm leading-6 text-slate-600">{step.text}</p>
                    </article>
                  ))}
                </div>
              </section>

              <div className="relative lg:pt-4">
                <IntakeForm
                  disabled={consultation.loading}
                  error={consultation.error}
                  onSubmit={consultation.startSession}
                />
              </div>
            </div>
          </section>

          <section className="animate-rise-in-delayed mt-6 rounded-[36px] border border-white/65 bg-white/70 p-6 shadow-panel backdrop-blur-xl sm:p-8">
            <div className="flex flex-col gap-4 lg:flex-row lg:items-end lg:justify-between">
              <div className="max-w-2xl">
                <p className="text-sm font-semibold uppercase tracking-[0.24em] text-accent">
                  Project Slice
                </p>
                <h2 className="mt-3 font-display text-4xl leading-tight text-ink">
                  Three paradigms, one readable product story.
                </h2>
              </div>
              <p className="max-w-2xl text-sm leading-7 text-slate-600">
                The technical architecture is still part of the story, but it now supports the
                primary action instead of competing with it. That keeps the landing screen focused
                while preserving the academic intent of the project.
              </p>
            </div>

            <div className="mt-8 grid gap-4 xl:grid-cols-3">
              {platformSlices.map((item) => (
                <article
                  key={item.badge}
                  className="rounded-[28px] border border-slate-200/80 bg-white/88 p-6 shadow-[0_14px_30px_rgba(15,23,40,0.06)]"
                >
                  <span className="inline-flex items-center rounded-full bg-accentSoft px-3 py-1 text-xs font-semibold uppercase tracking-[0.18em] text-accent">
                    {item.badge}
                  </span>
                  <h3 className="mt-5 text-xl font-semibold text-ink">{item.title}</h3>
                  <p className="mt-3 text-sm leading-7 text-slate-600">{item.text}</p>
                </article>
              ))}
            </div>
          </section>
        </div>
      </main>
    );
  }

  const safetySummary = consultation.redFlags.length
    ? `${consultation.redFlags.length} safety warning${consultation.redFlags.length > 1 ? "s" : ""} flagged`
    : "No safety warnings flagged";

  return (
    <main className="min-h-screen bg-app-gradient px-4 py-5 text-ink sm:px-6 lg:px-8">
      <div className="mx-auto max-w-[1600px]">
        <header className="mb-5 rounded-[32px] border border-white/60 bg-white/65 px-5 py-5 shadow-panel backdrop-blur xl:px-6">
          <div className="flex flex-col gap-4 xl:flex-row xl:items-center xl:justify-between">
            <div className="min-w-0">
              <p className="text-sm font-semibold uppercase tracking-[0.24em] text-accent">
                Educational Diagnostic Assistant
              </p>
              <div className="mt-2 flex flex-wrap items-center gap-3">
                <h1 className="font-display text-[2.4rem] leading-none text-ink sm:text-[2.8rem]">
                  Consultation for {consultation.session.alias}
                </h1>
                <span
                  className={`inline-flex items-center rounded-full px-3 py-1 text-xs font-semibold uppercase tracking-[0.14em] ${
                    consultation.redFlags.length
                      ? "bg-orange-100 text-warning"
                      : "bg-emerald-100 text-emerald-700"
                  }`}
                >
                  {safetySummary}
                </span>
              </div>
            </div>

            <div className="flex flex-wrap items-center gap-3 xl:justify-end">
              <span className="rounded-full border border-white/80 bg-white/80 px-4 py-2 text-sm font-medium text-slate-700 shadow-sm">
                {titleize(consultation.session.age_group)}
              </span>
              <span className="rounded-full border border-white/80 bg-white/80 px-4 py-2 text-sm font-medium text-slate-700 shadow-sm">
                {consultation.session.vitals.temperature_c
                  ? `${consultation.session.vitals.temperature_c} C`
                  : "No temperature logged"}
              </span>
              <button
                type="button"
                onClick={consultation.reset}
                className="inline-flex items-center justify-center rounded-full border border-slate-300 bg-white px-5 py-3 text-sm font-semibold text-ink transition hover:border-accent hover:text-accent"
              >
                Start new session
              </button>
            </div>
          </div>
        </header>

        {consultation.error ? (
          <div className="mb-5 rounded-[28px] border border-rose-200 bg-rose-50 px-5 py-4 text-sm text-rose-700">
            {consultation.error}
          </div>
        ) : null}

        <div className="grid gap-6 xl:h-[calc(100vh-12rem)] xl:grid-cols-[minmax(0,1.45fr)_390px]">
          <ChatPanel
            entries={consultation.session.consultation_history}
            nextQuestion={consultation.nextQuestion}
            disabled={consultation.loading}
            onSendMessage={consultation.submitFreeText}
            onAnswerQuestion={consultation.answerFollowUp}
          />
          <Sidebar
            state={consultation.session}
            diagnoses={consultation.diagnoses}
            redFlags={consultation.redFlags}
            normalizedInput={consultation.normalizedInput}
            explanationTrace={consultation.explanationTrace}
          />
        </div>
      </div>
    </main>
  );
}
