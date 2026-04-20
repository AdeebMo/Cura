humanize_atom(Atom, Label) :-
    atom_string(Atom, RawLabel),
    split_string(RawLabel, "_", "", LabelParts),
    atomic_list_concat(LabelParts, ' ', LabelAtom),
    atom_string(LabelAtom, Label).

symptom_words([], "no additional symptoms").
symptom_words([Only], OnlyString) :-
    humanize_atom(Only, OnlyString).
symptom_words([First, Second], Output) :-
    humanize_atom(First, FirstString),
    humanize_atom(Second, SecondString),
    format(string(Output), "~w and ~w", [FirstString, SecondString]),
    !.
symptom_words([Head | Tail], Output) :-
    Tail = [_ | _],
    append(Middle, [Last], Tail),
    maplist(humanize_atom, [Head | Middle], PrefixStrings),
    atomic_list_concat(PrefixStrings, ", ", PrefixText),
    humanize_atom(Last, LastString),
    format(string(Output), "~w, and ~w", [PrefixText, LastString]).

diagnosis_explanation(Condition, Matched, Missing, Conflicting, Explanation) :-
    humanize_atom(Condition, ConditionString),
    symptom_words(Matched, MatchedText),
    symptom_words(Missing, MissingText),
    symptom_words(Conflicting, ConflictingText),
    format(
        string(Explanation),
        "~w is suggested because the current evidence includes ~w. Useful remaining evidence would be ~w. Conflicting evidence is ~w.",
        [ConditionString, MatchedText, MissingText, ConflictingText]
    ).

diagnosis_trace(Condition, RuleStrength, Matched, Missing, Conflicting, Trace) :-
    humanize_atom(Condition, ConditionString),
    symptom_words(Matched, MatchedText),
    symptom_words(Missing, MissingText),
    symptom_words(Conflicting, ConflictingText),
    atom_string(RuleStrength, RuleStrengthString),
    format(
        string(Trace),
        "~w has ~w support from matched symptoms: ~w. Remaining useful evidence: ~w. Conflicting evidence: ~w.",
        [ConditionString, RuleStrengthString, MatchedText, MissingText, ConflictingText]
    ).
