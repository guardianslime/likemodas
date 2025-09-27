# likemodas/blog/add.py (CORREGIDO)

import reflex as rx
from ..auth.admin_auth import require_admin
from .forms import blog_post_add_form
from ..blog.state import BlogAdminState
from ..state import AppState # Importamos AppState para la previsualización
from ..ui.skeletons import skeleton_post_preview
from ..ui.components import star_rating_display_safe # <--- AÑADE ESTE IMPORT

def post_preview() -> rx.Component:
    """
    Componente de previsualización que ahora imita la tarjeta de producto de la tienda,
    actualizándose en tiempo real con los datos del formulario.
    """
    # Función auxiliar para formatear el precio de forma segura
    def format_preview_price(price_str: str) -> str:
        try:
            price_float = float(price_str)
            return f"${price_float:,.0f}".replace(",", ".")
        except (ValueError, TypeError):
            return "$0"

    return rx.box(
        rx.vstack(
            rx.vstack(
                rx.box(
                    rx.cond(
                        AppState.new_variants,
                        rx.image(src=rx.get_upload_url(AppState.new_variants[0].get("image_url", "")), width="100%", height="260px", object_fit="cover"),
                        rx.box(rx.icon("image_off", size=48), width="100%", height="260px", bg=rx.color("gray", 3), display="flex", align_items="center", justify_content="center")
                    ),
                    rx.badge(
                        rx.cond(AppState.is_imported, "Importado", "Nacional"),
                        color_scheme=rx.cond(AppState.is_imported, "purple", "cyan"),
                        variant="solid",
                        style={"position": "absolute", "top": "0.5rem", "left": "0.5rem", "z_index": "1"}
                    ),
                    position="relative", width="260px", height="260px",
                ),
                rx.vstack(
                    rx.text(
                        rx.cond(BlogAdminState.post_form_data["title"], BlogAdminState.post_form_data["title"], "Título del Producto"),
                        weight="bold", size="6", white_space="normal", text_overflow="initial", overflow="visible", min_height="3.5em",
                    ),
                    star_rating_display_safe(0, 0, size=24), # Un producto nuevo no tiene ratings
                    rx.text(format_preview_price(BlogAdminState.post_form_data["price_str"]), size="5", weight="medium"),
                    rx.hstack(
                        rx.badge(
                            "Envío a convenir", # Placeholder para el envío
                            color_scheme="gray", variant="soft", size="2",
                        ),
                        rx.cond(
                            AppState.is_moda_completa,
                            rx.tooltip(
                                rx.badge("Moda Completa", color_scheme="violet", variant="soft", size="2"),
                                content="Este item cuenta para el envío gratis en compras sobre $200.000"
                            ),
                        ),
                        spacing="3", align="center",
                    ),
                    spacing="2", align_items="start", width="100%"
                ),
                spacing="2", width="100%",
            ),
            rx.spacer(),
        ),
        width="290px",
        height="auto",
        min_height="450px", # Asegura una altura mínima consistente
        bg=rx.color_mode_cond("#f9f9f9", "#111111"),
        border=rx.color_mode_cond("1px solid #e5e5e5", "1px solid #1a1a1a"),
        border_radius="8px", box_shadow="md", padding="1em",
    )


@require_admin
def blog_post_add_content() -> rx.Component:
    """
    Página para añadir una nueva publicación, con el layout centrado
    correctamente gracias a la corrección en el layout base.
    """
    # Volvemos a usar rx.center, que ahora funcionará como se espera.
    return rx.center(
        rx.box(
            rx.grid(
                # Columna izquierda (Formulario)
                rx.vstack(
                    rx.heading("Crear Nueva Publicación", size="7", width="100%", text_align="left", margin_bottom="0.5em"),
                    blog_post_add_form(),
                    width="100%",
                    spacing="4",
                ),
                # Columna derecha (Previsualización)
                rx.vstack(
                    rx.heading("Previsualización", size="7", width="100%", text_align="left", margin_bottom="0.5em"),
                    post_preview(),
                    display=["none", "none", "flex", "flex"],
                    width="100%",
                    spacing="4",
                    position="sticky",
                    top="2em",
                ),
                columns={"initial": "1", "lg": "2"},
                gap="2.5em",
                width="100%",
            ),
            width="100%",
            # Mantenemos el ancho generoso que te gustó
            max_width="1800px",
            padding_y="2em",
        )
    )