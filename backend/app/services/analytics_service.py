from decimal import Decimal

from sqlalchemy import func
from sqlalchemy.orm import Session

from app.models.financial_movement import FinancialMovement


class AnalyticsService:
    @staticmethod
    def _safe_decimal(value) -> Decimal:
        if value is None:
            return Decimal("0.00")
        if isinstance(value, Decimal):
            return value
        return Decimal(str(value))

    @staticmethod
    def get_overview(db: Session, tenant_id):
        income_total = (
            db.query(func.sum(FinancialMovement.total_amount))
            .filter(
                FinancialMovement.tenant_id == tenant_id,
                FinancialMovement.kind == "income",
                FinancialMovement.status.in_(["proposed", "confirmed", "reconciled"]),
            )
            .scalar()
        )

        expense_total = (
            db.query(func.sum(FinancialMovement.total_amount))
            .filter(
                FinancialMovement.tenant_id == tenant_id,
                FinancialMovement.kind == "expense",
                FinancialMovement.status.in_(["proposed", "confirmed", "reconciled"]),
            )
            .scalar()
        )

        purchase_total = (
            db.query(func.sum(FinancialMovement.total_amount))
            .filter(
                FinancialMovement.tenant_id == tenant_id,
                FinancialMovement.kind == "expense",
                FinancialMovement.source_type == "excel_import",
                FinancialMovement.status.in_(["proposed", "confirmed", "reconciled"]),
            )
            .scalar()
        )

        income_net = (
            db.query(func.sum(FinancialMovement.net_amount))
            .filter(
                FinancialMovement.tenant_id == tenant_id,
                FinancialMovement.kind == "income",
                FinancialMovement.status.in_(["proposed", "confirmed", "reconciled"]),
            )
            .scalar()
        )

        purchases_net = (
            db.query(func.sum(FinancialMovement.net_amount))
            .filter(
                FinancialMovement.tenant_id == tenant_id,
                FinancialMovement.kind == "expense",
                FinancialMovement.source_type == "excel_import",
                FinancialMovement.status.in_(["proposed", "confirmed", "reconciled"]),
            )
            .scalar()
        )

        documents_processed = (
            db.query(func.count(FinancialMovement.id))
            .filter(FinancialMovement.tenant_id == tenant_id)
            .scalar()
        )

        pending_reviews = (
            db.query(func.count(FinancialMovement.id))
            .filter(
                FinancialMovement.tenant_id == tenant_id,
                FinancialMovement.needs_review.is_(True),
            )
            .scalar()
        )

        avg_ticket = (
            db.query(func.avg(FinancialMovement.total_amount))
            .filter(
                FinancialMovement.tenant_id == tenant_id,
                FinancialMovement.kind == "income",
                FinancialMovement.status.in_(["proposed", "confirmed", "reconciled"]),
            )
            .scalar()
        )

        income_total = AnalyticsService._safe_decimal(income_total)
        expense_total = AnalyticsService._safe_decimal(expense_total)
        purchase_total = AnalyticsService._safe_decimal(purchase_total)
        income_net = AnalyticsService._safe_decimal(income_net)
        purchases_net = AnalyticsService._safe_decimal(purchases_net)
        avg_ticket = AnalyticsService._safe_decimal(avg_ticket)

        gross_margin = income_net - purchases_net
        gross_margin_pct = (
            (gross_margin / income_net) if income_net > 0 else Decimal("0.00")
        )

        return {
            "total_income": income_total.quantize(Decimal("0.01")),
            "total_expenses": expense_total.quantize(Decimal("0.01")),
            "total_purchases": purchase_total.quantize(Decimal("0.01")),
            "gross_margin": gross_margin.quantize(Decimal("0.01")),
            "gross_margin_pct": gross_margin_pct.quantize(Decimal("0.0001")),
            "average_ticket": avg_ticket.quantize(Decimal("0.01")),
            "documents_processed": int(documents_processed or 0),
            "pending_reviews": int(pending_reviews or 0),
        }

    @staticmethod
    def get_monthly_profitability(db: Session, tenant_id):
        month_expr = func.to_char(FinancialMovement.movement_date, "YYYY-MM")

        rows = (
            db.query(
                month_expr.label("month"),
                func.sum(
                    FinancialMovement.net_amount
                ).filter(FinancialMovement.kind == "income").label("sales_net"),
                func.sum(
                    FinancialMovement.total_amount
                ).filter(FinancialMovement.kind == "income").label("sales_gross"),
                func.sum(
                    FinancialMovement.net_amount
                ).filter(
                    FinancialMovement.kind == "expense",
                    FinancialMovement.source_type == "excel_import",
                ).label("purchases_net"),
                func.sum(
                    FinancialMovement.total_amount
                ).filter(
                    FinancialMovement.kind == "expense",
                    FinancialMovement.source_type == "excel_import",
                ).label("purchases_gross"),
            )
            .filter(
                FinancialMovement.tenant_id == tenant_id,
                FinancialMovement.movement_date.isnot(None),
                FinancialMovement.status.in_(["proposed", "confirmed", "reconciled"]),
            )
            .group_by(month_expr)
            .order_by(month_expr)
            .all()
        )

        result = []

        for row in rows:
            sales_net = AnalyticsService._safe_decimal(row.sales_net)
            sales_gross = AnalyticsService._safe_decimal(row.sales_gross)
            purchases_net = AnalyticsService._safe_decimal(row.purchases_net)
            purchases_gross = AnalyticsService._safe_decimal(row.purchases_gross)

            gross_margin_amount = sales_net - purchases_net
            gross_margin_pct = (
                (gross_margin_amount / sales_net) if sales_net > 0 else Decimal("0.00")
            )
            purchase_to_sales_ratio_pct = (
                (purchases_net / sales_net) if sales_net > 0 else Decimal("0.00")
            )

            result.append(
                {
                    "month": row.month,
                    "sales_net": sales_net.quantize(Decimal("0.01")),
                    "sales_gross": sales_gross.quantize(Decimal("0.01")),
                    "purchases_net": purchases_net.quantize(Decimal("0.01")),
                    "purchases_gross": purchases_gross.quantize(Decimal("0.01")),
                    "gross_margin_amount": gross_margin_amount.quantize(Decimal("0.01")),
                    "gross_margin_pct": gross_margin_pct.quantize(Decimal("0.0001")),
                    "purchase_to_sales_ratio_pct": purchase_to_sales_ratio_pct.quantize(Decimal("0.0001")),
                }
            )

        return result

    @staticmethod
    def get_top_suppliers(db: Session, tenant_id, limit: int = 5):
        rows = (
            db.query(
                FinancialMovement.third_party_name.label("provider_name"),
                func.sum(FinancialMovement.total_amount).label("total_amount"),
            )
            .filter(
                FinancialMovement.tenant_id == tenant_id,
                FinancialMovement.kind == "expense",
                FinancialMovement.status.in_(["proposed", "confirmed", "reconciled"]),
                FinancialMovement.third_party_name.isnot(None),
            )
            .group_by(FinancialMovement.third_party_name)
            .order_by(func.sum(FinancialMovement.total_amount).desc())
            .limit(limit)
            .all()
        )

        return [
            {
                "provider_name": row.provider_name,
                "total_amount": AnalyticsService._safe_decimal(row.total_amount).quantize(Decimal("0.01")),
            }
            for row in rows
        ]

    @staticmethod
    def get_expenses_by_category(db: Session, tenant_id, limit: int = 6):
        rows = (
            db.query(
                FinancialMovement.category.label("category_name"),
                func.sum(FinancialMovement.total_amount).label("total_amount"),
            )
            .filter(
                FinancialMovement.tenant_id == tenant_id,
                FinancialMovement.kind == "expense",
                FinancialMovement.status.in_(["proposed", "confirmed", "reconciled"]),
                FinancialMovement.category.isnot(None),
            )
            .group_by(FinancialMovement.category)
            .order_by(func.sum(FinancialMovement.total_amount).desc())
            .limit(limit)
            .all()
        )

        return [
            {
                "category_name": row.category_name or "Sin categoría",
                "total_amount": AnalyticsService._safe_decimal(row.total_amount).quantize(Decimal("0.01")),
            }
            for row in rows
        ]