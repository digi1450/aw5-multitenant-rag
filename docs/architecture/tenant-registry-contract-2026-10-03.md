# AW5 tenant registration and registry contract — 2026-10-03

## Later administrator implementation — 2026-10-03

The [local onboarding portal](admin-onboarding-2026-10-03.md) now implements
explicit-ID CLI/API registration, private backend credential entry, key binding
proof, and existing/new role provisioning. Live login/model and command checks
passed; actual new project enrollment and ISO-01 remain unverified. Older
preparation sections below retain the state before this implementation.
Current source adds Discord role changes and explicit AW5 registration deletion;
see [the 2026-10-15 checkpoint](progress-2026-10-15.md). Automatic ingestion
metadata, arbitrary Dify app/key rebinding and automatic orphan repair remain
future work.

## Earlier Registry deployment update — 2026-10-03

The owner installed/tested the parser, Published v3.2 and authorized a switch
of the existing tenant. See the [v3.2 deployment record](../../dify/exports/aw5-rag-test4-7-v3-2-owner-supplied-2026-10-03.md).
Six Draft diagnostic turns, including same-conversation input replacement,
were inspected. Backend Registry code is now loaded and tenant 1 points at
the new Published app; health, active status, key binding and role eligibility
were checked. The owner subsequently reported a Discord answer after the
STRICT seek guard; this is not formal evaluation or isolation evidence.
The switch used a controlled one-time transaction and encrypted rollback;
the planned generic admin rebind API/UI is still not implemented. Ten open
ticket conversation pointers were reset because the previous conversations
belong to another app. Earlier preparation-only status below is historical.

## Owner-confirmed decisions

The owner confirmed this contract on 2026-10-03 after discussing existing
document metadata, Discord role provisioning and safe Dify key entry.
The following are design decisions, not claims of implemented admin features.

- One AW5 tenant is one software project; `tenant_id` remains the only project
  scope identifier. Dify's internal Workspace tenant identifier is separate.
- Administrators may specify an existing AW5 `tenant_id` when registering a
  project. Preserve document metadata rather than allocate a replacement ID.
  Reject collisions explicitly; never silently replace an existing mapping or
  choose another number. Active IDs remain stable. A deliberate reconnect or
  configuration update must be a distinct authorized operation.
- For new documents, register the project first so a future trusted ingestion
  path can apply its tenant metadata. Automatic assignment is not implemented.
- Target onboarding UX: a private AW5 admin form for tenant ID, name, Dify App
  ID/key, and selection of an existing Discord role or creation of a new role.
  The current hidden local CLI prompt remains a valid entry/recovery path.
- Dify keys go directly to the AW5 backend; never collect them in Discord
  messages, DMs or modals. Keep encryption at rest, masked/read-protected
  management, secret redaction and authenticated admin operations.
- A separate provisioning bot is optional. It can separate `Manage Roles`
  authority from the chat bot only if tokens and runtime access are actually
  separated. Which identity to use is deferred; no new bot is approved here.
- Backend registration binds role ID, app identity/key and project tenant.
  Validate the binding and selected corpus before activation. Partially
  configured projects stay pending; retries must not produce duplicate roles.
- Backend derives request tenant from the stored ticket and current Discord
  membership. Role names, user text, client IDs, file metadata and model output
  cannot independently grant scope. Metadata is a consistency check against
  registered scope, not a source of user authorization.

## Work sequence

1. Record the contract.
2. Repair the Registry boundary in the v3 path using backend-authorized data.
3. Add the admin UI, explicit-ID enrollment and optional role automation later.

We choose the backend-owned inventory approach for the Registry preparation:
reuse the fresh document scan instead of another SQL read in Dify. Preserve
Resolver, Code 1, Retrieval, Code 2, Writer and their RAG settings.

## Repository implementation prepared in this change

- `aw5_backend/service.py` retains one validated per-request inventory together
  with the checked Published workflow/dataset selection. Ask uses the ticket's
  tenant; `/list` reuses that scan and returns display fields only.
- `aw5_backend/integrations.py` retains document IDs, selected dataset IDs and
  optional `document_type` from Knowledge API metadata. It checks all document
  tenants, including non-available documents, and does not change metadata.
- `aw5_backend/source_registry.py` builds a bounded query-based shortlist from
  that inventory. It rejects mismatched tenant/dataset IDs, duplicate document
  IDs and oversized payloads. Available documents only; cap 20; filename/type/
  token score weights remain 100/50/10. Python Unicode tokenization/collation
  is not asserted equivalent to PostgreSQL for every language/name.
