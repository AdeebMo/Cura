from app.integrations.prolog_bridge import PrologBridge


def test_prolog_bridge_prefers_influenza_when_fever_and_cough_are_present() -> None:
    bridge = PrologBridge()
    result = bridge.diagnose(
        {
            "demographics": {"age_group": "adult", "sex": "female"},
            "vitals": {"temperature_c": 38.6},
            "confirmed_symptoms": ["fever", "cough"],
            "denied_symptoms": [],
            "unknown_symptoms": [],
            "asked_question_ids": [],
        }
    )

    assert result.diagnoses
    assert result.diagnoses[0].condition == "influenza"
    assert result.next_question is not None
    assert result.next_question.target_symptom in {"body_aches", "fatigue", "headache"}


def test_prolog_bridge_identifies_urinary_tract_infection_pattern() -> None:
    bridge = PrologBridge()
    result = bridge.diagnose(
        {
            "demographics": {"age_group": "adult", "sex": "female"},
            "vitals": {"temperature_c": 38.1},
            "confirmed_symptoms": ["painful_urination", "frequent_urination"],
            "denied_symptoms": [],
            "unknown_symptoms": [],
            "asked_question_ids": [],
        }
    )

    assert result.diagnoses
    assert result.diagnoses[0].condition == "urinary_tract_infection"
    assert result.next_question is not None
    assert result.next_question.target_symptom == "lower_abdominal_pain"


def test_prolog_bridge_flags_more_severe_dehydration_patterns() -> None:
    bridge = PrologBridge()
    result = bridge.diagnose(
        {
            "demographics": {"age_group": "adult", "sex": "male"},
            "vitals": {"hydration_status": "poor"},
            "confirmed_symptoms": ["dizziness", "dry_mouth", "reduced_urination"],
            "denied_symptoms": [],
            "unknown_symptoms": [],
            "asked_question_ids": [],
        }
    )

    assert result.diagnoses
    assert result.diagnoses[0].condition == "dehydration"
    assert {flag.id for flag in result.red_flags} >= {"severe_dehydration"}


def test_prolog_bridge_prefers_allergy_for_sneezing_and_runny_nose() -> None:
    bridge = PrologBridge()
    result = bridge.diagnose(
        {
            "demographics": {"age_group": "adult", "sex": "female"},
            "vitals": {},
            "confirmed_symptoms": ["sneezing", "runny_nose"],
            "denied_symptoms": [],
            "unknown_symptoms": [],
            "asked_question_ids": [],
        }
    )

    assert result.diagnoses
    assert result.diagnoses[0].condition == "allergy"
    assert result.next_question is not None
    assert result.next_question.target_symptom in {"itchy_eyes", "watery_eyes"}
