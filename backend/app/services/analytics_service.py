from collections import defaultdict
import csv
from datetime import date, timedelta
from decimal import Decimal
import io
from sqlalchemy.orm import Session, joinedload

from app.models import (
    InventoryBatch,
    Order,
    OrderItem,
    Product,
    ProductVariant,
    Role,
    User,
)
from app.services.inventory_service import InventoryService

NON_REVENUE_STATUSES = {"CANCELLED", "REFUNDED"}


class AnalyticsService:
    def __init__(self, db: Session) -> None:
        self.db = db

    def get_overview(self) -> dict:
        orders = self.db.query(Order).all()
        revenue_orders = [o for o in orders if o.status not in NON_REVENUE_STATUSES]
        total_revenue = sum((o.total_amount for o in revenue_orders), Decimal("0.00"))
        pending_orders = sum(
            1 for o in orders if o.status in {"PENDING", "PAYMENT_PENDING", "CONFIRMED"}
        )

        customer_role = self.db.query(Role).filter(Role.name == "customer").first()
        total_customers = (
            self.db.query(User).filter(User.role_id == customer_role.id).count()
            if customer_role
            else self.db.query(User).count()
        )
        total_products = (
            self.db.query(Product).filter(Product.is_archived.is_(False)).count()
        )

        inv_service = InventoryService(self.db)
        inv_items = inv_service.list_inventory()
        low_stock_products = sum(1 for i in inv_items if i.is_low_stock)
        out_of_stock_products = sum(1 for i in inv_items if i.is_out_of_stock)
        expiring = inv_service.list_expiring_batches(days=60)
        near_expiry_batches = len(expiring["expiring_soon"]) + len(expiring["expired"])

        return {
            "total_revenue": float(total_revenue),
            "total_orders": len(orders),
            "total_customers": total_customers,
            "total_products": total_products,
            "pending_orders": pending_orders,
            "low_stock_products": low_stock_products,
            "out_of_stock_products": out_of_stock_products,
            "near_expiry_batches": near_expiry_batches,
        }

    def get_sales_series(self, granularity: str = "daily") -> list[dict]:
        orders = (
            self.db.query(Order)
            .filter(~Order.status.in_(NON_REVENUE_STATUSES))
            .order_by(Order.created_at.asc())
            .all()
        )
        buckets: dict[str, dict] = {}
        for o in orders:
            dt = o.created_at
            if granularity == "yearly":
                key = dt.strftime("%Y")
            elif granularity == "monthly":
                key = dt.strftime("%Y-%m")
            elif granularity == "weekly":
                iso = dt.isocalendar()
                key = f"{iso.year}-W{iso.week:02d}"
            else:
                key = dt.strftime("%Y-%m-%d")

            if key not in buckets:
                buckets[key] = {"period": key, "revenue": 0.0, "orders": 0}
            buckets[key]["revenue"] = round(buckets[key]["revenue"] + float(o.total_amount), 2)
            buckets[key]["orders"] += 1
        return list(buckets.values())

    def get_best_sellers(self, limit: int = 10) -> list[dict]:
        items = (
            self.db.query(OrderItem)
            .join(Order, OrderItem.order_id == Order.id)
            .filter(~Order.status.in_(NON_REVENUE_STATUSES))
            .all()
        )
        agg: dict[str, dict] = {}
        for item in items:
            key = item.product_name_snapshot
            if key not in agg:
                agg[key] = {
                    "product_name": key,
                    "units_sold": 0,
                    "revenue": 0.0,
                }
            agg[key]["units_sold"] += item.quantity
            agg[key]["revenue"] = round(agg[key]["revenue"] + float(item.line_total), 2)
        ranked = sorted(agg.values(), key=lambda x: x["units_sold"], reverse=True)
        return ranked[:limit]

    def get_category_and_brand_sales(self) -> dict:
        items = (
            self.db.query(OrderItem)
            .join(Order, OrderItem.order_id == Order.id)
            .filter(~Order.status.in_(NON_REVENUE_STATUSES))
            .all()
        )
        by_category: dict[str, float] = defaultdict(float)
        by_brand: dict[str, float] = defaultdict(float)
        for item in items:
            cat = item.category_name_snapshot or "Uncategorized"
            brand = item.brand_name_snapshot or "Unknown"
            by_category[cat] = round(by_category[cat] + float(item.line_total), 2)
            by_brand[brand] = round(by_brand[brand] + float(item.line_total), 2)

        return {
            "by_category": [
                {"name": k, "revenue": v}
                for k, v in sorted(by_category.items(), key=lambda kv: kv[1], reverse=True)
            ],
            "by_brand": [
                {"name": k, "revenue": v}
                for k, v in sorted(by_brand.items(), key=lambda kv: kv[1], reverse=True)
            ],
        }

    def get_variant_analytics(self) -> dict:
        items = (
            self.db.query(OrderItem)
            .join(Order, OrderItem.order_id == Order.id)
            .filter(~Order.status.in_(NON_REVENUE_STATUSES))
            .all()
        )
        variant_ids = [i.variant_id for i in items if i.variant_id]
        variant_map: dict = {}
        if variant_ids:
            variants = (
                self.db.query(ProductVariant)
                .options(joinedload(ProductVariant.product))
                .filter(ProductVariant.id.in_(variant_ids))
                .all()
            )
            variant_map = {v.id: v for v in variants}

        lipstick_shades: dict[str, int] = defaultdict(int)
        foundation_shades: dict[str, int] = defaultdict(int)
        by_color: dict[str, int] = defaultdict(int)
        by_volume: dict[str, int] = defaultdict(int)

        for item in items:
            v = variant_map.get(item.variant_id)
            prod_name = item.product_name_snapshot.lower()
            shade = item.shade_name_snapshot or (v.shade_name if v else None)
            if shade:
                if "lip" in prod_name:
                    lipstick_shades[shade] += item.quantity
                if "foundation" in prod_name or "concealer" in prod_name:
                    foundation_shades[shade] += item.quantity
            color = v.color_name if v and v.color_name else shade
            if color:
                by_color[color] += item.quantity
            vol = item.volume_ml_snapshot or (v.volume_ml if v else None)
            if vol:
                by_volume[f"{vol} ml"] += item.quantity

        return {
            "lipstick_shades": [
                {"shade": k, "units_sold": v}
                for k, v in sorted(lipstick_shades.items(), key=lambda kv: kv[1], reverse=True)
            ],
            "foundation_shades": [
                {"shade": k, "units_sold": v}
                for k, v in sorted(foundation_shades.items(), key=lambda kv: kv[1], reverse=True)
            ],
            "by_color": [
                {"color": k, "units_sold": v}
                for k, v in sorted(by_color.items(), key=lambda kv: kv[1], reverse=True)
            ],
            "by_volume": [
                {"volume": k, "units_sold": v}
                for k, v in sorted(by_volume.items(), key=lambda kv: kv[1], reverse=True)
            ],
        }

    def get_inventory_analytics(self) -> dict:
        inv_service = InventoryService(self.db)
        items = inv_service.list_inventory()
        healthy = sum(1 for i in items if not i.is_low_stock and not i.is_out_of_stock)
        low_stock = sum(1 for i in items if i.is_low_stock)
        out_of_stock = sum(1 for i in items if i.is_out_of_stock)
        expiring = inv_service.list_expiring_batches(days=60)
        return {
            "status_breakdown": [
                {"status": "Healthy", "count": healthy},
                {"status": "Low Stock", "count": low_stock},
                {"status": "Out of Stock", "count": out_of_stock},
            ],
            "expiring_soon_count": len(expiring["expiring_soon"]),
            "expired_count": len(expiring["expired"]),
            "total_variants": len(items),
        }

    def export_csv_report(self, report_type: str) -> str:
        buf = io.StringIO()
        writer = csv.writer(buf)
        if report_type == "inventory":
            writer.writerow(
                ["SKU", "Product", "Variant", "Available", "Reserved", "Sellable", "Threshold"]
            )
            for row in InventoryService(self.db).list_inventory():
                writer.writerow(
                    [
                        row.sku,
                        row.product_name,
                        row.variant_label,
                        row.available_quantity,
                        row.reserved_quantity,
                        row.sellable_quantity,
                        row.low_stock_threshold,
                    ]
                )
        else:
            writer.writerow(
                ["Order Number", "Status", "Payment Method", "Payment Status", "Total USD", "Created At"]
            )
            for o in self.db.query(Order).order_by(Order.created_at.desc()).all():
                writer.writerow(
                    [
                        o.order_number,
                        o.status,
                        o.payment_method,
                        o.payment_status,
                        f"{o.total_amount:.2f}",
                        o.created_at.isoformat(),
                    ]
                )
        return buf.getvalue()

