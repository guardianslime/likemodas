import reflex as rx
from ..ui.base import base_page
from .state import BlogState

def render_post_card(post: dict) -> rx.Component:
    """Componente que renderiza una tarjeta para un post individual."""
    return rx.card(
        rx.vstack(
            # Muestra la primera imagen como portada, si existe alguna
            rx.cond(
                post["images"],
                rx.image(
                    src=rx.get_upload_url(post["images"][0]),
                    width="100%",
                    height="16em",
                    object_fit="cover",
                ),
                # Muestra un placeholder si no hay imágenes
                rx.box(
                    rx.icon("image-off", size=48, color="gray"),
                    width="100%",
                    height="16em",
                    bg=rx.color("gray", 3),
                    display="flex",
                    align_items="center",
                    justify_content="center",
                    border_radius="var(--radius-3)",
                )
            ),
            rx.heading(post["title"], size="5", margin_top="0.5em"),
            rx.text(post["content"], white_space="pre-wrap", no_of_lines=4), # Muestra un extracto
            
            # Galería de todas las imágenes del post
            rx.text("Imágenes:", weight="bold", margin_top="1em"),
            rx.flex(
                rx.foreach(
                    post["images"],
                    lambda img: rx.image(src=rx.get_upload_url(img), height="5em", width="auto", border_radius="md", shadow="sm")
                ),
                spacing="2",
                wrap="wrap",
            ),
            
            rx.button(
                "Eliminar Post", 
                on_click=lambda: BlogState.eliminar_post(post["id"]),
                color_scheme="red",
                variant="soft",
                margin_top="1em"
            ),
            spacing="3",
            align="start",
            width="100%"
        )
    )

def blog_list_page() -> rx.Component:
    """Página principal que muestra todos los posts en memoria."""
    return base_page(
        rx.vstack(
            rx.hstack(
                rx.heading("Mi Blog", size="8"),
                rx.spacer(),
                rx.link(rx.button("Añadir Nuevo Post", size="3"), href="/blog/add"),
                justify="between",
                align="center",
                width="100%"
            ),
            rx.divider(margin_y="1.5em"),
            rx.cond(
                BlogState.posts,
                rx.responsive_grid(
                    rx.foreach(BlogState.posts, render_post_card),
                    columns=[1, 2, 3],
                    spacing="4",
                    width="100%"
                ),
                rx.center(
                    rx.text("Aún no hay publicaciones. ¡Añade una!", color_scheme="gray"),
                    height="50vh"
                )
            ),
            width="100%",
            max_width="1200px",
            margin="auto",
            padding="1em"
        )
    )

def blog_add_page() -> rx.Component:
    """Página con el formulario para añadir un nuevo post."""
    return base_page(
        rx.vstack(
            rx.heading("Crear Nuevo Post", size="8", text_align="center"),
            rx.input(
                placeholder="Título de la publicación",
                on_change=lambda value: BlogState.set_form_field("title", value),
                size="3",
                width="100%"
            ),
            rx.text_area(
                placeholder="Escribe tu contenido aquí...",
                on_change=lambda value: BlogState.set_form_field("content", value),
                size="3",
                height='25vh',
                width='100%'
            ),
            rx.upload(
                rx.vstack(
                    rx.button("Seleccionar Archivos", color_scheme="gray", variant="soft"),
                    rx.text("o arrastra imágenes aquí."),
                    align="center"
                ),
                border="2px dashed #60a5fa",
                padding="3em",
                width="100%",
                multiple=True,
                on_drop=BlogState.handle_upload(rx.upload_files()),
            ),
            rx.cond(
                BlogState.imagenes_temporales,
                rx.box(
                    rx.text("Previsualización de imágenes:", weight="bold"),
                    rx.flex(
                        rx.foreach(
                            BlogState.imagenes_temporales,
                            lambda img: rx.box(
                                rx.image(src=rx.get_upload_url(img), height="6em", width="auto", border_radius="md"),
                                rx.icon(
                                    tag="trash",
                                    on_click=lambda: BlogState.eliminar_imagen_temp(img),
                                    position="absolute", top="4px", right="4px", cursor="pointer",
                                    padding="0.2em", bg="rgba(255, 255, 255, 0.7)", color="red", border_radius="full"
                                ),
                                position="relative"
                            )
                        ),
                        spacing="3", wrap="wrap", margin_top="0.5em"
                    ),
                    width="100%", padding="1em", border="1px solid", border_color=rx.color("gray", 5), border_radius="md"
                )
            ),
            rx.button("Publicar Post", on_click=BlogState.publicar_post, size="3", width="100%", color_scheme="green"),
            spacing="5",
            width="100%",
            max_width="800px",
            margin="auto",
            padding="2em"
        )
    )