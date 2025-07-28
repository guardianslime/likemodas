import reflex as rx
from ..auth.admin_auth import require_admin
import reflex_local_auth
from ..ui.base import base_page
from ..admin.state import AdminConfirmState, PaymentHistoryState
from ..models import PurchaseModel
from ..cart.state import CartState

# --- Componente de Tarjeta de Compra de Admin ---
def purchase_card_admin(purchase: PurchaseModel, is_history: bool = False) -> rx.Component:
    """Muestra los detalles de una compra en el panel de admin."""
    return rx.card(
        rx.vstack(
            rx.hstack(
                rx.vstack(
                    rx.text(f"Compra #{purchase.id}", weight="bold", size="5"),
                    rx.text(f"Cliente: {purchase.userinfo.user.username} ({purchase.userinfo.email})", size="3"),
                    rx.text(f"Fecha: {purchase.purchase_date_formatted}", size="3"),
                    align_items="start",
                ),
                rx.spacer(),
                rx.vstack(
                    rx.badge(purchase.status.to(str), color_scheme="blue", variant="soft", size="2"),
                    rx.heading(f"${purchase.total_price:,.2f}", size="6"),
                    align_items="end",
                ),
                width="100%",
            ),
            rx.divider(),
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
            rx.vstack(
                rx.text("Artículos:", weight="medium", size="4"),
                rx.foreach(purchase.items_formatted, lambda item: rx.text(item, size="3")),
                spacing="1",
                align_items="start",
                width="100%",
            ),
            rx.cond(
                ~is_history,
                rx.button(
                    "Confirmar Pago",
                    on_click=AdminConfirmState.confirm_payment(purchase.id),
                    width="100%",
                    margin_top="1em",
                )
            ),
            spacing="4",
            width="100%",
        ),
        width="100%",
    )

# --- Páginas de Admin (con contenido centrado) ---
@require_admin
def admin_confirm_page() -> rx.Component:
    """Página para que el admin confirme los pagos pendientes."""
    return base_page(
        rx.center(
            rx.vstack(
                rx.heading("Confirmar Pagos Pendientes", size="8"),
                rx.cond(
                    AdminConfirmState.pending_purchases,
                    rx.foreach(
                        AdminConfirmState.pending_purchases,
                        lambda p: purchase_card_admin(p, is_history=False)
                    ),
                    rx.center(rx.text("No hay compras pendientes por confirmar."), padding_y="2em")
                ),
                align="center", spacing="5", padding="2em", width="100%", max_width="960px", 
            ),
            width="100%"
        )
    )

@require_admin
def payment_history_page() -> rx.Component:
    """Página para que el admin vea el historial de pagos."""
    return base_page(
        rx.center(
            rx.vstack(
                rx.heading("Historial de Pagos", size="8"),
                rx.foreach(
                    PaymentHistoryState.purchases,
                    lambda p: purchase_card_admin(p, is_history=True)
                ),
                rx.cond(~PaymentHistoryState.purchases, rx.center(rx.text("No hay historial de compras."), padding_y="2em")),
                align="center", spacing="6", padding="2em", width="100%", max_width="960px",
            ),
            width="100%"
        )
    )

# --- ❌ ELIMINACIÓN DEL ANTIGUO FORMULARIO DE CHECKOUT ❌ ---
# La función `checkout_form` ha sido eliminada por completo.

# --- ✨ NUEVO COMPONENTE PARA MOSTRAR LA DIRECCIÓN DE ENVÍO ✨ ---
def display_default_address() -> rx.Component:
    """Muestra la dirección de envío predeterminada del usuario o un mensaje."""
    return rx.vstack(
        rx.heading("Datos de Envío", size="6", margin_top="1.5em", width="100%"),
        rx.cond(
            CartState.default_shipping_address,
            rx.box(
                rx.vstack(
                    rx.hstack(
                        rx.text(CartState.default_shipping_address.name, weight="bold"),
                        rx.spacer(),
                        rx.badge("Predeterminada", color_scheme="green"),
                        width="100%"
                    ),
                    rx.text(f"{CartState.default_shipping_address.address}, {CartState.default_shipping_address.neighborhood}"),
                    rx.text(f"{CartState.default_shipping_address.city}"),
                    rx.text(f"Tel: {CartState.default_shipping_address.phone}"),
                    rx.link("Cambiar dirección", href="/my-account/shipping-info", size="2", color_scheme="gray", margin_top="0.5em"),
                    align_items="start", spacing="2", width="100%"
                ),
                border="1px solid #ededed", border_radius="md", padding="1em", width="100%"
            ),
            rx.box(
                rx.vstack(
                    rx.text("No tienes una dirección de envío predeterminada."),
                    rx.link(rx.button("Añadir Dirección en Mi Cuenta"), href="/my-account/shipping-info", variant="soft"),
                    spacing="3", align_items="center"
                ),
                border="1px dashed #ededed", border_radius="md", padding="2em", width="100%", text_align="center"
            )
        ),
        rx.button(
            "Finalizar Compra", 
            on_click=CartState.handle_checkout, 
            width="100%", size="3", margin_top="1em", color_scheme="violet",
            is_disabled=~CartState.default_shipping_address 
        ),
        width="100%", spacing="4",
    )

# --- Componentes y Página del Carrito (Corregidos) ---
def cart_item_row(item: rx.Var) -> rx.Component:
    """Muestra una fila de producto en la tabla del carrito."""
    post, quantity = item[0], item[1]
    return rx.table.row(
        rx.table.cell(rx.text(post.title)),
        rx.table.cell(rx.hstack(rx.button("-", on_click=CartState.remove_from_cart(post.id), size="1"), rx.text(quantity), rx.button("+", on_click=CartState.add_to_cart(post.id), size="1"), align="center", spacing="3")),
        rx.table.cell(rx.text(rx.cond(post.price, f"${post.price:.2f}", "$0.00"))),
        rx.table.cell(rx.text(f"${(post.price * quantity):.2f}")),
    )

@reflex_local_auth.require_login
def cart_page() -> rx.Component:
    """Página del carrito de compras con la nueva lógica de dirección."""
    return base_page(
        rx.vstack(
            rx.heading("Mi Carrito", size="8"),
            rx.cond(
                CartState.cart_items_count > 0,
                rx.vstack(
                    rx.table.root(
                        rx.table.header(rx.table.row(rx.table.column_header_cell("Producto"), rx.table.column_header_cell("Cantidad"), rx.table.column_header_cell("Precio Unitario"), rx.table.column_header_cell("Subtotal"))),
                        rx.table.body(rx.foreach(CartState.cart_details, cart_item_row))
                    ),
                    rx.divider(),
                    rx.hstack(rx.heading("Total:", size="6"), rx.heading(f"${CartState.cart_total:.2f}", size="6"), justify="end", width="100%", padding_x="1em"),
                    # ✅ CAMBIO CLAVE: Se llama al nuevo componente en lugar del formulario
                    display_default_address(),
                    spacing="5", width="100%", max_width="700px"
                ),
                rx.center(
                    rx.vstack(rx.text("Tu carrito está vacío."), rx.link("Explorar productos", href="/blog/page"), spacing="3"),
                    min_height="50vh"
                )
            ),
            align="center", width="100%", padding="2em"
        )
    )