from fastapi import APIRouter, Depends, Query
from fastapi.responses import Response
from sqlalchemy.orm import Session

from app.api.deps import require_roles
from app.db.session import get_db
from app.models import User
from app.services.analytics_service import AnalyticsService

router = APIRouter(prefix="/admin", tags=["Analytics & Reports"])


@router.get("/analytics/overview")
def analytics_overview(
    _actor: User = Depends(require_roles("admin", "super_admin")),
    db: Session = Depends(get_db),
):
    return AnalyticsService(db).get_overview()


@router.get("/analytics/sales")
def analytics_sales(
    granularity: str = Query("daily", pattern="^(daily|weekly|monthly|yearly)$"),
    _actor: User = Depends(require_roles("admin", "super_admin")),
    db: Session = Depends(get_db),
):
    return AnalyticsService(db).get_sales_series(granularity=granularity)


@router.get("/analytics/best-sellers")
def analytics_best_sellers(
    limit: int = Query(10, ge=1, le=50),
    _actor: User = Depends(require_roles("admin", "super_admin")),
    db: Session = Depends(get_db),
):
    return AnalyticsService(db).get_best_sellers(limit=limit)


@router.get("/analytics/categories")
def analytics_categories(
    _actor: User = Depends(require_roles("admin", "super_admin")),
    db: Session = Depends(get_db),
):
    return AnalyticsService(db).get_category_and_brand_sales()


@router.get("/analytics/variants")
def analytics_variants(
    _actor: User = Depends(require_roles("admin", "super_admin")),
    db: Session = Depends(get_db),
):
    return AnalyticsService(db).get_variant_analytics()


@router.get("/analytics/inventory")
def analytics_inventory(
    _actor: User = Depends(require_roles("admin", "super_admin")),
    db: Session = Depends(get_db),
):
    return AnalyticsService(db).get_inventory_analytics()


@router.get("/reports/export")
def export_report(
    report_type: str = Query("sales", pattern="^(sales|inventory)$"),
    _actor: User = Depends(require_roles("admin", "super_admin")),
    db: Session = Depends(get_db),
):
    csv_data = AnalyticsService(db).export_csv_report(report_type)
    return Response(
        content=csv_data,
        media_type="text/csv",
        headers={
            "Content-Disposition": f'attachment; filename="glowcart-{report_type}-report.csv"'
        },
    )

