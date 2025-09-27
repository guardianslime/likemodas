# likemodas/blog/add.py (COMPLETO Y CORREGIDO)

import reflex as rx
from ..auth.admin_auth import require_admin
from .forms import blog_post_add_form
from .state import BlogAdminState
from ..ui.skeletons import skeleton_post_preview

def post_preview() -> rx.Component:
    """Componente de previsualización del post."""
    return rx.box(
        rx.cond(
            BlogAdminState.is_loading,
            skeleton_post_preview(),
            rx.vstack(
                rx.image(
                    src=BlogAdminState.post_form_data["main_image"],
                    width="100%",
                    height="auto",
                    object_fit="cover",
                    border_radius="md",
                ),
                # --- MODIFICACIÓN CLAVE AQUÍ ---
                # Se reemplaza el 'or' de Python por 'rx.cond' para manejar
                # el valor predeterminado de forma compatible con Reflex.
                rx.heading(
                    rx.cond(
                        BlogAdminState.post_form_data["title"],
                        BlogAdminState.post_form_data["title"],
                        "Título de la publicación"
                    ),
                    size="6"
                ),
                # --- Y AQUÍ TAMBIÉN ---
                rx.text(
                    rx.cond(
                        BlogAdminState.post_form_data["content"],
                        BlogAdminState.post_form_data["content"],
                        "Contenido de la publicación..."
                    )
                ),
                # --- FIN DE LAS MODIFICACIONES ---
                spacing="4",
                width="100%",
            )
        ),
        border="1px solid #e0e0e0",
        border_radius="lg",
        padding="1.5em",
        width="100%",
        height="100%",
    )

@require_admin
def blog_post_add_content() -> rx.Component:
    """Página para añadir una nueva publicación con layout responsivo."""
    return rx.box(
        rx.grid(
            # Columna izquierda (Formulario)
            rx.vstack(
                rx.heading("Crear Nueva Publicación", size="7", margin_bottom="1em"),
                blog_post_add_form(),
                width="100%",
                spacing="4",
            ),
            # Columna derecha (Previsualización)
            rx.vstack(
                rx.heading("Previsualización", size="7", margin_bottom="1em"),
                post_preview(),
                width="100%",
                spacing="4",
            ),
            columns=["1", "1", "2", "2", "2"],
            gap=4,
            width="100%",
        ),
        padding_x=["1em", "1em", "2em", "2em", "2em"],
        padding_y="2em",
        width="100%",
    )