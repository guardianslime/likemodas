import reflex as rx
# Se importa base_page para usarlo como layout principal
from..ui.base import base_page 
from full_stack_python.blog.state import BlogPublicState
from full_stack_python.navigation import routes
from full_stack_python.models import BlogPostModel # Asegúrate de importar el modelo

# --- ✨ NUEVA FUNCIÓN AUXILIAR PARA LA TARJETA ✨ ---
# Extraer la lógica de la tarjeta a su propia función mejora la legibilidad
# y facilita la reutilización si fuera necesario.
def _create_public_post_card(post: BlogPostModel) -> rx.Component:
    """Crea el componente de tarjeta para una publicación pública."""
    return rx.box(
        rx.link(
            rx.vstack(
                rx.box(
                    rx.cond(
                        post.images & (post.images.length() > 0),
                        rx.image(
                            src=rx.get_upload_url(post.images),
                            width="100%",
                            height="100%",
                            object_fit="cover",
                            border_radius="md",
                            style={
                                "transition": "transform 0.3s ease-in-out",
                                "_hover": {
                                    "transform": "scale(1.05)"
                                }
                            }
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
                    width="100%", # Cambiado de 260px a 100% para que se adapte a la columna
                    height="260px" # La altura puede permanecer fija o hacerse responsiva
                ),
                rx.text(
                    post.title,
                    weight="bold",
                    size="6",
                    padding_left="3px",
                    white_space="normal",
                    word_break="break-word",
                    color=rx.color_mode_cond("black", "white"),
                ),
                rx.text(
                    rx.cond(
                        post.price,
                        "$" + post.price.to(str),
                        "$0.00"
                    ),
                    color=rx.color_mode_cond("black", "white"),
                    size="6",
                    padding_left="3px",
                    white_space="normal",
                    word_break="break-word"
                ),
                spacing="2",
                align="start"
            ),
            href=f"{routes.BLOG_PUBLIC_DETAIL_ROUTE}/{post.id}"
        ),
        bg=rx.color_mode_cond("#f9f9f9", "#111111"),
        border=rx.color_mode_cond("1px solid #e5e5e5", "1px solid #1a1a1a"),
        border_radius="8px",
        box_shadow="md",
        min_height="380px"
    )

# --- ✨ FUNCIÓN DE PÁGINA REFACTORIZADA ✨ ---
def blog_public_page():
    """Página pública que muestra la galería de productos con un layout responsivo único."""

    my_child = rx.center(
        rx.vstack(
            rx.heading("Publicaciones", size="6"),
            
            # Se reemplazan los tres bloques mobile/tablet/desktop por una única rejilla.
            rx.grid(
                # rx.foreach itera sobre los posts y llama a la función auxiliar para cada uno.
                rx.foreach(
                    BlogPublicState.posts,
                    _create_public_post_card
                ),
                
                # Esta es la única línea necesaria para toda la lógica de responsividad.
                # - auto-fit: El navegador decide cuántas columnas caben.
                # - minmax(280px, 1fr): Cada columna tendrá un mínimo de 280px de ancho
                #   y crecerá para llenar el espacio sobrante.
                columns="repeat(auto-fit, minmax(280px, 1fr))",
                
                spacing="6",
                width="100%",
                max_width="1400px", # Un max_width para la rejilla en pantallas muy grandes.
                justify_content="center"
            ),
            
            spacing="6",
            width="100%",
            padding="2em",
            align="center"
        ),
        width="100%"
    )
    
    # Se envuelve el contenido con base_page para asegurar la consistencia.
    return base_page(my_child)