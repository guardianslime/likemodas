# likemodas/pages/search_results.py

import reflex as rx

from likemodas.cart.state import CartState
from ..ui.base import base_page
from ..ui.search_state import SearchState
# Se corrige la importación si es necesario, aunque en tu archivo ya parece estar bien
from ..articles.list import article_public_list_component 

def search_results_page() -> rx.Component:
    """Página que muestra los resultados de la búsqueda."""
    return base_page(
        rx.center(
            rx.vstack(
                rx.heading(f"Resultados para: '{SearchState.search_term}'", size="7"),
                
                rx.cond(
                    SearchState.search_results,
                    # Si hay resultados, se muestra la rejilla (sin cambios aquí)
                    rx.grid(
                        rx.foreach(
                            SearchState.search_results,
                            lambda post: rx.box(
                                # ... (la estructura de la tarjeta de producto no cambia)
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
                    # --- ✨ CAMBIO CLAVE AQUÍ ✨ ---
                    # Si no hay resultados, mostramos el mensaje personalizado.
                    rx.center(
                        # Usamos un f-string para incluir el término de búsqueda en el mensaje.
                        rx.text(f"😔 No se encontraron publicaciones con el nombre: '{SearchState.search_term}'"),
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