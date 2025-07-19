import reflex as rx
from ..ui.base import base_page 
from ..blog.state import BlogPublicState # Usamos el estado público que ya funciona
from ..navigation import routes

def _gallery_card(post):
    """Una tarjeta de la galería para un artículo."""
    return rx.box(
        rx.link(
            rx.vstack(
                rx.box(
                    rx.cond(
                        post.images & (post.images.length() > 0),
                        rx.image(
                            src=rx.get_upload_url(post.images[0]),
                            width="100%",
                            height="100%",
                            object_fit="cover",
                            border_radius="md",
                            style={"_hover": {"transform": "scale(1.05)"}}
                        ),
                        rx.box(
                            "Sin imagen",
                            width="100%",
                            height="100%",
                            bg="#eee",
                            align="center",
                            justify="center",
                            display="flex",
                            border_radius="md"
                        )
                    ),
                    position="relative",
                    width="260px",
                    height="260px"
                ),
                rx.text(
                    post.title,
                    weight="bold",
                    size="6",
                    color=rx.color_mode_cond("black", "white"),
                ),
                rx.text(
                    rx.cond(post.price, "$" + post.price.to(str), "$0.00"),
                    color=rx.color_mode_cond("black", "white"),
                    size="6",
                ),
                spacing="2",
                align="start"
            ),
            href=f"{routes.ARTICLE_LIST_ROUTE}/{post.id}"
        ),
        bg=rx.color_mode_cond("#f9f9f9", "#111111"),
        border=rx.color_mode_cond("1px solid #e5e5e5", "1px solid #1a1a1a"),
        border_radius="8px",
        box_shadow="md",
        min_height="380px"
    )

# --- ✨ COMPONENTE REUTILIZABLE CREADO ✨ ---
def article_public_list_component(columns: int = 4, limit: int = 100) -> rx.Component:
    """Un componente que muestra una rejilla de artículos públicos."""
    # Aunque el 'limit' se controla en el estado, se mantiene en la firma por consistencia.
    # La prop 'columns' aquí no se usa directamente, se define en el grid que lo llama.
    return rx.grid(
        rx.foreach(
            BlogPublicState.posts,
            _gallery_card
        ),
        columns={
            "base": "2",
            "md": "3",
            "lg": str(columns), # Usa el parámetro para definir las columnas
        },
        spacing="6",
        width="100%",
        max_width="11200px",
        justify_content="center"
    )

# --- PÁGINA PÚBLICA ACTUALIZADA PARA USAR EL COMPONENTE ---
def articles_public_gallery_page() -> rx.Component:
    """Página que muestra la galería de productos en la ruta /articles."""
    return base_page(
        rx.center(
            rx.vstack(
                rx.heading("Galería de Publicaciones", size="7"),
                # Ahora la página simplemente llama al componente reutilizable
                article_public_list_component(columns=6),
                spacing="6",
                width="100%",
                padding="2em",
                align="center"
            ),
            width="100%"
        )
    )