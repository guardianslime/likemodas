# likemodas/blog/public_detail.py

import reflex as rx
from .state import CommentState
from ..ui.carousel import carousel
from ..cart.state import CartState
from ..models import CommentModel
import math
# --- Nuevas importaciones directas para construir el layout ---
from ..ui.nav import public_navbar
from ..ui.base import fixed_color_mode_button

# ... (tus funciones _image_section, _info_section, _comment_card, etc., no cambian) ...

def blog_public_detail_page() -> rx.Component:
    """
    Página de detalle de producto con un layout manual para forzar la carga de estilos.
    """
    page_content = rx.center(
        rx.vstack(
            rx.heading("Detalle del Producto", size="9", margin_bottom="1em"),
            # El contenido original de la página va aquí
            rx.cond(
                CommentState.post,
                rx.grid(
                    _image_section(),
                    _info_section(),
                    columns={"base": "1", "md": "2"},
                    spacing="4",
                    align_items="start",
                    width="100%",
                    max_width="1400px",
                ),
                rx.center(rx.text("Publicación no encontrada.", color="red"))
            ),
            comment_section(),
            spacing="6",
            width="100%",
            padding="2em",
            align="center",
        ),
        width="100%",
    )

    # --- ESTRUCTURA DE LAYOUT MANUAL ---
    return rx.theme(
        rx.fragment(
            public_navbar(),
            rx.box(
                page_content,
                padding="1em", padding_top="6rem", width="100%", id="my-content-area-el"
            ),
            fixed_color_mode_button(),
        ),
        appearance="dark", has_background=True, panel_background="solid",
        scaling="90%", radius="medium", accent_color="sky"
    )