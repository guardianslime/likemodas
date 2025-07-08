import reflex as rx
from .state import BlogViewState

def blog_post_view_page():
    return rx.center(
        rx.cond(
            BlogViewState.post != None,
            rx.vstack(
                rx.heading(BlogViewState.post.title),
                rx.cond(
                    BlogViewState.imagen_actual != "",
                    rx.image(src=rx.get_upload_url(BlogViewState.imagen_actual), width="400px"),
                    rx.text("Sin imagen")
                ),
                rx.hstack(
                    rx.button("Anterior", on_click=BlogViewState.anterior_imagen, disabled=BlogViewState.img_idx == 0),
                    rx.button("Siguiente", on_click=BlogViewState.siguiente_imagen, disabled=BlogViewState.img_idx >= BlogViewState.post.images.length() - 1),
                ),
                rx.text(f"Precio: ${BlogViewState.post.price:.2f}"),
                rx.text(BlogViewState.post.content),
                padding="2em"
            ),
            rx.text("Cargando publicación...")
        )
    )
