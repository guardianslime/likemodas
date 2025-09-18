# likemodas/admin/store_page.py

import reflex as rx

from likemodas.blog.admin_page import edit_post_dialog
from ..auth.admin_auth import require_admin
from ..ui.components import product_gallery_component
from ..blog.public_page import product_detail_modal
from ..state import AppState, CartItemData
from .store_components import admin_store_gallery_component # Manten esta línea
from ..ui.components import searchable_select

# --- INICIO: NUEVO COMPONENTE PARA EL CARRITO DE VENTA DIRECTA ---

# ✨ INICIO: NUEVO COMPONENTE PARA EL CARRITO DESLIZABLE
def sliding_direct_sale_cart() -> rx.Component:
    """El sidebar deslizable para el carrito de venta directa."""
    # Ancho del sidebar, puedes ajustarlo si lo deseas
    SIDEBAR_WIDTH = "360px"

    # El contenido del sidebar (el mismo que ya tenías)
    sidebar_content = rx.vstack(
        rx.heading("Venta Directa", size="6"),
        rx.divider(),
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
            max_height="calc(100vh - 280px)", type="auto", scrollbars="vertical"
        ),
        rx.spacer(),
        rx.divider(),
        rx.button(
            "Confirmar Venta Directa",
            on_click=AppState.handle_direct_sale_checkout,
            is_disabled=~(AppState.direct_sale_buyer_id),
            width="100%", color_scheme="violet", size="3"
        ),
        spacing="4", height="100%", padding="1em",
        bg=rx.color("gray", 2), align="start", width=SIDEBAR_WIDTH,
    )

    # El contenedor principal que controla la animación de deslizamiento
    return rx.box(
        rx.hstack(
            # El "botón" o "mango" para abrir/cerrar el sidebar
            rx.box(
                rx.icon("shopping-cart", color="white"),
                on_click=AppState.toggle_direct_sale_sidebar,
                cursor="pointer", bg=rx.color("violet", 9),
                border_radius="8px 0 0 8px", # Bordes redondeados a la izquierda
                height="60px", width="40px",
                display="flex", align_items="center", justify_content="center",
            ),
            sidebar_content,
            align_items="center", spacing="0",
        ),
        position="fixed", top="0", right="0", height="100vh",
        display="flex", align_items="center",
        # La lógica de la animación: se mueve fuera de la pantalla hacia la derecha
        transform=rx.cond(
            AppState.show_direct_sale_sidebar,
            "translateX(0)",
            f"translateX({SIDEBAR_WIDTH})" # Se esconde hacia la derecha
        ),
        transition="transform 0.4s ease-in-out",
        z_index="1000",
    )
# ✨ FIN: NUEVO COMPONENTE PARA EL CARRITO DESLIZABLE

@require_admin
def admin_store_page() -> rx.Component:
    """Página de la tienda de admin con carrito deslizable."""
    
    main_content = rx.vstack(
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
            align="center",
            width="100%",
            spacing="4",
        ),
        rx.cond(
            AppState.filtered_admin_store_posts,
            product_gallery_component(posts=AppState.filtered_admin_store_posts),
            rx.center(
                rx.text("No se encontraron productos."), 
                padding="4em", 
                width="100%"
            )
        ),
        width="100%",
        spacing="5"
    )

    return rx.fragment(
        rx.box(
            # ✨ CORRECCIÓN: Se elimina el grid y se deja solo el contenido principal
            main_content,
            padding="2em",
        ),
        # ✨ CORRECCIÓN: Se añaden los componentes flotantes aquí
        product_detail_modal(),
        sliding_direct_sale_cart(),
    )

def sliding_direct_sale_cart() -> rx.Component:
    """El sidebar deslizable para el carrito de venta directa."""
    SIDEBAR_WIDTH = "24em" # Ancho del sidebar

    # El contenido del sidebar (lo que antes era direct_sale_cart_component)
    sidebar_content = rx.vstack(
        rx.heading("Venta Directa", size="6"),
        rx.divider(),
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
            max_height="calc(100vh - 280px)", type="auto", scrollbars="vertical"
        ),
        rx.spacer(),
        rx.divider(),
        rx.button(
            "Confirmar Venta Directa",
            on_click=AppState.handle_direct_sale_checkout,
            width="100%", color_scheme="violet", size="3"
        ),
        spacing="4", height="100%",  padding="1em",
        bg=rx.color("gray", 2), align="start", width=SIDEBAR_WIDTH,
    )

    # El contenedor principal que controla la animación de deslizamiento
    return rx.box(
        rx.hstack(
            # El "mango" para abrir/cerrar el sidebar
            rx.box(
                rx.icon("shopping-cart", color="white"),
                on_click=AppState.toggle_direct_sale_sidebar,
                cursor="pointer", bg=rx.color("violet", 9),
                border_radius="8px 0 0 8px", height="60px", width="40px",
                display="flex", align_items="center", justify_content="center",
            ),
            sidebar_content,
            align_items="center", spacing="0",
        ),
        position="fixed", top="0", right="0", height="100vh",
        display="flex", align_items="center",
        transform=rx.cond(
            AppState.show_direct_sale_sidebar,
            "translateX(0)",
            f"translateX({SIDEBAR_WIDTH})" # Se esconde hacia la derecha
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