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

def purchase_card_admin(purchase: PurchaseModel, is_history: bool = False) -> rx.Component:
    """Un componente reutilizable para mostrar una tarjeta de compra en el panel de admin."""
    return rx.card(
        rx.vstack(
            rx.hstack(
                rx.vstack(
                     # --- CAMBIO: Texto más grande ---
                    rx.text(f"Compra #{purchase.id}", weight="bold", size="5"),
                    rx.text(f"Cliente: {purchase.userinfo.user.username} ({purchase.userinfo.email})", size="3"),
                    rx.text(f"Fecha: {purchase.purchase_date_formatted}", size="3"),
                    align_items="start",
                ),
                rx.spacer(),
                rx.vstack(
                    rx.badge(purchase.status.to(str), color_scheme="blue", variant="soft", size="2"),
                    # --- CAMBIO: Total más grande ---
                    rx.heading(f"${purchase.total_price:,.2f}", size="6"),
                    align_items="end",
                ),
                width="100%",
            ),
            rx.divider(),
            rx.vstack(
                # --- CAMBIO: Textos más grandes ---
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
                # --- CAMBIO: Textos más grandes ---
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
            spacing="4", # Espaciado aumentado
            width="100%",
        ),
        width="100%",
        padding="1.5em", # Padding añadido
    )

# ... (el resto del archivo no cambia) ...

@require_admin
def payment_history_page() -> rx.Component:
    """Página para que el admin vea el historial de pagos."""
    return base_page(
        rx.vstack(
            rx.heading("Historial de Pagos", size="8"),
            rx.cond(
                PaymentHistoryState.purchases,
                rx.foreach(
                    PaymentHistoryState.purchases,
                    lambda p: purchase_card_admin(p, is_history=True)
                ),
                rx.center(
                    rx.text("No hay historial de compras."),
                    padding_y="2em",
                )
            ),
            align="center",
            spacing="6", # Espaciado aumentado
            padding="2em",
            width="100%",
            # --- CAMBIO: Ancho máximo aumentado para centrado y mejor visualización ---
            max_width="960px",
        )
    )