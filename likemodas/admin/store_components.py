# likemodas/admin/store_components.py

import reflex as rx
# --- RUTA CORREGIDA PARA LA NUEVA UBICACIÓN ---
# Desde 'admin', subimos un nivel a 'likemodas' (..) y accedemos a 'state'.
from ..state import AppState, ProductCardData

def admin_product_card(post: ProductCardData) -> rx.Component:
    """
    Tarjeta de producto para la vista de admin. Enlaza a la página de edición.
    """
    return rx.box(
        rx.vstack(
            rx.link(
                rx.vstack(
                    rx.box(
                        rx.cond(
                            post.image_urls & (post.image_urls.length() > 0),
                            rx.image(src=rx.get_upload_url(post.image_urls[0]), width="100%", height="260px", object_fit="cover"),
                            rx.box(rx.icon("image_off", size=48), width="100%", height="260px", bg=rx.color("gray", 3), display="flex", align_items="center", justify_content="center")
                        ),
                        width="260px", height="260px"
                    ),
                    rx.text(post.title, weight="bold", size="6"),
                    rx.text(post.price_cop, size="6"),
                    rx.box(height="21px"),
                    spacing="2", align="start"
                ),
                href=f"/blog/{post.id}/edit"
            ),
            rx.spacer(),
            rx.button(
                "Editar / Ver Detalles",
                on_click=rx.redirect(f"/blog/{post.id}/edit"),
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
