# AW5-RAG automatic-metadata temperature-zero candidate — 2026-09-07

## Status

**Saved local candidate; not imported, run, Published, promoted, or formally
evaluated.** The owner supplied `AW5-RAG Test-4.yml` after adding Automatic
Metadata Filtering and the custom `source_file` metadata field. This candidate
preserves that export and changes one setting for a controlled diagnostic.

## Files and identity

- Supplied source: `/Users/digital/Downloads/AW5-RAG Test-4.yml`
- Supplied SHA-256:
  `2869269da327e4ee90a51726af45dd1016bf1e93e6a353194c1dafc02ddcf88f`
- Candidate:
  `aw5-rag-automatic-metadata-temp0-candidate-2026-09-07.yml`
- Candidate SHA-256:
  `cc2e8ac7961e157ab020b1dc167dd1e81e118de3c10c7b52e2a5aeaed673af61`

## Exact change

Within the Knowledge Retrieval node's `metadata_model_config`, the candidate
changes only:

```yaml
temperature: 0.7
```

to:

```yaml
temperature: 0
```

The answer LLM configuration is unchanged.

## Static validation

- Both YAML files parsed successfully with the available Ruby/Psych parser.
- Both graphs contain 5 nodes, 4 edges, one Knowledge Retrieval node, and three
  Knowledge Base references.
- Automatic Metadata Filtering remains enabled.
- A unified diff contains only the temperature value change.
- No API key, authorization header, bearer token, password, or credential field
  was found by the bounded secret scan.

## Required runtime check

Import this file as a duplicate test application and repeat the owner-authorized
two-conversation, two-turn filename probe. Do not treat a successful single run
as repeatability evidence. The current main workflow remains unchanged until the
owner explicitly promotes a tested candidate.
