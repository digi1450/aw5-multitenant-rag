# Gemini Embedding 2 (AW5): signed local installation

## Outcome and scope

On 2026-09-02 the owner authorized signing the existing AW5 plugin and trusting
its public key in local Dify. **Gemini Embedding 2 (AW5) 0.1.4 installed
successfully** in Dify 1.17.0. The browser showed `Installation successful`, then
the provider card with `API key required`.

This verifies package acceptance, dependency installation and provider discovery.
It does not verify Google credentials, embedding inference, indexing, retrieval
quality or tenant isolation. No private corpus was uploaded and no model call was
made by this installation. The existing official Gemini provider remained listed
with its owner-configured `aw5-gemini` credential name.

## Cause and remedy

The original package lacked a trusted signature while the local daemon enforced
`FORCE_VERIFYING_SIGNATURE=true`. We retained enforcement and enabled third-party
verification with a new locally controlled public key, following
[Dify's signing guide](https://docs.dify.ai/en/develop-plugin/publishing/standards/third-party-signature-verification).

The original package and plugin source were preserved. Signing added only
`.verification.dify.json`; every original archive entry was compared byte-for-byte
with the signed archive and matched. The Dify CLI verified the signed package
against the generated public key before upload.

## Local artifacts

- Original: `dify/plugins/gemini-embedding-2-aw5-v0.1.4.difypkg`.
- Signed copy: `dify/plugins/gemini-embedding-2-aw5-v0.1.4.signed.difypkg`.
- Both packages remain ignored by the AW5 Git repository.
- Original SHA-256:
  `04365e1cc3b23f685dc5d9d75c226e978a0bb5b2d8bf490d8d38fb158c570c72`.
- Signed SHA-256:
  `dc916b77b4dff9b1bacd8df1d35327ad45d3ea8edd100101db0fa0daa25a2e3e`.
- Public PEM file SHA-256:
  `5532a3649ce0e122a6fe609c03174387741549ab994a197f9dabc712182eae44`.

The key pair is stored in `/Users/digital/Documents/Code/dify-local/.local-signing/`
as `aw5-plugin-signing.private.pem` and `aw5-plugin-signing.public.pem`. The
directory has mode `0700`, the private key has mode `0600`, and the directory is
excluded using the runtime checkout's `.git/info/exclude`. It is not mounted into
any container. Retain the private key securely for signing future approved builds;
any package signed by that key can be trusted by this deployment.

Only the public key is copied to `dify-local/docker/aw5-public-keys/`, also excluded
from the runtime Git checkout, and mounted read-only at `/app/aw5-public-keys` in
`plugin_daemon`. The Compose override sets:

```yaml
environment:
  FORCE_VERIFYING_SIGNATURE: "true"
  THIRD_PARTY_SIGNATURE_VERIFICATION_ENABLED: "true"
  THIRD_PARTY_SIGNATURE_VERIFICATION_PUBLIC_KEYS: /app/aw5-public-keys/aw5-plugin-signing.public.pem
volumes:
  - ./aw5-public-keys:/app/aw5-public-keys:ro
```

These three effective environment values were checked inside the recreated
daemon. Only `plugin_daemon` was recreated with
`docker compose up -d --no-deps plugin_daemon`; the database and other services
were not recreated. Localhost-only nginx publishing and the absence of a
host-published plugin debugging port were preserved.

The upload dialog displayed a `Verified by Dify` badge, but the actual trust
source here is the owner's newly configured signing key. This is not evidence of
Dify Marketplace review or endorsement.

## Future packages and rollback

Sign each approved new `.difypkg` with the retained private key, then verify it
using the public key before installing. Changing package contents requires a new
signature. Never put the private key into a package, Git commit or container.

The pre-change Compose override is preserved at
`dify-local/.local-signing/docker-compose.override.before-signing.yaml`. To revoke
this trust later, remove the third-party verification settings and public-key
mount from the current override, preserving unrelated changes, and recreate only
the daemon. Revoking a key does not uninstall a previously installed plugin.

No code, dependency or manifest version changes were needed. The separate plugin
Git repository remains unchanged; no commit, push or release was performed.
