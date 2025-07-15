# full_stack_python/blog/public_detail.py (VERSIÓN FINAL)

import reflex as rx
from ..ui.base import base_page
from .state import BlogViewState
from .. import navigation # Importamos navigation para los enlaces

# --- ✨ NUEVO COMPONENTE DE MENÚ ✨ ---
# Este es el nuevo menú de hamburguesa. Está aislado del resto de la página.
def fixed_public_navbar() -> rx.Component:
    """
    Un menú de hamburguesa con posicionamiento absoluto para evitar conflictos de layout.
    Este menú "flota" en la esquina superior derecha y no es afectado por otros elementos.
    """
    return rx.box(
        rx.menu.root(
            rx.menu.trigger(
                # Usamos un botón con el ícono para un mejor aspecto.
                rx.button(
                    rx.icon("menu", size=24), 
                    variant="soft", 
                    size="3"
                )
            ),
            rx.menu.content(
                # Mantenemos la misma funcionalidad de navegación que en las otras páginas.
                rx.menu.item("Home", on_click=navigation.NavState.to_home),
                rx.menu.item("Blog", on_click=navigation.NavState.to_blog),
                rx.menu.item("Productos", on_click=navigation.NavState.to_pulic_galeri),
                rx.menu.item("Pricing", on_click=navigation.NavState.to_pricing),
                rx.menu.item("Contact", on_click=navigation.NavState.to_contact),
                rx.menu.separator(),
                rx.menu.item("Login", on_click=navigation.NavState.to_login),
                rx.menu.item("Register", on_click=navigation.NavState.to_register),
            ),
        ),
        # --- LA CLAVE DE LA SOLUCIÓN ---
        # Usamos CSS puro con posicionamiento absoluto.
        style={
            "position": "absolute",
            "top": "1.5rem",      # 24px desde arriba
            "right": "1.5rem",     # 24px desde la derecha
            "z_index": "100",      # Nos aseguramos que esté por encima de otros elementos
        },
    )

# --- ✨ NUEVO LAYOUT PARA LA PÁGINA DE DETALLE ✨ ---
def blog_detail_layout(child: rx.Component) -> rx.Component:
    """
    Un layout personalizado que envuelve la página de detalle.
    Incluye el navbar flotante y el contenido principal.
    """
    return rx.box(
        fixed_public_navbar(), # 1. Añadimos el menú flotante
        rx.box(
            child,             # 2. Aquí irá el contenido (la rejilla con la imagen y el texto)
            padding_top="4rem", # Añadimos padding para que el contenido no quede debajo del menú
        ),
        position="relative",   # Es crucial para que el menú absoluto se posicione correctamente
        width="100%",
    )


def blog_public_detail_page() -> rx.Component:
    """
    Página que muestra el detalle de una publicación pública.
    Ahora utiliza el nuevo layout personalizado.
    """
    # El contenido de la página (la rejilla) no cambia.
    content_grid = rx.cond(
        BlogViewState.has_post,
        rx.grid(
            _image_section(),
            _info_section(),
            columns={"base": "1", "md": "2"},
            spacing="4",
            align_items="start",
            width="100%",
        ),
        rx.center(rx.text("Publicación no encontrada.", color="red"))
    )
    
    # Envolvemos la página con el layout base, y el contenido de la página
    # con nuestro nuevo layout de detalle.
    return base_page(
        blog_detail_layout(
            rx.box(
                content_grid,
                padding_y="2em",
                width="100%",
                max_width="1440px",
                margin="0 auto",
            )
        )
    )

# --- Componentes de la sección de imagen e información (SIN CAMBIOS) ---

def _image_section() -> rx.Component:
    """Sección que muestra la imagen principal y las flechas de navegación."""
    return rx.box(
        rx.image(
            src=rx.cond(
                BlogViewState.imagen_actual != "",
                rx.get_upload_url(BlogViewState.imagen_actual),
                "/no_image.png"
            ),
            width="100%",
            height="auto",
            max_height="550px",
            object_fit="contain",
            border_radius="md"
        ),
        rx.icon(tag="arrow_big_left", position="absolute", left="0.5em", top="50%", transform="translateY(-50%)", on_click=BlogViewState.anterior_imagen, cursor="pointer", box_size="2em"),
        rx.icon(tag="arrow_big_right", position="absolute", right="0.5em", top="50%", transform="translateY(-50%)", on_click=BlogViewState.siguiente_imagen, cursor="pointer", box_size="2em"),
        width="100%",
        max_width="600px",
        position="relative",
        border_radius="md",
        overflow="hidden"
    )

def _info_section() -> rx.Component:
    """Sección que muestra el título, precio y descripción."""
    return rx.vstack(
        rx.text(BlogViewState.post.title, size="7", font_weight="bold", margin_bottom="0.5em", text_align="left"),
        rx.text(BlogViewState.formatted_price, size="6", color="gray", text_align="left"),
        rx.text(BlogViewState.content, size="4", margin_top="1em", white_space="pre-wrap", text_align="left"),
        padding="1em",
        align="start",
        width="100%",
    )