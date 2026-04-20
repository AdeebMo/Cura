import { useState } from "react";

import {
  createSession,
  sendFollowUpTurn,
  sendFreeTextTurn,
} from "../../lib/api";
import type {
  CreateSessionRequest,
  Diagnosis,
  FollowUpQuestion,
  FollowUpResponse,
  NormalizedInput,
  SafetyAlert,
  SessionState,
} from "../../types/api";

interface ConsultationState {
  sessionId: string | null;
  session: SessionState | null;
  diagnoses: Diagnosis[];
  redFlags: SafetyAlert[];
  normalizedInput: NormalizedInput | null;
  explanationTrace: string[];
  nextQuestion: FollowUpQuestion | null;
  loading: boolean;
  error: string | null;
}

const initialState: ConsultationState = {
  sessionId: null,
  session: null,
  diagnoses: [],
  redFlags: [],
  normalizedInput: null,
  explanationTrace: [],
  nextQuestion: null,
  loading: false,
  error: null,
};

export function useConsultation() {
  const [state, setState] = useState<ConsultationState>(initialState);

  async function startSession(payload: CreateSessionRequest) {
    setState((current) => ({ ...current, loading: true, error: null }));

    try {
      const response = await createSession(payload);
      setState({
        sessionId: response.session_id,
        session: response.state,
        diagnoses: [],
        redFlags: [],
        normalizedInput: null,
        explanationTrace: [],
        nextQuestion: response.state.pending_question ?? null,
        loading: false,
        error: null,
      });
    } catch (error) {
      setState((current) => ({
        ...current,
        loading: false,
        error: error instanceof Error ? error.message : "Unable to start session",
      }));
    }
  }

  async function submitFreeText(message: string) {
    if (!state.sessionId) {
      return;
    }

    setState((current) => ({ ...current, loading: true, error: null }));

    try {
      const response = await sendFreeTextTurn(state.sessionId, message);
      setState((current) => ({
        ...current,
        session: response.state,
        diagnoses: response.diagnoses,
        redFlags: response.red_flags,
        normalizedInput: response.normalized_input ?? null,
        explanationTrace: response.explanation_trace,
        nextQuestion: response.next_question ?? null,
        loading: false,
        error: null,
      }));
    } catch (error) {
      setState((current) => ({
        ...current,
        loading: false,
        error: error instanceof Error ? error.message : "Unable to process symptoms",
      }));
    }
  }

  async function answerFollowUp(questionId: string, response: FollowUpResponse) {
    if (!state.sessionId) {
      return;
    }

    setState((current) => ({ ...current, loading: true, error: null }));

    try {
      const turn = await sendFollowUpTurn(state.sessionId, questionId, response);
      setState((current) => ({
        ...current,
        session: turn.state,
        diagnoses: turn.diagnoses,
        redFlags: turn.red_flags,
        explanationTrace: turn.explanation_trace,
        nextQuestion: turn.next_question ?? null,
        loading: false,
        error: null,
      }));
    } catch (error) {
      setState((current) => ({
        ...current,
        loading: false,
        error: error instanceof Error ? error.message : "Unable to process follow-up answer",
      }));
    }
  }

  function reset() {
    setState(initialState);
  }

  return {
    ...state,
    startSession,
    submitFreeText,
    answerFollowUp,
    reset,
  };
}
