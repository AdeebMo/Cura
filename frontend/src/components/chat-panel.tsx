import { useEffect, useRef, useState } from "react";

import type { ConsultationEntry, FollowUpQuestion, FollowUpResponse } from "../types/api";

interface ChatPanelProps {
  entries: ConsultationEntry[];
  nextQuestion?: FollowUpQuestion | null;
  disabled?: boolean;
  onSendMessage: (message: string) => Promise<void>;
  onAnswerQuestion: (questionId: string, response: FollowUpResponse) => Promise<void>;
}

const MAX_VISIBLE_ENTRIES = 8;

function MedicalAiIcon() {
  return (
    <svg aria-hidden="true" viewBox="0 0 24 24" fill="none" className="h-4.5 w-4.5">
      <path
        d="M12 7.5V16.5M7.5 12H16.5"
        stroke="currentColor"
        strokeWidth="1.8"
        strokeLinecap="round"
      />
      <path
        d="M18 4.5V7.5M16.5 6H19.5"
        stroke="currentColor"
        strokeWidth="1.8"
        strokeLinecap="round"
      />
      <path
        d="M18 16.5V18.5M17 17.5H19"
        stroke="currentColor"
        strokeWidth="1.8"
        strokeLinecap="round"
      />
    </svg>
  );
}

function SendIcon() {
  return (
    <svg aria-hidden="true" viewBox="0 0 20 20" fill="none" className="h-4.5 w-4.5">
      <path
        d="M4.5 10H14.5"
        stroke="currentColor"
        strokeWidth="1.8"
        strokeLinecap="round"
      />
      <path
        d="M10.5 6L14.5 10L10.5 14"
        stroke="currentColor"
        strokeWidth="1.8"
        strokeLinecap="round"
        strokeLinejoin="round"
      />
    </svg>
  );
}

function resizeTextarea(element: HTMLTextAreaElement | null) {
  if (!element) {
    return;
  }

  element.style.height = "0px";
  element.style.height = `${Math.min(element.scrollHeight, 180)}px`;
}

