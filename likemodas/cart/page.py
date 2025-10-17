# likemodas/cart/page.py (CORREGIDO)

import reflex as rx
import reflex_local_auth

from likemodas.utils.formatting import format_to_cop
from ..state import AppState, CartItemData

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
                    rx.text(f"{AppState.default_shipping_address.address}, {AppState.default_shipping_address.neighborhood}"),
                    rx.text(f"{AppState.default_shipping_address.city}"),
                    rx.text(f"Tel: {AppState.default_shipping_address.phone}"),
                    # --- ✨ MODIFICACIÓN: Enlace a "Cambiar dirección" en tonos morados ✨ ---
                    rx.link("Cambiar dirección", href="/my-account/shipping-info", size="2", color_scheme="violet", margin_top="0.5em"),
                    align_items="start", spacing="2", width="100%"
                ),
                border="1px solid #ededed", border_radius="md", padding="1em", width="100%"
            ),
            rx.box(
                rx.vstack(
                    rx.text("No tienes una dirección de envío predeterminada."),
                    # --- ✨ MODIFICACIÓN: Botón "Añadir Dirección" en tonos morados ✨ ---
                    rx.link(rx.button("Añadir Dirección en Mi Cuenta", color_scheme="purple"), href="/my-account/shipping-info", variant="soft"),
                    spacing="3", align_items="center"
                ),
                border="1px dashed #ededed", border_radius="md", padding="2em", width="100%", text_align="center"
            )
        ),
        # El botón de "Finalizar Compra" ya usa el color de acento por defecto (violet).
        rx.button(
            "Finalizar Compra", 
            on_click=AppState.handle_checkout, 
            width="100%", size="3", margin_top="1em",
            is_disabled=~AppState.default_shipping_address,
            
            # ✨ AÑADE ESTA LÍNEA ✨
            color_scheme="violet" 
        ),
        width="100%", spacing="4",
    )

# --- ✨ INICIO: AÑADE ESTA NUEVA FUNCIÓN ✨ ---
def ineligible_product_item(item: CartItemData) -> rx.Component:
    """Muestra un producto no elegible para Contra Entrega."""
    return rx.hstack(
        rx.image(
            src=rx.get_upload_url(item.image_url),
            width="40px",
            height="40px",
            object_fit="cover",
            border_radius="sm",
        ),
        rx.text(item.title, size="2"),
        align="center",
        spacing="3",
        width="100%",
    )
# --- ✨ FIN ✨ ---

def cart_item_row(item: CartItemData) -> rx.Component:
    """Renderiza una fila en la tabla del carrito.
    ✨ CORREGIDO: Ahora incluye una miniatura clickeable del producto.
    """
    return rx.table.row(
        rx.table.cell(
            # Usamos un hstack para alinear la imagen y el texto horizontalmente
            rx.hstack(
                # Lógica de la miniatura (similar a la del historial de compras)
                rx.box(
                    rx.image(
                        src=rx.get_upload_url(item.image_url),
                        alt=item.title,
                        width="60px",
                        height="60px",
                        object_fit="cover",
                        border_radius="md",
                    ),
                    # Al hacer clic, se abre el modal del producto
                    on_click=AppState.open_product_detail_modal(item.product_id),
                    cursor="pointer",
                    _hover={"transform": "scale(1.05)"},
                    transition="transform 0.2s",
                ),
                # Mantenemos la información de texto original
                rx.vstack(
                    rx.text(item.title, weight="bold"),
                    rx.foreach(
                        item.variant_details.items(),
                        lambda detail: rx.text(f"{detail[0]}: {detail[1]}", size="2", color_scheme="gray")
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
                # ✨ LÍNEAS CORREGIDAS ✨
                rx.button("-", on_click=lambda: AppState.remove_from_cart(item.cart_key), size="1", color_scheme="violet", variant="soft"),
                rx.text(item.quantity),
                rx.button("+", on_click=lambda: AppState.increase_cart_quantity(item.cart_key), size="1", color_scheme="violet", variant="soft"),
                align="center", spacing="3"
            )
        ),
        rx.table.cell(rx.text(item.price_cop)),
        rx.table.cell(rx.text(item.subtotal_cop)),
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
                    rx.table.body(rx.foreach(AppState.cart_details, cart_item_row))
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
                        # Los botones de radio se mantienen con su estilo por defecto,
                        # que se integra bien con el tema general.
                        rx.radio(
                            ["Online", "Contra Entrega", ], # Añade "Sistecredito"
                            value=AppState.payment_method,
                            on_change=AppState.set_payment_method,
                            spacing="4",
                            color_scheme="violet",
                        ),

                        # --- ✨ INICIO: CÓDIGO A AÑADIR PARA EL AVISO ✨ ---
                        rx.cond(
                            (AppState.payment_method == "Contra Entrega") & ~AppState.is_cod_available,
                            rx.callout.root(
                                rx.callout.icon(rx.icon("triangle-alert")),
                                rx.callout.text(
                                    "El servicio contra entrega solo está disponible si todos los productos son de tu misma ciudad."
                                ),
                                color_scheme="orange",
                                variant="soft",
                                margin_top="1em",
                            )
                        ),
                        # --- ✨ FIN ✨ ---

                        # --- ✨ INICIO: CÓDIGO A AÑADIR PARA LA LISTA DE ERRORES ✨ ---
                        rx.cond(
                            AppState.cod_ineligible_products,
                            rx.callout.root(
                                rx.callout.icon(rx.icon("circle-x")),
                                rx.vstack(
                                    rx.text("Los siguientes productos no se pueden enviar contra entrega a tu ciudad:", weight="bold"),
                                    rx.vstack(
                                        rx.foreach(
                                            AppState.cod_ineligible_products,
                                            ineligible_product_item,
                                        ),
                                        spacing="2",
                                        padding_top="0.5em",
                                        width="100%",
                                    ),
                                    spacing="2",
                                    align_items="start",
                                ),
                                color_scheme="red",
                                variant="soft",
                                margin_top="1em",
                            ),
                        ),
                        # --- ✨ FIN ✨ ---

                        # --- ✨ MODIFICACIÓN: Callout de información en tonos morados ✨ ---
                        rx.callout(
                            "Nota: En caso de devolución del pedido, se cobrará nuevamente el valor del envío para cubrir los costos logísticos del retorno.",
                            icon="info",
                            margin_top="1em",
                            width="100%",
                            color_scheme="purple", # Color principal del callout
                            variant="soft",
                        ),
                        # --- ✨ FIN DE LA MODIFICACIÓN ✨ ---
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
                    # --- ✨ MODIFICACIÓN: Enlace a "Explorar productos" en tonos morados ✨ ---
                    rx.link("Explorar productos", href="/", color_scheme="violet"),
                    spacing="3"
                ),
                min_height="50vh"
            )
        ),
        align="center", width="100%", padding="2em"
    )