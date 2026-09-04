# Gemini Embedding 2 local PDF pilot — 2026-09-02

## Scope and outcome

The owner approved a synthetic two-page PDF pilot after configuring the custom
Gemini Embedding 2 (AW5) provider credentials. Local Dify successfully indexed
native text and an image-only page, and each of three retrieval queries ranked
the expected source chunk first. This is a small ingestion/retrieval smoke test,
not an answer-quality evaluation or validation of the target AW5 workflow.

Only synthetic material was uploaded. No Nature Footprint material was used.
Chunk/query text and image content were processed by Google's cloud embedding
API through the custom provider; local Dify does not make this inference local.
No answer LLM or reranker was used.

## Fixture and configuration

- Local artifact: `output/pdf/aw5-local-pilot-2026-09-02/aw5-synthetic-text-image-pilot.pdf`.
- SHA-256: `387165bc7dde9d93273fc5a7eafdc46b7363b9c6a6ed7adbfa3d26f3d4e09a1e`.
- Page 1 has 447 native text characters, including audit retention of 37 days.
- Page 2 is a raster approval diagram with zero native text characters. Its
  labels include Mira, Orin, 11 hours and KITE-731, absent from native PDF text.
- Both rendered pages were visually inspected.
- Dify 1.17.0; custom Gemini Embedding 2 (AW5) plugin 0.1.4;
  model `gemini-embedding-2`.
- Dataset: `732f6ad0-313e-4fda-882c-737e311060ea`, UI name `aw5-synthetic-text...`.
- Document: `51fb6cf9-9722-4ca9-adfe-0af4557ccf36`.
- General chunking: delimiter `\n\n`, maximum 1024 characters, overlap 50;
  consecutive-whitespace preprocessing enabled, email/URL removal disabled.
- High Quality indexing; vector search, Top K 3, score threshold disabled,
  reranking disabled, summary and Q&A processing disabled.

These are pilot settings, not approved defaults for the real corpus.

## Observed retrieval results

Results below were read from Dify's Retrieval Testing UI. Scores are displayed,
rounded similarity scores, not probabilities or accuracy percentages.

| Case | Query | Rank 1 | Rank 2 | Expected source ranked first |
| --- | --- | --- | --- | --- |
| TEXT-01 | How long are audit records retained in Project Cedar Lantern? | Chunk-01 text, 0.77 | Chunk-02 image, 0.57 | Yes: text includes 37 days |
| IMAGE-01 | In the approval diagram, who gives final approval and how long is the authorization valid? | Chunk-02 image, 0.62 | Chunk-01 text, 0.59 | Yes: image contains Orin and 11 hours |
| IMAGE-02 | What request code is shown in the image-only approval diagram? | Chunk-02 image, 0.66 | Chunk-01 text, 0.60 | Yes: image contains KITE-731 |

Because there are only two chunks and Top K is three, both chunks appear in
every result. The observed distinction is their ranking. There were no distractor
documents or repeated runs. Retrieval of an image does not prove that an answer
LLM can receive, read or correctly answer from it.

## Image-processing evidence

The document and both segments have `completed` status with null errors.
Database inspection found:

1. Chunk-01 stores the native page-1 text.
2. Chunk-02 stores only
   `![image](/files/c0857bf9-ac8f-4dd5-afce-d715e13f536c/file-preview)`;
   it does not contain an OCR transcription of the diagram labels.
3. Chunk-02 has a 75,715-byte PNG attachment with that file ID.
4. The embedding cache has an entry keyed by that attachment ID for
   `digi1450/gemini_embedding_2_aw5/gemini_embedding_2_aw5` and
   `gemini-embedding-2`, with 13,842 stored vector bytes.

Inspection of the installed Dify PDF extractor shows native-text extraction
plus image extraction into file attachments. Its multimodal embedding cache
calls the provider for image documents, and the custom provider's image branch
sends image bytes as a Google GenAI `Part`. Together with the stored image
embedding and retrieval results, this supports direct image embedding rather
than an OCR-text-only route. It does not assert anything about the cloud model's
internal visual processing.

Dify recorded indexing latency of 4.694 seconds for this document. Its recorded
169 document tokens are not a verified total of billable image/text API usage.
Query latency, cost, vector dimensions, repeatability, Thai documents, scanned
multi-page documents, real-corpus quality and tenant isolation were not measured.

## Evidence and next boundary

Local, ignored evidence is in `output/pdf/aw5-local-pilot-2026-09-02/`:
`fixture-manifest.json`, `native-extracted-text.txt`, rendered pages,
`database-evidence.json`, `retrieval-results.json`, and `build_fixture.py`.

The next separate step would be selecting an answer model and verifying that a
Chatflow passes the retrieved image to a vision-capable LLM. No Chatflow was
created or published in this pilot, and no historical evaluation score or current
DSL was changed.
