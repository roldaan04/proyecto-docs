from decimal import Decimal
from uuid import UUID

from sqlalchemy.orm import Session

from app.models.financial_movement import FinancialMovement
from app.schemas.manual_movement import ManualMovementCreateRequest


class ManualMovementService:
    MOVEMENT_TYPE_MAP = {
        "payroll": {
            "kind": "expense",
            "category": "Nominas",
            "subcategory": "Personal",
            "business_area": "personal",
        },
        "social_security": {
            "kind": "expense",
            "category": "Seguridad social",
            "subcategory": "Cotizaciones",
            "business_area": "personal",
        },
        "tax": {
            "kind": "expense",
            "category": "Impuestos",
            "subcategory": "Tributos",
            "business_area": "fiscalidad",
        },
        "freelance_fee": {
            "kind": "expense",
            "category": "Colaboradores",
            "subcategory": "Servicios profesionales",
            "business_area": "operaciones",
        },
        "manual_expense": {
            "kind": "expense",
            "category": "Gasto manual",
            "subcategory": "General",
            "business_area": "general",
        },
        "manual_income": {
            "kind": "income",
            "category": "Ingreso manual",
            "subcategory": "General",
            "business_area": "general",
        },
    }

    @classmethod
    def create_manual_movement(
        cls,
        db: Session,
        tenant_id: UUID,
        payload: ManualMovementCreateRequest,
    ) -> FinancialMovement:
        movement_type = payload.movement_type.strip().lower()

        if movement_type not in cls.MOVEMENT_TYPE_MAP:
            raise ValueError("Tipo de movimiento manual no válido.")

        preset = cls.MOVEMENT_TYPE_MAP[movement_type]

        net_amount = payload.net_amount
        tax_amount = payload.tax_amount or Decimal("0.00")
        withholding_amount = payload.withholding_amount or Decimal("0.00")

        if net_amount is None:
            net_amount = payload.total_amount - tax_amount + withholding_amount

        movement = FinancialMovement(
            tenant_id=tenant_id,
            movement_date=payload.movement_date,
            kind=preset["kind"],
            status="confirmed",
            source_type="manual",
            source_document_id=None,
            source_financial_entry_id=None,
            source_purchase_entry_id=None,
            source_reference=movement_type,
            third_party_name=payload.third_party_name,
            third_party_tax_id=payload.third_party_tax_id,
            concept=payload.concept,
            category=payload.category or preset["category"],
            subcategory=payload.subcategory or preset["subcategory"],
            business_area=payload.business_area or preset["business_area"],
            net_amount=net_amount,
            tax_amount=tax_amount,
            withholding_amount=withholding_amount,
            total_amount=payload.total_amount,
            currency=payload.currency,
            document_type=None,
            confidence_score=None,
            needs_review=payload.needs_review,
            notes=payload.notes,
        )

        db.add(movement)
        db.commit()
        db.refresh(movement)
        return movement