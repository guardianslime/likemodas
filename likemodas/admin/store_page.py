# likemodas/admin/store_page.py (VERSIÓN FINAL, COMPLETA Y SIN DUPLICADOS)

import reflex as rx
from ..auth.admin_auth import require_admin
from ..ui.components import product_gallery_component, searchable_select
from ..blog.public_page import product_detail_modal
from ..state import AppState

def sliding_direct_sale_cart() -> rx.Component:
    """
    Sidebar deslizable para el carrito de venta directa con las dimensiones
    y posición del diseño original que te gustaba.
    """
    SIDEBAR_WIDTH = "380px"

    # El contenido interno del carrito
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
            max_height="calc(85vh - 250px)",
            type="auto",
            scrollbars="vertical"
        ),
        rx.spacer(),
        rx.divider(),
        rx.button(
            "Confirmar Venta Directa",
            on_click=AppState.handle_direct_sale_checkout,
            is_disabled=~(AppState.direct_sale_buyer_id),
            width="100%", color_scheme="violet", size="3"
        ),
        spacing="4", height="100%",
    )

    # El contenedor principal que controla la animación y el estilo
    return rx.box(
        rx.hstack(
            # El "mango" para abrir/cerrar
            rx.box(
                rx.icon("shopping-cart", color="white"),
                on_click=AppState.toggle_direct_sale_sidebar,
                cursor="pointer", bg=rx.color("violet", 9),
                border_radius="8px 0 0 8px",
                height="60px", width="40px",
                display="flex", align_items="center", justify_content="center",
            ),
            # Se envuelve el contenido en una 'card' para restaurar el estilo
            rx.card(
                sidebar_content,
                # Se define la altura fija que te gustaba
                height="85vh",
                width=SIDEBAR_WIDTH,
            ),
            align_items="center", spacing="0",
        ),
        position="fixed",
        # Se centra verticalmente en la pantalla
        top="50%",
        right="0",
        # Se usa 'transform' para centrar y para deslizar
        transform=rx.cond(
            AppState.show_direct_sale_sidebar,
            "translate(0, -50%)", # Centrado y visible
            f"translate({SIDEBAR_WIDTH}, -50%)" # Centrado y oculto a la derecha
        ),
        transition="transform 0.4s ease-in-out",
        z_index="1000",
    )

@require_admin
def admin_store_page() -> rx.Component:
    """Página de la tienda de admin con el carrito deslizable correcto."""
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
            main_content,
            padding="2em",
        ),
        product_detail_modal(),
        sliding_direct_sale_cart(),
    )