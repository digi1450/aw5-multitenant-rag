# AW5 Chatflow

Import [`exports/aw5-rag.yml`](exports/aw5-rag.yml) into Dify **1.17.0** as a Chatflow. Configure the official Gemini provider, select your own available answer/resolver models, and connect your project's Knowledge Bases to the single Knowledge Retrieval node before publishing.

The template is derived from the owner-supplied baseline export dated 2026-10-15. The original is preserved only in the owner's local backup. Public-template changes are limited to a generic app label/description, removing local Knowledge Base IDs, dropping the unused private embedding-plugin dependency, and removing an inactive duplicate Resolver prompt field. Retrieval settings, active prompts, code and topology are preserved.

The reference model names are `gemini-3.5-flash-lite` for source resolution and `gemini-3.5-flash` for writing. The export references official Gemini plugin 0.9.10. Availability depends on your account; selecting another model is a new configuration and does not inherit any prior result. Embedding is configured on your Knowledge Bases, independently of the Chatflow's LLM nodes.

`aw5_registry_json` is a required input supplied by the AW5 backend. The Chatflow cannot be tested by entering a question alone in Dify's preview. Complete [installation](../docs/installation.md) and test through the authorized backend/Discord path. Do not add project-specific IDs or sample facts as default workflow inputs.

Python sources for the Registry parser and current context selector are in [`code/`](code/README.md). The main workflow uses the six-input context selector.

Dify state does not synchronize with Git. When changing your deployment, save a dated, secret-free DSL export and record the configuration and test scope. Never commit private corpus files or provider credentials.
