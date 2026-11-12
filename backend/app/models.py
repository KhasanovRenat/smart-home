from datetime import datetime
from typing import Literal

from pydantic import BaseModel, ConfigDict, FiniteFloat
from sqlalchemy import DateTime, ForeignKey, String, func
from sqlalchemy.orm import Mapped, mapped_column

from .database import Base


class DeviceRow(Base):
    __tablename__ = "devices"

    id: Mapped[int] = mapped_column(primary_key=True)
    name: Mapped[str] = mapped_column(String(80))
    status: Mapped[str] = mapped_column(String(3))


class ReadingRow(Base):
    __tablename__ = "readings"

    id: Mapped[int] = mapped_column(primary_key=True)
    device_id: Mapped[int] = mapped_column(ForeignKey("devices.id"), index=True)
    value: Mapped[float]
    timestamp: Mapped[datetime] = mapped_column(DateTime(timezone=True), server_default=func.now())


class Device(BaseModel):
    model_config = ConfigDict(from_attributes=True)

    id: int
    name: str
    status: Literal["on", "off"]


class ToggleResult(BaseModel):
    status: Literal["success"] = "success"
    device: Device


class ReadingInput(BaseModel):
    value: FiniteFloat


class Reading(ReadingInput):
    model_config = ConfigDict(from_attributes=True)

    id: int
    device_id: int
    timestamp: datetime
