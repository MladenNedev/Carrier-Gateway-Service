from sqlalchemy.orm import DeclarativeBase, Mapped, mapped_column, relationship
from sqlalchemy import String, DateTime, ForeignKey, Enum as SAEnum, UniqueConstraint, Index
from sqlalchemy.dialects.postgresql import UUID
from sqlalchemy.sql import func
from app.domain.shipment import ShipmentStatus
from app.domain.shipment_event import ShipmentEventType, ShipmentEventSource
import uuid
import datetime

class Base(DeclarativeBase):
    pass

class MerchantModel(Base):
    __tablename__ = "merchants"

    id: Mapped[UUID] = mapped_column(UUID(as_uuid=True), primary_key=True, default=uuid.uuid4)
    name: Mapped[str] = mapped_column(String, nullable=False)
    created_at: Mapped[datetime.datetime] = mapped_column(DateTime(timezone=True), server_default=func.now())
    shipments: Mapped[list["ShipmentModel"]] = relationship(
        "ShipmentModel",
        order_by="ShipmentModel.created_at.desc()",
        cascade="all, delete-orphan",
        back_populates="merchant"
    )
    users: Mapped[list["UserModel"]] = relationship(
        "UserModel",
        order_by="UserModel.created_at.desc()",
        cascade="all, delete-orphan",
        back_populates="merchant"
    )

class UserModel(Base):
    __tablename__ = "users"

    id: Mapped[UUID] = mapped_column(UUID(as_uuid=True), primary_key=True, default=uuid.uuid4)
    email: Mapped[str] = mapped_column(String(255), unique=True, index=True, nullable=False)
    merchant_id: Mapped[UUID] = mapped_column(UUID(as_uuid=True), ForeignKey("merchants.id"), nullable=False)
    created_at: Mapped[datetime.datetime] = mapped_column(DateTime(timezone=True), server_default=func.now())
    updated_at: Mapped[datetime.datetime] = mapped_column(DateTime(timezone=True), server_default=func.now(), onupdate=func.now())
    merchant: Mapped[MerchantModel] = relationship("MerchantModel", back_populates="users")

class ShipmentModel(Base):
    __tablename__ = "shipments"
    __table_args__ = (
        UniqueConstraint("merchant_id", "external_reference", name="_uq_shipments_merchant_external_reference"),
        Index("ix_shipments_external_reference", "external_reference"),
    )

    id: Mapped[UUID] = mapped_column(UUID(as_uuid=True), primary_key=True, default=uuid.uuid4)
    user_id: Mapped[UUID | None] = mapped_column(UUID(as_uuid=True), ForeignKey("users.id"), nullable=True)
    merchant_id: Mapped[UUID] = mapped_column(UUID(as_uuid=True), ForeignKey("merchants.id"), nullable=False)
    external_reference: Mapped[str] = mapped_column(String(255), nullable=False)
    name: Mapped[str] = mapped_column(String, nullable=False)
    created_at: Mapped[datetime.datetime] = mapped_column(DateTime(timezone=True), server_default=func.now())
    updated_at: Mapped[datetime.datetime] = mapped_column(DateTime(timezone=True), server_default=func.now(), onupdate=func.now())
    merchant: Mapped[MerchantModel] = relationship("MerchantModel", back_populates="shipments")
    events: Mapped[list["ShipmentEventModel"]] = relationship(
        "ShipmentEventModel",
        order_by="ShipmentEventModel.occurred_at",
        back_populates="shipment",
        cascade="all, delete-orphan",
        lazy="selectin"
    )
    status: Mapped[ShipmentStatus] = mapped_column(SAEnum(ShipmentStatus, name="shipment_status"), nullable=False)
    

class ShipmentEventModel(Base):
    __tablename__ = "shipment_events"

    id: Mapped[UUID] = mapped_column(UUID(as_uuid=True), primary_key=True, default=uuid.uuid4)
    shipment_id: Mapped[UUID] = mapped_column(UUID(as_uuid=True), ForeignKey("shipments.id"), nullable=False)
    shipment: Mapped[ShipmentModel] = relationship(
        "ShipmentModel",
        back_populates="events"
    )

    type: Mapped[ShipmentEventType] = mapped_column(SAEnum(ShipmentEventType, name="shipment_event_type"), nullable=False)
    source: Mapped[ShipmentEventSource] = mapped_column(SAEnum(ShipmentEventSource, name="shipment_event_source"), nullable=False)
    reason: Mapped[str | None] = mapped_column(String, nullable=True)

    occurred_at: Mapped[datetime.datetime] = mapped_column(DateTime(timezone=True), server_default=func.now(), nullable=False)
    created_at: Mapped[datetime.datetime] = mapped_column(DateTime(timezone=True), server_default=func.now())
    updated_at: Mapped[datetime.datetime] = mapped_column(DateTime(timezone=True), server_default=func.now(), onupdate=func.now())
