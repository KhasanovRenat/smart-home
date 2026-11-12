from sqlalchemy import case, select, text, update
from sqlalchemy.dialects.postgresql import insert

from .database import Base, engine
from .models import DeviceRow, ReadingRow


def initialize_database():
    with engine.begin() as connection:
        # Реплики запускаются параллельно, поэтому создание таблиц выполняется по очереди.
        connection.execute(text("SELECT pg_advisory_xact_lock(902681)"))
        Base.metadata.create_all(connection)
        connection.execute(insert(DeviceRow).values([
            {"id": 1, "name": "Умный свет", "status": "off"},
            {"id": 2, "name": "Термостат", "status": "on"},
        ]).on_conflict_do_nothing(index_elements=["id"]))


def list_devices(session):
    return session.scalars(select(DeviceRow).order_by(DeviceRow.id)).all()


def toggle_device(session, device_id):
    statement = (
        update(DeviceRow).where(DeviceRow.id == device_id)
        .values(status=case((DeviceRow.status == "off", "on"), else_="off"))
        .returning(DeviceRow)
    )
    device = session.scalars(statement).one_or_none()
    if device is not None:
        session.commit()
    return device


def add_reading(session, device_id, value):
    reading = ReadingRow(device_id=device_id, value=value)
    session.add(reading)
    session.commit()
    session.refresh(reading)
    return reading


def list_readings(session, device_id):
    statement = (
        select(ReadingRow).where(ReadingRow.device_id == device_id)
        .order_by(ReadingRow.id.desc()).limit(100)
    )
    return session.scalars(statement).all()
