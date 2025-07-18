# full_stack_python/blog/public_detail.py (CÓDIGO CORREGIDO Y COMPLETO)

import reflex as rx
import reflex_local_auth
from..navigation.state import NavState
from .state import BlogViewState
from .. import navigation
from ..navigation.device import NavDeviceState
from ..navigation.state import force_reload_go_to
from ..ui.base import public_layout
from ..ui.base import fixed_color_mode_button
from ..ui.search_state import SearchState
from ..ui.nav import public_navbar # Importamos la public_navbar unificada
from ..ui.carousel import carousel 



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
    """Layout autónomo que ahora incluye el lightbox."""
    return rx.fragment(
        public_navbar(),
        rx.box(
            child,
            padding_y="2em",
            padding_top="6rem",
            width="100%",
            margin="0 auto",
        ),
        fixed_color_mode_button(),
        # 👇 Añadimos el componente lightbox al layout
        lightbox(
            open=BlogViewState.is_lightbox_open,
            close=BlogViewState.close_lightbox,
            slides=BlogViewState.lightbox_slides,
        )
    )

# --- PÁGINA DE DETALLE MODIFICADA ---
def image_with_expand_button(image_url: str) -> rx.Component:
    """Crea una caja con una imagen y un botón de expandir superpuesto."""
    return rx.box(
        rx.image(
            src=rx.get_upload_url(image_url),
            width="100%",
            height="auto",
            max_height="550px",
            object_fit="contain",
        ),
        rx.icon_button(
            rx.icon(tag="expand"),
            on_click=BlogViewState.open_modal(rx.get_upload_url(image_url)),
            position="absolute",
            top="0.5em",
            right="0.5em",
            variant="soft",
            cursor="pointer",
        ),
        position="relative",
    )

def _image_section() -> rx.Component:
    """Sección para el carrusel de imágenes."""
    return carousel(
        rx.foreach(
            BlogViewState.post.images,
            image_with_expand_button
        ),
        show_indicators=True,
        infinite_loop=True,
        emulate_touch=True,
        show_thumbs=False,
        show_arrows=True,
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

def blog_public_detail_page() -> rx.Component:
    """Página que muestra el detalle de una publicación pública."""
    content_grid = rx.cond(
        BlogViewState.has_post,
        rx.grid(
            _image_section(),
            _info_section(),
            columns={"base": "1", "md": "2"},
            spacing="4",
            align_items="start",
            width="100%",
            max_width="1120px",
        ),
        rx.center(rx.text("Publicación no encontrada.", color="red"))
    )
    
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
    
    return public_layout(
        rx.fragment(
            page_content,
            # Modal para mostrar la imagen ampliada
            rx.radix.themes.dialog.root(
                rx.radix.themes.dialog.content(
                    rx.radix.themes.dialog.body(
                        rx.image(src=BlogViewState.modal_image_src, width="100%", height="auto", object_fit="contain")
                    ),
                    rx.radix.themes.dialog.close(
                         rx.button("Cerrar", on_click=BlogViewState.close_modal, margin_top="1em", cursor="pointer")
                    ),
                    style={"max_width": "80vw", "max_height": "90vh", "padding": "1em"},
                ),
                open=BlogViewState.show_modal,
                on_open_change=BlogViewState.close_modal,
            )
        )
    )

