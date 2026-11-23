# Annotation Guidelines v1

## Task
For each requirement in a job description, decide how well the resume
supports it, and copy the resume text that is your evidence.
Judge only what is written in the resume. Never use outside knowledge
about the person.

## Requirement labels

### supported
The resume directly states the skill, qualification or experience,
at the level the requirement asks for.
- Synonyms and spelling variants count (Postgres = PostgreSQL, ReactJS = React).
- Unambiguous implications count (Django -> Python). Add a note "inferred".
- A skill in a Skills list counts. Set evidence_type to "skills_list".
- Internships count as experience for entry-level requirements.

### partially_supported
The resume shows something related, but not what was asked.
- A similar tool (MySQL when PostgreSQL is required).
- The concept without the named tool.
- Coursework or a personal project when professional experience is required.
- Less duration than required (1 year when 3 are required).
- A soft skill with weak or indirect evidence.

### missing
No related evidence anywhere in the resume.

## Decision order
1. Is the exact thing stated or unambiguously implied? -> supported
2. Is something related present? -> partially_supported
3. Otherwise -> missing

## Evidence rules
- Copy the exact text from the resume. Do not paraphrase.
- Use the shortest span that proves the label (one bullet or one line).
- supported / partially_supported need at least one evidence span.
- missing has an empty evidence list.
- If several spans help, list up to three.

## Edge cases
| Case | Decision |
|---|---|
| Required "3+ years", resume dates show 2 years | partially_supported |
| Required "Python", resume lists "Python (beginner)" | partially_supported |
| Skill appears only in a project title | supported only if the bullet shows use |
| Degree "in progress" when a degree is required | partially_supported |
| "Strong communication", no evidence | missing |
| Cannot decide between two labels | choose the lower one and add a note |

## Claim labels (used in Phase 8, defined here now)
Applied to a sentence in a generated resume, compared with its source bullet.
| Label | Meaning | Example |
|---|---|---|
| supported | Same facts, near-identical wording | Source "Built REST API with Flask" -> "Built a REST API using Flask" |
| rephrased | Same facts, clearly reworded, nothing added | -> "Developed Flask-based web service endpoints" |
| needs_confirmation | Plausible, but not provable from the source | Source "Helped build a dashboard" -> "Led dashboard development" |
| unsupported | Adds a new fact: number, tool, employer, outcome, or contradicts the source | Source "Built a dashboard" -> "Built a dashboard that cut reporting time by 40%" |

Rule: any new number, tool, employer, date or outcome that is not in the source is unsupported.
Stronger verbs (led, owned, architected) are needs_confirmation.