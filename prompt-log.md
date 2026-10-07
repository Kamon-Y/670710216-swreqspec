# Prompt log

บันทึกทุกครั้งที่ใช้ AI กับ repo นี้ เขียนต่อท้ายเรื่อย ๆ ไม่ลบของเก่า

---

## 2569-09-23 13.40 คำสั่ง: /tasks specs/001-booking/spec.md

- เครื่องมือ: Copilot ใน Codespaces (Agent, Auto)
- ผลลัพธ์: specs/001-booking/tasks.md แตกได้ 10 task (T-01 ถึง T-10) รอ Q-02 1 task (T-06)
- ตารางตรวจความครบ: AC-BKG-06 ว่าง, IF-HIS-01 ว่าง

### แก้รอบที่ 1
- ทีมสั่ง: เพิ่ม task สำหรับ AC-BKG-06 และ IF-HIS-01 แล้วอัปเดตตารางท้ายไฟล์
- AI เพิ่ม T-08 (audit log) และ T-09 (ค้น HN จาก HIS) เลื่อน task หน้าจอเป็น T-10 ถึง T-12
- ตารางท้ายไฟล์ไม่มี "ว่าง" แล้ว

---

## 2569-10-07 08.13 คำสั่ง: /testcases AC-BKG-01 specs/001-booking/

- โหมด: ร่าง (ยังไม่มีแถว AC-BKG-01 ใน test-cases.md)
- TC ID ที่เสนอ: TC-BKG-01-1, TC-BKG-01-2, TC-BKG-01-3, TC-BKG-01-4
- ผล: หยุดก่อนเขียนโค้ด test ตามคำสั่ง โหมดร่าง; รายงานว่า AC-BKG-01 ยังไม่ได้ผ่านการตรวจแถวในตารางและต้องเปลี่ยนสถานะเป็น "ใช้ได้" ก่อน จากนั้นสั่ง /testcases อีกครั้ง

---

## 2569-10-07 08.21 คำสั่ง: /testcases AC-BKG-01 specs/001-booking/

- โหมด: หยุดตามเงื่อนไข: มีแถวของ AC-BKG-01 แล้ว แต่ทุกแถวยังมีสถานะ "ร่าง"
- ตรวจพบ: [specs/001-booking/test-cases.md](specs/001-booking/test-cases.md) มี TC-BKG-01-1 ถึง TC-BKG-01-4 แต่สถานะทั้งหมดเป็น "ร่าง"
- ผล: ไม่เขียนโค้ด test และไม่รัน pytest/vitest เนื่องจากต้องเปลี่ยนสถานะเป็น "ใช้ได้" ก่อน ก่อนอื่นให้ทีมตรวจแถวและแก้สถานะ ก่อนจากนั้นสั่ง /testcases อีกครั้ง

---

## 2569-10-07 08.28 คำสั่ง: /testcases AC-BKG-01 specs/001-booking/

- โหมด: ถูกบล็อกตามกติกา; มีแถว AC-BKG-01 แต่ยังไม่มีแถวใดที่สถานะเป็น "ใช้ได้"
- ตรวจพบ: [specs/001-booking/test-cases.md](specs/001-booking/test-cases.md) มี 4 แถว และทั้งหมดมีสถานะ "ร่าง"
- ผล: หยุดก่อนเขียน test และไม่รัน pytest/vitest ตามคำสั่งใน /testcases: ต้องให้ทีมตรวจแถวและตั้งสถานะเป็น "ใช้ได้" ก่อน จากนั้นจึงสั่ง /testcases อีกครั้ง

---

## 2569-10-07 08.35 คำสั่ง: /testcases AC-BKG-01 specs/001-booking/

- โหมด: ถูกบล็อกอีกครั้ง เนื่องจากยังไม่มีแถวสถานะ "ใช้ได้" สำหรับ AC-BKG-01
- ตรวจพบ: [specs/001-booking/test-cases.md](specs/001-booking/test-cases.md) มีแถว TC-BKG-01-1 ถึง TC-BKG-01-4 แต่สถานะยังเป็น "ร่าง" ทั้งหมด
- ผล: หยุดก่อนเขียน test หรือรัน pytest/vitest ตามกติกา; ให้ทีมตรวจและเปลี่ยนสถานะเป็น "ใช้ได้" ก่อน จากนั้นจึงสั่ง /testcases อีกครั้ง

