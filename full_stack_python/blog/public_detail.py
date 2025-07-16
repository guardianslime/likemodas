# full_stack_python/blog/public_detail.py (CÓDIGO CORREGIDO Y COMPLETO)

import reflex as rx
import reflex_local_auth
from .state import BlogViewState
from .. import navigation
from ..navigation.device import NavDeviceState
from ..navigation.state import force_reload_go_to
from ..ui.base import fixed_color_mode_button
from ..ui.search_state import SearchState

# La navbar local no cambia, ya es correcta.
def _detail_page_navbar() -> rx.Component:
    """Una barra de navegación local solo para esta página, con estilo garantizado y recarga forzada."""
    return rx.box(
        rx.hstack(
            rx.hstack(
                rx.menu.root(
                    rx.menu.trigger(
                        rx.button(rx.icon("menu", size=24), variant="soft", size="3")
                    ),
                    rx.menu.content(
                        rx.menu.item("Home", on_click=force_reload_go_to(navigation.routes.HOME_ROUTE)),
                        rx.menu.item("Productos", on_click=force_reload_go_to(navigation.routes.BLOG_PUBLIC_PAGE_ROUTE)),
                        rx.menu.item("Pricing", on_click=force_reload_go_to(navigation.routes.PRICING_ROUTE)),
                        rx.menu.item("Contact", on_click=force_reload_go_to(navigation.routes.CONTACT_US_ROUTE)),
                        rx.menu.separator(),
                        rx.menu.item("Login", on_click=force_reload_go_to(reflex_local_auth.routes.LOGIN_ROUTE)),
                        rx.menu.item("Register", on_click=force_reload_go_to(reflex_local_auth.routes.REGISTER_ROUTE)),
                    ),
                ),
                rx.image(src="/logo.jpg", width="8em", height="auto", border_radius="md"),
                align="center",
                spacing="4",
            ),
            rx.input(
                placeholder="Buscar productos...",
                value=SearchState.search_term,
                on_change=SearchState.update_search,
                on_blur=SearchState.search_action,
                width=["60%", "65%", "70%", "72%"],
                height=["2.5em", "2.8em", "3em", "3.3em"],
                padding_x="4",
                border_radius="full",
            ),
            justify="between",
            align="center",
            width="100%",
        ),
        position="fixed", top="0", left="0", right="0",
        width="100%", padding="0.75rem 1rem", z_index="99",
        bg=rx.color_mode_cond("rgba(255, 255, 255, 0.8)", "rgba(29, 35, 48, 0.8)"),
        style={"backdrop_filter": "blur(10px)"},
        on_mount=NavDeviceState.on_mount,
    )

def standalone_public_layout(child: rx.Component) -> rx.Component:
    """Layout autónomo que usa la navbar local."""
    return rx.fragment(
        _detail_page_navbar(),
        rx.box(
            child,
            # Se elimina el padding superior de aquí para controlarlo en el contenedor principal
            padding_y="2em",
            width="100%",
            margin="0 auto",
        ),
        fixed_color_mode_button(),
    )

# --- PÁGINA DE DETALLE MODIFICADA ---
def blog_public_detail_page() -> rx.Component:
    """Página que muestra el detalle de una publicación pública con un layout controlado."""
    
    # El grid del producto se mantiene igual.
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
    
    # ✨ CAMBIO RADICAL: Se reemplaza rx.center y rx.vstack por un único rx.box con estilos directos.
    # Esto nos da control total sobre el layout para que coincida con la captura.
    page_content = rx.box(
        rx.heading("Detalle del Producto", size="8"),
        content_grid,
        # --- Parámetros de estilo para forzar el layout ---
        display="flex",              # Usa Flexbox para alinear
        flex_direction="column",     # Apila los elementos verticalmente
        align_items="center",        # Centra los elementos horizontalmente
        justify_content="center",    # Centra el bloque verticalmente (opcional)
        spacing="6",                 # Espacio entre el título y el producto
        width="100%",
        padding_top="6rem",          # Espacio para la navbar fija
        padding_x="2em",             # Padding horizontal
        min_height="100vh",          # Ocupa toda la altura de la pantalla
    )
    
    # Usamos el layout autónomo como antes, pero ahora con el contenido estilizado.
    return standalone_public_layout(page_content)


# --- El resto de los componentes (_image_section, _info_section) no cambian ---
def _image_section() -> rx.Component:
    return rx.box(
        rx.image(
            src=rx.cond(
                BlogViewState.imagen_actual != "",
                rx.get_upload_url(BlogViewState.imagen_actual),
                "/no_image.png"
            ),
            width="100%", height="auto", max_height="550px",
            object_fit="contain", border_radius="md",
        ),
        rx.icon(tag="arrow_big_left", position="absolute", left="0.5em", top="50%", transform="translateY(-50%)", on_click=BlogViewState.anterior_imagen, cursor="pointer", box_size="2em"),
        rx.icon(tag="arrow_big_right", position="absolute", right="0.5em", top="50%", transform="translateY(-50%)", on_click=BlogViewState.siguiente_imagen, cursor="pointer", box_size="2em"),
        width="100%", max_width="600px", position="relative",
        border_radius="md", overflow="hidden"
    )

def _info_section() -> rx.Component:
    return rx.vstack(
        rx.text(BlogViewState.post.title, size="7", font_weight="bold", margin_bottom="0.5em", text_align="left"),
        rx.text(BlogViewState.formatted_price, size="6", color="gray", text_align="left"),
        rx.text(BlogViewState.content, size="4", margin_top="1em", white_space="pre-wrap", text_align="left"),
        padding="1em", align="start", width="100%",
    )