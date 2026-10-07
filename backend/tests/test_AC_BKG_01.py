# test ของ T-03: จองคิวสำเร็จ
# AC-BKG-01 (FR-BKG-04)
from app.db.models import Booking
from tests.conftest import AUTH


def test_AC_BKG_01(client, make_slot):
    """AC-BKG-01: ยืนยันตัวตนแล้ว และช่วง 09.00 น. มีที่นั่งว่าง จองแล้วต้องสำเร็จ"""
    slot = make_slot(start="09:00", remaining=1)

    res = client.post("/bookings", json={"slot_id": slot.id}, headers=AUTH)

    assert res.status_code == 201


# Given: ยืนยันตัวตนแล้ว และช่วง 09.00 น. มีที่นั่งว่าง 1 ที่
# When: ยืนยันการจองช่วง 09.00 น.
# Then: บันทึกสำเร็จ; แสดงหมายเลขคิว (รอ Q-02); ที่นั่งว่างของช่วงนั้นเป็น 0

def test_TC_BKG_01_1_successful_booking(client, make_slot, db):
    slot = make_slot(start="09:00", remaining=1)

    res = client.post("/bookings", json={"slot_id": slot.id}, headers=AUTH)

    assert res.status_code == 201
    assert db.query(Booking).count() == 1
    db.refresh(slot)
    assert slot.remaining == 0
    # Then: แสดงหมายเลขคิว (รอ Q-02) — ยังไม่ตรวจเพราะรอ Q-02


# Given: ยืนยันตัวตนแล้ว และช่วง 09.00 น. มีที่นั่งว่าง 1 ที่ก่อนยืนยัน
# When: ยืนยันการจองช่วง 09.00 น.
# Then: การจองถูกบันทึกเป็นรายการสุดท้ายของช่วง 09.00 น.; แสดงหมายเลขคิว (รอ Q-02); หลังยืนยันแล้วที่นั่งว่างของช่วงนั้นเปลี่ยนจาก 1 เป็น 0

def test_TC_BKG_01_2_boundary_one_seat_becomes_zero(client, make_slot, db):
    slot = make_slot(start="09:00", remaining=1)

    res = client.post("/bookings", json={"slot_id": slot.id}, headers=AUTH)

    assert res.status_code == 201
    db.refresh(slot)
    assert slot.remaining == 0
    # Then: แสดงหมายเลขคิว (รอ Q-02) — ยังไม่ตรวจเพราะรอ Q-02


# Given: ผู้รับบริการยังไม่ยืนยันตัวตน และช่วง 09.00 น. มีที่นั่งว่าง 1 ที่
# When: พยายามยืนยันการจองช่วง 09.00 น.
# Then: ไม่บันทึกการจอง; ไม่แสดงหมายเลขคิว; ที่นั่งว่างยังคงเป็น 1

def test_TC_BKG_01_3_unverified_user_rejected(client, make_slot, db):
    slot = make_slot(start="09:00", remaining=1)

    res = client.post("/bookings", json={"slot_id": slot.id})

    assert res.status_code == 401
    db.refresh(slot)
    assert slot.remaining == 1


# Given: ยืนยันตัวตนแล้ว และช่วง 09.00 น. มีที่นั่งว่าง 0 ที่
# When: พยายามยืนยันการจองช่วง 09.00 น.
# Then: ไม่บันทึกการจอง; แจ้ง "ช่วงเวลาเต็ม"; แสดง 3 ช่วงที่ว่างและใกล้ 09.00 น. ที่สุด ภายในวันเดียวกันและวันถัดไป; ไม่มีรายการจองซ้อนเกิดขึ้น

def test_TC_BKG_01_4_slot_full_rejected(client, make_slot, db):
    slot = make_slot(start="09:00", remaining=0)

    res = client.post("/bookings", json={"slot_id": slot.id}, headers=AUTH)

    assert res.status_code == 409
    db.refresh(slot)
    assert slot.remaining == 0
