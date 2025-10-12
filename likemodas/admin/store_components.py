# En: likemodas/admin/store_components.py

import reflex as rx
from ..state import AppState, ProductCardData
# ✨ Se importa el componente de estrellas que faltaba ✨
from ..ui.components import star_rating_display_safe

def admin_product_card(post: ProductCardData) -> rx.Component:
    """
    Tarjeta de producto para la vista de admin, ahora con diseño y datos consistentes.
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
                    # ... (badge de importado se mantiene) ...
                ),
                rx.vstack(
                    rx.text(post.title, weight="bold", size="6"),
                    star_rating_display_safe(post.average_rating, post.rating_count, size=24),
                    rx.text(post.price_cop, size="5", weight="medium"),
                    
                    # --- ✨ INICIO: SE APLICA EL MISMO DISEÑO CORREGIDO AQUÍ ✨ ---
                    rx.vstack(
                        rx.hstack(
                            rx.badge(
                                post.shipping_display_text,
                                color_scheme="gray", variant="soft", size="2"
                            ),
                            rx.cond(
                                post.is_moda_completa_eligible,
                                rx.tooltip(
                                    rx.badge("Moda Completa", color_scheme="violet", variant="soft", size="2"),
                                    content=post.moda_completa_tooltip_text,
                                ),
                            ),
                            spacing="3", align="center",
                        ),
                        rx.cond(
                            post.combines_shipping,
                            rx.tooltip(
                                rx.badge("Envío Combinado", color_scheme="teal", variant="soft", size="2"),
                                content=post.envio_combinado_tooltip_text,
                            ),
                        ),
                        spacing="1",
                        align_items="start",
                        width="100%",
                    ),
                    # --- ✨ FIN DEL DISEÑO CORREGIDO ✨ ---

                    spacing="1", align_items="start", width="100%"
                ),
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