import type {
  CreateSessionRequest,
  CreateSessionResponse,
  FollowUpResponse,
  TurnResponse,
} from "../types/api";

const API_BASE_URL = import.meta.env.VITE_API_BASE_URL ?? "http://localhost:8000";

async function request<T>(path: string, init: RequestInit): Promise<T> {
  const response = await fetch(`${API_BASE_URL}${path}`, {
    headers: {
      "Content-Type": "application/json",
    },
    ...init,
  });

  if (!response.ok) {
    const payload = (await response.json().catch(() => null)) as { detail?: string } | null;
    throw new Error(payload?.detail ?? "Request failed");
  }

  return (await response.json()) as T;
}

export function createSession(payload: CreateSessionRequest): Promise<CreateSessionResponse> {
  return request<CreateSessionResponse>("/api/v1/sessions", {
    method: "POST",
    body: JSON.stringify(payload),
  });
}

export function sendFreeTextTurn(sessionId: string, message: string): Promise<TurnResponse> {
  return request<TurnResponse>(`/api/v1/sessions/${sessionId}/turns`, {
    method: "POST",
    body: JSON.stringify({
      type: "free_text",
      message,
    }),
  });
}

export function sendFollowUpTurn(
  sessionId: string,
  questionId: string,
  response: FollowUpResponse,
): Promise<TurnResponse> {
  return request<TurnResponse>(`/api/v1/sessions/${sessionId}/turns`, {
    method: "POST",
    body: JSON.stringify({
      type: "follow_up_answer",
      question_id: questionId,
      response,
    }),
  });
}

