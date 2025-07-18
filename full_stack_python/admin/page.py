# full_stack_python/admin/page.py
import reflex as rx
from ..ui.base import base_page
from .state import AdminConfirmState
from ..auth.admin_auth import require_admin

def pending_purchase_card(purchase: PurchaseModel) -> rx.Component:
    return rx.card(
        rx.vstack(
            rx.hstack(
                rx.text(f"Comprador: {purchase.userinfo.user.username} ({purchase.userinfo.email})", weight="bold"),
                rx.spacer(),
                rx.text(f"Fecha: {purchase.purchase_date.strftime('%d-%m-%Y')}")
            ),
            rx.divider(),
            rx.text("Items:"),
            rx.foreach(
                purchase.items,
                lambda item: rx.text(f"- {item.quantity}x {item.blog_post.title}")
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
    return base_page(
        rx.vstack(
            rx.heading("Confirmar Pagos Pendientes", size="8"),
            rx.cond(
                AdminConfirmState.pending_purchases,
                rx.foreach(AdminConfirmState.pending_purchases, pending_purchase_card),
                rx.text("No hay pagos pendientes de confirmación.")
            ),
            spacing="5",
            width="100%",
            max_width="1000px",
            align="center",
            padding="2em"
        )
    )