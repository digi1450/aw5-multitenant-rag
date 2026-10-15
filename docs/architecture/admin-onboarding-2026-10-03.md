# Local administrator onboarding — 2026-10-03

## Current source checkpoint — 2026-10-15

See [the current progress record](progress-2026-10-15.md). The portal now resolves
Dify App ID from the supplied App API key through the restricted digest view;
the user no longer needs to enter App ID. Registered projects show Discord role
names with expandable Role ID and Dify App ID details. A role-name lookup failure
retains the numeric binding without treating the role as deleted.

The portal implements existing/new role changes with a separate journal and
explicit AW5 project deletion with exact-name and stale-binding confirmation.
Deletion removes AW5 registration, dataset and ticket/conversation mappings and
completed journals; it does not delete Discord roles/messages or Dify resources.
Incomplete journals block deletion. Automatic orphan repair and arbitrary Dify
app/key rebinding remain unimplemented. The original checks below are dated
historical observations, not fresh deployment verification of these additions.

## Original implementation and deployment record

The AW5 backend serves a local form at `http://127.0.0.1:8765/admin`.
Discord `/aw5-admin` obtains a one-use link from the backend and replies
privately. There is one bot; no separate administrator bot is required.
The administrator supplies a stable AW5 tenant ID, display name, app API key,
and an existing project role or a request to create a role. The original form
also required Dify app UUID; current source resolves it from the key.
The backend uses its PostgreSQL registry, not per-project JSON files.
Existing tenant IDs and document metadata are not rewritten.

Configured owner-provided identifiers:

| Setting | Value |
| --- | --- |
| Guild | `1553804321160953937` |
| Admin channel | `1555932507952644288` |
| Admin role | `1555931570886410270` |
| Portal origin | `http://127.0.0.1:8765` |

The configured `.env` files remain ignored and private. Source defaults leave
administration disabled unless both channel and role are configured.

## Use

1. Give trusted administrators the AW5 Admin role. Allow View Channel,
   Send Messages, Read Message History and Use Application Commands in the
   private admin channel for that role and the bot. AW5 Admin does not require
   Discord Administrator or Manage Roles permission.
2. Give AW5-Bot Manage Roles if it should create roles, and keep its role above
   project roles. New roles have `permissions=0`, are not mentionable and do not
   confer server management powers. Selecting an existing safe role remains
   available without creation permission.
3. Prepare and Publish the project's Dify app yourself. It must accept required
   `aw5_registry_json`, use the generic backend registry contract, and retrieve
   only the intended project's Knowledge Bases. All documents must have the
   exact AW5 tenant ID you intend to register. The portal does not edit metadata,
   create Dify apps, alter workflows, or Publish.
4. Run `/aw5-admin` in the admin channel, then click the private link on the
   computer running AW5. It expires after three minutes and is consumed once.
5. Enter the explicit tenant ID and name, and that app's Service API key.
   The backend resolves its App ID through the restricted digest-only view. The workspace Knowledge API key is already
   backend configuration; do not use it as an app key. Select an existing role
   or choose creation of a role with the project name.
6. Submit. The backend proves app/key binding, inspects Published selection,
   checks document metadata and required registry input, and reserves an
   onboarding request before creating a role. It rechecks admin membership and
   Published selection before committing registration. Duplicate tenant IDs,
   app IDs and registered roles are rejected; no existing project is overwritten.
7. Give members the returned project role using Discord. `/start` automatically
   offers the projects their current roles authorize. No per-user AW5 enrollment
   or source-code edit is needed. Future Published dataset changes still use
   the existing automatic sync and metadata validation.

The legacy terminal/admin-token registration route now also requires an
explicit tenant ID and proves app/key binding. Its CLI flag is `--tenant-id`.
The portal performs the additional provisioning checks before committing.

## Trust and secret boundary

- The Discord bot authenticates to AW5 with its existing service token. The
  backend checks exact configured guild/channel and current member role before
  issuing a capability for the requesting Discord user. Channel visibility and
  client-provided user IDs alone are not authorization.
- The capability appears only in a URL fragment, not in a query or HTTP path.
  The page removes it from browser history and exchanges it for a session.
  Tokens are bearer capabilities: do not forward the private link.
