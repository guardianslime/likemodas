# likemodas/purchases/page.py (CORREGIDO)

import reflex as rx
import reflex_local_auth
from ..state import AppState, UserPurchaseHistoryCardData
from ..account.layout import account_layout

def purchase_detail_card(purchase: UserPurchaseHistoryCardData) -> rx.Component:
    """Componente para mostrar el detalle de una compra en el historial del usuario."""
    return rx.card(
        rx.vstack(
            rx.hstack(
                rx.vstack(
                    rx.text(f"Compra del: {purchase.purchase_date_formatted}", weight="bold", size="5"),
                    rx.text(f"ID de Compra: #{purchase.id}", size="2", color_scheme="gray"),
                    align_items="start",
                ),
                rx.spacer(),
                rx.vstack(
                    rx.badge(purchase.status, color_scheme="blue", variant="soft", size="2"), 
                    rx.heading(purchase.total_price_cop, size="6"), 
                    align_items="end",
                ),
                justify="between",
                width="100%",
            ),
            rx.divider(),
            rx.vstack(
                rx.text("Detalles de Envío:", weight="medium", size="4"),
                rx.text(f"Nombre: {purchase.shipping_name}", size="3"),
                rx.text(f"Dirección: {purchase.shipping_address}, {purchase.shipping_neighborhood}, {purchase.shipping_city}", size="3"),
                rx.text(f"Teléfono: {purchase.shipping_phone}", size="3"),
                spacing="1", align_items="start", width="100%",
            ),
            rx.divider(),
            rx.vstack(
                rx.text("Artículos Comprados:", weight="medium", size="4"),
                rx.foreach(
                    purchase.items_formatted,
                    lambda item_str: rx.text(item_str, size="3")
                ),
                spacing="1", align_items="start", width="100%",
            ),
            rx.link(
                rx.button("Imprimir Factura", variant="outline", width="100%", margin_top="1em"),
                href=f"/invoice?id={purchase.id}",
                is_external=False, # Abre en la misma app, pero en otra pestaña
                target="_blank", # Abre en una nueva pestaña
            ),
            # --- FIN DE LA ADICIÓN ---

            spacing="4", width="100%"
        ),
        width="100%", padding="1.5em",
    )


@reflex_local_auth.require_login
def purchase_history_content() -> rx.Component:
    """Página del historial de compras del usuario."""
    page_content = rx.center(
        rx.vstack(
            rx.heading("Mi Historial de Compras", size="7"),
            rx.input(
                placeholder="Buscar por ID o producto...",
                value=AppState.search_query_user_history,
                on_change=AppState.set_search_query_user_history, # Necesitarás este método en AppState
                width="100%", max_width="400px", margin_y="1.5em",
            ),
            rx.cond(
                AppState.filtered_user_purchases,
                rx.foreach(AppState.filtered_user_purchases, purchase_detail_card),
                rx.center(
                    rx.text("No se encontraron compras para tu búsqueda."),
                    padding_y="2em",
                )
            ),
            spacing="6", width="100%", max_width="960px", align="center"
        ),
        width="100%"
    )
    return account_layout(page_content)