# likemodas/purchases/page.py (VERSIÓN FINAL Y CORREGIDA)

import reflex as rx
import reflex_local_auth

from ..state import AppState, UserPurchaseHistoryCardData, PurchaseItemCardData
from ..account.layout import account_layout
from ..models import PurchaseStatus
from ..blog.public_page import product_detail_modal

def purchase_item_card(item: PurchaseItemCardData) -> rx.Component:
    """Componente para cada artículo, ahora responsivo."""
    return rx.hstack(
        rx.box(
            rx.image(
                src=rx.get_upload_url(item.image_url), alt=item.title, 
                # Se ajusta el tamaño para que sea consistente
                height="70px", width="70px", 
                object_fit="cover", border_radius="md"
            ),
            on_click=AppState.open_product_detail_modal(item.id),
            cursor="pointer", _hover={"opacity": 0.8},
        ),
        rx.vstack(
            rx.text(item.title, weight="bold", size="3"),
            rx.text(item.variant_details_str, size="2", color_scheme="gray", no_of_lines=1),
            align_items="start", spacing="1",
        ),
        rx.spacer(),
        rx.vstack(
            rx.text(f"{item.quantity}x {item.price_at_purchase_cop}", size="3"),
            rx.text(item.subtotal_cop, weight="bold", size="3", text_align="right"),
            align_items="end", spacing="1", min_width="90px",
        ),
        spacing="4", align="center", width="100%",
    )

def purchase_detail_card(purchase: UserPurchaseHistoryCardData) -> rx.Component:
    """La tarjeta de detalle de compra, ahora completamente responsiva."""
    return rx.card(
        rx.vstack(
            # Encabezado con fecha y estado
            rx.flex(
                rx.vstack(
                    rx.text(f"Compra del: {purchase.purchase_date_formatted}", weight="bold", size="5"), 
                    rx.text(f"ID: #{purchase.id}", size="2", color_scheme="gray"), 
                    align_items="start"
                ),
                rx.spacer(),
                rx.badge(purchase.status.replace("_", " ").title(), color_scheme="violet", variant="soft", size="2"),
                # Dirección del Flex cambia en móvil
                direction={"initial": "column", "sm": "row"},
                align={"initial": "start", "sm": "center"},
                justify="between", width="100%",
            ),
            rx.divider(),
            
            # Detalles de envío
            rx.vstack(
                rx.text("Detalles de Envío:", weight="medium", size="4"), 
                rx.text(f"Nombre: {purchase.shipping_name}", size="3"), 
                rx.text(f"Dirección: {purchase.shipping_address}, {purchase.shipping_neighborhood}, {purchase.shipping_city}", size="3"), 
                rx.text(f"Teléfono: {purchase.shipping_phone}", size="3"), 
                spacing="1", align_items="start", width="100%"
            ),
            rx.divider(),

            # Artículos
            rx.vstack(
                rx.text("Artículos Comprados:", weight="medium", size="4"),
                rx.text("Haz clic en un producto para ver los detalles o volver a comprar.", size="2", color_scheme="gray"),
                rx.vstack(
                    rx.foreach(AppState.purchase_items_map.get(purchase.id, []), purchase_item_card), 
                    spacing="3", width="100%"
                ),
                spacing="2", align_items="start", width="100%",
            ),

            # Totales de la compra
            rx.vstack(
                rx.hstack(rx.spacer(), rx.text("Envío:", size="4", weight="medium"), rx.text(purchase.shipping_applied_cop, size="4"), align="center", spacing="3"),
                rx.hstack(rx.spacer(), rx.heading("Total Compra:", size="5", weight="medium"), rx.heading(purchase.total_price_cop, size="6"), align="center", spacing="3"),
                align_items="end", width="100%", margin_top="1em", spacing="2"
            ),
            rx.divider(margin_y="1em"),

            # Botones de acción (ahora responsivos)
            rx.cond(
                purchase.status == PurchaseStatus.DELIVERED.value, 
                rx.flex(
                    rx.link(rx.button("Imprimir Factura", variant="outline", width="100%"), href=f"/invoice?id={purchase.id}", is_external=False, target="_blank", width="100%"), 
                    rx.button("Devolución o Cambio", on_click=AppState.go_to_return_page(purchase.id), variant="solid", color_scheme="orange", width="100%"), 
                    # Se apilan en móvil, se ponen en fila en PC
                    direction={"initial": "column", "sm": "row"},
                    spacing="3", margin_top="1em", width="100%"
                )
            ),
            # ... (otras condiciones para diferentes estados de compra)
            spacing="4", width="100%"
        ),
        width="100%", padding="1.5em",
    )

@reflex_local_auth.require_login
def purchase_history_content() -> rx.Component: # <-- NOMBRE CORREGIDO
    """Página del historial de compras del usuario."""
    page_content = rx.vstack(
        rx.heading("Mi Historial de Compras", size="8", text_align="center"),
        rx.text("Aquí puedes ver el estado y los detalles de todos tus pedidos.", color_scheme="gray", size="4", text_align="center"),
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
        align="center",
        spacing="6",
        width="100%",
        max_width="960px",
    )

    return rx.fragment(
        account_layout(page_content),
        product_detail_modal(),
    )