- Chat requests send `inputs.aw5_registry_json` as a JSON string and the captured
  `workflow_id` as a top-level request field. A compatible v3 replacement node
  receives the registry string and emits the existing `[{'data': [...]}]`
  wrapper used by Resolver and Code 2. No tenant or document scope is inferred
  by that node.
- Installed Dify source inspected in this change supports explicit Published
  workflow selection and checks that workflow against the key-selected app and
  Workspace. It rejects Draft IDs. Advanced-chat prepares request inputs anew
  even with an existing conversation; the payload is not frozen to the first
  question. These are source findings, not live API verification of this patch.

Explicit version selection narrows app/key and Publish-routing mismatch during
dispatch. The administrator registration path still does not independently
verify key/app identity before activation. Pinning does not freeze mutable KB
documents; those protections and direct Dify entry restrictions remain open.

## Dify Draft installation — pending

The owner will edit Dify manually. A separate Thai walkthrough is available in
[Dify Registry installation](dify-registry-manual-install-2026-10-03.md).

The preserved owner v3-4 export is untouched. Its original SQL Registry still
contains `tenant_id = '1'`. The running application is not fixed merely because
backend source sends a new input: legacy graphs do not consume it.

Use a duplicate Draft and retain a rollback export before installation:

1. In User Input, add a **required Paragraph** named `aw5_registry_json`, with
   maximum length 65536 and no default, diagnostic data or corpus-specific value.
2. Replace the Database Client GET FILE REGISTRY node with a Python Code node.
   Paste `dify/code/backend_file_registry.py`.
3. Define `registry_json` (String) from User Input → `aw5_registry_json`.
4. Define output `json` as Array[Object]. Reconnect the graph and both consumers:
   Resolver Jinja `source_registry` and Code 2 `source_registry` must read the
   replacement Registry → `json`, not the retired SQL node's ID.
5. Preserve every other node, prompt, retrieval setting, source-scope mode and
   Code 2 output. Remove the retired Database Client dependency only after
   confirming no other node uses it. Keep original snapshots as controls.
6. Missing/malformed/oversized registry is an error; an empty valid shortlist is
   `[{'data': []}]`. Never supply a default tenant or broaden scope on error.

This replacement imports only Python standard-library modules; sandbox import
support and graph rewiring still need a controlled node/Draft check. Required
paragraph input changes the direct Dify test/web UX: owner diagnostics must use
an explicitly generated authorized fixture. A user-supplied envelope is not
authentication, even if its contents pass structural validation.

There is no automatic Publish, container restart, or live Dify mutation in this
change. Do not activate Project B against the old hardcoded Registry. Before a
production switch, record the candidate export, authorize the bounded diagnostic
and deployment, and verify the actual Published graph consumes the contract.

## Verification and remaining work

The focused backend/bot/registry suite passes **44 offline tests**. Synthetic
tenant IDs other than 1 exercise the request contract; they are not another real
project, a formal evaluation, or ISO-01. Tests include fresh role/document
checks, tenant/dataset mismatch rejection, disabled file exclusion, exact
filenames, duplicate-name ambiguity, malformed input, payload limits, captured
version forwarding and reuse of one scan per operation.

Owner v3-4 export SHA-256 remains
`637d6169d571637e9c3505c4ee034f042f3d6288e6d92bef8cc17d14f54c72c2`.
No inference requests or corpus uploads were made. Current live RAG behavior,
node sandbox/rewiring, Publish pinning, shortlist parity on real questions,
latency/reliability and cross-project isolation remain unverified for this patch.

At the preparation checkpoint, explicit-ID CLI/API enrollment, the admin form,
role provisioning, automatic ingestion metadata and key binding were **planned**.
The later administrator implementation above supersedes the onboarding status. The old enrollment command returned a generated ID; the current command requires an explicit ID.
Switching an existing tenant to a new v3/duplicate App ID also needs a reviewed
rebind operation; the current CLI does not provide it. Publishing the duplicate
does not change the registered app. Preserve the existing tenant ID during that
future switch rather than registering another generated tenant.

Focused command:

```sh
.venv/bin/python -m unittest tests.test_aw5_backend tests.test_discord_bot tests.test_backend_source_registry
```
