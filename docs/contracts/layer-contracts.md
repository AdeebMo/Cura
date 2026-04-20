# Layer Contracts

## Frontend to Backend

### `POST /api/v1/sessions`

Request:

```json
{
  "alias": "Ava",
  "age_group": "adult",
  "sex": "female",
  "vitals": {
    "temperature_c": 38.6,
    "pain_severity": 3,
    "hydration_status": "normal"
  },
  "disclaimer_accepted": true
}
```

Response includes:

- `session_id`
- `assistant_message`
- `state`

### `POST /api/v1/sessions/{session_id}/turns`

Free text turn:

```json
{
  "type": "free_text",
  "message": "I have a high fever and I'm coughing a lot"
}
```

Follow-up response:

```json
{
  "type": "follow_up_answer",
  "question_id": "q_body_aches",
  "response": "yes"
}
```

Response includes:

- `assistant_message`
- `normalized_input`
- `diagnoses`
- `next_question`
- `red_flags`
- `state`

## Python to Lisp

Protocol:

- Python writes raw text to Lisp over `stdin`
- Lisp returns one S-expression on `stdout`

Example response:

```lisp
(:canonical-symptoms ("fever" "cough")
 :matched-phrases (("high fever" "fever") ("coughing" "cough"))
 :unknown-terms ())
```

Responsibilities:

- lowercase and sanitize text
- map synonyms to canonical symptom tokens
- remain stateless and pure

## Python to Prolog

Protocol:

- Python writes JSON to Prolog over `stdin`
- Prolog returns JSON on `stdout`

Example request:

```json
{
  "demographics": {
    "age_group": "adult",
    "sex": "female"
  },
  "vitals": {
    "temperature_c": 38.6
  },
  "confirmed_symptoms": ["fever", "cough"],
  "denied_symptoms": [],
  "unknown_symptoms": [],
  "asked_question_ids": []
}
```

Example response:

```json
{
  "diagnoses": [
    {
      "condition": "influenza",
      "rule_strength": "moderate",
      "matched_symptoms": ["fever", "cough"],
      "missing_symptoms": ["body_aches", "fatigue", "headache"],
      "conflicting_symptoms": [],
      "explanation": "Influenza matches the confirmed fever and cough pattern."
    }
  ],
  "next_question": {
    "id": "q_body_aches",
    "prompt": "Are you also experiencing body aches?",
    "target_symptom": "body_aches",
    "rationale": "Body aches help distinguish influenza from milder cold patterns."
  },
  "red_flags": [],
  "explanation_trace": [
    "influenza matched core symptoms fever, cough"
  ]
}
```

