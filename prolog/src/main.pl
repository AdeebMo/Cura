:- use_module(library(http/json)).
:- use_module(library(lists)).
:- use_module(library(readutil)).

:- ['facts.pl'].
:- ['questions.pl'].
:- ['red_flags.pl'].
:- ['explanations.pl'].
:- ['rules.pl'].

request_list(Request, Key, Values) :-
    (   get_dict(Key, Request, RawValues)
    ->  Values = RawValues
    ;   Values = []
    ).

string_or_atom_to_atom(Value, Atom) :-
    string(Value),
    atom_string(Atom, Value).
string_or_atom_to_atom(Value, Value) :-
    atom(Value).

request_atom_list(Request, Key, Values) :-
    request_list(Request, Key, RawValues),
    maplist(string_or_atom_to_atom, RawValues, Values).

request_dict(Request, Key, Value) :-
    (   get_dict(Key, Request, RawValue)
    ->  Value = RawValue
    ;   Value = _{}
    ).

temperature_red_flag(Vitals, Alert) :-
    get_dict(temperature_c, Vitals, Temperature),
    number(Temperature),
    Temperature >= 39.5,
    Alert = _{
        id: "very_high_fever",
        severity: "urgent",
        message: "A very high fever was reported and should be clinically reviewed.",
        trigger: "very_high_fever"
    }.

symptom_red_flag(Confirmed, Alert) :-
    member(Symptom, Confirmed),
    red_flag_symptom(Symptom, Severity, Message),
    atom_string(Symptom, Trigger),
    atom_string(Severity, SeverityString),
    Alert = _{
        id: Trigger,
        severity: SeverityString,
        message: Message,
        trigger: Trigger
    }.

collect_red_flags(Confirmed, Vitals, Alerts) :-
    findall(Alert, symptom_red_flag(Confirmed, Alert), SymptomAlerts),
    (   member(dizziness, Confirmed),
        member(dry_mouth, Confirmed),
        (member(reduced_urination, Confirmed); get_dict(hydration_status, Vitals, "poor"))
    ->  DerivedAlerts = [_{
            id: "severe_dehydration",
            severity: "urgent",
            message: "The dehydration pattern appears more severe and should be clinically reviewed urgently.",
            trigger: "severe_dehydration"
        }]
    ;   DerivedAlerts = []
    ),
    (   temperature_red_flag(Vitals, TemperatureAlert)
    ->  append(SymptomAlerts, [TemperatureAlert | DerivedAlerts], Alerts)
    ;   append(SymptomAlerts, DerivedAlerts, Alerts)
    ).

available_question(Diagnosis, Confirmed, Denied, Unknown, Asked, Priority-Question) :-
    member(Symptom, Diagnosis.missing_symptoms),
    \+ member(Symptom, Confirmed),
    \+ member(Symptom, Denied),
    \+ member(Symptom, Unknown),
    follow_up_question(Symptom, QuestionId, Prompt, Rationale, Priority),
    atom_string(QuestionId, QuestionIdString),
    \+ member(QuestionIdString, Asked),
    atom_string(Symptom, SymptomString),
    Question = _{
        id: QuestionIdString,
        prompt: Prompt,
        target_symptom: SymptomString,
        rationale: Rationale
    }.

compare_question_priority(Order, PriorityA-QuestionA, PriorityB-QuestionB) :-
    compare(Order0, PriorityB, PriorityA),
    (   Order0 == (=)
    ->  compare(Order, QuestionA.id, QuestionB.id)
    ;   Order = Order0
    ).

best_question_for_diagnosis(Diagnosis, Confirmed, Denied, Unknown, Asked, Question) :-
    findall(
        Priority-CandidateQuestion,
        available_question(Diagnosis, Confirmed, Denied, Unknown, Asked, Priority-CandidateQuestion),
        Candidates
    ),
    Candidates \= [],
    predsort(compare_question_priority, Candidates, [_-Question | _]).

next_question([Diagnosis | _], Confirmed, Denied, Unknown, Asked, Question) :-
    best_question_for_diagnosis(Diagnosis, Confirmed, Denied, Unknown, Asked, Question),
    !.
next_question([_ | Remaining], Confirmed, Denied, Unknown, Asked, Question) :-
    next_question(Remaining, Confirmed, Denied, Unknown, Asked, Question).

trace_line(Diagnosis, Trace) :-
    diagnosis_trace(
        Diagnosis.condition,
        Diagnosis.rule_strength,
        Diagnosis.matched_symptoms,
        Diagnosis.missing_symptoms,
        Diagnosis.conflicting_symptoms,
        Trace
    ).

build_response(Request, Response) :-
    request_atom_list(Request, confirmed_symptoms, Confirmed),
    request_atom_list(Request, denied_symptoms, Denied),
    request_atom_list(Request, unknown_symptoms, Unknown),
    request_list(Request, asked_question_ids, Asked),
    request_dict(Request, vitals, Vitals),
    ranked_diagnoses(Confirmed, Denied, Diagnoses),
    collect_red_flags(Confirmed, Vitals, Alerts),
    findall(Trace, (member(Diagnosis, Diagnoses), trace_line(Diagnosis, Trace)), ExplanationTrace),
    (   next_question(Diagnoses, Confirmed, Denied, Unknown, Asked, Question)
    ->  Response = _{
            diagnoses: Diagnoses,
            next_question: Question,
            red_flags: Alerts,
            explanation_trace: ExplanationTrace
        }
    ;   Response = _{
            diagnoses: Diagnoses,
            red_flags: Alerts,
            explanation_trace: ExplanationTrace
        }
    ).

main :-
    read_string(user_input, _, InputString),
    atom_string(InputAtom, InputString),
    atom_json_dict(InputAtom, Request, []),
    build_response(Request, Response),
    json_write_dict(current_output, Response),
    nl.

:- initialization(main, main).
