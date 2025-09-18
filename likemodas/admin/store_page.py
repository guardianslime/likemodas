# likemodas/admin/store_page.py

import reflex as rx

from likemodas.blog.admin_page import edit_post_dialog
from ..auth.admin_auth import require_admin
# --- 👇 1. IMPORTA LOS COMPONENTES PÚBLICOS ---
from ..ui.components import product_gallery_component
from ..blog.public_page import product_detail_modal
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
                # --- CORRECCIÓN CLAVE ---
                # Ahora pasamos la variable computada que ya tiene el formato correcto.
                # Ya no usamos rx.foreach aquí.
                searchable_select(
                    placeholder="Buscar por usuario o email...",
                    options=AppState.buyer_options_for_select,
                    on_change_select=AppState.set_direct_sale_buyer,
                    value_select="",
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
    return rx.fragment(
        rx.box(
            rx.grid(
                rx.vstack(
                    rx.heading("Tienda (Punto de Venta)", size="8"),
                    rx.text("Busca productos y añádelos al carrito de Venta Directa."),
                    rx.input(
                        placeholder="Buscar productos por nombre...",
                        value=AppState.search_term,
                        on_change=AppState.set_search_term,
                        width="100%",
                        max_width="500px",
                        margin_y="1.5em",
                        variant="surface",
                        color_scheme="violet"
                    ),
                    rx.cond(
                        AppState.displayed_posts,
                        product_gallery_component(posts=AppState.displayed_posts),
                        rx.center(rx.text("No se encontraron productos."), padding="4em")
                    ),
                    spacing="5",
                    width="100%",
                ),
                # Este box vacío ayuda a que el grid mantenga la primera columna a la izquierda
                rx.box(),
                columns="auto 0fr",
                spacing="6",
                width="100%",
            ),
            padding="2em",
            width="100%",
        ),
        product_detail_modal(),
        sliding_direct_sale_cart(),
    )

def responsive_direct_sale_cart() -> rx.Component:
    """
    CORREGIDO: Un componente de carrito que es un sidebar en desktop
    y un panel deslizable desde abajo (bottom sheet) en móviles.
    """
    SIDEBAR_WIDTH = "24em"
    SHEET_HEIGHT = "85vh"

    cart_content = rx.vstack(
        # --- El "tirador" para cerrar en móviles ---
        rx.box(
            rx.box(
                width="40px",
                height="6px",
                bg=rx.color("gray", 6),
                border_radius="full",
                on_click=AppState.toggle_direct_sale_sidebar,
                cursor="pointer",
            ),
            display={"initial": "flex", "md": "none"}, # Solo visible en móviles
            width="100%",
            justify_content="center",
            padding_top="0.5em",
            padding_bottom="1em",
        ),
        rx.heading("Venta Directa", size="6"),
        rx.divider(),
        # ... (El resto del contenido del vstack se mantiene igual que antes) ...
        rx.vstack(
            rx.text("Seleccionar Comprador (Opcional):", weight="bold"),
            searchable_select(
                placeholder="Buscar por usuario o email...",
                options=AppState.buyer_options_for_select,
                on_change_select=AppState.set_direct_sale_buyer,
                value_select="",
                search_value=AppState.search_query_all_buyers,
                on_change_search=AppState.set_search_query_all_buyers,
                filter_name="buyer_filter",
            ),
            align_items="start", width="100%"
        ),
        rx.divider(),
        rx.scroll_area(
            rx.vstack(
                rx.cond(
                    AppState.direct_sale_cart_details,
                    rx.foreach(
                        AppState.direct_sale_cart_details,
                        lambda item: rx.hstack(
                            rx.image(src=rx.get_upload_url(item.image_url), width="40px", height="40px", object_fit="cover", border_radius="sm"),
                            rx.vstack(
                                rx.text(item.title, size="2", weight="bold"),
                                rx.text(f"Cant: {item.quantity}", size="1"),
                                align_items="start", spacing="0"
                            ),
                            rx.spacer(),
                            rx.text(item.subtotal_cop, size="2"),
                            rx.icon_button(
                                rx.icon("minus", size=12),
                                on_click=AppState.remove_from_direct_sale_cart(item.cart_key),
                                size="1"
                            ),
                            width="100%", align="center"
                        )
                    ),
                    rx.center(rx.text("El carrito está vacío."), padding="2em")
                ),
                spacing="3", width="100%",
            ),
            max_height={"initial": f"calc({SHEET_HEIGHT} - 280px)", "md": "calc(100vh - 280px)"},
            type="auto", scrollbars="vertical"
        ),
        rx.spacer(),
        rx.divider(),
        rx.button(
            "Confirmar Venta Directa",
            on_click=AppState.handle_direct_sale_checkout,
            width="100%", color_scheme="violet", size="3"
        ),
        spacing="4",
        height="100%",
        padding="1em",
        align="start",
        width={"initial": "100%", "md": SIDEBAR_WIDTH} # Ancho responsivo
    )

    # --- El "mango" para abrir/cerrar en DESKTOP ---
    desktop_handle = rx.box(
        rx.icon("shopping-cart", color="white"),
        on_click=AppState.toggle_direct_sale_sidebar,
        cursor="pointer", bg=rx.color("violet", 9),
        border_radius="8px 0 0 8px", height="60px", width="40px",
        display={"initial": "none", "md": "flex"}, # Solo visible en desktop
        align_items="center", justify_content="center",
    )

    return rx.box(
        rx.hstack(
            desktop_handle,
            cart_content,
            align_items={"initial": "end", "md": "center"}, # Alinear al final en móvil
            spacing="0",
            height="100%",
            width="100%",
        ),
        # --- Lógica de Posición y Animación Responsiva ---
        position="fixed",
        top={"initial": "auto", "md": "0"},
        bottom={"initial": "0", "md": "auto"},
        left={"initial": "0", "md": "auto"},
        right="0",
        width={"initial": "100%", "md": SIDEBAR_WIDTH},
        height={"initial": "auto", "md": "100vh"},
        max_height={"initial": SHEET_HEIGHT, "md": "100vh"},
        bg=rx.color("gray", 2),
        border_radius={"initial": "1.5em 1.5em 0 0", "md": "0"},
        box_shadow="0 -4px 20px rgba(0, 0, 0, 0.2)",
        transform=rx.cond(
            AppState.show_direct_sale_sidebar,
            "translate(0, 0)", # Posición visible
            {"initial": "translateY(100%)", "md": f"translateX({SIDEBAR_WIDTH})"} # Posición oculta
        ),
        transition="transform 0.4s ease-in-out",
        z_index="1000",
    )

def mobile_cart_trigger() -> rx.Component:
    """
    Un botón flotante que solo aparece en móviles para abrir el carrito de venta.
    """
    return rx.box(
        rx.icon_button(
            rx.icon("shopping-cart", color="white"),
            on_click=AppState.toggle_direct_sale_sidebar,
            size="3",
            radius="full",
            color_scheme="violet",
            shadow="lg",
        ),
        # --- Lógica de Responsividad ---
        # "flex" en pantallas pequeñas (initial), "none" en medianas (md) y grandes
        display={"initial": "flex", "md": "none"},
        position="fixed",
        bottom="2rem",
        right="2rem",
        z_index="1001", # Un z-index alto para que esté por encima de otros elementos
    )