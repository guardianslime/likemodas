# likemodas/admin/store_page.py (CORREGIDO)

import reflex as rx
from ..auth.admin_auth import require_admin
from ..ui.components import product_gallery_component, searchable_select
from ..blog.public_page import product_detail_modal
from ..state import AppState, DirectSaleGroupDTO, DirectSaleVariantDTO # 👈 Asegúrate de importar los DTOs

# ✨ --- REEMPLAZA TODA ESTA FUNCIÓN --- ✨
def sliding_direct_sale_cart() -> rx.Component:
    """
    Sidebar deslizable para el carrito de venta directa, con el nuevo diseño
    de productos agrupados y controles de cantidad por variante.
    """
    SIDEBAR_WIDTH = "24em" # Un poco más ancho para la nueva información

    def render_variant_row(variant: DirectSaleVariantDTO) -> rx.Component:
        """Componente para renderizar una fila de variante con sus controles."""
        return rx.hstack(
            rx.text(variant.attributes_str, size="2", no_of_lines=1),
            rx.spacer(),
            rx.hstack(
                rx.icon_button(
                    rx.icon("minus", size=12),
                    on_click=AppState.remove_from_direct_sale_cart(variant.cart_key),
                    size="1",
                    variant="soft",
                ),
                rx.text(variant.quantity, size="2", width="20px", text_align="center"),
                rx.icon_button(
                    rx.icon("plus", size=12),
                    on_click=AppState.increase_direct_sale_cart_quantity(variant.cart_key),
                    size="1",
                    variant="soft",
                ),
                spacing="2",
                align="center"
            ),
            width="100%",
            justify="between",
            align="center",
        )

    def render_product_group(group: DirectSaleGroupDTO) -> rx.Component:
        """Componente para renderizar un grupo de producto en el carrito."""
        return rx.vstack(
            rx.hstack(
                rx.image(
                    src=rx.get_upload_url(group.image_url),
                    width="50px",
                    height="50px",
                    object_fit="cover",
                    border_radius="sm"
                ),
                rx.vstack(
                    rx.text(group.title, size="3", weight="bold", no_of_lines=1),
                    rx.text(group.subtotal_cop, size="2", color_scheme="gray"),
                    align_items="start",
                    spacing="0"
                ),
                width="100%",
                align="center",
                spacing="3",
            ),
            rx.vstack(
                rx.foreach(group.variants, render_variant_row),
                spacing="2",
                width="100%",
                padding_left="1em",
                margin_top="0.5em"
            ),
            rx.divider(margin_y="0.75em"),
            spacing="2",
            width="100%",
            align_items="start",
        )

    sidebar_panel = rx.vstack(
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
                    AppState.direct_sale_grouped_cart,
                    rx.foreach(
                        AppState.direct_sale_grouped_cart,
                        render_product_group
                    ),
                    rx.center(rx.text("El carrito está vacío."), padding="2em")
                ),
                spacing="3",
                width="100%",
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
            is_disabled=~(AppState.direct_sale_cart), # Deshabilitado si el carrito está vacío
            width="100%", color_scheme="violet", size="3"
        ),
        spacing="4", height="100%",
    )

    return rx.box(
        rx.hstack(
            rx.box(
                rx.icon("shopping-cart", color="white"),
                on_click=AppState.toggle_direct_sale_sidebar,
                cursor="pointer", bg=rx.color("violet", 9),
                border_radius="8px 0 0 8px",
                height="60px", width="40px",
                display="flex", align_items="center", justify_content="center",
            ),
            rx.card(
                sidebar_panel,
                height="85vh",
                width=SIDEBAR_WIDTH,
            ),
            align_items="center", spacing="0",
        ),
        position="fixed",
        top="50%",
        right="0",
        transform=rx.cond(
            AppState.show_direct_sale_sidebar,
            "translate(0, -50%)",
            f"translate({SIDEBAR_WIDTH}, -50%)"
        ),
        transition="transform 0.4s ease-in-out",
        z_index="1000",
    )

# La función admin_store_page() no necesita cambios, ya que llama a la función de arriba.
@require_admin
def admin_store_page() -> rx.Component:
    # ... (código existente de admin_store_page) ...
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
        # Pasa el parámetro para indicar que el modal es para venta directa
        product_detail_modal(is_for_direct_sale=True),
        sliding_direct_sale_cart(),
    )