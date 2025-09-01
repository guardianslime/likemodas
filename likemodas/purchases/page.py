import reflex as rx
import reflex_local_auth

from ..state import AppState, UserPurchaseHistoryCardData, PurchaseItemCardData
from ..account.layout import account_layout
from ..models import PurchaseStatus
from ..blog.public_page import product_detail_modal

def purchase_item_thumbnail(item: PurchaseItemCardData) -> rx.Component:
    """Componente para mostrar la miniatura de un artículo comprado individual."""
    return rx.box(
        rx.vstack(
            rx.box(
                rx.image(
                    src=rx.get_upload_url(item.image_url),
                    alt=item.title,
                    width="100px",
                    height="100px",
                    object_fit="cover",
                    border_radius="md",
                ),
                on_click=AppState.open_product_detail_modal(item.id),
                cursor="pointer",
                position="relative",
                _hover={"transform": "scale(1.05)"},
                transition="transform 0.2s",
            ),
            rx.vstack(
                rx.text(
                    f"{item.quantity}x {item.price_at_purchase_cop}", 
                    size="2",
                    color_scheme="gray",
                ),
                rx.text(
                    item.subtotal_cop,
                    size="3",
                    weight="bold",
                ),
                spacing="0",
                align_items="center",
                margin_top="0.25em"
            ),
            spacing="1",
            align="center",
        ),
        width="110px",
    )

def purchase_items_gallery(items: rx.Var[list[PurchaseItemCardData]]) -> rx.Component:
    """Renderiza la galería de artículos para una compra."""
    return rx.vstack(
        rx.text("Artículos Comprados:", weight="medium", size="4"),
        rx.text("Haz clic en un producto para ver los detalles o volver a comprar.", size="2", color_scheme="gray"),
        rx.scroll_area(
            rx.hstack(
                rx.foreach(
                    items,
                    purchase_item_thumbnail
                ),
                spacing="4",
                padding_y="0.5em",
            ),
            type="auto",
            scrollbars="horizontal",
            width="100%",
        ),
        spacing="2", align_items="start", width="100%",
    )

