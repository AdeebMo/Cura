export type AgeGroup = "child" | "teen" | "adult" | "older_adult";
export type Sex = "female" | "male" | "other" | "prefer_not_to_say";
export type FollowUpResponse = "yes" | "no" | "unknown";

export interface Vitals {
  temperature_c?: number;
  pain_severity?: number;
  hydration_status?: "normal" | "reduced" | "poor";
}

export interface ConsultationEntry {
  role: "user" | "assistant";
  message: string;
  timestamp: string;
  metadata: Record<string, unknown>;
}

export interface MatchedPhrase {
  source: string;
  canonical: string;
}

export interface NormalizedInput {
  canonical_symptoms: string[];
  matched_phrases: MatchedPhrase[];
  unknown_terms: string[];
}

export interface Diagnosis {
  condition: string;
  rule_strength: string;
  matched_symptoms: string[];
  missing_symptoms: string[];
  conflicting_symptoms: string[];
  explanation: string;
}

export interface SafetyAlert {
  id: string;
  severity: string;
  message: string;
  trigger: string;
}

export interface FollowUpQuestion {
  id: string;
  prompt: string;
  target_symptom: string;
  rationale: string;
}

export interface SessionState {
  session_id: string;
  alias: string;
  age_group: AgeGroup;
  sex?: Sex | null;
  vitals: Vitals;
  confirmed_symptoms: string[];
  denied_symptoms: string[];
  unknown_symptoms: string[];
  asked_question_ids: string[];
  pending_question?: FollowUpQuestion | null;
  consultation_history: ConsultationEntry[];
  created_at: string;
  updated_at: string;
}

export interface CreateSessionRequest {
  alias: string;
  age_group: AgeGroup;
  sex?: Sex | null;
  vitals: Vitals;
  disclaimer_accepted: boolean;
}

export interface CreateSessionResponse {
  session_id: string;
  assistant_message: string;
  state: SessionState;
}

export interface TurnResponse {
  assistant_message: string;
  normalized_input?: NormalizedInput | null;
  diagnoses: Diagnosis[];
  next_question?: FollowUpQuestion | null;
  red_flags: SafetyAlert[];
  explanation_trace: string[];
  state: SessionState;
}

