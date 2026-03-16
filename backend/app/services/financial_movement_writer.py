from decimal import Decimal
from uuid import UUID

from sqlalchemy.orm import Session

from app.models.financial_entry import FinancialEntry
from app.models.financial_movement import FinancialMovement
from app.models.purchase_entry import PurchaseEntry


class FinancialMovementWriter:
    @staticmethod
    def _safe_decimal(value) -> Decimal | None:
        if value is None:
            return None
        if isinstance(value, Decimal):
            return value
        return Decimal(str(value))

    @staticmethod
    def get_by_financial_entry_id(
        db: Session,
        financial_entry_id: UUID,
    ) -> FinancialMovement | None:
        return (
            db.query(FinancialMovement)
            .filter(FinancialMovement.source_financial_entry_id == financial_entry_id)
            .first()
        )

    @staticmethod
    def get_by_purchase_entry_id(
        db: Session,
        purchase_entry_id: UUID,
    ) -> FinancialMovement | None:
        return (
            db.query(FinancialMovement)
            .filter(FinancialMovement.source_purchase_entry_id == purchase_entry_id)
            .first()
        )

    @staticmethod
    def exists_for_financial_entry(
        db: Session,
        financial_entry_id: UUID,
    ) -> bool:
        return FinancialMovementWriter.get_by_financial_entry_id(db, financial_entry_id) is not None

    @staticmethod
    def exists_for_purchase_entry(
        db: Session,
        purchase_entry_id: UUID,
    ) -> bool:
        return FinancialMovementWriter.get_by_purchase_entry_id(db, purchase_entry_id) is not None

    @staticmethod
    def create_from_financial_entry(
        db: Session,
        entry: FinancialEntry,
    ) -> FinancialMovement:
        movement = FinancialMovement(
            tenant_id=entry.tenant_id,
            movement_date=entry.issue_date,
            kind=entry.kind,
            status="proposed" if entry.status_review == "pending" else "confirmed",
            source_type="document",
            source_document_id=entry.document_id,
            source_financial_entry_id=entry.id,
            source_purchase_entry_id=None,
            source_reference=str(entry.extraction_run_id) if entry.extraction_run_id else None,
            third_party_name=entry.supplier_or_customer,
            third_party_tax_id=None,
            concept=entry.notes,
            category=entry.category,
            subcategory=None,
            business_area="general",
            net_amount=FinancialMovementWriter._safe_decimal(entry.tax_base),
            tax_amount=FinancialMovementWriter._safe_decimal(entry.tax_amount),
            withholding_amount=Decimal("0.00"),
            total_amount=FinancialMovementWriter._safe_decimal(entry.total_amount),
            currency=entry.currency or "EUR",
            document_type=entry.category,
            confidence_score=None,
            needs_review=(entry.status_review == "pending"),
            notes=f"Movimiento generado desde FinancialEntry {entry.id}",
        )

        db.add(movement)
        db.commit()
        db.refresh(movement)
        return movement

    @staticmethod
    def sync_from_financial_entry(
        db: Session,
        entry: FinancialEntry,
    ) -> FinancialMovement:
        movement = FinancialMovementWriter.get_by_financial_entry_id(db, entry.id)

        if not movement:
            return FinancialMovementWriter.create_from_financial_entry(db, entry)

        movement.movement_date = entry.issue_date
        movement.kind = entry.kind
        movement.status = "proposed" if entry.status_review == "pending" else "confirmed"
        movement.source_type = "document"
        movement.source_document_id = entry.document_id
        movement.source_financial_entry_id = entry.id
        movement.source_reference = str(entry.extraction_run_id) if entry.extraction_run_id else None
        movement.third_party_name = entry.supplier_or_customer
        movement.concept = entry.notes
        movement.category = entry.category
        movement.net_amount = FinancialMovementWriter._safe_decimal(entry.tax_base)
        movement.tax_amount = FinancialMovementWriter._safe_decimal(entry.tax_amount)
        movement.total_amount = FinancialMovementWriter._safe_decimal(entry.total_amount)
        movement.currency = entry.currency or "EUR"
        movement.document_type = entry.category
        movement.needs_review = (entry.status_review == "pending")
        movement.notes = f"Movimiento sincronizado desde FinancialEntry {entry.id}"

        db.add(movement)
        db.commit()
        db.refresh(movement)
        return movement

    @staticmethod
    def delete_by_financial_entry_id(
        db: Session,
        financial_entry_id: UUID,
    ) -> bool:
        movement = FinancialMovementWriter.get_by_financial_entry_id(db, financial_entry_id)
        if not movement:
            return False

        db.delete(movement)
        db.commit()
        return True

    @staticmethod
    def create_from_purchase_entry(
        db: Session,
        entry: PurchaseEntry,
    ) -> FinancialMovement:
        movement = FinancialMovement(
            tenant_id=entry.tenant_id,
            movement_date=entry.issue_date or entry.order_date,
            kind="expense",
            status="confirmed" if entry.status == "active" else "draft",
            source_type="excel_import",
            source_document_id=entry.source_document_id,
            source_financial_entry_id=None,
            source_purchase_entry_id=entry.id,
            source_reference=entry.source_reference,
            third_party_name=entry.provider_name,
            third_party_tax_id=None,
            concept=entry.notes,
            category=entry.category,
            subcategory=entry.subcategory,
            business_area="general",
            net_amount=FinancialMovementWriter._safe_decimal(entry.net_amount),
            tax_amount=FinancialMovementWriter._safe_decimal(entry.tax_amount),
            withholding_amount=Decimal("0.00"),
            total_amount=FinancialMovementWriter._safe_decimal(entry.total_amount),
            currency=entry.currency or "EUR",
            document_type=None,
            confidence_score=None,
            needs_review=False,
            notes=f"Movimiento generado desde PurchaseEntry {entry.id}",
        )

        db.add(movement)
        db.commit()
        db.refresh(movement)
        return movement

    @staticmethod
    def sync_from_purchase_entry(
        db: Session,
        entry: PurchaseEntry,
    ) -> FinancialMovement:
        movement = FinancialMovementWriter.get_by_purchase_entry_id(db, entry.id)

        if not movement:
            return FinancialMovementWriter.create_from_purchase_entry(db, entry)

        movement.movement_date = entry.issue_date or entry.order_date
        movement.kind = "expense"
        movement.status = "confirmed" if entry.status == "active" else "draft"
        movement.source_type = "excel_import"
        movement.source_document_id = entry.source_document_id
        movement.source_purchase_entry_id = entry.id
        movement.source_reference = entry.source_reference
        movement.third_party_name = entry.provider_name
        movement.concept = entry.notes
        movement.category = entry.category
        movement.subcategory = entry.subcategory
        movement.net_amount = FinancialMovementWriter._safe_decimal(entry.net_amount)
        movement.tax_amount = FinancialMovementWriter._safe_decimal(entry.tax_amount)
        movement.total_amount = FinancialMovementWriter._safe_decimal(entry.total_amount)
        movement.currency = entry.currency or "EUR"
        movement.needs_review = False
        movement.notes = f"Movimiento sincronizado desde PurchaseEntry {entry.id}"

        db.add(movement)
        db.commit()
        db.refresh(movement)
        return movement

    @staticmethod
    def delete_by_purchase_entry_id(
        db: Session,
        purchase_entry_id: UUID,
    ) -> bool:
        movement = FinancialMovementWriter.get_by_purchase_entry_id(db, purchase_entry_id)
        if not movement:
            return False

        db.delete(movement)
        db.commit()
        return True