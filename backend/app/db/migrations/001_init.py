from sqlalchemy.engine import Engine

from app.db.models import Base


def upgrade(engine: Engine) -> None:
    # รองรับ CON-TECH-01, DOM-PDPA-01 และ IF-HIS-01 ด้วย schema ตาม spec
    Base.metadata.create_all(engine)