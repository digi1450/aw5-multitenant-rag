# Dify node code and installation references

## Backend-owned GET FILE REGISTRY — deployment recorded 2026-10-03

[`backend_file_registry.py`](backend_file_registry.py) replaces the SQL Registry
with a strict parser for the backend-authorized `aw5_registry_json` input. It
preserves the old Registry `json` wrapper consumed downstream. In the v3.2
graph the Registry parser is Code 1 and the context selector is Code 3; older
candidate instructions below use the previous node numbering. No tenant,
filename, document ID or dataset ID is hardcoded. Installation and tenant-1
registration were recorded on 2026-10-03; see `../exports/CURRENT.md`. Use
the [contract and Draft wiring instructions](../../docs/architecture/tenant-registry-contract-2026-10-03.md).
Do not change Code 2 or its six-input/five-output behavior during that wiring.

## Historical required-source Code 2 candidate

**Current workflow reference:** the owner-supplied
[Test4.7 v3-4 snapshot](../exports/aw5-rag-test4-7-v3-4-owner-supplied-2026-10-03.md)
contains the latest six-input/five-output Code 2 with other-source reservation
and fallback messages. The four-input Python file and installation steps below
describe the earlier intermediate candidate; they are not the current Code 2.
Use the preserved export and its handoff record when continuing current work.

สถานะ 2026-10-03: เตรียมโค้ดสำหรับติดตั้งด้วยมือใน Draft ของ Test4.7 v3
ผ่านการทดสอบ Python ออฟไลน์ 16 กรณี และ replay ผล Retrieval จาก run เดิม
ได้ outputs เดิมทั้งสาม field ตรงกัน ต่อมา owner ส่งผล single-node fixture
SELECTED และ ALL ซึ่งผ่านทั้งสองกรณี และรัน Draft v3 หนึ่งคำถาม
ตรวจ actual Writer prompt แล้วได้รับ selection_report และ context ที่เลือกจริง
นี่เป็น exploratory diagnostic ไม่ใช่การ Publish, formal evaluation,
หลักฐาน repeatability หรือ tenant isolation

ไฟล์ [required_source_context.py](required_source_context.py) เป็นโค้ดทั้งหมด
ที่คัดลอกไปวางใน Code 2 ได้ ใช้ standard library `json` และมี `main`
ตามรูปแบบ Code node ไม่มีชื่อไฟล์ corpus, tenant, document ID หรือ dataset ID
ตายตัว limit 15 เป็นงบ context กลาง ไม่ใช่ค่าที่พิสูจน์ว่าเหมาะที่สุด

## ตั้งค่า Code 2

1. ทำบน Draft candidate และเก็บโค้ดเดิมไว้สำหรับย้อนกลับ
   การเตรียมครั้งนี้เก็บ pre-change graph และ Code 2 ไว้ใน
   `output/workflow-candidates/2026-10-03-test4-7-v3-required-source-context/`
   ซึ่งเป็น local-only graph snapshot ไม่ใช่ DSL export ที่ import ได้ทั้ง app
2. ตั้ง Input Variables ตามตาราง แล้ววางโค้ดทั้งหมดจากไฟล์ Python
3. เพิ่ม Output Variable `selection_report` เป็น String
4. ตรวจ outputs เดิม `result`, `has_evidence`, `evidence_count`
   และ Context ของ LLM ที่อ่าน Code 2.result

| Input | เลือกตัวแปรจาก | Runtime type |
|---|---|---|
| `results` | Knowledge Retrieval → result | Array[Object] |
| `scope_mode` | Scope Resolver → structured_output → scope_mode | String |
| `document_names_csv` | Scope Resolver → structured_output → document_names_csv | String |
| `source_registry` | Get File Registry → json | Array[Object] |

| Output | Type |
|---|---|
| `result` | Array[Object] |
| `has_evidence` | Boolean |
| `evidence_count` | Number |
| `selection_report` | String |

อย่าเลือก `filter_names` จาก Code 1 เป็นรายชื่อ required sources:
NON_STRICT ส่ง null เพื่อเปิดการค้น แต่ชื่อที่ต้องตอบถึงยังอยู่ใน Resolver
อย่าเลือก Registry.text หรือส่งชื่อไฟล์/ID เป็นค่าตายตัว

## พฤติกรรมและข้อมูลรายงาน

- ALL: context เท่ากับ valid Top 15 เดิม ไม่ต้องมี Registry shortlist
- SELECTED: จับคู่ชื่อ exact กับ ID จาก Registry ต้องได้ ID เดียวต่อชื่อ
  ใช้ ID เลือก candidate อันดับสูงสุดจากแต่ละไฟล์ แล้วเติมตามอันดับเดิม
- ไม่ fuzzy match, เปลี่ยนตัวพิมพ์, แก้ชื่อ หรือสร้าง alias
- Unknown/ambiguous Registry mapping และ UNRESOLVED: ส่ง context ว่าง
  ค่า input ผิดรูปแบบ เช่น SELECTED ที่ไม่มีชื่อ แจ้ง error
- จำนวน anchors มากกว่า 15: เลือกตามอันดับ Retrieval ที่ดีที่สุด
  และรายงานไฟล์ที่เกินเพดาน ห้ามเพิ่มเพดานเงียบ ๆ
