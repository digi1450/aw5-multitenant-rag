# วิธีแก้ Dify v3: GET FILE REGISTRY ใช้ข้อมูลจาก backend

สถานะปัจจุบัน: เจ้าของติดตั้งและ Publish v3.2 เมื่อ 2026-10-03 แล้ว
ดู `dify/exports/CURRENT.md` และบันทึก deployment ก่อนทำงานต่อ ขั้นตอนด้านล่าง
เก็บเป็นคู่มือการติดตั้งเดิม ไม่ได้หมายความว่ายังรอติดตั้ง และไม่ใช่การยืนยัน
ว่า export เก่าตรงกับทุกการแก้ไขในระบบล่าสุด

## 1. เก็บของเดิมและทำบนสำเนา Draft

Export v3 ปัจจุบันเก็บเป็น rollback แล้ว Duplicate app สำหรับแก้ registry
อย่าแก้ไฟล์ export ที่เก็บเป็นหลักฐานย้อนหลังใน repository

## 2. เพิ่ม input ใน User Input / Start

| ช่อง | ค่า |
| --- | --- |
| Variable name | `aw5_registry_json` |
| Type | Paragraph / ข้อความหลายบรรทัด |
| Required | เปิด |
| Maximum length | `65536` |
| Default | เว้นว่าง |

ช่องนี้รับ JSON string ที่ backend สร้างหลังตรวจสิทธิ์และไฟล์แล้ว ไม่ใช่ช่อง
ใส่ Dify API key และไม่ต้องเพิ่ม input `tenant_id` ให้ผู้ใช้เลือกเอง

## 3. เปลี่ยน GET FILE REGISTRY

สร้าง **Code node → Python** สำหรับแทน Database Client node เดิม ใช้ชื่อ
GET FILE REGISTRY ได้ วางโค้ดทั้งไฟล์
[`backend_file_registry.py`](../../dify/code/backend_file_registry.py)

ตั้ง Input Variables:

| ชื่อใน Code node | เลือกตัวแปรจาก |
| --- | --- |
| `registry_json` | User Input → `aw5_registry_json` |

ตั้ง Output Variables:

| ชื่อ | Type |
| --- | --- |
| `json` | Array[Object] |

โค้ดคืน wrapper รูปแบบเดียวกับ SQL tool เดิม: `[{"data": [...]}]`
ไม่ต้องใส่ SQL, database password หรือ tenant ID ลงในโหนดใหม่

## 4. เชื่อมเส้นและตัวแปรใหม่

เส้น workflow: `User Input → GET FILE REGISTRY ใหม่ → Scope Resolver`

ใช้ตัวเลือกตัวแปรของ Dify เลือก output จากโหนดใหม่ทั้งสองจุด:

1. Scope Resolver → Jinja2 variable `source_registry`
   เลือก **GET FILE REGISTRY ใหม่ → json**
2. Code 2 → Input variable `source_registry`
   เลือก **GET FILE REGISTRY ใหม่ → json**

แม้โหนดจะใช้ชื่อเดิม แต่ node ID ใหม่อาจต่างกัน ตัวแปรที่อ้าง SQL node เดิม
จึงต้องเลือกใหม่ ไม่ควรพิมพ์ node ID ตายตัว ตรวจให้ไม่มีตัวแปรอ้างโหนดที่ลบ
แล้วจึงถอด SQL node เก่าออกจาก path ที่ทำงาน

## 5. เก็บส่วนอื่นของ v3 ไว้ตามเดิม

รักษา Resolver prompt/schema, Code 1, Retrieval, Code 2 และ Writer โดยเฉพาะ
STRICT/NON_STRICT, `seek_other_sources`, context limit และ fallback เดิม
ครั้งนี้เปลี่ยนผู้จัดหา Registry เท่านั้น

## 6. บันทึก Draft แล้วแจ้งว่าเชื่อมเสร็จ

ยังไม่ต้อง Publish หรือรีสตาร์ตบริการเพื่อทดลองทั้งระบบทันที ควรตรวจ
การ parse ใน Code node และการเชื่อมตัวแปรก่อน พร้อมเก็บ snapshot หลังแก้

การ Test Run ใน Dify โดยตรงต้องมี `aw5_registry_json` เพราะเป็น required input
ให้ใช้ payload ที่ backend สร้าง หรือ fixture แยกเฉพาะ node diagnostic;
อย่าใส่ JSON/ชื่อไฟล์/tenant ตัวอย่างเป็น Default ของ app การผ่าน parser
ด้วย fixture ไม่ใช่หลักฐานตรวจสิทธิ์หรือ isolation

หลังตรวจ Draft และอนุมัติการเปิดใช้ ค่อย Publish และชี้โปรเจกต์ไปยัง app ที่
ใช้ contract นี้ ระบบยังใช้ SQL เดิมจนกว่าจะติดตั้ง/เปิดใช้การเปลี่ยนนี้จริง

ถ้าแก้บนสำเนาหรือ app v3 ที่มี App ID ต่างจากตัวที่ Discord ใช้อยู่ การกด
Publish อย่างเดียวจะไม่เปลี่ยน app ที่ backend ผูกไว้ ขั้นเปิดใช้ต้องเปลี่ยน
App ID/key ของโปรเจกต์เดิมอย่างมีการตรวจสอบ โดยรักษา `tenant_id` เดิม
ไว้ ไม่ลงทะเบียนเป็นโปรเจกต์ใหม่เพื่อให้ระบบออกเลขใหม่ ปัจจุบัน CLI ยังไม่มี
คำสั่ง rebind/update นี้ จึงเป็นขั้นเปิดใช้ที่ต้องเตรียมแยกหลังตรวจ Draft

## การทำงานหลังเชื่อมครบ

Backend ตรวจเจ้าของ ticket และยศปัจจุบัน → อ่าน Published selection →
ตรวจ metadata ของไฟล์ในขอบเขตนั้น → ทำ Registry shortlist → ส่ง JSON string
ให้ Dify → โหนดใหม่แปลงเป็นข้อมูลที่ Resolver และ Code 2 ใช้ต่อ

ไม่มี API key ผ่าน Discord และไม่มี `tenant_id = 1` ในโค้ด registry ใหม่
แต่ยังต้องตรวจ live integration และอีกโปรเจกต์จริงก่อนอ้างว่า isolation ผ่าน

สถานะ backend, ข้อสรุปที่ล็อกไว้ และข้อจำกัด:
[tenant-registry-contract-2026-10-03.md](tenant-registry-contract-2026-10-03.md)
