# likemodas/purchases/page.py (VERSIÓN MODIFICADA)

import reflex as rx
import reflex_local_auth
from ..ui.base import base_page
from .state import PurchaseHistoryState
from ..models import PurchaseModel
from ..account.layout import account_layout # ✅ Importamos el nuevo layout

def purchase_detail_card(purchase: PurchaseModel) -> rx.Component:
    # (Esta función no cambia)
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
    # ✅ Se envuelve el contenido en el nuevo account_layout
    page_content = rx.vstack(
        rx.heading("Mi Historial de Compras", size="7"),
        rx.cond(
            PurchaseHistoryState.purchases,
            rx.foreach(PurchaseHistoryState.purchases, purchase_detail_card),
            rx.text("No tienes compras anteriores.")
        ),
        spacing="5",
        width="100%",
        max_width="800px",
        align="center"
    )
    
    return base_page(account_layout(page_content))