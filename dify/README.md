# Dify workflow artifacts

The active AW5-RAG Chatflow currently lives in Dify Cloud and is not synchronized automatically with GitHub.

After a meaningful workflow change:

1. Export the application DSL/YAML from Dify.
2. Remove or verify that the export contains no API keys, tokens, or private credentials.
3. Save it under `dify/exports/` with a date or version in the filename.
4. Commit the export together with a short note describing the tested change.

Do not place provider API keys or private corpus files in this directory.
