from datetime import date
from typing import Optional

from fastapi import APIRouter, Depends, Query
from sqlalchemy.orm import Session

from app.core.database import get_db
from app.core.dependencies import get_current_tenant
from app.models.tenant import Tenant
from app.schemas.analytics import (
    AnalyticsOverviewResponse,
    CategoryMetricRow,
    MonthlyFlowRow,
    ProviderMetricRow,
    TaxMonthlyFlowRow,
    TopThirdPartyRow,
)
from app.services.analytics_service import AnalyticsService

router = APIRouter(prefix="/analytics", tags=["Analytics"])


@router.get("/overview", response_model=AnalyticsOverviewResponse)
def get_analytics_overview(
    date_from: Optional[date] = Query(default=None),
    date_to: Optional[date] = Query(default=None),
    current_tenant: Tenant = Depends(get_current_tenant),
    db: Session = Depends(get_db),
):
    return AnalyticsService.get_overview(db, current_tenant.id, date_from=date_from, date_to=date_to)


@router.get("/monthly-flow", response_model=list[MonthlyFlowRow])
def get_monthly_flow(
    date_from: Optional[date] = Query(default=None),
    date_to: Optional[date] = Query(default=None),
    current_tenant: Tenant = Depends(get_current_tenant),
    db: Session = Depends(get_db),
):
    return AnalyticsService.get_monthly_flow(db, current_tenant.id, date_from=date_from, date_to=date_to)


@router.get("/top-customers", response_model=list[TopThirdPartyRow])
def get_top_customers(
    limit: int = Query(default=5, ge=1, le=20),
    date_from: Optional[date] = Query(default=None),
    date_to: Optional[date] = Query(default=None),
    current_tenant: Tenant = Depends(get_current_tenant),
    db: Session = Depends(get_db),
):
    return AnalyticsService.get_top_customers(db, current_tenant.id, limit, date_from=date_from, date_to=date_to)


@router.get("/top-suppliers", response_model=list[TopThirdPartyRow])
def get_top_suppliers(
    limit: int = Query(default=5, ge=1, le=20),
    date_from: Optional[date] = Query(default=None),
    date_to: Optional[date] = Query(default=None),
    current_tenant: Tenant = Depends(get_current_tenant),
    db: Session = Depends(get_db),
):
    return AnalyticsService.get_top_suppliers(db, current_tenant.id, limit, date_from=date_from, date_to=date_to)


@router.get("/expenses-by-category", response_model=list[CategoryMetricRow])
def get_expenses_by_category(
    limit: int = Query(default=6, ge=1, le=20),
    date_from: Optional[date] = Query(default=None),
    date_to: Optional[date] = Query(default=None),
    current_tenant: Tenant = Depends(get_current_tenant),
    db: Session = Depends(get_db),
):
    return AnalyticsService.get_expenses_by_category(db, current_tenant.id, limit, date_from=date_from, date_to=date_to)


@router.get("/income-by-category", response_model=list[CategoryMetricRow])
def get_income_by_category(
    limit: int = Query(default=6, ge=1, le=20),
    date_from: Optional[date] = Query(default=None),
    date_to: Optional[date] = Query(default=None),
    current_tenant: Tenant = Depends(get_current_tenant),
    db: Session = Depends(get_db),
):
    return AnalyticsService.get_income_by_category(db, current_tenant.id, limit, date_from=date_from, date_to=date_to)


@router.get("/tax-monthly-flow", response_model=list[TaxMonthlyFlowRow])
def get_tax_monthly_flow(
    date_from: Optional[date] = Query(default=None),
    date_to: Optional[date] = Query(default=None),
    current_tenant: Tenant = Depends(get_current_tenant),
    db: Session = Depends(get_db),
):
    return AnalyticsService.get_tax_monthly_flow(db, current_tenant.id, date_from=date_from, date_to=date_to)
