# Synthetic demo corpus

These three files describe an invented library-loan service and were written for this repository. They contain no original case-study material, student details or real personal data.

Import each file into its own Dify Knowledge Base:

- [`requirements.md`](requirements.md)
- [`design.md`](design.md)
- [`schema.md`](schema.md)

Set a numeric `tenant_id` on every imported document, using the same ID that you register in AW5. Optional `document_type` values are `requirements`, `design` and `schema`. The file names and example questions must not be hardcoded into workflow prompts, branches or defaults.

Try asking what evidence describes loan creation, comparing the loan rule with the schema constraint, or explicitly asking for evidence from one file. These are demonstration ideas, not an evaluation protocol or guaranteed expected answers.
