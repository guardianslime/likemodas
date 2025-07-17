import reflex as rx
import reflex_local_auth
from..navigation.state import NavState
from .state import BlogViewState
from .. import navigation
from ..navigation.device import NavDeviceState
from ..navigation.state import force_reload_go_to
from ..ui.base import fixed_color_mode_button
from ..ui.search_state import SearchState
from ..ui.nav import public_navbar

# --- Se importa el componente de carrusel ---
from ..ui.carousel import swiper_carousel


# Esta función se mantiene según tu estructura original.
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
                border_width="1px",
                font_size=rx.breakpoints(sm="2", md="3", lg="3"),
            ),
            justify="between",
            align="center",
            width="100%",
        ),
        position="fixed",
        top="0",
        left="0",
        right="0",
        width="100%",
        padding="0.75rem 1rem",
        z_index="99",
        bg=rx.color_mode_cond("#ffffffF0", "#1D2330F0"),
        style={"backdrop_filter": "blur(10px)"},
        on_mount=NavDeviceState.on_mount,
    )

# Esta función se mantiene según tu estructura original.
def standalone_public_layout(child: rx.Component) -> rx.Component:
    """Layout autónomo que usa la navbar local."""
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
    )

# --- PÁGINA DE DETALLE MODIFICADA ---
def blog_public_detail_page() -> rx.Component:
    """Página que muestra el detalle de una publicación pública."""
    
    content_grid = rx.cond(
        BlogViewState.has_post,
        rx.grid(
            # --- ✨ CORRECCIÓN AQUÍ: Se pasa un ID único al carrusel ✨ ---
            swiper_carousel(image_urls=BlogViewState.post_image_urls, carousel_id="public-detail-page"),
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
    
    return standalone_public_layout(page_content)


# --- Se elimina la función _image_section ya que fue reemplazada por el carrusel ---
# (Esta sección ya estaba eliminada en el código que me pasaste, lo cual es correcto)

# Esta función se mantiene según tu estructura original.
def _info_section() -> rx.Component:
    return rx.vstack(
        rx.text(BlogViewState.post.title, size="7", font_weight="bold", margin_bottom="0.5em", text_align="left"),
        rx.text(BlogViewState.formatted_price, size="6", color="gray", text_align="left"),
        rx.text(BlogViewState.content, size="4", margin_top="1em", white_space="pre-wrap", text_align="left"),
        padding="1em",
        align="start",
        width="100%",
    )