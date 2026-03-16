from decimal import Decimal
from pydantic import BaseModel


class AnalyticsOverviewResponse(BaseModel):
    total_income: Decimal
    total_expenses: Decimal
    total_purchases: Decimal
    gross_margin: Decimal
    gross_margin_pct: Decimal
    average_ticket: Decimal
    documents_processed: int
    pending_reviews: int


class MonthlyProfitabilityRow(BaseModel):
    month: str
    sales_net: Decimal
    sales_gross: Decimal
    purchases_net: Decimal
    purchases_gross: Decimal
    gross_margin_amount: Decimal
    gross_margin_pct: Decimal
    purchase_to_sales_ratio_pct: Decimal


class CategoryMetricRow(BaseModel):
    category_name: str
    total_amount: Decimal


class ProviderMetricRow(BaseModel):
    provider_name: str
    total_amount: Decimal