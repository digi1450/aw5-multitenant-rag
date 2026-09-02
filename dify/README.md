# Dify workflow artifacts

The recorded baseline and experiments were run in Dify Cloud. The confirmed target
is now **Dify self-hosted on the owner's computer with locally stored knowledge,
cloud models, and one Knowledge Retrieval node**. See the
[current direction](../docs/architecture/current-direction-2026-09-02.md).
The owner subsequently supplied [AW5-RAG 1.2](exports/aw5-rag-1.2-current-2026-09-02.md)
as the current workflow; its export is preserved without modification. This update
does not install Dify, migrate knowledge, or modify a live workflow. No running Dify
application synchronizes automatically with GitHub.

After an authorized meaningful workflow change:

1. Export the application DSL/YAML from Dify.
2. Remove or verify that the export contains no API keys, tokens, or private credentials.
3. Save it under `dify/exports/` with a date or version in the filename.
4. Record the tested change and limitations. Commit or push only when the owner
   explicitly authorizes it.

Do not place provider API keys or private corpus files in this directory.

The owner-confirmed current export, frozen baseline, and dated candidate evidence are recorded in
[`exports/CURRENT.md`](exports/CURRENT.md). Consult that pointer instead of inferring
the latest workflow from filenames alone. The current export still uses TOR/SDS/ER
branches and source-specific prompts; preserve it as current-state evidence, not a
template for new uploads or the planned single-retrieval workflow.
Model/provider selection, reranking, knowledge-base organization, and installation
details remain undecided; ask the owner before selecting them.

## Custom model plugins

Custom model plugins are maintained in separate Git repositories. A local plugin
checkout may be placed under `dify/plugins/`, but that directory, generated
`.difypkg` files, and local `.env` credentials are excluded from this repository.
