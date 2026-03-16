from datetime import date
from decimal import Decimal
from pydantic import BaseModel, Field


class ManualMovementCreateRequest(BaseModel):
    movement_date: date
    movement_type: str = Field(..., min_length=1)  # payroll | social_security | tax | freelance_fee | manual_expense | manual_income
    third_party_name: str = Field(..., min_length=1, max_length=255)
    third_party_tax_id: str | None = None
    concept: str = Field(..., min_length=1, max_length=255)

    category: str | None = None
    subcategory: str | None = None
    business_area: str | None = "administracion"

    net_amount: Decimal | None = None
    tax_amount: Decimal | None = Decimal("0.00")
    withholding_amount: Decimal | None = Decimal("0.00")
    total_amount: Decimal

    currency: str = "EUR"
    notes: str | None = None
    needs_review: bool = False