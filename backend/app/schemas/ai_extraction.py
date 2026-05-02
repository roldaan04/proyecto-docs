from typing import Literal
from pydantic import BaseModel, Field


class AIExtractionResult(BaseModel):
    document_type: Literal["invoice", "ticket", "receipt", "other"] = "other"
    operation_kind: Literal["income", "expense", "unknown"] = "unknown"

    issuer_name: str | None = None
    issuer_tax_id: str | None = None
    receiver_name: str | None = None
    receiver_tax_id: str | None = None
    third_party_name: str | None = None
    third_party_tax_id: str | None = None

    invoice_number: str | None = None
    issue_date: str | None = None
    due_date: str | None = None

    tax_base: float | None = None
    vat_amount: float | None = None
    irpf_amount: float | None = None
    total_amount: float | None = None
    currency: str = "EUR"

    category: str | None = None
    confidence_score: float = Field(default=0.0, ge=0.0, le=1.0)
    needs_review: bool = True
    review_reason: str | None = None
