# full_stack_python/purchases/page.py (CORREGIDO Y COMPLETO)

import reflex as rx
import reflex_local_auth
from ..ui.base import base_page
from .state import PurchaseHistoryState
from ..cart.state import CartState
from ..models import PurchaseModel

def purchase_detail_card(purchase: PurchaseModel) -> rx.Component:
    return rx.card(
        rx.vstack(
            rx.hstack(
                rx.text(f"Compra del: {purchase.purchase_date_formatted}", weight="bold"),
                rx.spacer(),
                rx.badge(purchase.status.to(str), color_scheme="blue"),
                justify="between",
                width="100%"
            ),
            rx.divider(),
            rx.foreach(
                purchase.items_formatted,
                lambda item_str: rx.text(item_str)
            ),
            rx.divider(),
            rx.text(f"Total: ${purchase.total_price:.2f}", weight="bold", align_self="flex-end"),
            spacing="3",
            width="100%"
        )
    )

@reflex_local_auth.require_login
def purchase_history_page() -> rx.Component:
    return base_page(
        rx.vstack(
            rx.heading("Mi Historial de Compras", size="8"),
            rx.cond(
                CartState.purchase_successful,
                rx.callout(
                    "¡Gracias por tu compra! Tu orden está pendiente de confirmación.",
                    icon="check",
                    color_scheme="green"
                )
            ),
            # --- ✨ CORRECCIÓN: Condición más robusta para evitar el error ---
            rx.cond(
                (PurchaseHistoryState.purchases) & (PurchaseHistoryState.purchases.length() > 0),
                rx.foreach(PurchaseHistoryState.purchases, purchase_detail_card),
                rx.text("No tienes compras anteriores.")
            ),
            spacing="5",
            width="100%",
            max_width="800px",
            align="center",
            padding="2em"
        )
    )