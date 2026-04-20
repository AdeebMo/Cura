:- use_module(library(lists)).

count_overlap(Candidates, Confirmed, Count, Matches) :-
    intersection(Candidates, Confirmed, Matches),
    length(Matches, Count).

count_conflicts(Candidates, Denied, Count, Matches) :-
    intersection(Candidates, Denied, Matches),
    length(Matches, Count).

rule_strength(RequiredMatched, RequiredCount, SupportiveMatched, ConflictCount, strong) :-
    RequiredMatched =:= RequiredCount,
    SupportiveMatched >= 1,
    ConflictCount =:= 0,
    !.
rule_strength(RequiredMatched, RequiredCount, _, ConflictCount, moderate) :-
    RequiredMatched =:= RequiredCount,
    ConflictCount =< 1,
    !.
rule_strength(RequiredMatched, _, SupportiveMatched, ConflictCount, weak) :-
    RequiredMatched >= 1,
    SupportiveMatched >= 0,
    ConflictCount =< 1.

disease_score(Condition, Confirmed, Denied, Score, Diagnosis) :-
    disease(Condition, Required, Supportive, Contra),
    append(Required, Supportive, DiseaseSymptoms),
    length(Required, RequiredCount),
    count_overlap(Required, Confirmed, RequiredMatchedCount, MatchedRequired),
    count_overlap(Supportive, Confirmed, SupportiveMatchedCount, MatchedSupportive),
    count_conflicts(DiseaseSymptoms, Denied, DiseaseConflictCount, DiseaseConflicts),
    count_overlap(Contra, Confirmed, ContraConflictCount, ContraConflicts),
    TotalConflictCount is DiseaseConflictCount + ContraConflictCount,
    rule_strength(RequiredMatchedCount, RequiredCount, SupportiveMatchedCount, TotalConflictCount, RuleStrength),
    Score is (RequiredMatchedCount * 4) + (SupportiveMatchedCount * 2) - (TotalConflictCount * 3),
    Score > 0,
    append(MatchedRequired, MatchedSupportive, MatchedSymptoms),
    subtract(DiseaseSymptoms, MatchedSymptoms, MissingSymptoms),
    append(DiseaseConflicts, ContraConflicts, ConflictingSymptoms),
    diagnosis_explanation(Condition, MatchedSymptoms, MissingSymptoms, ConflictingSymptoms, Explanation),
    Diagnosis = diagnosis{
        condition: Condition,
        rule_strength: RuleStrength,
        matched_symptoms: MatchedSymptoms,
        missing_symptoms: MissingSymptoms,
        conflicting_symptoms: ConflictingSymptoms,
        explanation: Explanation
    }.

compare_scores(Order, ScoreA-DiagnosisA, ScoreB-DiagnosisB) :-
    compare(Order0, ScoreB, ScoreA),
    (   Order0 == (=)
    ->  length(DiagnosisA.missing_symptoms, MissingA),
        length(DiagnosisB.missing_symptoms, MissingB),
        compare(Order1, MissingA, MissingB),
        (   Order1 == (=)
        ->  compare(Order, DiagnosisA.condition, DiagnosisB.condition)
        ;   Order = Order1
        )
    ;   Order = Order0
    ).

extract_diagnosis(_-Diagnosis, Diagnosis).

take_first_n(_, 0, []) :- !.
take_first_n([], _, []).
take_first_n([Head | Tail], N, [Head | Result]) :-
    N > 0,
    NextN is N - 1,
    take_first_n(Tail, NextN, Result).

ranked_diagnoses(Confirmed, Denied, Diagnoses) :-
    findall(
        Score-Diagnosis,
        disease_score(_, Confirmed, Denied, Score, Diagnosis),
        ScoredDiagnoses
    ),
    predsort(compare_scores, ScoredDiagnoses, SortedScoredDiagnoses),
    maplist(extract_diagnosis, SortedScoredDiagnoses, SortedDiagnoses),
    take_first_n(SortedDiagnoses, 3, Diagnoses).
