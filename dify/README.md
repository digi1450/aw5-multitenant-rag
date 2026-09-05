# Dify workflow artifacts

The recorded baseline and experiments were run in Dify Cloud. The confirmed target
is now **Dify self-hosted on the owner's computer with locally stored knowledge,
cloud models, and one Knowledge Retrieval node**. See the
[current direction](../docs/architecture/current-direction-2026-09-02.md).
The owner subsequently promoted the Published
[self-hosted main workflow](exports/aw5-rag-self-hosted-main-2026-09-06.md);
its export is preserved without modification. It uses one retrieval node and one
deterministic source-enrichment Code node before the answer LLM. No running Dify
application synchronizes automatically with GitHub.

After an authorized meaningful workflow change:

1. Export the application DSL/YAML from Dify.
2. Remove or verify that the export contains no API keys, tokens, or private credentials.
3. Save it under `dify/exports/` with a date or version in the filename.
4. Record the tested change and limitations. Commit or push only when the owner
   explicitly authorizes it.

Do not place provider API keys or private corpus files in this directory.

The owner-confirmed current main export, previous snapshots, frozen baseline, and dated candidate evidence are recorded in
[`exports/CURRENT.md`](exports/CURRENT.md). Consult that pointer instead of inferring
the latest workflow from filenames alone. The current export uses one retrieval
node over three Knowledge Bases, generic source enrichment and a generic
evidence-grounded prompt. Its Published path and targeted five-case diagnostic
are recorded; formal quality, repeatability and isolation remain unverified.

## Custom model plugins

Custom model plugins are maintained in separate Git repositories. A local plugin
checkout may be placed under `dify/plugins/`, but that directory, generated
`.difypkg` files, and local `.env` credentials are excluded from this repository.
