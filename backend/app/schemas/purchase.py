from datetime import date, datetime
from decimal import Decimal
from uuid import UUID

from pydantic import BaseModel, Field


class PurchaseEntryBase(BaseModel):
    provider_name: str = Field(..., min_length=1, max_length=255)
    issue_date: date | None = None
    order_date: date | None = None

    net_amount: Decimal = Field(default=Decimal("0.00"))
    tax_amount: Decimal = Field(default=Decimal("0.00"))
    total_amount: Decimal = Field(default=Decimal("0.00"))

    currency: str = "EUR"
    category: str | None = None
    subcategory: str | None = None
    notes: str | None = None
    source_type: str = "excel_import"
    source_reference: str | None = None
    status: str = "active"


class PurchaseEntryCreate(PurchaseEntryBase):
    pass


class PurchaseEntryUpdate(BaseModel):
    provider_name: str | None = None
    issue_date: date | None = None
    order_date: date | None = None

    net_amount: Decimal | None = None
    tax_amount: Decimal | None = None
    total_amount: Decimal | None = None

    currency: str | None = None
    category: str | None = None
    subcategory: str | None = None
    notes: str | None = None
    status: str | None = None


class PurchaseEntryResponse(PurchaseEntryBase):
    id: UUID
    tenant_id: UUID
    source_document_id: UUID | None
    import_batch_id: UUID | None
    month_key: str | None
    row_fingerprint: str
    created_at: datetime
    updated_at: datetime

    class Config:
        from_attributes = True


class PurchaseImportResponse(BaseModel):
    batch_id: UUID
    filename_original: str
    rows_detected: int
    rows_imported: int
    rows_skipped: int
    status: str
    error_message: str | None = None


class PurchaseImportBatchResponse(BaseModel):
    id: UUID
    tenant_id: UUID
    uploaded_by_user_id: UUID | None
    source_document_id: UUID | None

    filename_original: str
    storage_key: str | None
    mime_type: str | None
    file_size: int | None
    checksum: str | None

    rows_detected: int
    rows_imported: int
    rows_skipped: int

    status: str
    error_message: str | None

    started_at: datetime | None
    finished_at: datetime | None
    created_at: datetime
    updated_at: datetime

    class Config:
        from_attributes = True