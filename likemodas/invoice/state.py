# likemodas/invoice/state.py (VERSIÓN FINAL Y CORRECTA)
from __future__ import annotations
import reflex as rx
import sqlmodel
import sqlalchemy
from typing import Optional

# Importamos todo lo necesario desde el estado principal
from ..state import AppState, InvoiceData, InvoiceItemData
from ..models import PurchaseModel, UserInfo, PurchaseItemModel, BlogPostModel
from ..utils.formatting import format_to_cop


class InvoiceState(rx.State):
    """Un estado INDEPENDIENTE y aislado para la factura."""
    is_loading: bool = True
    invoice_data: Optional[InvoiceData] = None

    @rx.event
    async def on_load_invoice_page(self):
        """
        Se ejecuta al cargar la página de la factura. Pide los datos al AppState.
        """
        self.is_loading = True
        self.invoice_data = None

        purchase_id_str = self.router.query_params.get("id", "0")
        try:
            purchase_id = int(purchase_id_str)
            if purchase_id <= 0:
                yield rx.toast.error("ID de factura no válido.")
                self.is_loading = False
                return
        except ValueError:
            yield rx.toast.error("ID de factura no válido.")
            self.is_loading = False
            return

        # Pedimos al AppState que nos dé los datos de la factura
        invoice_result = await self.get_state(AppState).get_invoice_data(purchase_id)

        if invoice_result:
            self.invoice_data = invoice_result
        else:
            yield rx.toast.error("Factura no encontrada o no tienes permisos para verla.")

        self.is_loading = False