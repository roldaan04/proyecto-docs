import uuid
from datetime import datetime, date
from decimal import Decimal

from sqlalchemy import String, DateTime, Date, ForeignKey, Text, Numeric, UniqueConstraint
from sqlalchemy.dialects.postgresql import UUID
from sqlalchemy.orm import Mapped, mapped_column, relationship

from app.core.database import Base


class PurchaseEntry(Base):
    __tablename__ = "purchase_entries"
    __table_args__ = (
        UniqueConstraint(
            "tenant_id",
            "row_fingerprint",
            name="uq_purchase_entries_tenant_row_fingerprint",
        ),
    )

    id: Mapped[uuid.UUID] = mapped_column(UUID(as_uuid=True), primary_key=True, default=uuid.uuid4)

    tenant_id: Mapped[uuid.UUID] = mapped_column(
        UUID(as_uuid=True),
        ForeignKey("tenants.id", ondelete="CASCADE"),
        nullable=False,
        index=True,
    )

    source_document_id: Mapped[uuid.UUID | None] = mapped_column(
        UUID(as_uuid=True),
        ForeignKey("documents.id", ondelete="SET NULL"),
        nullable=True,
        index=True,
    )

    import_batch_id: Mapped[uuid.UUID | None] = mapped_column(
        UUID(as_uuid=True),
        ForeignKey("purchase_import_batches.id", ondelete="SET NULL"),
        nullable=True,
        index=True,
    )

    provider_name: Mapped[str] = mapped_column(String(255), nullable=False, index=True)

    issue_date: Mapped[date | None] = mapped_column(Date, nullable=True, index=True)
    order_date: Mapped[date | None] = mapped_column(Date, nullable=True, index=True)

    month_key: Mapped[str | None] = mapped_column(String(7), nullable=True, index=True)  # YYYY-MM

    net_amount: Mapped[Decimal] = mapped_column(Numeric(12, 2), nullable=False, default=0)
    tax_amount: Mapped[Decimal] = mapped_column(Numeric(12, 2), nullable=False, default=0)
    total_amount: Mapped[Decimal] = mapped_column(Numeric(12, 2), nullable=False, default=0)

    currency: Mapped[str] = mapped_column(String(10), nullable=False, default="EUR")
    category: Mapped[str | None] = mapped_column(String(100), nullable=True, index=True)
    subcategory: Mapped[str | None] = mapped_column(String(100), nullable=True, index=True)

    notes: Mapped[str | None] = mapped_column(Text, nullable=True)

    source_type: Mapped[str] = mapped_column(
        String(50),
        nullable=False,
        default="excel_import",
        index=True,
    )  # excel_import / manual / document_extraction

    source_reference: Mapped[str | None] = mapped_column(String(255), nullable=True)
    status: Mapped[str] = mapped_column(String(50), nullable=False, default="active", index=True)

    row_fingerprint: Mapped[str] = mapped_column(String(128), nullable=False, index=True)

    created_at: Mapped[datetime] = mapped_column(DateTime, default=datetime.utcnow, nullable=False, index=True)
    updated_at: Mapped[datetime] = mapped_column(
        DateTime,
        default=datetime.utcnow,
        onupdate=datetime.utcnow,
        nullable=False,
    )

    tenant = relationship("Tenant", back_populates="purchase_entries")
    source_document = relationship("Document", back_populates="purchase_entries")
    import_batch = relationship("PurchaseImportBatch", back_populates="entries")