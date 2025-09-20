# Ruta: likemodas/admin/store_components.py
import reflex as rx
from ..state import AppState, ProductCardData, DirectSaleGroupDTO, DirectSaleVariantDTO
from ..ui.components import searchable_select

def admin_product_card(post: ProductCardData) -> rx.Component:
    """
    Tarjeta de producto para la vista de admin. Ahora lee desde 'variants'.
    """
    return rx.box(
        rx.vstack(
            rx.vstack(
                rx.box(
                    rx.cond(
                        post.variants & (post.variants.length() > 0),
                        rx.image(src=rx.get_upload_url(post.variants[0].get("image_url", "")), width="100%", height="260px", object_fit="cover"),
                        rx.box(rx.icon("image_off", size=48), width="100%", height="260px", bg=rx.color("gray", 3), display="flex", align_items="center", justify_content="center")
                    ),
                    width="260px", height="260px"
                ),
                rx.text(post.title, weight="bold", size="6"),
                rx.text(post.price_cop, size="6"),
                rx.box(height="21px"),
                spacing="2", align="start"
            ),
            rx.spacer(),
            rx.button(
                "Editar / Ver Detalles",
                on_click=AppState.start_editing_post(post.id),
                width="100%",
                variant="outline"
            ),
            align="center", spacing="2", height="100%"
        ),
        width="290px", height="450px", bg=rx.color_mode_cond("#f9f9f9", "#111111"),
        border=rx.color_mode_cond("1px solid #e5e5e5", "1px solid #1a1a1a"),
        border_radius="8px", box_shadow="md", padding="1em",
    )

def admin_store_gallery_component(posts: rx.Var[list[ProductCardData]]) -> rx.Component:
    """
    Galería de productos para administradores.
    """
    return rx.flex(
        rx.foreach(
            posts,
            admin_product_card,
        ),
        wrap="wrap", spacing="6", justify="center", width="100%", max_width="1800px",
    )

def sliding_direct_sale_cart() -> rx.Component:
    """
    Sidebar deslizable para el carrito de venta directa.
    """
    SIDEBAR_WIDTH = "16em"

    def render_variant_row(variant: DirectSaleVariantDTO) -> rx.Component:
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
            is_disabled=~(AppState.direct_sale_cart),
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