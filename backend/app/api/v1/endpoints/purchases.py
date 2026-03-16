import uuid

from fastapi import APIRouter, Depends, File, HTTPException, Query, UploadFile, status
from sqlalchemy.orm import Session

from app.core.database import get_db
from app.core.dependencies import get_current_tenant, get_current_user
from app.models.tenant import Tenant
from app.models.user import User
from app.schemas.purchase import (
    PurchaseEntryResponse,
    PurchaseEntryUpdate,
    PurchaseImportResponse,
)
from app.services.purchase_import_service import PurchaseImportService
from app.services.purchase_service import PurchaseService

router = APIRouter(prefix="/purchases", tags=["Purchases"])


@router.post(
    "/import",
    response_model=PurchaseImportResponse,
    status_code=status.HTTP_201_CREATED,
)
async def import_purchases_excel(
    file: UploadFile = File(...),
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_user),
    tenant: Tenant = Depends(get_current_tenant),
):
    service = PurchaseImportService(db)
    batch = await service.import_excel(
        tenant_id=tenant.id,
        user_id=current_user.id if current_user else None,
        file=file,
    )

    return PurchaseImportResponse(
        batch_id=batch.id,
        filename_original=batch.filename_original,
        rows_detected=batch.rows_detected,
        rows_imported=batch.rows_imported,
        rows_skipped=batch.rows_skipped,
        status=batch.status,
        error_message=batch.error_message,
    )


@router.get(
    "",
    response_model=list[PurchaseEntryResponse],
)
def list_purchases(
    provider_name: str | None = Query(default=None),
    month_key: str | None = Query(default=None),
    category: str | None = Query(default=None),
    status_value: str | None = Query(default=None, alias="status"),
    skip: int = Query(default=0, ge=0),
    limit: int = Query(default=100, ge=1, le=500),
    db: Session = Depends(get_db),
    tenant: Tenant = Depends(get_current_tenant),
    _: User = Depends(get_current_user),
):
    service = PurchaseService(db)
    return service.list_entries(
        tenant_id=tenant.id,
        provider_name=provider_name,
        month_key=month_key,
        category=category,
        status=status_value,
        skip=skip,
        limit=limit,
    )


@router.get(
    "/{entry_id}",
    response_model=PurchaseEntryResponse,
)
def get_purchase(
    entry_id: uuid.UUID,
    db: Session = Depends(get_db),
    tenant: Tenant = Depends(get_current_tenant),
    _: User = Depends(get_current_user),
):
    service = PurchaseService(db)
    entry = service.get_entry(tenant_id=tenant.id, entry_id=entry_id)

    if not entry:
        raise HTTPException(status_code=404, detail="Compra no encontrada.")

    return entry


@router.patch(
    "/{entry_id}",
    response_model=PurchaseEntryResponse,
)
def update_purchase(
    entry_id: uuid.UUID,
    payload: PurchaseEntryUpdate,
    db: Session = Depends(get_db),
    tenant: Tenant = Depends(get_current_tenant),
    _: User = Depends(get_current_user),
):
    service = PurchaseService(db)
    entry = service.update_entry(
        tenant_id=tenant.id,
        entry_id=entry_id,
        payload=payload,
    )

    if not entry:
        raise HTTPException(status_code=404, detail="Compra no encontrada.")

    return entry


@router.delete(
    "/{entry_id}",
    status_code=status.HTTP_204_NO_CONTENT,
)
def delete_purchase(
    entry_id: uuid.UUID,
    db: Session = Depends(get_db),
    tenant: Tenant = Depends(get_current_tenant),
    _: User = Depends(get_current_user),
):
    service = PurchaseService(db)
    deleted = service.delete_entry(tenant_id=tenant.id, entry_id=entry_id)

    if not deleted:
        raise HTTPException(status_code=404, detail="Compra no encontrada.")

    return None