import importlib

import pytest
from sqlalchemy import create_engine, inspect
from sqlalchemy.engine import Engine


initial_migration = importlib.import_module("app.db.migrations.001_init")


@pytest.fixture
def database_engine() -> Engine:
    # รองรับการทดสอบ schema ของ T-01 ด้วย SQLite ในหน่วยความจำตาม plan
    test_engine = create_engine("sqlite:///:memory:")
    initial_migration.upgrade(test_engine)
    return test_engine


def test_schema_has_booking_tables(database_engine: Engine) -> None:
    # ตรวจ CON-TECH-01, DOM-PDPA-01 และ IF-HIS-01 ตามเงื่อนไขเสร็จของ T-01
    table_names = set(inspect(database_engine).get_table_names())
    assert table_names == {"slots", "bookings", "audit_logs"}

    booking_columns = {
        column["name"] for column in inspect(database_engine).get_columns("bookings")
    }
    assert "national_id" not in booking_columns
    assert "hn" in booking_columns