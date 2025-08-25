# likemodas/admin/page.py (VERSIÓN CORREGIDA)

import reflex as rx

from likemodas.models import PurchaseStatus
from ..auth.admin_auth import require_admin
from ..state import AppState, AdminPurchaseCardData

def purchase_card_admin(purchase: AdminPurchaseCardData) -> rx.Component:
    """Muestra los detalles de una compra y las acciones correspondientes a su estado."""
    return rx.card(
        rx.vstack(
            # --- La sección superior con los detalles del cliente, envío y artículos no cambia ---
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
                rx.text("Artículos:", weight="medium", size="4"),
                rx.foreach(purchase.items_formatted, lambda item: rx.text(item, size="3")),
                spacing="1", align_items="start", width="100%", margin_bottom="1em"
            ),
            
            # --- ✨ INICIO DE LA NUEVA LÓGICA DE ACCIONES CONDICIONALES ✨ ---
            rx.cond(
                purchase.status == PurchaseStatus.PENDING.value,
                # Si está pendiente, solo se puede confirmar el pago
                rx.button(
                    "Confirmar Pago",
                    on_click=AppState.admin_confirm_payment(purchase.id),
                    width="100%",
                )
            ),
            rx.cond(
                purchase.status == PurchaseStatus.CONFIRMED.value,
                # Si está confirmado, se puede establecer el tiempo y notificar
                rx.vstack(
                    rx.divider(),
                    rx.text("Establecer tiempo de entrega:", size="3", weight="medium"),
                    rx.hstack(
                        rx.input(placeholder="Días", type="number", on_change=lambda val: AppState.set_admin_delivery_time(purchase.id, "days", val)),
                        rx.input(placeholder="Horas", type="number", on_change=lambda val: AppState.set_admin_delivery_time(purchase.id, "hours", val)),
                        rx.input(placeholder="Minutos", type="number", on_change=lambda val: AppState.set_admin_delivery_time(purchase.id, "minutes", val)),
                        spacing="3", width="100%",
                    ),
                    rx.button("Notificar Envío", on_click=AppState.notify_shipment(purchase.id), width="100%", margin_top="0.5em"),
                    width="100%", spacing="2", margin_top="1em"
                )
            ),
            rx.cond(
                purchase.status == PurchaseStatus.SHIPPED.value,
                # Si ya fue enviado, se muestra un mensaje
                rx.callout(
                    "Envío notificado al cliente. Esperando confirmación de entrega.",
                    icon="check_circle",
                    color_scheme="green",
                    width="100%",
                    margin_top="1em",
                )
            ),
            # --- ✨ FIN DE LA LÓGICA DE ACCIONES CONDICIONALES ✨ ---

            spacing="4", width="100%",
        ), width="100%",
    )


def purchase_card_history(purchase: AdminPurchaseCardData) -> rx.Component:
    """
    Muestra los detalles de una compra YA CONFIRMADA en el historial.
    """
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
            rx.link(
                rx.button("Imprimir Factura", variant="soft", color_scheme="gray", width="100%", margin_top="1em"),
                href=f"/invoice?id={purchase.id}",
                target="_blank",
            ),
            spacing="4", width="100%",
        ), width="100%",
    )

@require_admin
def admin_confirm_content() -> rx.Component:
    """Página de admin para gestionar órdenes activas."""
    return rx.center(
        rx.vstack(
            rx.heading("Gestionar Órdenes Activas", size="8"),
            rx.cond(
                # Usa la nueva lista de compras activas
                AppState.active_purchases,
                rx.foreach(AppState.active_purchases, purchase_card_admin),
                rx.center(rx.text("No hay compras activas para gestionar."), padding_y="2em")
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
                on_change=AppState.set_search_query_admin_history,
                width="100%", max_width="400px", margin_y="1.5em",
            ),
            rx.cond(
                AppState.filtered_admin_purchases,
                rx.foreach(AppState.filtered_admin_purchases, purchase_card_history),
                rx.center(rx.text("No se encontró historial para la búsqueda."), padding_y="2em")
            ),
            align="center", spacing="6", padding="2em", width="100%", max_width="960px",
        ), width="100%"
    )