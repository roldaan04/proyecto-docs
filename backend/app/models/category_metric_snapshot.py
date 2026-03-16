import uuid
from datetime import datetime
from decimal import Decimal

from sqlalchemy import String, DateTime, ForeignKey, Numeric, UniqueConstraint
from sqlalchemy.dialects.postgresql import UUID
from sqlalchemy.orm import Mapped, mapped_column, relationship

from app.core.database import Base


class CategoryMetricSnapshot(Base):
    __tablename__ = "category_metric_snapshots"
    __table_args__ = (
        UniqueConstraint(
            "tenant_id",
            "month_key",
            "metric_type",
            "category_name",
            name="uq_category_metric_snapshots_tenant_month_type_category",
        ),
    )

    id: Mapped[uuid.UUID] = mapped_column(UUID(as_uuid=True), primary_key=True, default=uuid.uuid4)

    tenant_id: Mapped[uuid.UUID] = mapped_column(
        UUID(as_uuid=True),
        ForeignKey("tenants.id", ondelete="CASCADE"),
        nullable=False,
        index=True,
    )

    month_key: Mapped[str] = mapped_column(String(7), nullable=False, index=True)
    metric_type: Mapped[str] = mapped_column(String(30), nullable=False, index=True)  # sales / purchases
    category_name: Mapped[str] = mapped_column(String(100), nullable=False, index=True)

    units: Mapped[Decimal] = mapped_column(Numeric(14, 2), nullable=False, default=0)
    net_amount: Mapped[Decimal] = mapped_column(Numeric(14, 2), nullable=False, default=0)
    gross_amount: Mapped[Decimal] = mapped_column(Numeric(14, 2), nullable=False, default=0)

    created_at: Mapped[datetime] = mapped_column(DateTime, default=datetime.utcnow, nullable=False, index=True)

    tenant = relationship("Tenant", back_populates="category_metric_snapshots")