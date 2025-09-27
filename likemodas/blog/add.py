# likemodas/blog/add.py (CORREGIDO)

import reflex as rx
from ..auth.admin_auth import require_admin
from .forms import blog_post_add_form
from ..blog.state import BlogAdminState
from ..state import AppState # Importamos AppState para la previsualización
from ..ui.skeletons import skeleton_post_preview

def post_preview() -> rx.Component:
    """
    Componente de previsualización que ahora se actualiza en tiempo real
    mostrando la primera imagen subida y los datos del formulario.
    """
    return rx.box(
        rx.vstack(
            # --- LÓGICA DE IMAGEN CORREGIDA ---
            # Muestra la primera imagen de la lista de variantes subidas.
            rx.cond(
                AppState.new_variants,
                rx.image(
                    src=rx.get_upload_url(AppState.new_variants[0].get("image_url", "")),
                    width="100%",
                    height="auto",
                    max_height="300px", # Limitamos la altura para mejor visualización
                    object_fit="cover",
                    border_radius="md",
                ),
                # Muestra un placeholder si no hay imágenes
                rx.center(
                    rx.icon("image_off", size=48, color=rx.color("gray", 8)),
                    width="100%",
                    height="300px",
                    bg=rx.color("gray", 3),
                    border_radius="md"
                )
            ),
            # El título y contenido se mantienen, ya que estaban bien conectados.
            rx.heading(
                rx.cond(
                    BlogAdminState.post_form_data["title"],
                    BlogAdminState.post_form_data["title"],
                    "Título de la publicación"
                ),
                size="6",
                margin_top="1em"
            ),
            rx.text(
                rx.cond(
                    BlogAdminState.post_form_data["content"],
                    BlogAdminState.post_form_data["content"],
                    "Contenido de la publicación..."
                ),
                no_of_lines=5 # Limitamos las líneas para que no se extienda demasiado
            ),
            spacing="4",
            width="100%",
        ),
        border="1px solid",
        border_color=rx.color("gray", 6),
        border_radius="lg",
        padding="1.5em",
        width="100%",
        height="100%",
    )

@require_admin
def blog_post_add_content() -> rx.Component:
    """Página para añadir una nueva publicación con un layout responsivo y funcional."""
    return rx.box(
        # --- LAYOUT RESPONSIVO CORREGIDO ---
        # 1 columna en móvil, 2 en pantallas grandes (lg).
        rx.grid(
            # Columna izquierda (Formulario)
            rx.vstack(
                # Este es el único título que conservamos.
                rx.heading("Crear Nueva Publicación", size="7", width="100%", text_align="left", margin_bottom="0.5em"),
                blog_post_add_form(),
                width="100%",
                spacing="4",
            ),
            # Columna derecha (Previsualización)
            rx.vstack(
                rx.heading("Previsualización", size="7", width="100%", text_align="left", margin_bottom="0.5em"),
                post_preview(),
                # Se oculta en móvil para dar prioridad al formulario
                display=["none", "none", "flex", "flex"],
                width="100%",
                spacing="4",
            ),
            columns={"initial": "1", "lg": "2"}, # Responsividad clave
            gap="2em",
            width="100%",
        ),
        padding_x=["1em", "2em", "4em"], # Padding adaptable
        padding_y="2em",
        width="100%",
    )