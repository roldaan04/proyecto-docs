from fastapi import APIRouter, Depends, Query
from sqlalchemy.orm import Session

from app.core.database import get_db
from app.core.dependencies import get_current_tenant
from app.models.tenant import Tenant
from app.schemas.analytics import (
    AnalyticsOverviewResponse,
    MonthlyProfitabilityRow,
    ProviderMetricRow,
    CategoryMetricRow,
)
from app.services.analytics_service import AnalyticsService

router = APIRouter(prefix="/analytics", tags=["Analytics"])


@router.get("/overview", response_model=AnalyticsOverviewResponse)
def get_analytics_overview(
    current_tenant: Tenant = Depends(get_current_tenant),
    db: Session = Depends(get_db),
):
    return AnalyticsService.get_overview(db, current_tenant.id)


@router.get("/monthly-profitability", response_model=list[MonthlyProfitabilityRow])
def get_monthly_profitability(
    current_tenant: Tenant = Depends(get_current_tenant),
    db: Session = Depends(get_db),
):
    return AnalyticsService.get_monthly_profitability(db, current_tenant.id)


@router.get("/top-suppliers", response_model=list[ProviderMetricRow])
def get_top_suppliers(
    limit: int = Query(default=5, ge=1, le=20),
    current_tenant: Tenant = Depends(get_current_tenant),
    db: Session = Depends(get_db),
):
    return AnalyticsService.get_top_suppliers(db, current_tenant.id, limit)


@router.get("/expenses-by-category", response_model=list[CategoryMetricRow])
def get_expenses_by_category(
    limit: int = Query(default=6, ge=1, le=20),
    current_tenant: Tenant = Depends(get_current_tenant),
    db: Session = Depends(get_db),
):
    return AnalyticsService.get_expenses_by_category(db, current_tenant.id, limit)