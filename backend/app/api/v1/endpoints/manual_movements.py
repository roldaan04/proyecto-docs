from fastapi import APIRouter, Depends, HTTPException, Query, status
from sqlalchemy.orm import Session

from app.core.database import get_db
from app.core.dependencies import get_current_tenant, get_current_user
from app.models.tenant import Tenant
from app.models.user import User
from app.schemas.financial_movement import FinancialMovementResponse
from app.schemas.manual_movement import ManualMovementCreateRequest
from app.services.financial_movement_service import FinancialMovementService
from app.services.manual_movement_service import ManualMovementService

router = APIRouter(prefix="/manual-movements", tags=["Manual Movements"])


@router.post("", response_model=FinancialMovementResponse, status_code=status.HTTP_201_CREATED)
def create_manual_movement(
    payload: ManualMovementCreateRequest,
    db: Session = Depends(get_db),
    tenant: Tenant = Depends(get_current_tenant),
    _: User = Depends(get_current_user),
):
    try:
        return ManualMovementService.create_manual_movement(db, tenant.id, payload)
    except ValueError as e:
        raise HTTPException(status_code=400, detail=str(e))


@router.get("", response_model=list[FinancialMovementResponse])
def list_manual_movements(
    category: str | None = Query(default=None),
    third_party_name: str | None = Query(default=None),
    skip: int = Query(default=0, ge=0),
    limit: int = Query(default=100, ge=1, le=500),
    db: Session = Depends(get_db),
    tenant: Tenant = Depends(get_current_tenant),
    _: User = Depends(get_current_user),
):
    service = FinancialMovementService(db)
    return service.list_by_tenant(
        tenant.id,
        source_type="manual",
        category=category,
        third_party_name=third_party_name,
        skip=skip,
        limit=limit,
    )