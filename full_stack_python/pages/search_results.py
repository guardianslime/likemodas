# full_stack_python/pages/search_results.py

import reflex as rx

from full_stack_python.cart.state import CartState
from ..ui.base import base_page
from ..ui.search_state import SearchState
from ..articles.list import article_public_list_component # Reutilizamos el componente de la galería

def search_results_page() -> rx.Component:
    """Página que muestra los resultados de la búsqueda."""
    return base_page(
        rx.center(
            rx.vstack(
                # Título dinámico que muestra lo que se buscó
                rx.heading(f"Resultados para: '{SearchState.search_term}'", size="7"),
                
                rx.cond(
                    # Verificamos si hay resultados
                    SearchState.search_results,
                    # Si hay resultados, los mostramos en una rejilla
                    rx.grid(
                        rx.foreach(
                            SearchState.search_results,
                            # Reutilizamos la tarjeta de producto existente
                            lambda post: rx.box(
                                # ... (copiamos la estructura de la tarjeta de blog_public_page)
                                rx.vstack(
                                    rx.link(
                                        rx.vstack(
                                            rx.box(
                                                rx.cond(
                                                    post.images & (post.images.length() > 0),
                                                    rx.image(src=rx.get_upload_url(post.images[0]), width="100%", height="260px", object_fit="cover", border_radius="md"),
                                                    rx.box("Sin imagen", width="100%", height="260px", bg="#eee", align="center", justify="center", display="flex", border_radius="md")
                                                ),
                                                width="260px", height="260px"
                                            ),
                                            rx.text(post.title, weight="bold", size="6", color=rx.color_mode_cond("black", "white")),
                                            rx.text(rx.cond(post.price, "$" + post.price.to_string(), "$0.00"), color=rx.color_mode_cond("black", "white"), size="6"),
                                            spacing="2", align="start"
                                        ),
                                        href=f"/blog-public/{post.id}"
                                    ),
                                    rx.button(
                                        "Añadir al Carrito",
                                        on_click=lambda: CartState.add_to_cart(post.id),
                                        width="100%",
                                        margin_top="0.5em"
                                    ),
                                    align="start", spacing="2"
                                ),
                                bg=rx.color_mode_cond("#f9f9f9", "#111111"),
                                border=rx.color_mode_cond("1px solid #e5e5e5", "1px solid #1a1a1a"),
                                border_radius="8px",
                                box_shadow="md",
                                padding="1em",
                                min_height="380px"
                            )
                        ),
                        columns={"base": "2", "md": "3", "lg": "6"},
                        spacing="6",
                        width="100%",
                    ),
                    # Si no hay resultados, mostramos un mensaje
                    rx.center(
                        rx.text("😔 No se encontraron publicaciones que coincidan con tu búsqueda."),
                        padding="4em",
                        min_height="40vh"
                    )
                ),
                spacing="6",
                width="100%",
                padding="2em",
                align="center"
            ),
            width="100%"
        )
    )