- การเลือกแต่ละ input entry เกิดครั้งเดียว แต่ยังเก็บ chunks ต่าง ๆ จาก
  เอกสารเดียวกันได้ และไม่เพิ่ม global deduplication ที่เปลี่ยน ALL behavior
- กรองรายการว่างตามเดิม รักษา original order และ metadata เดิม
  SOURCE_METADATA ใช้ document_id, document_name, dataset_id, dataset_name

`selection_report` เป็น JSON string มี fields:

- `candidate_coverage`: not_required / unresolved / complete / partial
- `required_sources`: ชื่อและ ID ที่ resolve ได้จาก Registry
- `required_sources_present`: มี candidate ใน context
- `required_sources_not_retrieved`: ไม่มี candidate ที่ระบุ ID ได้ในผลค้น
- `required_sources_omitted_by_limit`: มี candidate แต่พื้นที่ไม่พอ
- `required_sources_unresolved`: ชื่อจับคู่กับ Registry ไม่ได้แบบเอกเทศ

`complete` หมายถึง candidate ครบตามแหล่งที่ระบุเท่านั้น ไม่ได้หมายถึงตอบครบ
รายงานไม่พบ candidate ไม่ใช่การยืนยันว่าเอกสารทั้งฉบับไม่มีข้อมูลนั้น
Registry ที่ไม่ครบหรือ scope ผิดยังเป็นข้อจำกัดจาก upstream
Code 2 เลือกจากผล Retrieval ที่ได้รับเท่านั้น ไม่ได้ให้อำนาจค้นโครงการอื่น
ไม่มีการกัน candidate จากไฟล์อื่นที่ไม่ได้ระบุชื่อใน patch นี้

## ตรวจโหนดก่อนทดสอบคำตอบ

local-only diagnostic fixture ถูกเตรียมไว้ที่
`output/workflow-candidates/2026-10-03-test4-7-v3-required-source-context/`:

- `node-test-results.json`: 30 candidates, A.pdf อยู่ลำดับ 17
- `node-test-registry.json`: Registry สำหรับชื่อ A.pdf และ ID จำลอง

ใน Test Run ของ Code 2 ให้ใช้ results จาก fixture แรก, SELECTED,
document_names_csv = A.pdf และ source_registry จาก fixture ที่สอง
ต้องได้ 15 items ที่ metadata.position เป็น 1–14 และ 17 ตามลำดับ
selection_report ต้องแสดง A.pdf ใน required_sources_present
fixture ใช้เฉพาะการทดสอบโหนด ไม่ใช่ default, prompt หรือ routing ของ app

ทดสอบ ALL ด้วย results ชุดเดียวกัน: ต้องได้ 1–15 ตามเดิม
ฟอร์ม Test Run อาจบังคับทุกช่อง ให้ใช้ A.pdf ในช่องชื่อสำหรับ ALL ได้
และ Registry fixture เดิมได้ โหมด ALL ไม่ใช้สองค่านี้เพื่อเลือก context

## การใช้รายงานใน Writer เป็นขั้นถัดไป

การประกาศ output ใหม่ไม่ส่งให้ Writer อัตโนมัติ ให้นำ selection_report เข้า system prompt
ผ่านตัวเลือกตัวแปรของ Dify แยกจาก retrieved evidence และระบุว่าเป็นสถานะ
candidate coverage เท่านั้น Writer ต้องตรวจ content ก่อนอ้างข้อเท็จจริง
และใช้ document_id ใน required_sources คู่กับ SOURCE_METADATA เพื่อระบุไฟล์
ให้ถูกต้อง ห้ามใช้สถานะ present/complete แทนการตรวจว่ามีหลักฐานรองรับคำตอบ

Owner-run วันที่ 2026-10-03 ยืนยันการเชื่อมรายงานและ context สำหรับหนึ่งคำถาม
แบบ SELECTED / NON_STRICT ในบทสนทนาใหม่ หลักฐานอยู่ใน local-only package
`output/research-evidence/experiments/2026-10-03-test4-7-v3-required-source-writer-owner-run/`
รอบนี้ required source อยู่ rank 1 จึงไม่ทดสอบกรณี required source ต่ำกว่า rank 15
ในข้อมูลจริง ส่วน missing/multiple required sources ยังไม่ผ่าน live diagnostic
Citation metadata เก็บทุก candidate ที่ส่งเป็น context ไม่ได้ยืนยันว่าแต่ละไฟล์
ถูกใช้รองรับข้อเท็จจริงในคำตอบ จึงยังไม่ถือว่าตรวจ citation precision ครบ

## ตรวจออฟไลน์

```sh
python3 -m unittest discover -s tests -p 'test_dify_required_source_context.py' -v
```

ชุดทดสอบใช้ข้อมูลจำลองทั่วไป มีกรณีลำดับ 1/17/30, หลายไฟล์, ไม่มี candidate,
ชื่อซ้ำ, exact names, malformed inputs, metadata หาย, overflow และ ALL
การ replay ผลค้นจริงทำในหน่วยความจำ เก็บเพียง hashes และรายงานไว้ใน
`output/research-evidence/experiments/2026-10-03-test4-7-v3-required-source-code2-offline/`
โดยไม่ได้ยิงโมเดลเพิ่ม หลักฐานทั้งหมดอยู่ในเครื่องและถูก exclude จาก Git