export function ChatPanel({
  entries,
  nextQuestion,
  disabled,
  onSendMessage,
  onAnswerQuestion,
}: ChatPanelProps) {
  const [message, setMessage] = useState("");
  const [showEarlierMessages, setShowEarlierMessages] = useState(false);
  const scrollContainerRef = useRef<HTMLDivElement | null>(null);
  const textareaRef = useRef<HTMLTextAreaElement | null>(null);
  const visibleEntries = showEarlierMessages ? entries : entries.slice(-MAX_VISIBLE_ENTRIES);
  const hiddenCount = entries.length - visibleEntries.length;

  useEffect(() => {
    const scrollContainer = scrollContainerRef.current;
    if (!scrollContainer) {
      return;
    }

    const frame = window.requestAnimationFrame(() => {
      scrollContainer.scrollTop = scrollContainer.scrollHeight;
    });

    return () => window.cancelAnimationFrame(frame);
  }, [entries.length, nextQuestion?.id]);

  useEffect(() => {
    resizeTextarea(textareaRef.current);
  }, [message]);

  async function submitMessage() {
    if (!message.trim()) {
      return;
    }

    const nextMessage = message.trim();
    setMessage("");
    await onSendMessage(nextMessage);
  }

  async function handleSubmit(event: React.FormEvent<HTMLFormElement>) {
    event.preventDefault();
    await submitMessage();
  }

  return (
    <section className="flex min-h-[720px] flex-col overflow-hidden rounded-[32px] border border-white/70 bg-white/88 shadow-panel backdrop-blur xl:h-full xl:min-h-0">
      <div
        ref={scrollContainerRef}
        className="modern-scrollbar flex-1 overflow-y-auto bg-[linear-gradient(180deg,rgba(248,251,253,0.74)_0%,rgba(255,255,255,0)_22%)]"
      >
        <div className="flex w-full flex-col gap-5 px-5 pb-6 pt-4 sm:px-6">
          <div className="flex justify-end">
            <span
              className={`inline-flex items-center rounded-full px-3 py-1 text-xs font-semibold uppercase tracking-[0.16em] ${
                nextQuestion
                  ? "bg-accentSoft text-accent"
                  : disabled
                    ? "bg-slate-100 text-slate-600"
                    : "bg-emerald-100 text-emerald-700"
              }`}
            >
              {nextQuestion ? "Follow-up ready" : disabled ? "Reviewing input" : "Listening"}
            </span>
          </div>

          {hiddenCount > 0 ? (
            <button
              type="button"
              onClick={() => setShowEarlierMessages((current) => !current)}
              className="self-center rounded-full border border-slate-200 bg-white px-4 py-2 text-sm font-medium text-slate-600 transition hover:border-accent hover:text-accent"
            >
              {showEarlierMessages
                ? "Hide earlier messages"
                : `Show earlier messages (${hiddenCount})`}
            </button>
          ) : null}

          {visibleEntries.map((entry, index) => {
            const assistant = entry.role === "assistant";

            return (
              <article
                key={`${entry.timestamp}-${index}`}
                className={`flex w-full ${assistant ? "items-start gap-3" : "justify-end"}`}
              >
                {assistant ? (
                  <div className="mt-1 flex h-8 w-8 shrink-0 items-center justify-center rounded-2xl border border-accent/10 bg-white text-accent shadow-[0_8px_20px_rgba(15,23,40,0.05)]">
                    <MedicalAiIcon />
                  </div>
                ) : null}

                <div
                  className={`w-fit ${
                    assistant
                      ? "max-w-[min(88%,72rem)] rounded-[24px] rounded-tl-md border border-slate-200/80 bg-white px-4 py-3.5 shadow-[0_12px_28px_rgba(15,23,40,0.06)]"
                      : "max-w-[min(72%,34rem)] rounded-[24px] rounded-tr-md bg-ink px-4 py-3 text-white shadow-[0_16px_28px_rgba(15,23,40,0.14)]"
                  }`}
                >
                  <p
                    className={`whitespace-pre-line text-[15px] leading-7 ${
                      assistant ? "text-slate-700" : "text-white"
                    }`}
                  >
                    {entry.message}
                  </p>
                </div>
              </article>
            );
          })}
        </div>
      </div>

      <div className="border-t border-slate-100/80 bg-white/94 px-4 py-3 sm:px-5">
        <div className="w-full">
          {nextQuestion ? (
            <div className="mb-3 rounded-[24px] border border-accent/15 bg-accentSoft/85 px-4 py-3.5">
              <div className="flex flex-col gap-3 sm:flex-row sm:items-end sm:justify-between">
                <div className="max-w-2xl">
                  <p className="text-xs font-semibold uppercase tracking-[0.22em] text-accent">
                    Next clinical question
                  </p>
                  <p className="mt-2 text-[15px] font-semibold leading-6 text-ink">
                    {nextQuestion.prompt}
                  </p>
                  <p className="mt-1.5 text-sm leading-6 text-slate-600">
                    {nextQuestion.rationale}
                  </p>
                </div>
                <div className="flex flex-wrap gap-2.5">
                  {(["yes", "no", "unknown"] as const).map((response) => (
                    <button
                      key={response}
                      type="button"
                      disabled={disabled}
                      onClick={() => onAnswerQuestion(nextQuestion.id, response)}
                      className="rounded-full border border-accent/15 bg-white px-4 py-2 text-sm font-semibold text-ink transition hover:border-accent hover:text-accent disabled:cursor-not-allowed disabled:opacity-60"
                    >
                      {response === "yes" ? "Yes" : response === "no" ? "No" : "Not sure"}
                    </button>
                  ))}
                </div>
              </div>
            </div>
          ) : null}

          <form
            className="rounded-[26px] border border-slate-200 bg-white px-3 py-2 shadow-[0_14px_30px_rgba(15,23,40,0.06)]"
            onSubmit={handleSubmit}
          >
            <label htmlFor="chat-message" className="sr-only">
              Describe your symptoms
            </label>
            <div className="flex items-end gap-2">
              <textarea
                id="chat-message"
                ref={textareaRef}
                rows={1}
                value={message}
                onChange={(event) => setMessage(event.target.value)}
                onKeyDown={(event) => {
                  if (event.key === "Enter" && !event.shiftKey) {
                    event.preventDefault();
                    void submitMessage();
                  }
                }}
                disabled={disabled}
                placeholder="Describe symptoms in plain language..."
                className="min-h-[44px] flex-1 resize-none border-0 bg-transparent px-3 py-2 text-[15px] leading-7 text-ink outline-none transition placeholder:text-slate-400 focus:ring-0 disabled:cursor-not-allowed disabled:opacity-60"
              />
              <button
                type="submit"
                aria-label="Send message"
                disabled={disabled || !message.trim()}
                className="inline-flex h-10 w-10 shrink-0 items-center justify-center rounded-full bg-ink text-white transition hover:bg-slate-900 disabled:cursor-not-allowed disabled:opacity-60"
              >
                <SendIcon />
              </button>
            </div>
          </form>

          <p className="mt-2 text-center text-xs leading-5 text-slate-500">
            Educational, non-emergency use only.
          </p>
        </div>
      </div>
    </section>
  );
}
