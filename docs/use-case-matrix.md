# Use-Case Matrix

Use this as a checklist before the final demo and as a quick reference during practice.

| Scenario | Example input | Expected normalization | Expected Prolog outcome | Why it matters |
| --- | --- | --- | --- | --- |
| Influenza-style respiratory pattern | `I have a high fever and coughing.` | `fever`, `cough`; phrase mappings for `high fever` and `coughing` | `influenza` near the top, follow-up about `body_aches`, `fatigue`, or `headache` | Demonstrates phrase normalization and follow-up reasoning |
| Allergy pattern | `I am sneezing` or `I am sneezing and have a runny nose` | direct token match for `sneezing`; maybe phrase match for `runny nose` | `allergy` is plausible or leading with eye-related follow-up | Good explanation example for direct token match vs phrase mapping |
| Covid-like viral pattern | `I lost my sense of smell and have fever and cough` | `loss_of_taste_smell`, `fever`, `cough` | `covid_like_viral_infection` rises in ranking | Shows multi-word phrase mapping and cross-condition overlap |
| UTI pattern | `I have painful urination and frequent urination` | `painful_urination`, `frequent_urination` | `urinary_tract_infection` leading, follow-up about lower abdominal pain | Good non-respiratory use case |
| Dehydration pattern | `I feel dizzy, my mouth is dry, and I am urinating less` | `dizziness`, `dry_mouth`, `reduced_urination` | `dehydration` leading, urgent dehydration alert may appear if vitals support it | Good red-flag explanation path |
| Emergency-style red flag | `I have chest pain and trouble breathing` | `chest_pain`, `difficulty_breathing` | urgent red flags triggered | Strong safety-defense example |
| Gastrointestinal pattern | `I feel nauseous and keep throwing up` | `nausea`, `persistent_vomiting` | food-poisoning-like reasoning may appear; urgent vomiting alert may appear | Shows richer synonym coverage |
| Follow-up answer | user answers `yes`, `no`, or `unknown` to asked question | no Lisp normalization for follow-up answer | Prolog re-runs with updated symptom state | Important to explain that follow-up answers skip Lisp |
| Invalid follow-up ID | answer sent with wrong `question_id` | none | backend rejects turn | Good validation example |
| Disclaimer rejected | session created with `disclaimer_accepted=false` | none | backend rejects session | Good safety and scope example |

## What To Remember

- Normalization is not diagnosis.
- `matched_phrases` does not mean "all recognized symptoms."
- Python is the coordinator.
- Lisp cleans language into symbols.
- Prolog reasons over symbols.
