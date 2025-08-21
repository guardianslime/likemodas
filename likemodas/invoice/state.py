# likemodas/invoice/state.py (NUEVO ARCHIVO)
from __future__ import annotations
import reflex as rx
import sqlmodel
import sqlalchemy
from typing import Optional, List

from ..state import AppState
from ..models import PurchaseModel, UserInfo, PurchaseItemModel, BlogPostModel
from ..utils.formatting import format_to_cop

# 1. MOVEMOS LAS CLASES DTO AQUÍ
class InvoiceItemData(rx.Base):
    """Un modelo específico para cada línea de artículo en la factura."""
    name: str
    quantity: int
    price: float

    @property
    def price_cop(self) -> str:
        return format_to_cop(self.price)

    @property
    def total_cop(self) -> str:
        return format_to_cop(self.price * self.quantity)

class InvoiceData(rx.Base):
    """DTO para contener toda la información necesaria para una factura."""
    id: int
    purchase_date_formatted: str
    status: str
    items: list[InvoiceItemData]
    customer_name: str
    customer_email: str
    shipping_full_address: str
    shipping_phone: str
    subtotal_cop: str
    total_price_cop: str

# 2. CREAMOS EL ESTADO AISLADO
class InvoiceState(AppState):
    """Un estado dedicado únicamente a gestionar la lógica de la factura."""

    invoice_data: Optional[InvoiceData] = None

    @rx.event
    def on_load_invoice_page(self):
        """Carga los datos de la compra para la factura."""
        self.invoice_data = None
        purchase_id_str = self.router.query_params.get("id", "0")
        try:
            purchase_id = int(purchase_id_str)
            if purchase_id <= 0:
                return rx.toast.error("ID de factura no válido.")
        except ValueError:
            return rx.toast.error("ID de factura no válido.")

        with rx.session() as session:
            purchase = session.exec(
                sqlmodel.select(PurchaseModel)
                .options(
                    sqlalchemy.orm.joinedload(PurchaseModel.userinfo).joinedload(UserInfo.user),
                    sqlalchemy.orm.joinedload(PurchaseModel.items).joinedload(PurchaseItemModel.blog_post)
                )
                .where(PurchaseModel.id == purchase_id)
            ).one_or_none()

            if not purchase:
                return rx.toast.error(f"No se encontró la compra #{purchase_id}.")

            if not self.is_admin and (not self.authenticated_user_info or self.authenticated_user_info.id != purchase.userinfo_id):
                return rx.toast.error("Acceso denegado a esta factura.")

            invoice_items = [
                InvoiceItemData(
                    name=item.blog_post.title,
                    quantity=item.quantity,
                    price=item.price_at_purchase
                )
                for item in purchase.items if item.blog_post
            ]

            self.invoice_data = InvoiceData(
                id=purchase.id,
                purchase_date_formatted=purchase.purchase_date_formatted,
                status=purchase.status.value,
                items=invoice_items,
                customer_name=purchase.shipping_name,
                customer_email=purchase.userinfo.email if purchase.userinfo else "N/A",
                shipping_full_address=f"{purchase.shipping_address}, {purchase.shipping_neighborhood}, {purchase.shipping_city}",
                shipping_phone=purchase.shipping_phone,
                subtotal_cop=format_to_cop(purchase.total_price),
                total_price_cop=purchase.total_price_cop,
            )

        yield
        # Opcional: Descomenta la siguiente línea si quieres que la impresión se active automáticamente
        # return rx.call_script("window.print()")