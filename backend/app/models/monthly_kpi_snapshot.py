import uuid
from datetime import datetime
from decimal import Decimal

from sqlalchemy import String, DateTime, ForeignKey, Numeric, Integer, UniqueConstraint
from sqlalchemy.dialects.postgresql import UUID
from sqlalchemy.orm import Mapped, mapped_column, relationship

from app.core.database import Base


class MonthlyKpiSnapshot(Base):
    __tablename__ = "monthly_kpi_snapshots"
    __table_args__ = (
        UniqueConstraint("tenant_id", "month_key", name="uq_monthly_kpi_snapshots_tenant_month"),
    )

    id: Mapped[uuid.UUID] = mapped_column(UUID(as_uuid=True), primary_key=True, default=uuid.uuid4)

    tenant_id: Mapped[uuid.UUID] = mapped_column(
        UUID(as_uuid=True),
        ForeignKey("tenants.id", ondelete="CASCADE"),
        nullable=False,
        index=True,
    )

    month_key: Mapped[str] = mapped_column(String(7), nullable=False, index=True)  # YYYY-MM

    total_sales_net: Mapped[Decimal] = mapped_column(Numeric(14, 2), nullable=False, default=0)
    total_sales_gross: Mapped[Decimal] = mapped_column(Numeric(14, 2), nullable=False, default=0)

    total_purchases_net: Mapped[Decimal] = mapped_column(Numeric(14, 2), nullable=False, default=0)
    total_purchases_gross: Mapped[Decimal] = mapped_column(Numeric(14, 2), nullable=False, default=0)

    gross_margin_amount: Mapped[Decimal] = mapped_column(Numeric(14, 2), nullable=False, default=0)
    gross_margin_pct: Mapped[Decimal] = mapped_column(Numeric(8, 4), nullable=False, default=0)
    purchase_to_sales_ratio_pct: Mapped[Decimal] = mapped_column(Numeric(8, 4), nullable=False, default=0)

    tickets_count: Mapped[int] = mapped_column(Integer, nullable=False, default=0)
    average_ticket: Mapped[Decimal] = mapped_column(Numeric(12, 2), nullable=False, default=0)

    documents_processed: Mapped[int] = mapped_column(Integer, nullable=False, default=0)
    pending_reviews: Mapped[int] = mapped_column(Integer, nullable=False, default=0)

    created_at: Mapped[datetime] = mapped_column(DateTime, default=datetime.utcnow, nullable=False, index=True)
    updated_at: Mapped[datetime] = mapped_column(
        DateTime,
        default=datetime.utcnow,
        onupdate=datetime.utcnow,
        nullable=False,
    )

    tenant = relationship("Tenant", back_populates="monthly_kpi_snapshots")