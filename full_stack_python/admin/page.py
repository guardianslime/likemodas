# full_stack_python/admin/page.py (RECONSTRUIDO Y COMPLETO)

import reflex as rx
from ..ui.base import base_page
from .state import AdminConfirmState
from ..auth.admin_auth import require_admin
from ..models import PurchaseModel

def pending_purchase_card(purchase: PurchaseModel) -> rx.Component:
    """
    Una tarjeta visual para cada compra pendiente.
    """
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
            rx.hstack(
                rx.text(f"Total: ${purchase.total_price:.2f}", weight="bold"),
                rx.spacer(),
                rx.button(
                    "Confirmar Pago",
                    on_click=AdminConfirmState.confirm_payment(purchase.id),
                    color_scheme="green"
                )
            ),
            spacing="3",
            width="100%"
        )
    )

@require_admin
def admin_confirm_page() -> rx.Component:
    """
    Página donde los administradores pueden ver y confirmar pagos pendientes.
    """
    return base_page(
        rx.vstack(
            rx.heading("Confirmar Pagos Pendientes", size="8"),
            
            # --- ✨ CORRECCIÓN: Se usa la variable computada 'has_pending_purchases' ---
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
        # Limpia la notificación de nueva compra al visitar la página
        on_mount=AdminConfirmState.clear_notification
    )