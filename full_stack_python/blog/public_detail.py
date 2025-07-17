# full_stack_python/blog/public_detail.py (CÓDIGO CORREGIDO Y COMPLETO)

import reflex as rx
import reflex_local_auth
from..navigation.state import NavState
from .state import BlogViewState
from .. import navigation
from ..navigation.device import NavDeviceState
from ..navigation.state import force_reload_go_to
from ..ui.base import fixed_color_mode_button
from ..ui.search_state import SearchState
from ..ui.nav import public_navbar # Importamos la public_navbar unificada

# Esta es la barra de navegación local, con el estilo correcto y la recarga forzada.
# ELIMINAMOS _detail_page_navbar() ya que usaremos public_navbar()
def _detail_page_navbar() -> rx.Component:
    """
    Una barra de navegación local que ahora es visual y funcionalmente idéntica
    a la `public_navbar` global, utilizando navegación SPA.
    """
    return rx.box(
        rx.hstack(
            # Lado Izquierdo: Menú y Logo (sin cambios estructurales)
            rx.hstack(
                rx.menu.root(
                    rx.menu.trigger(
                        rx.button(rx.icon("menu", size=24), variant="soft", size="3")
                    ),
                    rx.menu.content(
                        # --- CAMBIO 1: Lógica de Navegación Unificada ---
                        # Se reemplaza `force_reload_go_to` por los métodos de `NavState`
                        # para lograr una navegación SPA fluida y consistente.
                        rx.menu.item("Home", on_click=NavState.to_home),
                        rx.menu.item("Productos", on_click=NavState.to_pulic_galeri),
                        rx.menu.item("Pricing", on_click=NavState.to_pricing),
                        rx.menu.item("Contact", on_click=NavState.to_contact),
                        rx.menu.separator(),
                        rx.menu.item("Login", on_click=NavState.to_login),
                        rx.menu.item("Register", on_click=NavState.to_register),
                    ),
                ),
                rx.image(src="/logo.jpg", width="8em", height="auto", border_radius="md"),
                align="center",
                spacing="4",
            ),
            
            # Campo de búsqueda con estilos corregidos
            rx.input(
                placeholder="Buscar productos...",
                value=SearchState.search_term,
                on_change=SearchState.update_search,
                on_blur=SearchState.search_action,
                width=["60%", "65%", "70%", "72%"],
                height=["2.5em", "2.8em", "3em", "3.3em"],
                padding_x="4",
                border_radius="full",
                # --- CAMBIO 2: Corrección del Borde ---
                # Se añade `border_width` para resolver el fallo visual de "reducción de grosor".
                border_width="1px",
                # --- CAMBIO 3: Alineación del Tamaño de Fuente ---
                # Se añade `font_size` responsivo para una paridad visual completa.
                font_size=rx.breakpoints(sm="2", md="3", lg="3"),
            ),
            justify="between",
            align="center",
            width="100%",
        ),
        # Estilos del contenedor principal, ahora idénticos a `public_navbar`
        position="fixed",
        top="0",
        left="0",
        right="0",
        width="100%",
        padding="0.75rem 1rem",
        z_index="99",
        # --- CAMBIO 4: Estandarización del Fondo ---
        # Se utilizan los mismos valores de `public_navbar` para una apariencia perfecta.
        bg=rx.color_mode_cond("#ffffffF0", "#1D2330F0"),
        style={"backdrop_filter": "blur(10px)"},
        on_mount=NavDeviceState.on_mount,
    )

def standalone_public_layout(child: rx.Component) -> rx.Component:
    """Layout autónomo que usa la navbar local."""
    return rx.fragment(
        public_navbar(), # <--- CAMBIO: Ahora usa la public_navbar unificada
        rx.box(
            child,
            padding_y="2em",
            padding_top="6rem", # Asegura el padding correcto para la navbar fija
            width="100%",
            margin="0 auto",
        ),
        fixed_color_mode_button(),
    )

# --- PÁGINA DE DETALLE MODIFICADA ---
def blog_public_detail_page() -> rx.Component:
    """Página que muestra el detalle de una publicación pública."""
    
    # Este es el contenido principal de la página (la imagen y la información).
    content_grid = rx.cond(
        BlogViewState.has_post,
        rx.grid(
            _image_section(),
            _info_section(),
            columns={"base": "1", "md": "2"},
            spacing="4",
            align_items="start",
            width="100%",
            max_width="1120px", # Se añade un ancho máximo
        ),
        rx.center(rx.text("Publicación no encontrada.", color="red"))
    )
    
    # ✨ CAMBIO: Se envuelve el contenido en una estructura centrada con título.
    # Esto imita el layout de la página de la galería.
    page_content = rx.center(
        rx.vstack(
            rx.heading("Detalle del Producto", size="8", margin_bottom="1em"),
            content_grid,
            spacing="6",
            width="100%",
            padding="2em",
            align="center",
        ),
        width="100%",
    )
    
    return standalone_public_layout(page_content)


# --- Componentes de la sección de imagen e información (SIN CAMBIOS) ---
def _image_section() -> rx.Component:
    return rx.html(
        "div",
        rx.box(
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
                border_radius="md",
                transition="transform 0.3s ease-in-out",
            ),
            rx.icon(
                tag="arrow_big_left",
                position="absolute",
                left="0.5em",
                top="50%",
                transform="translateY(-50%)",
                on_click=BlogViewState.anterior_imagen,
                cursor="pointer",
                box_size="2em",
                z_index=2,
                color="white",
                bg="rgba(0,0,0,0.3)",
                border_radius="full",
                padding="0.2em"
            ),
            rx.icon(
                tag="arrow_big_right",
                position="absolute",
                right="0.5em",
                top="50%",
                transform="translateY(-50%)",
                on_click=BlogViewState.siguiente_imagen,
                cursor="pointer",
                box_size="2em",
                z_index=2,
                color="white",
                bg="rgba(0,0,0,0.3)",
                border_radius="full",
                padding="0.2em"
            ),
            width="100%",
            max_width="600px",
            position="relative",
            border_radius="md",
            overflow="hidden",
        ),
        # 👇 Aquí van las props del <div>
        on_touch_start=BlogViewState.on_touch_start,
        on_touch_end=BlogViewState.on_touch_end,
        on_mouse_down=BlogViewState.on_touch_start,
        on_mouse_up=BlogViewState.on_touch_end,
    )

def _info_section() -> rx.Component:
    return rx.vstack(
        rx.text(BlogViewState.post.title, size="7", font_weight="bold", margin_bottom="0.5em", text_align="left"),
        rx.text(BlogViewState.formatted_price, size="6", color="gray", text_align="left"),
        rx.text(BlogViewState.content, size="4", margin_top="1em", white_space="pre-wrap", text_align="left"),
        padding="1em",
        align="start",
        width="100%",
    )
