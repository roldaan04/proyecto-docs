import uuid
from typing import Sequence

from sqlalchemy import select, func
from sqlalchemy.orm import Session

from app.models.purchase_entry import PurchaseEntry
from app.schemas.purchase import PurchaseEntryUpdate
from app.services.financial_movement_writer import FinancialMovementWriter


class PurchaseService:
    def __init__(self, db: Session):
        self.db = db

    def list_entries(
        self,
        tenant_id: uuid.UUID,
        *,
        provider_name: str | None = None,
        month_key: str | None = None,
        category: str | None = None,
        status: str | None = None,
        skip: int = 0,
        limit: int = 100,
    ) -> Sequence[PurchaseEntry]:
        stmt = select(PurchaseEntry).where(PurchaseEntry.tenant_id == tenant_id)

        if provider_name:
            stmt = stmt.where(func.lower(PurchaseEntry.provider_name).contains(provider_name.strip().lower()))

        if month_key:
            stmt = stmt.where(PurchaseEntry.month_key == month_key)

        if category:
            stmt = stmt.where(func.lower(PurchaseEntry.category) == category.strip().lower())

        if status:
            stmt = stmt.where(func.lower(PurchaseEntry.status) == status.strip().lower())

        stmt = stmt.order_by(PurchaseEntry.issue_date.desc().nullslast(), PurchaseEntry.created_at.desc())
        stmt = stmt.offset(skip).limit(limit)

        return self.db.execute(stmt).scalars().all()

    def get_entry(self, tenant_id: uuid.UUID, entry_id: uuid.UUID) -> PurchaseEntry | None:
        stmt = select(PurchaseEntry).where(
            PurchaseEntry.id == entry_id,
            PurchaseEntry.tenant_id == tenant_id,
        )
        return self.db.execute(stmt).scalar_one_or_none()

    def update_entry(
        self,
        tenant_id: uuid.UUID,
        entry_id: uuid.UUID,
        payload: PurchaseEntryUpdate,
    ) -> PurchaseEntry | None:
        entry = self.get_entry(tenant_id, entry_id)
        if not entry:
            return None

        data = payload.model_dump(exclude_unset=True)

        for field, value in data.items():
            setattr(entry, field, value)

        if entry.issue_date:
            entry.month_key = entry.issue_date.strftime("%Y-%m")

        if "net_amount" in data or "total_amount" in data:
            if entry.net_amount is not None and entry.total_amount is not None:
                entry.tax_amount = entry.total_amount - entry.net_amount

        self.db.add(entry)
        self.db.commit()
        self.db.refresh(entry)

        FinancialMovementWriter.sync_from_purchase_entry(self.db, entry)

        return entry

    def delete_entry(self, tenant_id: uuid.UUID, entry_id: uuid.UUID) -> bool:
        entry = self.get_entry(tenant_id, entry_id)
        if not entry:
            return False

        FinancialMovementWriter.delete_by_purchase_entry_id(self.db, entry.id)

        self.db.delete(entry)
        self.db.commit()
        return True