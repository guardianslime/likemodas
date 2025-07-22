# likemodas/cart/page.py (VERSIÓN CON SINTAXIS DEFINITIVA)

import reflex as rx
import reflex_local_auth
from ..ui.base import base_page
from ..cart.state import CartState, ProductCardData
from .. import navigation


def cart_item_row(item: rx.Var) -> rx.Component:
    post = item[0]
    quantity = item[1]
    return rx.table.row(
        rx.table.cell(rx.text(post.title)),
        rx.table.cell(
            rx.hstack(
                rx.button("-", on_click=CartState.remove_from_cart(post.id), size="1"),
                rx.text(quantity),
                rx.button("+", on_click=CartState.add_to_cart(post.id), size="1"),
                align="center", spacing="3"
            )
        ),
        rx.table.cell(rx.text(rx.cond(post.price, f"${post.price:.2f}", "$0.00"))),
        rx.table.cell(rx.text(f"${(post.price * quantity):.2f}")),
    )

def _shipping_summary() -> rx.Component:
    """Componente para mostrar la dirección de envío predeterminada."""
    return rx.box(
        rx.vstack(
            rx.heading("Enviar a:", size="5"),
            rx.divider(),
            # Condición: Muestra la dirección si existe
            rx.cond(
                CartState.shipping_name != "",
                rx.vstack(
                    rx.text(CartState.shipping_name, weight="bold"),
                    rx.text(f"{CartState.shipping_address}, {CartState.shipping_neighborhood}"),
                    rx.text(f"{CartState.shipping_city}"),
                    rx.text(f"Tel: {CartState.shipping_phone}"),
                    rx.link(
                        "Cambiar dirección",
                        href=navigation.routes.SHIPPING_INFO_ROUTE,
                        size="2",
                        color_scheme="gray",
                        margin_top="0.5em"
                    ),
                    align_items="start",
                    spacing="1"
                ),
                # Mensaje si no hay dirección predeterminada
                rx.vstack(
                    rx.text("No has configurado una dirección de envío predeterminada."),
                    rx.link(
                        rx.button("Configurar Dirección", variant="soft"),
                        href=navigation.routes.SHIPPING_INFO_ROUTE
                    ),
                    align="center",
                    spacing="3",
                    padding="1em"
                )
            ),
            spacing="3",
            align_items="start",
            width="100%",
        ),
        border="1px solid #ededed",
        border_radius="md",
        padding="1.5em",
        margin_top="1.5em",
        width="100%"
    )


@reflex_local_auth.require_login
def cart_page() -> rx.Component:
    """Página del carrito de compras rediseñada."""
    return base_page(
        rx.vstack(
            rx.heading("Mi Carrito", size="8"),
            rx.cond(
                CartState.cart_items_count > 0,
                rx.vstack(
                    # La tabla del carrito no cambia
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
                        justify="end", width="100%", padding_x="1em"
                    ),
                    
                    # --- 👇 AQUÍ ESTÁ EL CAMBIO PRINCIPAL 👇 ---
                    # 1. Mostramos el resumen de la dirección
                    _shipping_summary(),
                    
                    # 2. El botón ahora finaliza la compra directamente
                    rx.button(
                        "Finalizar Compra",
                        on_click=CartState.handle_final_checkout,
                        is_disabled=(CartState.shipping_name == ""), # Deshabilitado si no hay dirección
                        width="100%",
                        size="3",
                        margin_top="1em"
                    ),
                    # --- 👆 FIN DEL CAMBIO 👆 ---
                    
                    spacing="5", width="100%", max_width="700px"
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
            align="center", width="100%", padding="2em"
        )
    )