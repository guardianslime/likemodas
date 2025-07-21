import reflex as rx
from ..ui.base import base_page
from .state import AdminConfirmState, PaymentHistoryState
from ..auth.admin_auth import require_admin
from ..models import PurchaseModel

def pending_purchase_card(purchase: PurchaseModel) -> rx.Component:
    return rx.card(
        rx.vstack(
            rx.hstack(
                rx.text(f"Comprador: {purchase.userinfo.user.username} ({purchase.userinfo.email})", weight="bold"),
                rx.spacer(),
                rx.text(f"Fecha: {purchase.purchase_date_formatted}")
            ),
            rx.divider(),
            rx.text("Items:"),
            rx.foreach(
                purchase.items_formatted,
                lambda item_str: rx.text(item_str)
            ),
            rx.divider(),
            rx.vstack(
                rx.text("Datos de Envío:", weight="medium"),
                rx.box(
                    # --- LÍNEA AÑADIDA PARA MOSTRAR EL NOMBRE ---
                    rx.text(f"Nombre: {purchase.shipping_name}"),
                    rx.text(f"Ciudad: {purchase.shipping_city}"),
                    rx.text(f"Dirección: {purchase.shipping_address}"),
                    rx.text("Barrio: ", rx.cond(purchase.shipping_neighborhood, purchase.shipping_neighborhood, "No especificado")),
                    rx.text(f"Teléfono: {purchase.shipping_phone}"),
                    padding_left="1em", font_size="0.9em", color=rx.color("gray", 11),
                ),
                spacing="1", align_items="start", width="100%"
            ),
            rx.divider(),
            rx.hstack(
                rx.text(f"Total: ${purchase.total_price:.2f}", weight="bold"),
                rx.spacer(),
                rx.button(
                    "Confirmar Pago",
                    on_click=lambda: AdminConfirmState.confirm_payment(purchase.id),
                    color_scheme="green"
                )
            ),
            spacing="3",
            width="100%"
        )
    )


@require_admin
def admin_confirm_page() -> rx.Component:
    return base_page(
        rx.vstack(
            rx.heading("Confirmar Pagos Pendientes", size="8"),
            rx.cond(
                AdminConfirmState.has_pending_purchases,
                rx.foreach(
                    AdminConfirmState.pending_purchases,
                    pending_purchase_card
                ),
                rx.center(
                    rx.text("🎉 ¡Excelente! No hay pagos pendientes de confirmación."),
                    padding="2em",
                    bg=rx.color("green", 2),
                    border_radius="md",
                    width="100%"
                )
            ),
            spacing="5",
            width="100%",
            max_width="1000px",
            align="center",
            padding="2em"
        ),
        on_mount=AdminConfirmState.clear_notification
    )

def confirmed_purchase_card(purchase: PurchaseModel) -> rx.Component:
    return rx.card(
        rx.vstack(
            rx.hstack(
                rx.text(f"Comprador: {purchase.userinfo.user.username} ({purchase.userinfo.email})", weight="bold"),
                rx.spacer(),
                rx.text(f"Confirmado: {purchase.confirmed_at_formatted}")
            ),
            rx.divider(),
            rx.text("Items:"),
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

@require_admin
def payment_history_page() -> rx.Component:
    return base_page(
        rx.vstack(
            rx.heading("Historial de Pagos Confirmados", size="8"),
            rx.cond(
                PaymentHistoryState.has_confirmed_purchases,
                rx.foreach(
                    PaymentHistoryState.confirmed_purchases,
                    confirmed_purchase_card
                ),
                rx.center(
                    rx.text("📜 Aún no hay pagos confirmados en el historial."),
                    padding="2em",
                    bg=rx.color("gray", 2),
                    border_radius="md",
                    width="100%"
                )
            ),
            spacing="5",
            width="100%",
            max_width="1000px",
            align="center",
            padding="2em"
        )
    )