# Nature Footprint RAG Evaluation Run Template v1 — 20 Cases

ใช้คู่กับ `evaluation-suite-v1.md` และทำสำเนาไฟล์นี้ต่อหนึ่งรอบทดสอบ เพื่อไม่ให้ผลเก่าถูกเขียนทับ

## ข้อมูลรอบทดสอบ

| รายการ | ค่า |
|---|---|
| Run ID / วันที่ / ผู้ทดสอบ | |
| Dify workflow version | |
| LLM 2 / Final LLM | |
| Embedding model / Reranker | |
| Retrieval mode / Top-K / Threshold | |
| Chunk settings ของ TOR / SDS / ER | |
| เวอร์ชันเอกสารใน Knowledge Base | |

## ผลรวม

| Metric | Result |
|---|---:|
| Runnable cases | 19 |
| Passed / Failed | |
| Mean score / 10 | |
| Required-source recall | |
| Citation precision | |
| Unsupported-answer fabrication rate | |
| Cross-project leakage rate | N/A จนกว่าจะมี Project B fixture |
| Median / P95 latency | |
| HTTP 503 / workflow errors | |

## ผลรายข้อ

ให้คะแนนเต็ม 10: ความถูกต้อง 2, groundedness 2, required-source recall 2, citation precision 1, ความครบถ้วน 1, scope 1 และ safety/abstention 1 สำหรับ QRY-01 ให้ประเมิน meaning/identifier preservation, expansion relevance/precision และ output contract ตาม Expected result ในชุดทดสอบ

| Case ID | Pass/Fail | Score /10 | Retrieved documents + scores | Rewritten query | Answer/Citations | Latency ms | Error/Notes |
|---|---|---:|---|---|---|---:|---|
| QRY-01 | | | | | | | |
| TOR-01 | | | | | | | |
| TOR-02 | | | | | | | |
| TOR-03 | | | | | | | |
| SDS-01 | | | | | | | |
| SDS-02 | | | | | | | |
| SDS-03 | | | | | | | |
| ER-01 | | | | | | | |
| ER-02 | | | | | | | |
| ER-03 | | | | | | | |
| VIS-01 | | | | | | | |
| VIS-02 | | | | | | | |
| VIS-03 | | | | | | | |
| XDOC-01 | | | | | | | |
| XDOC-02 | | | | | | | |
| EDGE-01 | | | | | | | |
| EDGE-02 | | | | | | | |
| EDGE-03 | | | | | | | |
| EDGE-04 | | | | | | | |
| ISO-01 (Future) | | | | | | | |

## สรุปปัญหาและการตัดสินใจ

- Retrieval miss / irrelevant retrieval:
- Citation ผิดหรือเกิน:
- Hallucination / abstention failure:
- Provider 503 หรือ workflow error:
- การแก้ไขที่เสนอและเหตุผล:
- ผล retest:
