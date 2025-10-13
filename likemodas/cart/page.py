import reflex as rx
import reflex_local_auth
from typing import List, Dict

# --- ✨ ESTA ES LA CORRECCIÓN ✨ ---
from reflex.vars import Var
from reflex_magic.utils.types import cast

from likemodas.utils.formatting import format_to_cop
from ..state import AppState

def display_default_address() -> rx.Component:
    return rx.vstack(
        rx.heading("Datos de Envío", size="6", margin_top="1.5em", width="100%"),
        rx.cond(
            AppState.default_shipping_address,
            rx.box(
                rx.vstack(
                    rx.hstack(
                        rx.text(AppState.default_shipping_address.name, weight="bold"),
                        rx.spacer(),
                        rx.badge("Predeterminada", color_scheme="green"),
                        width="100%"
                    ),
                    rx.text(AppState.default_shipping_address.address, ", ", AppState.default_shipping_address.neighborhood),
                    rx.text(AppState.default_shipping_address.city),
                    rx.text("Tel: ", AppState.default_shipping_address.phone),
                    rx.link("Cambiar dirección", href="/my-account/shipping-info", size="2", color_scheme="violet", margin_top="0.5em"),
                    align_items="start", spacing="2", width="100%"
                ),
                border="1px solid #ededed", border_radius="md", padding="1em", width="100%"
            ),
            rx.box(
                rx.vstack(
                    rx.text("No tienes una dirección de envío predeterminada."),
                    rx.link(rx.button("Añadir Dirección en Mi Cuenta", color_scheme="purple"), href="/my-account/shipping-info", variant="soft"),
                    spacing="3", align_items="center"
                ),
                border="1px dashed #ededed", border_radius="md", padding="2em", width="100%", text_align="center"
            )
        ),
        rx.button(
            "Finalizar Compra",
            on_click=AppState.handle_checkout,
            width="100%", size="3", margin_top="1em",
            is_disabled=~AppState.default_shipping_address,
            color_scheme="violet"
        ),
        width="100%", spacing="4",
    )

def cart_item_row(item: Var[Dict[str, Any]]) -> rx.Component:
    """Renderiza una fila en la tabla del carrito."""
    return rx.table.row(
        rx.table.cell(
            rx.hstack(
                rx.box(
                    rx.image(
                        src=rx.get_upload_url(item["image_url"]),
                        alt=item["title"],
                        width="60px",
                        height="60px",
                        object_fit="cover",
                        border_radius="md",
                    ),
                    on_click=AppState.open_product_detail_modal(item["product_id"]),
                    cursor="pointer",
                    _hover={"transform": "scale(1.05)"},
                    transition="transform 0.2s",
                ),
                rx.vstack(
                    rx.text(item["title"], weight="bold"),
                    rx.foreach(
                        cast(item["variant_details"], List[Dict[str, str]]),
                        lambda detail: rx.text(detail["key"], ": ", detail["value"], size="2", color_scheme="gray")
                    ),
                    align_items="start",
                    spacing="1"
                ),
                spacing="4",
                align="center",
            )
        ),
        rx.table.cell(
            rx.hstack(
                rx.button("-", on_click=lambda: AppState.remove_from_cart(item["cart_key"]), size="1", color_scheme="violet", variant="soft"),
                rx.text(item["quantity"]),
                rx.button("+", on_click=lambda: AppState.increase_cart_quantity(item["cart_key"]), size="1", color_scheme="violet", variant="soft"),
                align="center", spacing="3"
            )
        ),
        rx.table.cell(rx.text(item["price_cop"])),
        rx.table.cell(rx.text(item["subtotal_cop"])),
    )

@reflex_local_auth.require_login
def cart_page_content() -> rx.Component:
    return rx.vstack(
        rx.heading("Mi Carrito", size="8", color_scheme="violet"),
        rx.cond(
            AppState.cart_items_count > 0,
            rx.vstack(
                rx.table.root(
                    rx.table.header(rx.table.row(rx.table.column_header_cell("Producto"), rx.table.column_header_cell("Cantidad"), rx.table.column_header_cell("Precio Unitario"), rx.table.column_header_cell("Subtotal"))),
                    rx.table.body(rx.foreach(AppState.cart_details_for_view, cart_item_row))
                ),
                rx.divider(),
                rx.vstack(
                    rx.hstack(
                        rx.text("Subtotal (IVA Incluido):", size="5"),
                        rx.spacer(),
                        rx.text(AppState.subtotal_cop, size="5"),
                        width="100%"
                    ),
                    rx.hstack(
                        rx.text("Envío:", size="5"),
                        rx.spacer(),
                        rx.cond(
                            AppState.cart_summary["free_shipping_achieved"],
                            rx.badge("¡Gratis por tu compra!", color_scheme="green", size="2"),
                            rx.text(AppState.shipping_cost_cop, size="5")
                        ),
                        width="100%"
                    ),
                    rx.divider(),
                    rx.hstack(
                        rx.heading("Total:", size="6"),
                        rx.spacer(),
                        rx.heading(AppState.grand_total_cop, size="6"),
                        width="100%"
                    ),

                    rx.divider(),
                    rx.vstack(
                        rx.heading("Método de Pago", size="5", width="100%"),
                        rx.radio(
                            ["Online", "Contra Entrega"],
                            value=AppState.payment_method,
                            on_change=AppState.set_payment_method,
                            spacing="4",
                            color_scheme="violet",
                        ),
                        rx.callout(
                            "Nota: En caso de devolución del pedido, se cobrará nuevamente el valor del envío para cubrir los costos logísticos del retorno.",
                            icon="info",
                            margin_top="1em",
                            width="100%",
                            color_scheme="purple",
                            variant="soft",
                        ),
                        spacing="3",
                        align_items="start",
                        width="100%",
                        padding_y="1em",
                    ),
                    spacing="3",
                    padding_y="1em",
                ),
                display_default_address(),
                spacing="5", width="100%", max_width="700px"
            ),
            rx.center(
                rx.vstack(
                    rx.text("Tu carrito está vacío."),
                    rx.link("Explorar productos", href="/", color_scheme="violet"),
                    spacing="3"
                ),
                min_height="50vh"
            )
        ),
        align="center", width="100%", padding="2em"
    )