def purchase_detail_card(purchase: UserPurchaseHistoryCardData) -> rx.Component:
    """
    SOLUCIÓN DEFINITIVA: Renderiza la tarjeta de compra y sus artículos
    usando un patrón seguro que funciona tanto en la compilación como en el navegador.
    """
    return rx.card(
        rx.vstack(
            # ... (Toda la parte superior de la tarjeta se mantiene igual: ID, Envío, etc.) ...
            rx.hstack(
                rx.vstack(
                    rx.text(f"Compra del: {purchase.purchase_date_formatted}", weight="bold", size="5"),
                    rx.text(f"ID de Compra: #{purchase.id}", size="2", color_scheme="gray"),
                    align_items="start",
                ),
                rx.spacer(),
                rx.badge(purchase.status, color_scheme="blue", variant="soft", size="2"),
                width="100%",
            ),
            rx.divider(),
            rx.vstack(
                rx.text("Detalles de Envío:", weight="medium", size="4"),
                rx.text(f"Nombre: {purchase.shipping_name}", size="3"),
                rx.text(f"Dirección: {purchase.shipping_address}, {purchase.shipping_neighborhood}, {purchase.shipping_city}", size="3"),
                rx.text(f"Teléfono: {purchase.shipping_phone}", size="3"),
                spacing="1", align_items="start", width="100%",
            ),
            rx.divider(),
            
            # --- 👇 INICIO DE LA LÓGICA CORREGIDA Y DEFINITIVA 👇 ---
            rx.vstack(
                rx.text("Artículos Comprados:", weight="medium", size="4"),
                rx.text("Haz clic en un producto para ver los detalles o volver a comprar.", size="2", color_scheme="gray"),
                
                # PATRÓN SEGURO:
                # 1. Comprueba si la ID de la compra existe como clave en el mapa.
                rx.cond(
                    AppState.purchase_items_map.contains(purchase.id),
                    # 2. Si existe, renderiza el rx.foreach usando el mapa.
                    rx.scroll_area(
                        rx.hstack(
                            rx.foreach(
                                AppState.purchase_items_map[purchase.id],
                                purchase_item_thumbnail
                            ),
                            spacing="4", padding_y="0.5em",
                        ),
                        type="auto", scrollbars="horizontal", width="100%",
                    )
                ),
                spacing="2", align_items="start", width="100%",
            ),
            # --- FIN DE LA LÓGICA CORREGIDA ---
            
            # ... (El resto de la tarjeta: Totales, Botones, etc. se mantiene igual) ...
             rx.vstack(
                rx.hstack(
                    rx.spacer(),
                    rx.text("Envío:", size="4", weight="medium"),
                    rx.text(purchase.shipping_applied_cop, size="4"),
                    align="center",
                    spacing="3",
                ),
                rx.hstack(
                    rx.spacer(),
                    rx.heading("Total Compra:", size="5", weight="medium"),
                    rx.heading(purchase.total_price_cop, size="6"),
                    align="center",
                    spacing="3",
                ),
                align_items="end",
                width="100%",
                margin_top="1em",
                spacing="2"
            ),
            rx.cond(
                purchase.status == PurchaseStatus.SHIPPED.value,
                rx.vstack(
                    rx.divider(margin_y="1em"),
                    rx.callout.root(
                        rx.callout.icon(rx.icon("truck")),
                        rx.callout.text(
                            "Tu pedido está en camino. ",
                            rx.text.strong(f"Llegada estimada: {purchase.estimated_delivery_date_formatted}"),
                        ),
                        color_scheme="green",
                        size="2",
                    ),
                    rx.button(
                        "Confirmar Recepción del Pedido",
                        on_click=AppState.user_confirm_delivery(purchase.id),
                        width="100%",
                        margin_top="0.5em"
                    ),
                    spacing="2",
                    width="100%"
                )
            ),
            rx.cond(
                purchase.status == PurchaseStatus.DELIVERED.value,
                 rx.vstack(
                    rx.divider(margin_y="1em"),
                    rx.text("¡Pedido entregado! Gracias por tu compra.", size="3", color_scheme="violet"),
                    width="100%",
                    align_items="center"
                 )
            ),
            rx.cond(
                purchase.status == PurchaseStatus.DELIVERED.value,
                rx.hstack(
                    rx.link(
                        rx.button("Imprimir Factura", variant="outline", width="100%"),
                        href=f"/invoice?id={purchase.id}",
                        is_external=False,
                        target="_blank",
                        width="100%",
                    ),
                    rx.button(
                        "Devolución o Cambio",
                        on_click=AppState.go_to_return_page(purchase.id),
                        variant="solid",
                        color_scheme="orange",
                        width="100%",
                    ),
                    spacing="3",
                    margin_top="1em",
                    width="100%",
                ),
            ),
            spacing="4", width="100%"
        ),
        width="100%", padding="1.5em",
    )

@reflex_local_auth.require_login
def purchase_history_content() -> rx.Component:
    """Página del historial de compras del usuario."""
    page_content = rx.center(
        rx.vstack(
            rx.heading("Mi Historial de Compras", size="7"),
            rx.input(
                placeholder="Buscar por ID o producto...",
                value=AppState.search_query_user_history,
                on_change=AppState.set_search_query_user_history,
                width="100%", max_width="400px", margin_y="1.5em",
            ),
            rx.cond(
                AppState.filtered_user_purchases,
                rx.foreach(AppState.filtered_user_purchases, purchase_detail_card),
                rx.center(
                    rx.text("No se encontraron compras para tu búsqueda."),
                    padding_y="2em",
                )
            ),
            product_detail_modal(),
            spacing="6", width="100%", max_width="960px", align="center"
        ),
        width="100%",
        # ✨ Se ejecuta al cargar la página para auto-confirmar entregas antiguas
        on_mount=AppState.check_for_auto_confirmations
    )
    return account_layout(page_content)