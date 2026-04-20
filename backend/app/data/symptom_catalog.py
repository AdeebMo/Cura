from __future__ import annotations

from dataclasses import dataclass


@dataclass(frozen=True, slots=True)
class SymptomSeed:
    canonical_key: str
    display_name: str
    body_system: str
    intake_priority: int
    is_red_flag_candidate: bool = False
    active: bool = True


SYMPTOM_CATALOG: tuple[SymptomSeed, ...] = (
    SymptomSeed("fever", "Fever", "General", 98, True),
    SymptomSeed("cough", "Cough", "Respiratory", 94),
    SymptomSeed("difficulty_breathing", "Difficulty breathing", "Respiratory", 100, True),
    SymptomSeed("chest_pain", "Chest pain", "Cardiopulmonary", 100, True),
    SymptomSeed("chest_tightness", "Chest tightness", "Respiratory", 88, True),
    SymptomSeed("runny_nose", "Runny or stuffy nose", "Respiratory", 72),
    SymptomSeed("sneezing", "Sneezing", "Respiratory", 68),
    SymptomSeed("sore_throat", "Sore throat", "Respiratory", 78),
    SymptomSeed("body_aches", "Body aches", "General", 75),
    SymptomSeed("fatigue", "Fatigue", "General", 76),
    SymptomSeed("headache", "Headache", "Neurologic", 74),
    SymptomSeed("itchy_eyes", "Itchy eyes", "ENT / Eye", 52),
    SymptomSeed("watery_eyes", "Watery eyes", "ENT / Eye", 48),
    SymptomSeed("loss_of_taste_smell", "Loss of taste or smell", "Neurologic", 82),
    SymptomSeed("painful_urination", "Painful urination", "Urinary", 92),
    SymptomSeed("frequent_urination", "Frequent urination", "Urinary", 86),
    SymptomSeed("lower_abdominal_pain", "Lower abdominal pain", "Abdominal", 80),
    SymptomSeed("nausea", "Nausea", "Gastrointestinal", 70),
    SymptomSeed("vomiting", "Vomiting", "Gastrointestinal", 86),
    SymptomSeed("persistent_vomiting", "Persistent vomiting", "Gastrointestinal", 97, True),
    SymptomSeed("diarrhea", "Diarrhea", "Gastrointestinal", 78),
    SymptomSeed("abdominal_cramps", "Abdominal cramps", "Gastrointestinal", 76),
    SymptomSeed("dizziness", "Dizziness", "Neurologic", 83),
    SymptomSeed("confusion", "Confusion", "Neurologic", 98, True),
    SymptomSeed("dry_mouth", "Dry mouth", "Hydration", 66),
    SymptomSeed("reduced_urination", "Reduced urination", "Hydration", 90),
    SymptomSeed("thirst", "Increased thirst", "Hydration", 64),
)
