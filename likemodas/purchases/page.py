# likemodas/purchases/page.py (VERSIÓN COMPLETA Y DEFINITIVA)

import reflex as rx
import reflex_local_auth

from ..state import AppState, UserPurchaseHistoryCardData, PurchaseItemCardData
from ..account.layout import account_layout
from ..models import PurchaseStatus
from ..blog.public_page import product_detail_modal

def purchase_item_card(item: PurchaseItemCardData) -> rx.Component:
    """
    [VERSIÓN FINAL Y CORREGIDA]
    Muestra un solo artículo comprado. Usa un hstack con propiedades flex
    para asegurar que la imagen siempre sea visible y que el texto
    se alinee correctamente en cualquier tamaño de pantalla.
    """
    return rx.hstack(
        # Columna 1: Imagen del producto
        rx.box(
            rx.image(
                src=rx.get_upload_url(item.image_url),
                alt=item.title,
                height="70px",
                width="70px",
                object_fit="cover",
                border_radius="md",
            ),
            # Se asegura que la imagen no se encoja
            flex_shrink=0,
            # Redirige a la página principal para abrir el modal correctamente
            on_click=rx.redirect(f"/?product_id_to_load={item.id}"),
            cursor="pointer",
            _hover={"opacity": 0.8},
        ),
        # Columna 2: Título y detalles (ocupa el espacio flexible)
        rx.vstack(
            rx.text(item.title, weight="bold", size="3"),
            rx.text(item.variant_details_str, size="2", color_scheme="gray"),
            align_items="start",
            spacing="1",
            flex_grow=1,  # Permite que este elemento ocupe el espacio del medio
        ),
        # Columna 3: Cantidad y precio
        rx.vstack(
            rx.text(f"{item.quantity}x {item.price_at_purchase_cop}", size="3"),
            align_items="end",
            spacing="1",
            flex_shrink=0,  # Evita que esta columna se encoja
        ),
        spacing="4",
        align_items="center",
        width="100%",
    )

def purchase_detail_card(purchase: UserPurchaseHistoryCardData) -> rx.Component:
    """
    [VERSIÓN FINAL Y CORREGIDA] 
    Muestra dirección y teléfono SIEMPRE. Si hay guía, muestra el rastreo abajo.
    """
    return rx.card(
        rx.vstack(
            # --- Encabezado (Igual que antes) ---
            rx.flex(
                rx.vstack(
                    rx.text(f"Compra del: {purchase.purchase_date_formatted}", weight="bold", size="5"),
                    rx.text(f"ID: #{purchase.id}", size="2", color_scheme="gray"),
                    align_items="start",
                ),
                rx.spacer(),
                rx.badge(purchase.status.replace("_", " ").title(), color_scheme="violet", variant="soft", size="2"),
                direction={"initial": "column", "sm": "row"},
                align={"initial": "start", "sm": "center"},
                justify="between",
                width="100%",
            ),
            rx.divider(),
            
            # --- Detalles de Envío (CORREGIDO) ---
            rx.vstack(
                rx.text("Detalles de Envío:", weight="medium", size="4"),
                
                # 1. INFORMACIÓN DE CONTACTO (Siempre visible)
                rx.text(f"Nombre: {purchase.shipping_name}", size="3"),
                rx.text(f"Dirección: {purchase.shipping_address}, {purchase.shipping_neighborhood}, {purchase.shipping_city}", size="3"),
                # AQUÍ ESTÁ LA LÍNEA DEL TELÉFONO QUE PEDISTE MANTENER:
                rx.text(f"Teléfono: {purchase.shipping_phone}", size="3"), 
                
                # 2. INFORMACIÓN DE GUÍA (Solo si existe, aparece abajo)
                rx.cond(
                    purchase.tracking_number,
                    rx.box(
                        rx.callout(
                            rx.vstack(
                                rx.text(f"Empresa: {purchase.shipping_carrier}", weight="bold"),
                                rx.text(f"Guía: {purchase.tracking_number}"),
                                rx.link(
                                    rx.button("Rastrear Pedido", size="2", variant="outline", color_scheme="blue", margin_top="0.5em", width="100%"),
                                    href=purchase.tracking_url,
                                    is_external=True
                                ),
                                spacing="1", width="100%"
                            ),
                            icon="truck",
                            color_scheme="blue",
                            size="2",
                            width="100%"
                        ),
                        width="100%", margin_top="0.5em"
                    )
                ),
                
                spacing="1", align_items="start", width="100%",
            ),
            rx.divider(),
            
            # --- Artículos Comprados (Igual que antes) ---
            rx.vstack(
                rx.text("Artículos Comprados:", weight="medium", size="4"),
                rx.text("Haz clic en un producto para ver los detalles o volver a comprar.", size="2", color_scheme="gray"),
                rx.vstack(
                    rx.foreach(AppState.purchase_items_map.get(purchase.id, []), purchase_item_card),
                    spacing="3", width="100%",
                ),
                spacing="2", align_items="start", width="100%",
            ),
            
            # --- Sección de Totales (Igual que antes) ---
            rx.hstack(
                rx.spacer(),
                rx.grid(
                    rx.text("Envío:", size="4", weight="medium", text_align="right"),
                    rx.text(purchase.shipping_applied_cop, size="4", text_align="right"),
                    rx.heading("Total Compra:", size="5", weight="bold", text_align="right"),
                    rx.heading(purchase.total_price_cop, size="6", text_align="right"),
                    columns="2", spacing_x="4", spacing_y="2", align_items="center",
                ),
                width="100%", margin_top="1em",
            ),
            rx.divider(margin_y="1em"),
            
            # --- Botones de Acción (Igual que antes) ---
             rx.cond(
                purchase.status == PurchaseStatus.DELIVERED.value,
                rx.flex(
                    rx.link(rx.button("Imprimir Factura", variant="outline", width="100%"), href=f"/invoice?id={purchase.id}", is_external=False, target="_blank", width="100%"),
                    rx.button("Devolución o Cambio", on_click=AppState.go_to_return_page(purchase.id), variant="solid", color_scheme="orange", width="100%"),
                    direction={"initial": "column", "sm": "row"},
                    spacing="3", margin_top="1em", width="100%",
                ),
            ),
             rx.cond(
                purchase.status == PurchaseStatus.SHIPPED.value, 
                rx.vstack(
                    rx.callout(f"Tu pedido llegará aproximadamente el: {purchase.estimated_delivery_date_formatted}", icon="truck", color_scheme="blue", width="100%"), 
                    rx.button("He Recibido mi Pedido", on_click=AppState.user_confirm_delivery(purchase.id), width="100%", margin_top="0.5em", color_scheme="green"), 
                    spacing="3", width="100%"
                )
            ),
            spacing="4", width="100%",
        ),
        width="100%",
        min_width="370px", # Diseño responsivo mantenido
        padding="1.5em",
    )

@reflex_local_auth.require_login
def purchase_history_content() -> rx.Component:
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