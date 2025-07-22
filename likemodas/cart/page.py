import reflex as rx
from ..auth.admin_auth import require_admin
import reflex_local_auth
from ..ui.base import base_page
# --- 👇 CORRECCIÓN CLAVE AQUÍ 👇 ---
# Se importa tanto AdminConfirmState como PaymentHistoryState desde el nuevo módulo de admin.
from ..admin.state import AdminConfirmState, PaymentHistoryState
from ..models import PurchaseModel
from ..cart.state import CartState, ProductCardData

def purchase_card_admin(purchase: PurchaseModel, is_history: bool = False) -> rx.Component:
    """
    Un componente reutilizable para mostrar una tarjeta de compra en el panel de admin.
    --- DISEÑO ACTUALIZADO CON TEXTO MÁS GRANDE ---
    """
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
    )

@require_admin
def admin_confirm_page() -> rx.Component:
    """Página para que el admin confirme los pagos pendientes."""
    return base_page(
        rx.vstack(
            rx.heading("Confirmar Pagos Pendientes", size="8"),
            rx.cond(
                AdminConfirmState.pending_purchases,
                rx.foreach(
                    AdminConfirmState.pending_purchases,
                    lambda p: purchase_card_admin(p, is_history=False)
                ),
                rx.center(
                    rx.text("No hay compras pendientes por confirmar."),
                    padding_y="2em",
                )
            ),
            align="center",
            spacing="5",
            padding="2em",
            width="100%",
            max_width="960px",
        )
    )

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
            max_width="960px",
        )
    )

# ... El resto del archivo no necesita cambios ...
def checkout_form() -> rx.Component:
    """Un formulario de envío con la nueva disposición y menús desplegables."""
    return rx.form(
        rx.vstack(
            rx.heading("Datos de Envío", size="6", margin_top="1.5em", width="100%"),
            rx.grid(
                rx.vstack(
                    rx.text("Nombre Completo*"),
                    rx.input(name="shipping_name", type="text", required=True),
                    spacing="1", align_items="start",
                ),
                rx.vstack(
                    rx.text("Teléfono de Contacto*"),
                    rx.input(name="shipping_phone", type="tel", required=True),
                    spacing="1", align_items="start",
                ),
                rx.vstack(
                    rx.text("Ciudad*"),
                    rx.select(
                        CartState.cities,
                        placeholder="Selecciona una ciudad...",
                        on_change=CartState.set_shipping_city_and_reset_neighborhood,
                        value=CartState.shipping_city,
                    ),
                    spacing="1", align_items="start",
                ),
                rx.vstack(
                    rx.text("Barrio"),
                    rx.select(
                        CartState.neighborhoods,
                        placeholder="Selecciona un barrio...",
                        on_change=CartState.set_shipping_neighborhood,
                        value=CartState.shipping_neighborhood,
                        is_disabled=~rx.Var.list(CartState.neighborhoods).length() > 0,
                    ),
                    spacing="1", align_items="start",
                ),
                rx.vstack(
                    rx.text("Dirección de Entrega*"),
                    rx.input(name="shipping_address", type="text", required=True),
                    spacing="1", align_items="start",
                    grid_column="span 2",
                ),
                columns="2",
                spacing="4",
                width="100%",
            ),
            rx.button("Finalizar Compra", type="submit", width="100%", size="3", margin_top="1em"),
            spacing="4",
            width="100%",
        ),
        on_submit=CartState.handle_checkout,
    )

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
                        justify="end", width="100%", padding_x="1em"
                    ),
                    checkout_form(),
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
