# likemodas/cart/page.py (VERSIÓN FINAL Y ESTRUCTURALMENTE CORRECTA)

import reflex as rx
import reflex_local_auth
from ..ui.base import base_page
from ..cart.state import CartState, ProductCardData

def checkout_form_dialog() -> rx.Component:
    """Un diálogo modal con el formulario de datos de envío."""
    return rx.dialog.root(
        rx.dialog.trigger(
            rx.button("Proceder al Pago", size="3"),
        ),
        rx.dialog.content(
            rx.dialog.title("Completa tus Datos de Envío"),
            rx.dialog.description(
                "Necesitamos esta información para poder enviar tu pedido.",
                padding_bottom="1em",
            ),
            # --- ESTRUCTURA CORREGIDA PARA EL FORMULARIO Y BOTONES ---
            rx.flex(
                rx.input(
                    placeholder="Ciudad*", on_change=CartState.set_shipping_city, 
                    value=CartState.shipping_city, type="text"
                ),
                rx.input(
                    placeholder="Barrio (Opcional)", on_change=CartState.set_shipping_neighborhood,
                    value=CartState.shipping_neighborhood, type="text"
                ),
                rx.input(
                    placeholder="Dirección de Entrega*", on_change=CartState.set_shipping_address,
                    value=CartState.shipping_address, type="text"
                ),
                rx.input(
                    placeholder="Teléfono de Contacto*", on_change=CartState.set_shipping_phone,
                    value=CartState.shipping_phone, type="tel"
                ),
                direction="column",
                spacing="3",
                padding_top="1em"
            ),
            rx.flex(
                rx.dialog.close(
                    rx.button("Cancelar", variant="soft", color_scheme="gray"),
                ),
                # El botón de confirmar ahora también está envuelto en rx.dialog.close
                rx.dialog.close(
                    rx.button("Confirmar Compra", on_click=CartState.handle_checkout),
                ),
                padding_top="1em",
                spacing="3",
                justify="end",
            ),
            style={"max_width": "450px"},
        ),
    )


def cart_item_row(item: rx.Var) -> rx.Component:
    """Fila para un item en el carrito."""
    post = item[0]
    quantity = item[1]
    return rx.table.row(
        rx.table.cell(rx.text(post.title)),
        rx.table.cell(
            rx.hstack(
                rx.button("-", on_click=CartState.remove_from_cart(post.id), size="1"),
                rx.text(quantity),
                rx.button("+", on_click=CartState.add_to_cart(post.id), size="1"),
                align="center",
                spacing="3"
            )
        ),
        rx.table.cell(rx.text(rx.cond(post.price, f"${post.price:.2f}", "$0.00"))),
        rx.table.cell(rx.text(f"${(post.price * quantity):.2f}")),
    )

@reflex_local_auth.require_login
def cart_page() -> rx.Component:
    """Página del carrito de compras."""
    return base_page(
        rx.vstack(
            rx.heading("Mi Carrito", size="8"),
            rx.cond(
                CartState.cart_items_count > 0,
                rx.vstack(
                    rx.table.root(
                        rx.table.header(
                            rx.table.row(
                                rx.table.column_header_cell("Producto"),
                                rx.table.column_header_cell("Cantidad"),
                                rx.table.column_header_cell("Precio Unitario"),
                                rx.table.column_header_cell("Subtotal"),
                            )
                        ),
                        rx.table.body(rx.foreach(CartState.cart_details, cart_item_row))
                    ),
                    rx.divider(),
                    rx.hstack(
                        rx.heading("Total:", size="6"),
                        rx.heading(f"${CartState.cart_total:.2f}", size="6"),
                        justify="end",
                        width="100%",
                        padding_x="1em"
                    ),
                    checkout_form_dialog(),
                    spacing="5",
                    width="100%",
                    max_width="900px"
                ),
                rx.center(
                    rx.vstack(
                        rx.text("Tu carrito está vacío."),
                        rx.link("Explorar productos", href="/blog/page"),
                        spacing="3"
                    ),
                    min_height="50vh"
                )
            ),
            align="center",
            width="100%",
            padding="2em"
        )
    )