import reflex as rx
from .state import BlogViewState

def blog_post_view_page():
    return rx.center(
        rx.cond(
            BlogViewState.post & (BlogViewState.post.images != None),
            rx.vstack(
                rx.image(
                    src=rx.get_upload_url(BlogViewState.imagen_actual),
                    width="400px"
                ),
                rx.hstack(
                    rx.button(
                        "←",
                        on_click=BlogViewState.anterior_imagen,
                        disabled=BlogViewState.img_idx == 0
                    ),
                    rx.button(
                        "→",
                        on_click=BlogViewState.siguiente_imagen,
                        disabled=BlogViewState.img_idx == rx.len(BlogViewState.post.images) - 1
                    ),
                ),
                rx.text(f"Precio: ${BlogViewState.post.price}", weight="bold"),
                rx.text(BlogViewState.post.content),
            ),
            rx.text("Cargando publicación o no disponible."),
        )
    )
