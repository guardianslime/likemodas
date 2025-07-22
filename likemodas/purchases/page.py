import reflex as rx
import reflex_local_auth
from ..ui.base import base_page
from .state import PurchaseHistoryState
from ..models import PurchaseModel
from ..account.layout import account_layout

def purchase_detail_card(purchase: PurchaseModel) -> rx.Component:
    """
    Componente para mostrar el detalle de una compra en el historial del usuario.
    --- DISEÑO ACTUALIZADO CON TEXTO MÁS GRANDE Y CENTRADO ---
    """
    return rx.card(
        rx.vstack(
            # Sección Superior: Fecha y Estado
            rx.hstack(
                rx.vstack(
                    rx.text(f"Compra del: {purchase.purchase_date_formatted}", weight="bold", size="5"),
                    rx.text(f"ID de Compra: #{purchase.id}", size="2", color_scheme="gray"),
                    align_items="start",
                ),
                rx.spacer(),
                rx.vstack(
                    rx.badge(purchase.status.to(str), color_scheme="blue", variant="soft", size="2"),
                    rx.heading(f"${purchase.total_price:.2f}", size="6"),
                    align_items="end",
                ),
                justify="between",
                width="100%",
            ),
            rx.divider(),
            
            # Sección de Envío
            rx.vstack(
                rx.text("Detalles de Envío:", weight="medium", size="4"),
                rx.text(f"Nombre: {purchase.shipping_name}", size="3"),
                rx.text(f"Dirección: {purchase.shipping_address}, {purchase.shipping_neighborhood}, {purchase.shipping_city}", size="3"),
                rx.text(f"Teléfono: {purchase.shipping_phone}", size="3"),
                spacing="1",
                align_items="start",
                width="100%",
            ),
            rx.divider(),

            # Sección de Artículos
            rx.vstack(
                rx.text("Artículos Comprados:", weight="medium", size="4"),
                rx.foreach(
                    purchase.items_formatted,
                    lambda item_str: rx.text(item_str, size="3")
                ),
                spacing="1",
                align_items="start",
                width="100%",
            ),
            
            spacing="4",
            width="100%"
        ),
        width="100%",
        padding="1.5em",
    )

@reflex_local_auth.require_login
def purchase_history_page() -> rx.Component:
    """Página del historial de compras del usuario."""
    # ✅ CAMBIO: Se envuelve el vstack en un rx.center para centrarlo horizontalmente.
    page_content = rx.center(
        rx.vstack(
            rx.heading("Mi Historial de Compras", size="7"),
            rx.cond(
                PurchaseHistoryState.purchases,
                rx.foreach(PurchaseHistoryState.purchases, purchase_detail_card),
                rx.center(
                    rx.text("No tienes compras anteriores."),
                    padding_y="2em",
                )
            ),
            spacing="6",
            width="100%",
            max_width="960px",
            align="center"
        ),
        width="100%" # Hacemos que el center ocupe todo el ancho disponible.
    )
    
    return base_page(account_layout(page_content))
