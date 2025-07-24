# likemodas/blog/detail.py

import reflex as rx
from ..auth.admin_auth import require_admin
from ..ui.base import base_page
from .state import BlogPostState
from .notfound import blog_post_not_found
# --- 👇 Importa desde el nuevo archivo de componentes 👇 ---
from .detail_components import _image_section, _info_section

@require_admin
def blog_post_detail_page() -> rx.Component:
    """Página que muestra el detalle de un post del admin."""
    content_grid = rx.cond(
        BlogPostState.post,
        rx.grid(
            _image_section(),
            _info_section(),
            columns={"base": "1", "md": "2"},
            spacing="4",
            align_items="start",
            width="100%",
            max_width="1120px",
        ),
        blog_post_not_found()
    )
    return base_page(
        rx.center(
            rx.vstack(
                rx.heading("Detalle de mi Publicación", size="8", margin_bottom="1em"),
                content_grid,
                spacing="6",
                width="100%",
                padding="2em",
                align="center",
            ),
            width="100%",
        )
    )