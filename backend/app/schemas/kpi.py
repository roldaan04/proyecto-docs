from datetime import datetime
from decimal import Decimal
from uuid import UUID

from pydantic import BaseModel


class MonthlyKpiSnapshotResponse(BaseModel):
    id: UUID
    tenant_id: UUID
    month_key: str

    total_sales_net: Decimal
    total_sales_gross: Decimal
    total_purchases_net: Decimal
    total_purchases_gross: Decimal

    gross_margin_amount: Decimal
    gross_margin_pct: Decimal
    purchase_to_sales_ratio_pct: Decimal

    tickets_count: int
    average_ticket: Decimal
    documents_processed: int
    pending_reviews: int

    created_at: datetime
    updated_at: datetime

    class Config:
        from_attributes = True