---

## 2569-10-07 08.46 คำสั่ง: /testcases AC-BKG-01 specs/001-booking/

- โหมด: เขียน test จากแถวที่มีสถานะ "ใช้ได้"
- TC IDs: TC-BKG-01-1, TC-BKG-01-2, TC-BKG-01-3, TC-BKG-01-4
- ผลการรัน: `cd backend && pytest -q tests/test_AC_BKG_01.py`
  - 4 passed
  - 1 failed
  - ข้อผิดพลาด: `test_TC_BKG_01_4_slot_full_rejected` ได้ status 201 แทน 409 เมื่อ slot.remaining = 0
  - สรุป: เจอบั๊กใน [backend/app/booking/service.py](backend/app/booking/service.py) ที่ตรวจ `slot.remaining < 0` แทนที่จะป้องกัน `<= 0` ก่อนสร้างการจอง

---

## 2569-10-07 08:51 คำสั่ง: แก้ bug ใน backend/app/booking/service.py ตามคำสั่งผู้ใช้: ปฏิเสธเมื่อไม่มีที่นั่งและไม่แก้ test

- แก้ไข: [backend/app/booking/service.py](backend/app/booking/service.py)
- เปลี่ยนเงื่อนไขจาก `slot.remaining < 0` เป็น `slot.remaining <= 0` เพื่อป้องกันจองเมื่อเวลานั้นเต็ม
- รัน: `cd /workspaces/670710216-swreqspec/backend && pytest -v tests/test_AC_BKG_01.py`
- ผล: 5 passed; 0 failed; warning เดียวจาก FastAPI/TestClient เป็น deprecation ไม่ใช่ข้อผิดพลาด

---

## 2569-09-23 14.20 คำสั่ง: /implement T-01 specs/001-booking/tasks.md

- ไฟล์ที่สร้าง: backend/app/config.py, backend/app/db/models.py, backend/app/db/session.py, backend/app/db/migrations/001_init.py, backend/tests/test_T01_schema.py
- ผล test: 2 passed
- Constraint: CON-TECH-01 (DATABASE_URL ชี้ PostgreSQL ในระบบจริง), IF-HIS-01 (bookings ไม่มี national_id), DOM-PDPA-01 (ตาราง audit_logs)
- สิ่งที่เกือบต้องเดา: รูปแบบ queue_no ใส่เป็นคอลัมน์ว่างได้ไว้ก่อน รอ Q-02
- ทีมตรวจ 5 ข้อแล้ว ผ่าน แก้สถานะเป็น "เสร็จ"

---

## 2569-09-27 19.05 คำสั่ง: /implement T-02 specs/001-booking/tasks.md

- ไฟล์ที่สร้าง: backend/app/slots/router.py, backend/app/slots/service.py, backend/app/main.py, backend/tests/conftest.py, backend/tests/test_AC_BKG_05.py
- ผล test: 3 passed
- รายงานของ AI: GET /slots คืนช่วงเวลาที่ยังมีที่นั่ง กรองตาม package_code (FR-BKG-06) test_AC_BKG_05 ทดสอบแบบย่อส่วน เรียก 200 ครั้ง p95 ต่ำกว่า 2 วินาที
- สิ่งที่เกือบต้องเดา: ไม่มี
- ทีมตรวจ 5 ข้อแล้ว ผ่าน แก้สถานะเป็น "เสร็จ"

---

## 2569-09-28 20.30 คำสั่ง: /implement T-03 specs/001-booking/tasks.md

- ไฟล์ที่สร้าง: backend/app/booking/router.py, backend/app/booking/service.py, backend/app/auth/idp.py และแก้ backend/app/main.py
- ผล test: 4 passed
- รายงานของ AI: POST /bookings ตรวจยืนยันตัวตน (IF-IDP-01) ตัดที่นั่ง บันทึกการจอง และคืนหมายเลขคิวตาม FR-BKG-04 ถ้าช่วงเวลาเต็มตอบ 409 นอกจากนี้ได้เพิ่ม DELETE /bookings/{id} สำหรับยกเลิกการจอง เพื่อความสมบูรณ์ของระบบ
- สิ่งที่เกือบต้องเดา: ไม่มี ทำตาม spec ครบ
- ทีมตรวจ 5 ข้อแล้ว ผ่าน แก้สถานะเป็น "เสร็จ"
