# Plan: จองคิวตรวจสุขภาพ (Booking)

Spec ID: SPEC-BKG-001 | Status: Draft v2 | Source: specs/001-booking/spec.md

## 1. สรุปแนวทาง (5 บรรทัด)
- ฟีเจอร์นี้ให้ผู้รับบริการที่ยืนยันตัวตนแล้วเลือกแพ็กเกจ วัน และช่วงเวลาตรวจสุขภาพ เพื่อรับหมายเลขคิวและยืนยันการจอง
- ระบบจะคำนวณช่วงเวลาและจำนวนที่นั่งคงเหลือแบบ read-heavy แล้วป้องกันสภาวะจองซ้ำผ่านกฎตรวจก่อนบันทึก
- เมื่อช่วงเวลาเต็ม ระบบจะเสนอ 3 ตัวเลือกภายในวันเลือกและวันถัดไป โดยไม่สร้างรายการจองจนกว่าจะยืนยันใหม่
- การบันทึกการจองแยกจากกระบวนการส่งข้อความแจ้งเตือนแบบ asynchronous เพื่อให้การจองไม่ถูก block จากการส่ง SMS/LINE
- ระบบต้องมี audit log และการป้องกันข้อมูลตาม constraints โดยไม่เก็บเลขบัตรประชาชนในตารางการจอง

## 2. เทคโนโลยีที่ใช้

| สิ่งที่เลือก | มาจาก | หมายเหตุ |
|---|---|---|
| React (Vite) | ทีมเลือกเอง ไม่ได้มาจาก spec | ใช้สำหรับหน้าแสดงตารางเวลาและฟอร์มจองคิว |
| Python FastAPI | ทีมเลือกเอง ไม่ได้มาจาก spec | ใช้สำหรับ API จองคิวและข้อมูลช่วงเวลา |
| MySQL | CON-TECH-01 | ใช้เก็บ booking, slot availability, notification queue และ audit log |
| TLS 1.2+ | NFR-SEC-01 | ใช้ที่ layer transport และเซิร์ฟเวอร์ API |
| SMS/LINE async notification | IF-NOT-01 | ระบบแจ้งเตือนไม่ปิดกั้นการบันทึกการจอง |

## 3. โมเดลข้อมูล

| Entity | ฟิลด์หลัก | รองรับ FR/Constraint |
|---|---|---|
| `booking` | booking_id, patient_hn, package_id, booking_date, slot_start_time, slot_end_time, status, queue_number, created_at, updated_at | FR-BKG-02, FR-BKG-04, FR-BKG-05, DOM-PDPA-01 |
| `slot_availability` | slot_date, slot_start_time, package_id, capacity, remaining_seats, version | FR-BKG-01, FR-BKG-03, FR-BKG-06 |
| `patient_reference` | hn, authenticated_at, source_system | IF-IDP-01, IF-HIS-01 |
| `notification_queue` | notification_id, booking_id, channel, payload, status, retry_count, next_retry_at | FR-BKG-04, FR-BKG-05, IF-NOT-01, NFR-REL-02 |
| `audit_log` | log_id, actor_user_id, accessed_at, patient_hn, action, metadata | DOM-PDPA-01 |

หมายเหตุ:
- ไม่มีฟิลด์เลขบัตรประชาชนใน `booking` หรือ `audit_log` ตาม `IF-HIS-01`
- `patient_reference` ใช้ HN เป็น identifier ภายในระบบ และค้นข้อมูลจาก HIS ผ่านเลขบัตรประชาชนภายนอกเท่านั้น

## 4. API / หน้าจอ

| ชื่อ | รายละเอียด | รองรับ |
|---|---|---|
| GET `/api/availability` | รับ `packageId`, `dateFrom`, `dateTo`, `timezone` ผลลัพธ์คือรายการช่วงเวลาว่างพร้อมจำนวนที่นั่งคงเหลือ | FR-BKG-01, FR-BKG-06 |
| POST `/api/bookings/validate` | รับ `hn`, `packageId`, `slotId`, `bookingDate` ตรวจว่ามีคิวที่ยังไม่ได้ใช้ในวันเดียวกันหรือไม่ พร้อมข้อมูล slot ที่เลือก | FR-BKG-02 |
| POST `/api/bookings` | รับ `hn`, `packageId`, `slotId`, `bookingDate` บันทึก booking, ตัด remaining_seats, สร้าง queue_number, ส่งคำขอแจ้งเตือน | FR-BKG-04 |
| POST `/api/bookings/{bookingId}/retry-notification` | ส่งซ้ำข้อความแจ้งเตือนสำหรับ booking ที่ไม่สำเร็จ | FR-BKG-05, NFR-REL-02 |
| GET `/bookings` (หน้า UI) | แสดงรายการชั่วโมงว่าง, โควตา, และแจ้งช่วงเวลาเต็มพร้อม 3 ตัวเลือก | FR-BKG-01, FR-BKG-03 |

## 5. ตารางตรวจ Constraints

