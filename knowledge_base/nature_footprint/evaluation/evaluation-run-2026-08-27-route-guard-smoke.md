# AW5-RAG Route Guard Candidate — Manual Smoke Run — 2026-08-27

## Run status

- Candidate: `../../../dify/exports/aw5-rag-route-guard-candidate-2026-08-27.yml`
- Execution surface: Dify Preview, manually run and reported by the project owner
- Scope: seven representative questions covering ER-only, SDS-only, TOR-only, and multi-source routes
- Final routing result: **7/7 expected routes** after one Route Guard correction and retest
- Answer/citation result: owner confirmed the seven displayed answers and citations were correct; the corrected ER relationship retest also returned the expected answer
- This is a smoke run, not a fresh execution of the full 19-case suite

## Cases

| # | Question facet | Expected route | Final observed route | Outcome |
|---:|---|---|---|---|
| 1 | RBAC tables for users, roles, permissions, and organization membership | ER | ER | Correct answer included `UM_USER`, `UM_ROLE`, `UM_USER_ROLE`, `UM_FUNCTION`, `UM_ROLE_FUNCTION`, and `UM_USER_ORG`; citation confirmed. |
| 2 | `CALC_ASSESSMENT` to `CALC_RESULT` relationship and `MD_INDICATOR` link | ER | ER after Guard fix | Initial Guard incorrectly enabled TOR because `tor` matched inside `indicator`; token-boundary regex fixed it. Retest executed ER only and returned the expected relationships. |
| 3 | Upload/import formats, validation, and error reporting | SDS | SDS | Correct SDS answer and citation confirmed. |
| 4 | Figure 4-11 Scope 1–3 Ton CO2e values and percentages | SDS | SDS | Correct numeric evidence and citation confirmed. |
| 5 | Four indicator groups required by TOR clause 4.5 | TOR | TOR | Correct four groups and TOR citation confirmed. |
| 6 | SDS user groups plus ER tables supporting user/role/permission/organization membership | SDS + ER | SDS + ER | Correct cross-document answer and citations confirmed. |
| 7 | Compare TOR clause 4.5 with SDS figure 3-8 and identify missing indicators | TOR + SDS | TOR + SDS | Correct comparison, concluded none were missing, and citations confirmed. |

## Additional retrieval evidence

- ER Top K was increased from 6 to 7 because `UM_USER` appeared at result position 7 with score `0.3024823813773895` in the inspected RBAC retrieval output.
- Positions 1–6 were unchanged from the earlier result; the added seventh result supplied the missing base user table.
- This is targeted evidence for the RBAC completeness defect, not a general proof that Top K 7 improves every ER question.

## What this proves

- The final exported Guard corrects the observed `TOR` substring bug.
- The tested single-source and cross-source questions executed the intended branches.
- The seven representative answers were usable with precise citations in the owner-reviewed Preview runs.

## What remains unverified

- The 19 executable v1 questions have not been rerun after the final Guard and ER Top K 7 changes.
- Stability across repeated runs is not established.
- `ISO-01`, trusted tenant/project filtering, conversation memory, production deployment, and current Published state are not proven.

Do not promote this candidate over the frozen `19/19` baseline until the full regression passes and its evidence is recorded.
