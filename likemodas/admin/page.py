# likemodas/admin/page.py (CORREGIDO)

import reflex as rx
from ..auth.admin_auth import require_admin
from ..state import AppState, AdminPurchaseCardData

def purchase_card_admin(purchase: AdminPurchaseCardData, is_history: bool = False) -> rx.Component:
    """Muestra los detalles de una compra en el panel de admin."""
    return rx.card(
        rx.vstack(
            rx.hstack(
                rx.vstack(
                    rx.text(f"Compra #{purchase.id}", weight="bold", size="5"),
                    rx.text(f"Cliente: {purchase.customer_name} ({purchase.customer_email})", size="3"),
                    rx.text(f"Fecha: {purchase.purchase_date_formatted}", size="3"),
                    align_items="start",
                ),
                rx.spacer(),
                rx.vstack(
                    rx.badge(purchase.status, color_scheme="blue", variant="soft", size="2"),
                    rx.heading(purchase.total_price_cop, size="6"),
                    align_items="end",
                ), width="100%",
            ),
            rx.divider(),
            rx.vstack(
                rx.text("Detalles de Envío:", weight="medium", size="4"),
                rx.text(f"Nombre: {purchase.shipping_name}", size="3"),
                rx.text(f"Dirección: {purchase.shipping_full_address}", size="3"),
                rx.text(f"Teléfono: {purchase.shipping_phone}", size="3"),
                spacing="1", align_items="start", width="100%",
            ),
            rx.divider(),
            rx.vstack(
                rx.text("Artículos:", weight="medium", size="4"),
                rx.foreach(purchase.items_formatted, lambda item: rx.text(item, size="3")),
                spacing="1", align_items="start", width="100%",
            ),
            rx.cond(
                ~is_history,
                rx.button("Confirmar Pago", on_click=lambda: AppState.confirm_payment(purchase.id), width="100%", margin_top="1em")
            ),
            spacing="4", width="100%",
        ), width="100%",
    )

@require_admin
def admin_confirm_content() -> rx.Component:
    """Página de admin para confirmar pagos pendientes."""
    return rx.center(
        rx.vstack(
            rx.heading("Confirmar Pagos Pendientes", size="8"),
            rx.cond(
                AppState.pending_purchases,
                rx.foreach(AppState.pending_purchases, lambda p: purchase_card_admin(p, is_history=False)),
                rx.center(rx.text("No hay compras pendientes por confirmar."), padding_y="2em")
            ),
            align="center", spacing="5", padding="2em", width="100%", max_width="960px", 
        ), width="100%"
    )

@require_admin
def payment_history_content() -> rx.Component:
    """Página de admin para ver el historial de pagos."""
    return rx.center(
        rx.vstack(
            rx.heading("Historial de Pagos", size="8"),
            rx.input(
                placeholder="Buscar por ID, cliente o email...", 
                value=AppState.search_query_admin_history,
                on_change=AppState.set_search_query_admin_history, # Necesitarás este método en AppState
                width="100%", max_width="400px", margin_y="1.5em",
            ),
            rx.cond(
                AppState.filtered_admin_purchases,
                rx.foreach(AppState.filtered_admin_purchases, lambda p: purchase_card_admin(p, is_history=True)),
                rx.center(rx.text("No se encontró historial para la búsqueda."), padding_y="2em")
            ),
            align="center", spacing="6", padding="2em", width="100%", max_width="960px",
        ), width="100%"
    )