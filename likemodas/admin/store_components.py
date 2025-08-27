# likemodas/admin/store_components.py (CORREGIDO)

import reflex as rx
from ..state import AppState, ProductCardData

def admin_product_card(post: ProductCardData) -> rx.Component:
    """
    Tarjeta de producto para la vista de admin. Ahora abre el modal de edición
    directamente desde el estado.
    """
    return rx.box(
        rx.vstack(
            rx.vstack(
                rx.box(
                    # --- 👇 LÍNEA CORREGIDA 👇 ---
                    # Se cambió 'post.image_urls' por 'post.variants'
                    rx.cond(
                        post.variants & (post.variants.length() > 0),
                        # --- 👇 LÍNEA CORREGIDA 👇 ---
                        # Se obtiene la URL del primer objeto en la lista 'variants'
                        rx.image(src=rx.get_upload_url(post.variants[0].get("image_url", "")), width="100%", height="260px", object_fit="cover"),
                        rx.box(rx.icon("image_off", size=48), width="100%", height="260px", bg=rx.color("gray", 3), display="flex", align_items="center", justify_content="center")
                    ),
                    width="260px", height="260px"
                ),
                rx.text(post.title, weight="bold", size="6"),
                rx.text(post.price_cop, size="6"),
                rx.box(height="21px"), # Espaciador para mantener la altura
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