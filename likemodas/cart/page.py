# likemodas/cart/page.py

import reflex as rx
import reflex_local_auth
from ..ui.base import base_page
from .state import CartState

def display_default_address() -> rx.Component:
    """Muestra la dirección de envío predeterminada o un mensaje para configurarla."""
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
            width="100%", size="3", margin_top="1em",
            is_disabled=~CartState.default_shipping_address 
        ),
        width="100%", spacing="4",
    )

def cart_item_row(item: rx.Var) -> rx.Component:
    post, quantity = item[0], item[1]
    return rx.table.row(
        rx.table.cell(rx.text(post.title)),
        rx.table.cell(rx.hstack(rx.button("-", on_click=CartState.remove_from_cart(post.id), size="1"), rx.text(quantity), rx.button("+", on_click=CartState.add_to_cart(post.id), size="1"), align="center", spacing="3")),
        rx.table.cell(rx.text(post.price_cop)), # ✅ CAMBIO AQUÍ
        rx.table.cell(rx.text(subtotal)),     # ✅ CAMBIO AQUÍ
    )

@reflex_local_auth.require_login
def cart_page() -> rx.Component:
    return base_page(
        rx.vstack(
            rx.heading("Mi Carrito", size="8", color_scheme="violet"),
            rx.cond(
                CartState.cart_items_count > 0,
                rx.vstack(
                    rx.table.root(
                        rx.table.header(rx.table.row(rx.table.column_header_cell("Producto"), rx.table.column_header_cell("Cantidad"), rx.table.column_header_cell("Precio Unitario"), rx.table.column_header_cell("Subtotal"))),
                        rx.table.body(rx.foreach(CartState.cart_details, cart_item_row))
                    ),
                    rx.divider(),
                    rx.hstack(
                        rx.heading("Total:", size="6"),
                        rx.heading(CartState.cart_total_cop, size="6"), # ✅ CAMBIO AQUÍ
                        justify="end", width="100%", padding_x="1em"
                    ),
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