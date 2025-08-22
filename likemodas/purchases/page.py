# likemodas/purchases/page.py (VERSIÓN FINAL CON SOLUCIÓN AL ERROR DE COMPILACIÓN)

import reflex as rx
import reflex_local_auth

from ..state import AppState, UserPurchaseHistoryCardData, PurchaseItemCardData
from ..account.layout import account_layout
from ..models import PurchaseStatus
from ..blog.public_page import product_detail_modal

# --- ✨ 1. CREACIÓN DE UN SUB-COMPONENTE PARA LA GALERÍA DE ARTÍCULOS ✨ ---
# Este componente encapsula el `rx.foreach` que estaba causando el error.
# Al ser un componente independiente, Reflex puede resolver los tipos de datos correctamente.

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
            rx.text(
                item.price_at_purchase_cop,
                size="2",
                weight="medium",
                text_align="center",
                margin_top="0.25em"
            ),
            spacing="1",
            align="center",
        ),
        width="110px",
    )

def purchase_items_gallery(items: rx.Var[list[PurchaseItemCardData]]) -> rx.Component:
    """El nuevo componente que renderiza la galería de artículos para una compra."""
    return rx.vstack(
        rx.text("Artículos Comprados:", weight="medium", size="4"),
        rx.text("Haz clic en un producto para ver los detalles o volver a comprar.", size="2", color_scheme="gray"),
        rx.scroll_area(
            rx.hstack(
                # Este `rx.foreach` ahora está en un contexto aislado y funciona correctamente.
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
    """Componente principal que muestra una compra. Ahora es más simple."""
    return rx.card(
        rx.vstack(
            # ... (la sección con el ID de compra y los detalles de envío no cambia) ...
            rx.hstack(
                rx.vstack(
                    rx.text(f"Compra del: {purchase.purchase_date_formatted}", weight="bold", size="5"),
                    rx.text(f"ID de Compra: #{purchase.id}", size="2", color_scheme="gray"),
                    align_items="start",
                ),
                rx.spacer(),
                rx.vstack(
                    rx.badge(purchase.status, color_scheme="blue", variant="soft", size="2"),
                    align_items="end",
                ),
                justify="between",
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
            
            # --- ✨ INICIO DE LA SOLUCIÓN DEFINITIVA: LLAMADA MODIFICADA ✨ ---
            # En lugar de pasar `purchase.items`, usamos el nuevo mapa del estado
            # para obtener los artículos de forma indirecta, lo que evita el error del compilador.
            purchase_items_gallery(items=AppState.purchase_items_map.get(purchase.id, [])),
            # --- ✨ FIN DE LA SOLUCIÓN DEFINITIVA ✨ ---
            
            rx.hstack(
                rx.spacer(),
                rx.heading("Total Compra:", size="5", weight="medium"),
                rx.heading(purchase.total_price_cop, size="6"),
                align="center",
                spacing="3",
                margin_top="1em",
            ),
            
            rx.cond(
                purchase.status != PurchaseStatus.PENDING.value,
                rx.link(
                    rx.button("Imprimir Factura", variant="outline", width="100%", margin_top="1em"),
                    href=f"/invoice?id={purchase.id}",
                    is_external=False, 
                    target="_blank",
                ),
            ),
            spacing="4", width="100%"
        ),
        width="100%", padding="1.5em",
    )


@reflex_local_auth.require_login
def purchase_history_content() -> rx.Component:
    """Página del historial de compras del usuario. (Sin cambios en esta función)"""
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
        width="100%"
    )
    return account_layout(page_content)

