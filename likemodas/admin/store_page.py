# likemodas/admin/store_page.py

import reflex as rx

from likemodas.blog.admin_page import edit_post_dialog
from ..auth.admin_auth import require_admin
from ..state import AppState, CartItemData
from .store_components import admin_store_gallery_component # Reutilizamos la galería
from ..ui.components import searchable_select # Reutilizamos el selector

# --- INICIO: NUEVO COMPONENTE PARA EL CARRITO DE VENTA DIRECTA ---

def direct_sale_cart_component() -> rx.Component:
    """Componente de UI para el carrito de venta directa."""
    return rx.card(
        rx.vstack(
            rx.heading("Venta Directa", size="6"),
            rx.divider(),
            
            # Selector de Comprador
            rx.vstack(
                rx.text("Seleccionar Comprador:", weight="bold"),
                searchable_select(
                    placeholder="Buscar por usuario o email...",
                    options=rx.foreach(
                        AppState.filtered_all_users_for_sale,
                        lambda user: (user.user.username + f" ({user.email})", user.id.to_string())
                    ),
                    on_change_select=AppState.set_direct_sale_buyer,
                    value_select="", # No necesitamos mantener el valor aquí
                    search_value=AppState.search_query_all_buyers,
                    on_change_search=AppState.set_search_query_all_buyers,
                    filter_name="buyer_filter",
                ),
                align_items="start",
                width="100%"
            ),
            
            rx.divider(),
            
            # Lista de Items en el Carrito
            rx.scroll_area(
                rx.vstack(
                    rx.foreach(
                        AppState.direct_sale_cart_details,
                        lambda item: rx.hstack(
                            rx.image(src=rx.get_upload_url(item.image_url), width="40px", height="40px", object_fit="cover", border_radius="sm"),
                            rx.vstack(
                                rx.text(item.title, size="2", weight="bold"),
                                rx.text(f"Cantidad: {item.quantity}", size="1"),
                                align_items="start", spacing="0"
                            ),
                            rx.spacer(),
                            rx.text(item.subtotal_cop, size="2"),
                            rx.icon_button(
                                rx.icon("minus", size=12),
                                on_click=AppState.remove_from_direct_sale_cart(item.cart_key),
                                size="1"
                            ),
                            width="100%",
                            align="center"
                        )
                    ),
                    spacing="2",
                    width="100%"
                ),
                max_height="40vh",
                type="auto",
                scrollbars="vertical"
            ),
            
            rx.spacer(),
            rx.divider(),
            
            # Botón de Confirmación
            rx.button(
                "Confirmar Venta Directa",
                on_click=AppState.handle_direct_sale_checkout,
                is_disabled=~(AppState.direct_sale_buyer_id), # Deshabilitado si no hay comprador
                width="100%",
                color_scheme="violet",
                size="3"
            ),
            
            spacing="4",
            height="100%",
        ),
        width="100%",
        max_width="400px",
        height="85vh",
    )

# --- FIN: NUEVO COMPONENTE ---

@require_admin
def admin_store_page() -> rx.Component:
    """Página principal de la tienda para administradores con función de venta directa."""
    return rx.box(
        rx.grid(
            # Columna Izquierda: Galería y Búsqueda
            rx.vstack(
                rx.heading("Tienda (Punto de Venta)", size="8"),
                rx.text("Busca productos y añádelos al carrito de Venta Directa."),
                # Aquí puedes añadir una barra de búsqueda si lo deseas
                rx.divider(margin_y="1.5em"),
                rx.cond(
                    AppState.admin_store_posts,
                    admin_store_gallery_component(posts=AppState.admin_store_posts),
                    rx.center(rx.text("No hay productos para mostrar."), padding="4em")
                ),
                spacing="5",
                width="100%",
            ),

            # Columna Derecha: Carrito de Venta Directa
            direct_sale_cart_component(),
            
            columns="3fr 1fr", # Proporción de las columnas
            spacing="6",
            width="100%",
        ),
        
        # El modal de edición/detalle se reutiliza
        edit_post_dialog(),
        
        padding="2em",
        width="100%",
    )