| Constraint ID | ถูกนำไปใช้ที่ไหนใน plan | สถานะ |
|---|---|---|
| CON-TECH-01 | MySQL ถูกใช้เป็น datastore สำหรับ booking, availability, notification queue และ audit log | ใช้แล้ว |
| DOM-PDPA-01 | `audit_log` ถูกออกแบบเพื่อบันทึกผู้เข้าถึง เวลา และ patient_hn ทุกครั้งที่เข้าถึงข้อมูลสุขภาพ | ใช้แล้ว |
| IF-IDP-01 | `patient_reference` และ API validation ตรวจว่าได้ยืนยันตัวตนก่อนเข้าถึงข้อมูลผู้รับบริการ | ใช้แล้ว |
| IF-HIS-01 | `patient_reference` ใช้ HN ในระบบ และไม่เก็บเลขบัตรประชาชนใน `booking` | ใช้แล้ว |
| IF-NOT-01 | `notification_queue` แยกกระบวนการส่ง SMS/LINE ออกจาก transaction บันทึก booking | ใช้แล้ว |

## 6. แผนทดสอบจาก Acceptance Criteria

| AC ID | ชื่อ test | ทดสอบอย่างไร |
|---|---|---|
| AC-BKG-01 | `test_AC_BKG_01_booking_success_reduces_capacity` | ตั้งค่า slot 09.00 มีที่นั่ง 1, ยืนยันการจองแล้วตรวจว่าบันทึก booking และ remaining_seats = 0 |
| AC-BKG-02 | `test_AC_BKG_02_reject_duplicate_same_day_queue` | สร้างคิวที่ยังไม่ได้ใช้ในวันเดียวกัน แล้วลองจองอีกครั้ง ต้องปฏิเสธและแสดงหมายเลขคิวเดิม |
| AC-BKG-03 | `test_AC_BKG_03_offer_three_alternatives_next_day` | ปลอมสถานการณ์ slot เต็ม, ยืนยันการจองแล้วตรวจว่ามีข้อความ “ช่วงเวลาเต็ม” และเสนอ 3 option รวมวันเลือกและวันถัดไป |
| AC-BKG-04 | `test_AC_BKG_04_booking_persists_when_notification_fails` | จำลอง SMS/LINE error แล้วตรวจว่าการจองยังบันทึกและ notification_queue ถูกสร้างพร้อม retry ภายใน 5 นาที |
| AC-BKG-05 | `test_AC_BKG_05_availability_latency_under_two_seconds` | load test 200 user พร้อมกัน ตรวจ p95 latency ของ GET /api/availability <= 2 วินาที |
| AC-BKG-06 | `test_AC_BKG_06_audit_log_records_access` | จำลองการเปิดดูข้อมูลการจอง ตรวจว่ามี audit_log ที่ระบุ actor, time, patient_hn |

## 7. ลำดับงาน

1. ตั้งโครงสร้าง API และ schema ฐานข้อมูลสำหรับ `booking`, `slot_availability`, `notification_queue`, `audit_log` ตาม `FR-BKG-01`, `FR-BKG-04`, `DOM-PDPA-01`
2. สร้าง API ดูช่วงเวลาว่างและจำนวนที่นั่งคงเหลือ `GET /api/availability` ตาม `FR-BKG-01`
3. สร้างกฎตรวจเรื่องคิวที่ยังไม่ได้ใช้ในวันเดียวกันและห้ามจองซ้ำตาม `FR-BKG-02` และ `AC-BKG-02`
4. สร้าง flow กรณี slot เต็มพร้อมเสนอ 3 ตัวเลือกรวมวันเลือกและวันถัดไปตาม `FR-BKG-03` และ `AC-BKG-03`
5. สร้าง transaction จองคิวและตัด remaining_seats พร้อมสร้าง queue_number ตาม `FR-BKG-04` และ `AC-BKG-01`
6. สร้างระบบ notification queue + retry ภายใน 5 นาที ตาม `FR-BKG-05`, `IF-NOT-01`, `NFR-REL-02`, `AC-BKG-04`
7. เพิ่ม audit log และความปลอดภัยสำหรับการเข้าถึงข้อมูลตาม `DOM-PDPA-01`, `IF-IDP-01`, `IF-HIS-01`, `AC-BKG-06`
8. ทดสอบประสิทธิภาพและความครบถ้วนตาม `NFR-PERF-01`, `AC-BKG-05`, และตรวจสอบการทำงานครบทุกรายการจาก AC

## 8. สิ่งที่ยังไม่ทำ
- `Q-02`: "คิวที่ยังไม่ได้ใช้" ครอบคลุมสถานะใดบ้าง เช่น รอเข้ารับบริการ หมดเวลา ไม่มาตามนัด หรือจองค้างชำระ? -> ส่วนที่เกี่ยวข้องกับข้อนี้จะยังไม่สร้างจนกว่าจะได้คำตอบ
- `Q-03`: หมายเลขคิวรีเซ็ตรายวัน หรือนับต่อเนื่อง? -> ส่วนที่เกี่ยวข้องกับข้อนี้จะยังไม่สร้างจนกว่าจะได้คำตอบ