- Sessions expire after 15 minutes, are held in backend memory, and require an
  HttpOnly/SameSite Strict cookie. Mutations also require the exact configured
  Origin and an in-memory CSRF token. Every portal request rechecks the current
  admin role; changes already in flight cannot be undone by later role removal.
- The browser sends the app key directly to loopback AW5. There is no Discord
  message/modal containing the key and no localStorage/sessionStorage entry.
  Keys are encrypted with the existing backend Fernet key at rest.
- `aw5_app_key_bindings_v1` is a separate restricted Dify database projection:
  only app UUID and SHA-256 token digest for app tokens. The sync reader receives
  SELECT on this projection; it receives no access to the API token base table
  or plaintext tokens. The existing Published projection remains unchanged.
  This is an explicit narrow DB dependency, not a documented Dify Service API.
- The portal remains loopback only. Remote administrators and Codex Cloud cannot
  open this host's localhost URL. Remote access, HTTPS and federation would need
  a separately authorized design; this deployment does not expose a public port.

## Provisioning failure and retry

`onboarding_requests` is an AW5 database journal. A request is bound to the
administrator and a fingerprint of its submitted settings. App registration
and journal completion commit in the same database transaction. Replay of a
completed request returns the registered project; it does not create a new role.
The page preserves a retry ID only in its current memory while the data stays
unchanged. Unique tenant/app reservations also protect retries after refresh.

Discord creation has no automatic retry: a timeout may have created a role even
if no reply arrived. Such operations are retained as `needs_attention`, or
`in_progress` after a process crash. They do not activate a new project. Repeating
registration is rejected until the external state is reconciled. A role created
before a later Publish/authorization/DB failure can remain unused in Discord.

**Recovery limitation:** automatic orphan repair and arbitrary Dify app/key
rebinding remain unavailable. Role changes and deliberate registration deletion
are now implemented as described above; deletion cannot bypass pending journals.
Inspect the journal's request/tenant/app/state/role fields, the actual Discord
role and AW5 project row. If the role ID was not returned, inspect Discord's
role list/audit log rather than guessing from a display name alone. An operator
must deliberately reconcile/remove the orphan and reservation before a new
attempt. Do not delete a reservation or repeat role creation blindly. Secrets,
key ciphertext and full private database dumps are not recovery evidence.

## Verification and limits

**Current offline check (2026-10-15):** all 100 tests passed with
`.venv/bin/python -m unittest discover -s tests`. This uses fixture dependencies
and mocks; it does not validate live role creation, Dify inference or isolation.


**Historical offline check (2026-10-03):** 57 focused tests passed: existing backend/bot/registry
44 cases plus 12 onboarding cases and one HTTP route/security case. Coverage
includes guild/channel restriction, admin role removal, link single use/expiry,
Origin/CSRF checks, app-key and tenant-metadata failure, required registry input,
explicit tenant IDs/encrypted key, completed-request replay, ambiguous creation,
and a Publish change before registration. HTTP tests use fixture dependencies,
not real Dify inference or Discord role creation.

**Verified live without inference or project creation:** owner has the configured
admin role; bot initially lacked Manage Roles and had it after the owner changed
permissions; existing tenant 1 remains active; the key digest view accepts its
actual app key and rejects a wrong fixture key. Backend health returned 200.
Login exchanged successfully into an HttpOnly/SameSite Strict session; model
returned one existing project and role creation enabled; link replay returned
403 and logout returned 200. Discord guild commands include `aw5-admin` along
with start/ask/list/close. API and bot containers were recreated to load `.env`
changes and mounted sources.

**Verified SQL in isolation:** real AW5 PostgreSQL TEMP tables confirmed explicit
IDs, atomic registration/journal completion, completed-state protection and
duplicate rejection. The transaction was rolled back; no fixture project or
role was added to the actual registry.

**Not verified:** an actual new role/new project enrollment, real Project B,
ISO-01 isolation, orphan repair, remote multi-admin use, and large-file load.
The owner previously reported a Discord answer after the v3.2 strict seek guard;
this onboarding check did not send another question or evaluate RAG quality.

Read-only pre-change projection state, admin configuration rollback values and
local deployment notes are in ignored `output/admin-onboarding/2026-10-03/`.
No credentials were printed or committed. No commit/push was performed for this
implementation; unrelated pending registry/export changes remain preserved.
